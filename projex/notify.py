#!/usr/bin/python

""" Provides methods for notification routes such as email, IM, SMS, etc. """

# define authorship information
__authors__         = ['Eric Hulser']
__author__          = ','.join(__authors__)
__credits__         = []
__copyright__       = 'Copyright (c) 2011, Projex Software'
__license__         = 'LGPL'

# maintanence information
__maintainer__      = 'Projex Software'
__email__           = 'team@projexsoftware.com'

#------------------------------------------------------------------------------

import base64
import datetime
import os
import re
import socket
import smtplib
import logging

import projex.text

# support windows server
try:
    import sspi
except ImportError:
    sspi = None

# support python26+
try:
    from email.mime.multipart import MIMEMultipart
    from email.mime.image import MIMEImage
    from email.mime.text import MIMEText
    from email.mime.base import MIMEBase
    from email.encoders import encode_base64

# support previous versions of python
except ImportError:
    from email.Encoders import encode_base64
    from email import MIMEMultipart,\
                      MIMEImage,\
                      MIMEText,\
                      MIMEBase

logger = logging.getLogger(__name__)

from projex    import  errors, \
                       regex

NOTIFY_SERVER               = os.getenv('PROJEX_NOTIFY_SERVER','localhost')
NOTIFY_SERVER_MSX = os.getenv('PROJEX_NOTIFY_SERVER_MSX', 'False') == 'True'
NOTIFY_IM_DOMAIN_SENDER     = os.getenv('PROJEX_NOTIFY_IM_DOMAIN_SENDER', '')
NOTIFY_IM_DOMAIN_RECEIVER   = os.getenv('PROJEX_NOTIFY_IM_DOMAIN_RECEIVER', '')

SMTP_EHLO_OKAY = 250
SMTP_AUTH_CHALLENGE = 334
SMTP_AUTH_OKAY = 235

def connectMSExchange(server):
    """
    Creates a connection for the inputed server to a Microsoft Exchange server.
    
    :credit     http://stackoverflow.com/questions/2916396/smtp-through-exchange-using-integrated-windows-authentication-ntlm-using-pytho
    
    :param      server | <smtplib.SMTP>
    
    :usage      |>>> import smtplib
                |>>> import projex.notify
                |>>> smtp = smtplib.SMTP('mail.server.com')
                |>>> projex.notify.connectMSExchange(smtp)
    
    :return     (<bool> success, <str> reason)
    """
    if not sspi:
        return (False, 'No sspi module found.')
    
    # send the SMTP EHLO command
    code, response = server.ehlo()
    if code != SMTP_EHLO_OKAY:
        return (False, 'Server did not respond to EHLO command.')
    
    sspi_client = sspi.ClientAuth('NTLM')
    
    # generate NTLM Type 1 message
    sec_buffer = None
    err, sec_buffer = sspi_client.authorize(sec_buffer)
    buffer = sec_buffer[0].Buffer
    ntlm_message = base64.encodestring(buffer).replace('\n', '')
    
    # send NTLM Type 1 message -- Authentication Request
    code, response = server.docmd('AUTH', 'NTLM ' + ntlm_message)
    
    # verify the NTLM Type 2 response -- Challenge Message
    if code != SMTP_AUTH_CHALLENGE:
        msg = 'Server did not respond as expected to NTLM negotiate message'
        return (False, msg)
    
    # generate NTLM Type 3 message
    err, sec_buffer = sspi_client.authorize(base64.decodestring(response))
    buffer = sec_buffer[0].Buffer
    ntlm_message = base64.encodestring(buffer).replace('\n', '')
    
    # send the NTLM Type 3 message -- Response Message
    code, response = server.docmd('', ntlm_message)
    if code != SMTP_AUTH_OKAY:
        return (False, response)
    
    return (True, '')
    

def sendEmail(sender, 
              recipients, 
              subject, 
              body, 
              attachments = None, 
              cc = None,
              bcc = None, 
              contentType = 'text/html', 
              server = None,
              useMSExchange = None,
              encoding = 'utf-8'):
    """
    Sends an email from the inputed email address to the
    list of given recipients with the inputed subject and 
    body.  This will also attach the inputed list of 
    attachments to the email.  The server value will default 
    to mail.<sender_domain> and you can use a ':' to specify 
    a port for the server.
    
    :param      sender          <str>
    :param      recipients      <list> [ <str>, .. ]
    :param      subject         <str>
    :param      body            <str>
    :param      attachments     <list> [ <str>, .. ]
    :param      cc              <list> [ <str>, .. ]
    :param      bcc             <list> [ <str>, .. ]
    :param      contentType     <str>
    :param      server          <str>
    
    :return     <bool> success
    """
    if attachments == None:
        attachments = []
    if cc == None:
        cc = []
    if bcc == None:
        bcc = []
    
    if server is None:
        server = NOTIFY_SERVER
    if useMSExchange is None:
        useMSExchange = NOTIFY_SERVER_MSX
    
    # normalize the data
    sender      = str(sender)
    recipients  = map(str, recipients)
    
    # make sure we have valid information
    if ( not isEmail(sender) ):
        err = errors.NotifyError( '%s is not a valid email address' % sender )
        logger.error(err)
        return False
    
    # make sure there are recipients
    if ( not recipients ):
        err = errors.NotifyError( 'No recipients were supplied.' )
        logger.error(err)
        return False
    
    # build the server domain
    if ( not server ):
        err = errors.NotifyError( 'No email server specified' )
        logger.error(err)
        return False
    
    # create the email
    # pylint: disable-msg=E1101
    msg                 = MIMEMultipart( _subtype = 'related' )
    msg['Subject']      = projex.text.toUtf8(subject)
    msg['From']         = sender
    msg['To']           = ','.join(recipients)
    msg['Cc']           = ','.join([str(addr) for addr in cc if isEmail(addr)])
    msg['Date']         = str(datetime.datetime.now())
    msg['Content-type'] = 'Multipart/mixed'
    
    msg.preamble        = 'This is a multi-part message in MIME format.'
    msg.epilogue        = ''
    
    # build the body
    bodyhtml            = projex.text.toUtf8(body)
    eattach             = []
    
    # include inline images
    filepaths = re.findall('<img\s+src="(file:///[^"]+)"[^/>]*/?>', bodyhtml)
    for filepath in filepaths:
        filename = filepath.replace('file:///','')
        if os.path.exists(filename) and not filename in attachments:
            # replace with the attachment id
            cid         = 'cid:%s' % os.path.basename( filename )
            bodyhtml    = bodyhtml.replace( filename, cid )
            
            # add the image to the attachments
            fp = open( str(filename), 'rb' )
            msgImage = MIMEImage(fp.read())
            fp.close()
            
            # add the msg image to the msg
            content_id  = '<%s>' % os.path.basename( filename )
            inline_link = 'inline; filename="%s"' % os.path.basename(filename)
            msgImage.add_header( 'Content-ID', content_id )
            msgImage.add_header( 'Content-Disposition', inline_link )
            
            eattach.append(msgImage)
            attachments.append(filename)
    
    # create the body text
    msgText                 = MIMEText(bodyhtml, contentType, encoding)
    msgText['Content-type'] = contentType
    
    # include attachments
    for attach in attachments:
        fp = open( str(attach), 'rb' )
        txt = MIMEBase( 'application', 'octet-stream' )
        txt.set_payload( fp.read() )
        fp.close()
        
        encode_base64(txt)
        attachment = 'attachment; filename="%s"' % os.path.basename(attach)
        txt.add_header('Content-Disposition', attachment)
        eattach.append(txt)
    
    eattach.insert(0, msgText)
    
    # add the attachments to the message
    for attach in eattach:
        msg.attach(attach)
    
    # create the connection to the email server
    try:
        smtp_server = smtplib.SMTP(str(server))
    except socket.gaierror, err:
        logger.error(err)
        return False
    except Exception, err:
        logger.error(err)
        return False
    
    # connect to a microsoft exchange server if specified
    if useMSExchange:
        success, response = connectMSExchange(smtp_server)
        if not success:
            logger.debug('Could not connect to MS Exchange: ' + response)
    
    try:
        smtp_server.sendmail(sender, recipients, msg.as_string())
        smtp_server.close()
    except Exception, err:
        logger.error(err)
        return False
    
    return True

def sendIm( sender, 
            password, 
            receivers, 
            body, 
            senderDomain = NOTIFY_IM_DOMAIN_SENDER, 
            receiverDomain = NOTIFY_IM_DOMAIN_RECEIVER ):
    """
    Sends an instant message to the inputed receivers from the
    given user.  The senderDomain is an override to be used 
    when no domain is supplied, same for the receiverDomain.
    
    :param      sender          <str>
    :param      password        <str>
    :param      receivers       <list> [ <str>, .. ]
    :param      body            <str>
    :param      senderDomain    <str>   
    :param      receiverDomain  <str>
    
    :return     <bool> success
    """
    # pylint: disable-msg=F0401
    try:
        import xmpp
        
    except ImportError:
        err = errors.NotifyError( 'xmpp python library was not found' )
        logger.error(err)
        return False
    
    # make sure there is a proper domain as part of the sender 
    if ( not '@' in sender ):
        sender += '@' + senderDomain
    
    # create a jabber user connection
    print sender
    user     = xmpp.protocol.JID(sender)
    
    # create a connection to an xmpp client
    client  = xmpp.Client( user.getDomain(), debug = [] )
    connection = client.connect( secure = 0, use_srv = False )
    if ( not connection ):
        text = 'Could not create a connection to xmpp (%s)' % sender
        err = errors.NotifyError( text )
        logger.error(err)
        return False
    
    # authenticate the session
    auth = client.auth( user.getNode(), password, user.getResource() )
    if ( not auth ):
        text = 'Jabber not authenticated: (%s, %s)' % (sender, password)
        err = errors.NotifyError( text )
        logger.error(err)
        return False
    
    count = 0
    
    # send the message to the inputed receivers
    for receiver in receivers:
        if ( not '@' in receiver ):
            receiver += '@' + receiverDomain
        
        # create the message
        msg = xmpp.protocol.Message( receiver, body )
        
        # create the html message
        html_http = { 'xmlns': 'http://jabber.org/protocol/xhtml-im' }
        html_node = xmpp.Node( 'html', html_http )
        enc_msg   = body.encode('utf-8')
        xml = '<body xmlns="http://www.w3.org/1999/xhtml">%s</body>' % enc_msg
        html_node.addChild( node = xmpp.simplexml.XML2Node( xml ) )
        
        msg.addChild( node = html_node )
        
        client.send( msg )
        count += 1  
    
    return count > 0

def isEmail( address ):
    """
    Checks to make sure that the inputed address 
    follows proper web email address formatting
    
    :param      address     <str>
    
    :return     <bool> success
    """
    return re.match(regex.EMAIL, str(address)) != None