#!/usr/bin/python

""" Defines common commands that can be used to streamline ui development. """

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

import binascii
import imp
import os
import re
import subprocess
import sys

import projex.text

from xml.etree import ElementTree

from PyQt4 import QtCore,\
                  QtGui,\
                  QtXml,\
                  QtWebKit,\
                  QtNetwork,\
                  uic

#from projexui.widgets.xviewwidget import XView
from projexui.widgets import xviewwidget #import XView

USE_COMPILED = os.environ.get('PROJEXUI_USE_COMPILED', '').lower() == 'true'
QT_WRAPPER   = os.environ.get('PROJEXUI_QT_WRAPPER', 'PyQt4')

def ancestor(qobject, classType):
    """
    Looks up the ancestor of the inputed QObject based on the given class type.
    
    :param      qobject   | <QObject>
                classType | <subclass of QObject> || <str>
    
    :return     <subclass of QObject> || None
    """
    parent = qobject
    is_class = True
    while parent:
        if type(parent).__name__ == classType:
            break
        
        if is_class:
            try:
                if isinstance(parent, classType): break
            except TypeError:
                is_class = False
        
        parent = parent.parent()
    
    return parent

def buildResourceFile(rscpath, outpath=''):
    """
    Generates a Qt resource module based on the given source path.  This will
    take all the files and folders within the source and generate a new XML
    representation of that path.  An optional outpath can be provided as the
    generated resource path, by default it will be called the name of the
    source path.
    
    :param      rscpath | <str>
                buildpath | <str>
    """
    if not outpath:
        filename = os.path.basename(rscpath).split('.')[0] + '_rc.py'
        outpath = os.path.join(os.path.dirname(rscpath), filename)
    
    # make sure it is not outdated
    subprocess.call(['%s-rcc.exe' % QT_WRAPPER.lower(), '-o', outpath, rscpath])

def generateUiClasses(srcpath):
    """
    Generates the UI classes using the compilation system for Qt.
    
    :param      srcpath | <str>
    """
    import_qt(globals())
    
    for root, folders, files in os.walk(srcpath):
        for file in files:
            name, ext = os.path.splitext(file)
            if ext != '.ui':
                continue
            
            wrapper = '_' + QT_WRAPPER.lower()
            outfile = os.path.join(root, name + wrapper + '_ui.py')
            f = open(outfile, 'w')
            uic.compileUi(os.path.join(root, file), f)
            f.close()

def generateResourceFile(srcpath, outpath='', buildpath='', build=True):
    """
    Generates a Qt resource file based on the given source path.  This will
    take all the files and folders within the source and generate a new XML
    representation of that path.  An optional outpath can be provided as the
    generated resource path, by default it will be called the name of the
    source path.
    
    :param      srcpath | <str>
                outpath | <str>
    """
    if not outpath:
        outpath = os.path.join(os.path.dirname(srcpath), 
                               os.path.basename(srcpath) + '.qrc')
        relpath = './%s' % os.path.basename(srcpath)
    else:
        relpath = os.path.relpath(srcpath, os.path.dirname(outpath))
    
    xml = ElementTree.Element('RCC')
    xml.set('header', 'projexui.resources')
    srcpath = os.path.normpath(str(srcpath)).replace('\\', '/')
    for root, folders, files in os.walk(srcpath):
        prefix = os.path.normpath(root).replace('\\', '/')
        prefix = prefix.replace(srcpath, '').strip('/')
        
        xresource = ElementTree.SubElement(xml, 'qresource')
        if prefix:
            xresource.set('prefix', prefix)
        
        for file in files:
            xfile = ElementTree.SubElement(xresource, 'file')
            xfile.set('alias', file)
            xfile.text = os.path.join(relpath, prefix, file).replace('\\', '/')
    
    projex.text.xmlindent(xml)
    xml_str = ElementTree.tostring(xml)
    
    # save the exported information
    f = open(outpath, 'w')
    f.write(xml_str)
    f.close()
    
    if build:
        buildResourceFile(outpath, buildpath)

def generatePixmap(base64_data):
    """
    Generates a new pixmap based on the inputed base64 data.
    
    :param      base64 | <str>
    """
    import_qt(globals())
    
    binary_data = binascii.a2b_base64(base64_data)
    arr = QtCore.QByteArray.fromRawData(binary_data)
    img = QtGui.QImage.fromData(arr)
    return QtGui.QPixmap(img)

def import_qt(glbls):
    """ Delayed qt loader. """
    if 'QtCore' in glbls:
        return
        
    #from projexui.qt import QtCore, QtGui, wrapVariant, uic
    #from projexui.widgets.xloggersplashscreen import XLoggerSplashScreen
    
    glbls['QtCore'] = QtCore
    glbls['QtGui'] = QtGui
    glbls['wrapVariant'] = wrapVariant
    glbls['uic'] = uic
    glbls['XLoggerSplashScreen'] = XLoggerSplashScreen

def findUiActions( widget ):
    """
    Looks up actions for the inputed widget based on naming convention.
    
    :param      widget | <QWidget>
    
    :return     [<QAction>, ..]
    """
    import_qt(globals())
    
    output = []
    for action in widget.findChildren(QtGui.QAction):
        name = str(action.objectName()).lower()
        if ( name.startswith('ui') and name.endswith('act') ):
            output.append(action)
    return output

def localizeShortcuts(widget):
    """
    Shifts all action shortcuts for the given widget to us the
    WidgetWithChildrenShortcut context, effectively localizing it to this
    widget.
    
    :param      widget | <QWidget>
    """
    import_qt(globals())
    
    for action in widget.findChildren(QtGui.QAction):
        action.setShortcutContext(QtCore.Qt.WidgetWithChildrenShortcut)

def loadUi(modulefile, inst, uifile=None):
    """
    Load the ui file based on the module file location and the inputed class.
    
    :param      modulefile  | <str>
                inst        | <subclass of QWidget>
                uifile      | <str> || None
    
    :return     <QWidget>
    """
    import_qt(globals())
    
    currpath = QtCore.QDir.currentPath()
    
    if not uifile:
        uifile = uiFile(modulefile, inst)
    
    # use compiled information vs. dynamic generation
    widget = None
    if USE_COMPILED:
        path, name = os.path.split(uifile)
        wrapper = '_' + QT_WRAPPER.lower()
        modulepath = os.path.join(path, name.replace('.ui', wrapper + '_ui.py'))
        
        if os.path.exists(modulepath):
            name = os.path.basename(modulepath).split('.')[0]
            file, pathname = os.path.split(modulepath)
            
            # import the module
            module = sys.modules.get(name)
            
            if not module:
                f = open(modulepath, 'r')
                module = imp.load_module(name,
                                         f,
                                         pathname,
                                         ('.py', 'r', imp.PY_SOURCE))
                f.close()
            
            # load the module information
            cls = getattr(module, 'Ui_%s' % inst.__class__.__name__, None)
            if not cls:
                for key in module.__dict__.keys():
                    if key.startswith('Ui_'):
                        cls = getattr(module, key)
                        break
            
            # generate the class information
            if cls:
                widget = cls()
                widget.setupUi(inst)
                inst.__dict__.update(widget.__dict__)
    
    if not widget:
        # normalize the path
        print ("\nnot widget before uifile assignment: " + uifile)
        uifile = os.path.normpath(uifile)
        print ("\nnot widget after uifile assignment: " + uifile)
        QtCore.QDir.setCurrent(os.path.dirname(uifile))
        
        widget = uic.loadUi(uifile, inst)
        QtCore.QDir.setCurrent(currpath)
    
    inst.addActions(findUiActions(inst))
    
    return widget

def exec_( window, data ):
    """
    Executes the startup data for the given main window.  This method needs to 
    be called in conjunction with the setup method.
    
    :sa     setup
    
    :param      window  | <QWidget>
                data    | { <str> key: <variant> value, .. }
    
    :return     <int> err
    """
    import_qt(globals())
    
    if 'splash' in data:
        data['splash'].finish(window)
    
    if not window.parent():
        window.setAttribute(QtCore.Qt.WA_DeleteOnClose)
    
    if 'app' in data:
        # setup application information
        data['app'].setPalette(window.palette())
        data['app'].setWindowIcon(window.windowIcon())
        
        # connects the xview system to widget focusing
        #from projexui.widgets.xviewwidget import XView
        try:
            data['app'].focusChanged.connect(XView.updateCurrentView,
                                             QtCore.Qt.UniqueConnection)
        except:
            pass
        
        # create the tray menu
        if not window.windowIcon().isNull():
            menu   = QtGui.QMenu(window)
            action = menu.addAction('Quit')
            action.triggered.connect( window.close )
            
            # create the tray icon
            tray_icon = QtGui.QSystemTrayIcon(window)
            tray_icon.setObjectName('trayIcon')
            tray_icon.setIcon(window.windowIcon())
            tray_icon.setContextMenu(menu)
            tray_icon.setToolTip(data['app'].applicationName())
            tray_icon.show()
            window.destroyed.connect(tray_icon.deleteLater)
        
        return data['app'].exec_()
    
    return 0

def setup(applicationName,
          applicationType=None,
          style='plastique',
          splash='',
          splashType=None,
          splashTextColor='white',
          splashTextAlign=None):
    """
    Wrapper system for the QApplication creation process to handle all proper
    pre-application setup.  This method will verify that there is no application
    running, creating one if necessary.  If no application is created, a None
    value is returned - signaling that there is already an app running.  If you
    need to specify your own QApplication subclass, you can do so through the 
    applicationType parameter.
    
    :note       This method should always be used with the exec_ method to 
                handle the post setup process.
    
    :param      applicationName | <str>
                applicationType | <subclass of QApplication> || None
                style    | <str> || <QStyle> | style to use for the new app
                splash   | <str> | filepath to use for a splash screen
                splashType   | <subclass of QSplashScreen> || None
                splashTextColor   | <str> || <QColor>
                splashTextAlign   | <Qt.Alignment>
    
    :usage      |import projexui
                |
                |def main(argv):
                |   # initialize the application
                |   data = projexui.setup()
                |   
                |   # do some initialization code
                |   window = MyWindow()
                |   window.show()
                |   
                |   # execute the application
                |   projexui.exec_(window, data)
    
    :return     { <str> key: <variant> value, .. }
    """
    import_qt(globals())
    
    output = {}
    
    # check to see if there is a qapplication running
    if not QtGui.QApplication.instance():
        # make sure we have a valid QApplication type
        if applicationType is None:
            applicationType = QtGui.QApplication
        
        app = applicationType([applicationName])
        app.setApplicationName(applicationName)
        if style:
            app.setStyle(style)
        
        app.setQuitOnLastWindowClosed(True)
        
        # utilized with the projexui.config.xschemeconfig
        app.setProperty('useScheme', wrapVariant(True))
        output['app'] = app
    
    # create a new splash screen if desired
    if splash:
        if not splashType:
            splashType = XLoggerSplashScreen
        
        pixmap = QtGui.QPixmap(splash)
        screen = splashType(pixmap)
        
        if splashTextAlign is None:
            splashTextAlign = QtCore.Qt.AlignLeft | QtCore.Qt.AlignBottom
        
        screen.setTextColor(QtGui.QColor(splashTextColor))
        screen.setTextAlignment(splashTextAlign)
        screen.show()
        
        QtGui.QApplication.instance().processEvents()
        
        output['splash'] = screen
    
    return output

def topWindow():
    """
    Returns the very top window for all Qt purposes.
    
    :return     <QWidget> || None
    """
    import_qt(globals())
    
    window = QtGui.QApplication.instance().activeWindow()
    if not window:
        return None
    
    parent = window.parent()
    
    while ( parent ):
        window = parent
        parent = window.parent()
        
    return window

def testWidget( widgetType ):
    """
    Creates a new instance for the widget type, settings its properties \
    to be a dialog and parenting it to the base window.
    
    :param      widgetType  | <subclass of QWidget>
    """
    import_qt(globals())
    
    window = QtGui.QApplication.instance().activeWindow()
    widget = widgetType(window)
    widget.setWindowFlags(QtCore.Qt.Dialog)
    widget.show()
    
    return widget

def uiFile( modulefile, inst ):
    """
    Returns the ui file for the given instance and module file.
    
    :param      moduleFile | <str>
                inst       | <QWidget>
    
    :return     <str>
    """
    clsname     = inst.__class__.__name__.lower()
    basepath    = os.path.dirname(str(modulefile))
    uifile      = os.path.join(basepath, 'ui/%s.ui' % clsname)
    
    # strip out compiled filepath
    uifile      = re.sub('[\w\.]+\?\d+', '', uifile)
    return uifile