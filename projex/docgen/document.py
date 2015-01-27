#!/usr/bin/python

""" Defines the document class that is used with the docgen system. """

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

import inspect
import logging
import new
import os
import re
import xml.sax.saxutils

from projex              import text
from projex              import wikitext

from projex.docgen       import templates
from projex.docgen       import commands

logger = logging.getLogger(__name__)

DATA_TYPE_ORDER = [
    'module',
    'class',
    'variable',
    'member',
    'property',
    'enum',
    'function',
    'method',
    'signal',
    'slot',
    'abstract method',
    'class method',
    'static method',
    'deprecated method',
    'built-in',
]

DATA_PRIVACY_ORDER = [
    'public',
    'imported public',
    'protected',
    'imported protected',
    'private',
    'imported private',
    'built-in',
    'imported built-in',
]

DATA_ORDER = []
for privacy in DATA_PRIVACY_ORDER:
    for typ in DATA_TYPE_ORDER:
        DATA_ORDER.append('%s %s' % (privacy, typ))

class Attribute(tuple):
    """ Used to map tuple returns to support different python versions. """
    def __init__( self, member_tuple ):
        super(Attribute, self).__init__(member_tuple)
        
        self.name           = member_tuple[0]
        self.kind           = member_tuple[1]
        self.defining_class = member_tuple[2]
        self.object         = member_tuple[3]
        
        if ( hasattr(self.object, 'func_type') ):
            self.kind = self.object.func_type

#------------------------------------------------------------------------------

class DocumentData(object):
    """ Struct to hold data about a document object. """
    name      = None
    value     = None
    dataType  = None
    privacy   = None
    
    def section( self ):
        """
        Returns the section type for this data by joining the privacy and \
        type information.
        
        :return     <str>
        """
        return (self.privacy + ' ' + self.dataType)
    
    @staticmethod
    def create( name, 
                value, 
                kind = 'data',
                defaultVarType = 'variable', 
                defaultFuncType ='function' ):
        
        """
        Creates a new document data instance.
        
        :return     <DocumentData>
        """
        # look for private members
        results = re.match('^(_\w+)__.+', name)
        if ( results ):
            name = name.replace(results.group(1), '')
        
        # determine the privacy level for this data
        privacy = 'public'
        
        if ( name.startswith('__') and name.endswith('__') ):
            privacy = 'built-in'
        elif ( name.startswith('__') ):
            privacy = 'private'
        elif ( name.startswith('_') ):
            privacy = 'protected'
            
        docdata          = DocumentData()
        docdata.name     = name
        docdata.value    = value
        
        # look for specific kinds of methods
        if ( kind == 'method' ):
            type_name = type(value).__name__
            
            if ( type_name == 'pyqtSignal' ):
                kind = 'signal'
            elif ( type_name == 'pyqtSlot' ):
                kind = 'slot'
            elif ( type_name == 'pyqtProperty' ):
                kind = 'property'
                
        elif ( hasattr(value, 'func_type') ):
            kind = getattr(value, 'func_type')
        
        
        if ( kind != 'data' ):
            docdata.dataType = kind
        else:
            docdata.dataType = commands.defaultValueType( value, 
                                                      defaultVarType,
                                                      defaultFuncType )
        docdata.privacy  = privacy
        
        return docdata

#------------------------------------------------------------------------------

class Document(object):
    """ 
    Defines the class that collects all documentation for a python 
    object. 
    """
    
    cache           = {}
    aliases         = {}
    reverseAliases  = {}
    
    def __init__( self ):
        self._object            = None
        self._parent            = None
        self._objectName        = ''
        self._html              = ''
        self._allMembersHtml    = ''
        self._title             = ''
        self._data              = {}
        self._sourceHtml        = {}
        self._children          = []
    
    # protected methods
    def _bases( self, cls, recursive = False ):
        """
        Looks up the bases for the inputed obj instance.
        
        :param      obj         |  <object>
        :param      recursive   |  <bool>
        
        :return     [<cls>, ..]
        """
        if ( not inspect.isclass( cls ) ):
            return []
            
        output = list(cls.__bases__[:])
        if ( not recursive ):
            return output
        
        for basecls in output:
            output += self._bases(basecls, recursive = recursive)
        
        return list(set(output))
    
    def _collectMembers( self, obj ):
        if ( not inspect.isclass( obj ) ):
            return []
            
        try:
            members = inspect.classify_class_attrs(self._object)
            
        except AttributeError:
            members = []
        
        # support python25-
        if ( members and type(members[0]) == tuple ):
            members = [ Attribute(member) for member in members ]
        
        return members
    
    def _generateAllMemberSummary( self, member ):
        """
        Generates the member summary documentation.
        
        :param      member      <Attribute>
        
        :return     <str>
        """
        try:
            obj = getattr(member.defining_class, member.name)
        except AttributeError:
            return ''
            
        key = member.name
        cls = member.defining_class
        
        if ( 'method' in member.kind ):
            docname = cls.__module__ + '-' + cls.__name__
            
            doc = Document.cache.get(docname)
            if ( doc ):
                opts = (doc.url(relativeTo = self), key, key)
                href = '<a href="%s#%s">%s</a>' % opts
            else:
                href = key
            
            kind = member.kind
            if ( hasattr(obj, 'func_type') ):
                kind = obj.func_type
            
            templ = '%s::%s%s'
            if ( 'static' in kind ):
                templ += ' [static]'
            elif ( 'class' in kind ):
                templ += ' [class]'
            elif ( 'abstract' in kind ):
                templ += ' [abstract]'
            elif ( 'deprecated' in kind ):
                templ += ' [deprecated]'
            
            return templ % (cls.__name__, href, self._generateArgs(obj))
            
        else:
            opts = (cls.__name__, key, type(member.object).__name__)
            return '%s::%s : %s' % opts
    
    def _generateAllMembersDocs(self):
        """
        Generates the all members documentation for this document.
        
        :return     <str>
        """
        if ( not inspect.isclass(self._object) ):
            return ''
        
        members = self._collectMembers(self._object)
        member_docs = []
        
        members.sort( lambda x, y: cmp( x.name, y.name ) )
        
        for member in members:
            if ( member.name.startswith('__') and member.name.endswith('__') ):
                continue
                
            member_doc = self._generateAllMemberSummary(member)
            if ( member_doc ):
                member_docs.append('<li>%s</li>' % member_doc)
        
        environ = commands.ENVIRON.copy()
        environ['members_left']  = '\n'.join( member_docs[:len(member_docs)/2])
        environ['members_right'] = '\n'.join( member_docs[len(member_docs)/2:])
        environ['title']         = self.title()
        environ['base_url']      = self.baseurl()
        environ['static_url']    = environ['base_url'] + '/_static'
        environ['navigation'] %= environ
        
        return templates.template('allmembers.html') % environ
    
    def _generateArgs(self, obj):
        """
        Generates the argument information for the inputed object.
        
        :param      obj  |  <variant>
        
        :return     <str>
        """
        try:
            return inspect.formatargspec( *inspect.getargspec( obj ) )
        except TypeError:
            try:
                return self._generateArgs( obj.im_func )
            except AttributeError:
                pass
        
        if ( isinstance( obj, new.instancemethod ) and
             hasattr( obj.im_func, 'func_args' ) ):
            return obj.im_func.func_args
        
        return '(*args, **kwds) [unknown]'
        
    def _generateHtml( self ):
        """
        Generates the HTML documentation for this document.
        
        :return     <str>
        """
        if ( self.isNull() or self._html ):
            return self._html
        
        # generate module docs
        if ( inspect.ismodule( self._object ) ):
            return self._generateModuleDocs()
        
        # generate class docs
        elif ( inspect.isclass( self._object ) ):
            return self._generateClassDocs()
        
        # not sure what this is
        return ''
    
    def _generateClassDocs( self ):
        """
        Generates class documentation for this object.
        """
        html = []
        
        self.parseData()
        
        # determine the inheritance
        bases = []
        for base in self._bases( self._object ):
            doc = commands.findDocument(base)
            
            if ( doc ):
                opt = {}
                opt['text'] = base.__name__
                opt['url'] = doc.url( relativeTo = self )
                bases.append( templates.template('link_standard.html') % opt )
            else:
                bases.append( base.__name__ )
        
        if ( len(bases) > 1 ):
            basestxt = ', '.join(bases[:-1])
            inherits = 'Inherits %s and %s.' % (basestxt, bases[-1])
        elif (len(bases) == 1):
            inherits = 'Inherits %s.' % bases[0]
        else:
            inherits = ''
        
        # determine the subclasses
        subclasses = []
        for subcls in self._subclasses( self._object ):
            doc = commands.findDocument(subcls)
            
            if ( doc ):
                opt = {}
                opt['text'] = subcls.__name__
                opt['url'] = doc.url( relativeTo = self )
                subclasses.append( templates.template('link_standard.html') % opt )
            else:
                subclasses.append( subcls.__name__ )
        
        if ( len(subclasses) > 1 ):
            subs = ', '.join(subclasses[:-1])
            inherited_by = 'Inherited by %s and %s.' % (subs, subclasses[-1])
        elif ( len(subclasses) == 1 ):
            inherited_by = 'Inherited by %s.' % (subclasses[0])
        else:
            inherited_by = ''
        
        allmembers = self.objectName().split('.')[-1] + '-allmembers.html'
        
        # generate the module environ
        environ = commands.ENVIRON.copy()
        environ['title']        = self.title()
        environ['allmembers']   = './' + allmembers
        environ['breadcrumbs']  = self.breadcrumbs()
        environ['url']          = self.url()
        environ['doctype']      = 'Class'
        environ['inherits']     = inherits
        environ['inherited_by'] = inherited_by
        
        modname = self._object.__module__
        moddoc = Document.cache.get(modname)
        if ( moddoc ):
            modurl              = moddoc.url(relativeTo = self)
            environ['module']   = '<a href="%s">%s</a>' % (modurl, modname)
        else:
            environ['module']   = modname
        
        html.append( templates.template('header_class.html') % environ )
        
        # generate the summary report
        gdata = self.groupedData()
        keys = [key for key in gdata.keys() if key in DATA_ORDER]
        keys.sort(lambda x, y: cmp(DATA_ORDER.index(x), DATA_ORDER.index(y)))
        
        for key in keys:
            html.append( self._generateSummary( key, gdata[key] ) )
        
        # generate the main documentation
        maindocs = self._generateObjectDocs( self._object )
        if ( maindocs ):
            environ = commands.ENVIRON.copy()
            environ['type'] = 'Class'
            environ['contents'] = maindocs
            html.append( templates.template('docs_main.html') % environ )
        
        # generate the member documentation
        funcs = self.data().values()
        html.append( self._generateMemberDocs( 'Member Documentation', 
                                                funcs))
        
        # generate the document environ
        return '\n'.join(html)
    
    def _generateMemberDocs( self, title, data ):
        """
        Generates the member documentation for the inputed set of data.
        
        :param      title  |  <str>
        :param      data   | [ <DocumentData>, .. ]
        """
        if ( not data ):
            return ''
            
        bases       = []
        subclasses  = []
        
        # generate the html
        html = []
        
        data.sort(lambda x, y: cmp(x.name, y.name))
        for entry in data:
            # generate function information
            if ( 'function' in entry.dataType or 'method' in entry.dataType ):
                # lookup base methods for reimplimintation
                reimpliments = []
                for base in bases:
                    if ( entry.name in base.__dict__ ):
                        doc = commands.findDocument(base)
                        if ( doc ):
                            opt = {}
                            opt['text'] = base.__name__
                            opt['url']  = doc.url( relativeTo = self )
                            opt['url'] += '#' + entry.name
                            
                            href = templates.template('link_standard.html') % opt
                            reimpliments.append( href )
                        else:
                            reimpliments.append( entry.name )
                
                reimpliment_doc = ''
                if ( reimpliments ):
                    urls = ','.join(reimpliments)
                    reimpliment_doc = 'Reimpliments from %s.' % urls
                
                # lookup submodules for reimplimentation
                reimplimented = []
                for subcls in subclasses:
                    if ( entry.name in subcls.__dict__ ):
                        doc = commands.findDocument(subcls)
                        if ( doc ):
                            opt = {}
                            opt['text'] = subcls.__name__
                            opt['url']  = doc.url( relativeTo = self )
                            opt['url'] += '#' + entry.name
                            
                            href = templates.template('link_standard.html') % opt
                            reimplimented.append( href )
                        else:
                            reimplimented.append( entry.name )
                
                reimplimented_doc = ''
                if ( reimplimented ):
                    urls = ','.join(reimplimented)
                    reimplimented_doc = 'Reimplimented by %s.' % urls
                
                func_split = entry.dataType.split(' ')
                desc = ''
                if ( len(func_split) > 1 ):
                    desc = '[%s]' % func_split[0]
                
                # add the function to the documentation
                environ = commands.ENVIRON.copy()
                environ['type'] = entry.dataType
                environ['name'] = entry.name
                environ['args'] = self._generateArgs( entry.value )
                environ['desc'] = desc
                environ['contents'] = self._generateObjectDocs(entry.value)
                environ['reimpliments']  = reimpliment_doc
                environ['reimplimented'] = reimplimented_doc
                
                html.append( templates.template('docs_function.html') % environ )
            
            elif ( entry.dataType == 'enum' ):
                environ = commands.ENVIRON.copy()
                environ['name'] = entry.name
                
                value_contents = []
                values = entry.value.values()
                values.sort()
                for value in values:
                    value_opts = {}
                    value_opts['key']   = entry.value[value]
                    value_opts['value'] = value
                    value_templ = templates.template('docs_enum_value.html')
                    value_item = value_templ % value_opts
                    value_contents.append( value_item )
                
                environ['contents'] = '\n'.join(value_contents)
                
                html.append( templates.template('docs_enum.html') % environ )
            
        environ            = {}
        environ['title']   = title
        environ['contents'] = '\n'.join( html )
        
        return templates.template('docs_members.html') % environ
    
    def _generateModuleDocs( self ):
        """
        Generates module documentation for this object.
        """
        html = []
        
        # generate the module environ
        environ = commands.ENVIRON.copy()
        environ['title']        = self.title()
        environ['base_url']     = self.baseurl()
        environ['static_url']   = environ['base_url'] + '/_static'
        environ['breadcrumbs']  = self.breadcrumbs()
        environ['url']          = self.url()
        environ['doctype']      = 'Module'
        
        if ( '__init__' in self._object.__file__ ):
            environ['doctype'] = 'Package'
        
        url_split = environ['url'].split('/')
        sources_url = './%s-source.html' % url_split[-1].split('.')[0]
        environ['sources']      = sources_url
        environ['navigation'] %= environ
        
        html.append( templates.template('header_module.html') % environ )
        
        # generate the summary report
        gdata = self.groupedData()
        for key in sorted( gdata.keys(), key = lambda x: DATA_ORDER.index(x)):
            value = gdata[key]
            html.append( self._generateSummary( key, gdata[key] ) )
            
        # generate the main documentation
        maindocs = self._generateObjectDocs( self._object )
        if ( maindocs ):
            environ = commands.ENVIRON.copy()
            environ['type'] = 'Module'
            environ['contents'] = maindocs
            
            html.append( templates.template('docs_main.html') % environ )
        
        # generate the member documentation
        html.append( self._generateMemberDocs('Module Function Documentation', 
                                               self.data().values()))
        
        return '\n'.join(html)
        
    def _generateObjectDocs( self, obj ):
        """
        Generates documentation based on the inputed object's docstring and
        member variable information.
        
        :param      obj  |  <str>
        
        :return     <str> html
        """
        # get the documentation
        try:
            docs = inspect.getdoc(obj)
        except AttributeError:
            pass
            
        if ( docs == None ):
            try:
                docs = inspect.getcomments(obj)
            except AttributeError:
                docs = ''
        
        return wikitext.render(docs,
                               commands.url_handler,
                               options=commands.RENDER_OPTIONS)
    
    def _generateSourceDocs( self ):
        """
        Return the documentation containing the source code.
        
        :return     <str>
        """
        if ( not inspect.ismodule(self._object) ):
            return ''
        
        # load the code file
        codefilename = os.path.splitext( self._object.__file__ )[0]
        codefilename += '.py'
        
        codefile = open(codefilename, 'r')
        code = codefile.read()
        codefile.close()
        
        environ = commands.ENVIRON.copy()
        environ['code']         = xml.sax.saxutils.escape(code)
        environ['title']        = self.title()
        environ['base_url']     = self.baseurl()
        environ['static_url']   = environ['base_url'] + '/_static'
        environ['breadcrumbs']  = self.breadcrumbs(includeSelf = True)
        environ['navigation'] %= environ
        
        return templates.template('source.html') % environ
    
    def _generateSummary( self, section, values, columns = 1 ):
        """
        Generates summary information for the inputed section and value
        data.
        
        :param      section  |  <str>
        :param      values   |  [ <DocumentData>, .. ]
        :param      columns  |  <int>
        
        :return     <str>
        """
        # strip out built-in variables
        newvalues = []
        for value in values:
            if ( not (value.privacy == 'built-in' and 
                      value.dataType == 'variable' )):
                newvalues.append(value)
        values = newvalues
        
        if ( not values ):
            return ''
        
        # split the data into columns
        values.sort( lambda x, y: cmp( x.name.lower(), y.name.lower() ) )
        url = self.url()
        
        coldata = []
        if ( columns > 1 ):
            pass
        else:
            coldata = [values]
        
        html = []
        processed = []
        for colitem in coldata:
            for data in colitem:
                data_environ = {}
                data_environ['url']  = url
                data_environ['name'] = data.name
                data_environ['type'] = data.dataType
                processed.append( data.name )
                
                if ( 'function' in data.dataType or
                     'method' in data.dataType ):
                    data_environ['args'] = self._generateArgs( data.value )
                    templ = templates.template('summary_function.html')
                    html.append( templ % data_environ )
                
                elif ( data.dataType == 'enum' ):
                    templ = templates.template('summary_enum.html')
                    html.append( templ % data_environ )
                
                elif ( 'variable' in data.dataType or
                       'member' in data.dataType ):
                    try:
                        value = getattr(self._object, data.name)
                    except AttributeError:
                        value = None
                        
                    data_environ['value_type'] = type(value).__name__
                    templ = templates.template('summary_variable.html')
                    html.append( templ % data_environ )
                    
                else:
                    datadoc = commands.findDocument(data.value)
                    if ( datadoc ):
                        opts = {}
                        opts['text'] = data.name
                        opts['url']  = datadoc.url( relativeTo = self )
                        
                        contents = templates.template('link_standard.html') % opts
                    else:
                        contents = data.name
                    
                    data_environ['contents'] = contents
                    templ = templates.template('summary_item.html')
                    html.append( templ % data_environ )
                    
        # update the bases environ
        members = self._collectMembers(self._object)
        inherited_members = {}
        
        for member in members:
            mem_name  = member.name
            mem_kind  = member.kind
            mem_cls   = member.defining_class
            mem_value = member.object
            
            if ( hasattr(member.object, 'func_type') ):
                mem_kind = member.object.func_type
            
            if ( mem_cls == self._object ):
                continue
            
            data = DocumentData.create( mem_name,
                                        mem_value,
                                        mem_kind,
                                        'member',
                                        'method' )
            
            if ( section != data.section() ):
                continue
        
            inherited_members.setdefault( mem_cls, 0 )
            inherited_members[mem_cls] += 1
        
        inherit_summaries = []
        templ = templates.template('summary_inherit.html')
        bases = self._bases( self._object, True )
        inherits = inherited_members.keys()
        inherits.sort( lambda x, y: cmp( bases.index(x), bases.index(y) ) )
        
        for inherited in inherits:
            count = inherited_members[inherited]
            doc = commands.findDocument( inherited )
            if ( not doc ):
                continue
                
            opt = {}
            opt['count'] = count
            opt['base']  = inherited.__name__
            opt['url']   = doc.url( relativeTo = self )
            opt['type']  = section
            
            inherit_summaries.append( templ % opt )
        
        # generate the summary information
        words     = [word.capitalize() for word in text.words(section)]
        words[-1] = text.pluralize(words[-1])
        
        summary_environ = {}
        summary_environ['contents'] = '\n'.join(html)
        summary_environ['section'] = ' '.join(words)
        summary_environ['inherits'] = '\n'.join(inherit_summaries)
        
        return templates.template('summary.html') % summary_environ
    
    def _subclasses( self, obj ):
        """
        Looks up all the classes that inherit from this object.
        
        :param      obj         |  <object>
        
        :return     [<cls>, ..]
        """
        output = []
        for doc in Document.cache.values():
            doc_obj = doc.object()
            if ( inspect.isclass( doc_obj ) and
                 obj in doc_obj.__bases__ ):
                output.append( doc_obj )
        return output
    
#------------------------------------------------------------------------------
    
    # public methods
    def addChild( self, child ):
        """
        Adds the inputed document as a sub-child for this document.
        
        :param      child  |  <Document>
        """
        child._parent = self
        self._children.append(child)
    
    def allMembersHtml( self ):
        """
        Returns the documentation for all the members linked to this document.
        This method only applies to class objects.
        
        :return     <str>
        """
        if ( not inspect.isclass( self._object ) ):
            return ''
            
        if ( not self._allMembersHtml ):
            self._allMembersHtml = self._generateAllMembersDocs()
        
        return self._allMembersHtml
    
    def baseurl( self ):
        """
        Returns the relative url to get back to the root of the documentation
        api.
        
        :return     <str>
        """
        baseurl   = self.url()
        count     = len(baseurl.split('/'))
        return ('../' * count).strip('/')
    
    def breadcrumbs(self, 
                    relativeTo = None, 
                    first = True, 
                    includeSelf = False):
        """
        Creates a link to all of the previous modules for this item.
        
        :param      relativeTo  |  <Document>  | Relative to another document.
                    first       |  <bool>
                    includeSelf |  <bool>      | Create a link to this doc.
        
        :return     <str>
        """
        basecrumbs = ''
        
        if ( not relativeTo ):
            relativeTo = self
            basecrumbs = self.title().split('.')[-1]
        
        if ( includeSelf ):
            opts = {
                'url': './' + os.path.split(self.url())[1],
                'text': self.title().split('.')[-1]
            }
            
            basecrumbs = templates.template('link_breadcrumbs.html') % opts
            
        if ( inspect.isclass( self._object ) ):
            doc = Document.cache.get( self._object.__module__ )
        elif ( inspect.ismodule( self._object ) ):
            parent_mod = '.'.join( self._object.__name__.split('.')[:-1] )
            doc = Document.cache.get( parent_mod )
        else:
            doc = None
        
        if ( doc ):
            opts = {}
            opts['url']   = doc.url(relativeTo)
            opts['text' ] = doc.title().split('.')[-1]
            
            link = templates.template('link_breadcrumbs.html') % opts
            
            subcrumbs = doc.breadcrumbs(relativeTo, first = False)
        else:
            subcrumbs = ''
            link = ''
        
        parts = []
        
        if ( first ):
            # add the home url
            baseurl = self.baseurl()
            
            home_url   = '%s/index.html' % baseurl
            home_opts  = { 'text': 'Home', 'url': home_url }
            home_part  = templates.template('link_breadcrumbs.html') % home_opts
            
            parts.append(home_part)
            
            # add the api url
            api_url   = '%s/api/index.html' % baseurl
            api_opts  = { 'text': 'API', 'url': api_url }
            api_part  = templates.template('link_breadcrumbs.html') % api_opts
            
            parts.append(api_part)
            
        if ( subcrumbs ):
            parts.append( subcrumbs )
        if ( link ):
            parts.append( link )
        if ( basecrumbs ):
            parts.append( basecrumbs )
            
        return ''.join( parts )
        
    def children( self ):
        """
        Returns the child documents for this instance.
        
        :return     [ <Document>, .. ]
        """
        return self._children
    
    def data( self ):
        """
        Returns the data that has been loaded for this document.
        
        :return     <dict>
        """
        return self._data
    
    def export( self, basepath, page = None ):
        """
        Exports the html files for this document and its children to the 
        given basepath.
        
        :param      basepath  |  <str>
        :param      page      |  <str> || None
        
        :return     <bool> success
        """
        # make sure the base path exists
        if ( not os.path.exists( basepath ) ):
            return False
        
        basepath    = os.path.normpath(basepath)
        url         = self.url()
        filename    = os.path.join(basepath, url)
        docpath     = os.path.dirname(filename)
        
        # add the doc path
        if ( not os.path.exists(docpath) ):
            os.makedirs(docpath)
        
        if ( not page ):
            page = templates.template('page.html')
        
        # setup the default environ
        commands.url_handler.setRootUrl(self.baseurl())
        
        doc_environ = commands.ENVIRON.copy()
        doc_environ['title']    = self.title()
        doc_environ['base_url'] = self.baseurl()
        doc_environ['static_url'] = doc_environ['base_url'] + '/_static'
        doc_environ['contents'] = self.html()
        doc_environ['breadcrumbs'] = self.breadcrumbs(includeSelf = True)
        doc_environ['navigation'] %= doc_environ
        
        # generate the main html file
        exportfile = open(filename, 'w')
        exportfile.write( page % doc_environ )
        exportfile.close()
        
        # generate the all members html file
        allmember_html = self.allMembersHtml()
        if ( allmember_html ):
            fpath, fname = os.path.split(filename)
            fname = fname.split('.')[0] + '-allmembers.html'
            afilesource = os.path.join(fpath, fname)
            doc_environ['contents'] = allmember_html
            
            # create the crumbs
            crumbs = self.breadcrumbs(includeSelf = True)
            opts = {'url': '#', 'text': 'All Members'}
            crumbs += templates.template('link_breadcrumbs.html') % opts
            
            doc_environ['breadcrumbs'] = crumbs
            
            # save the all members file
            membersfile = open(afilesource, 'w')
            membersfile.write( page % doc_environ )
            membersfile.close()
        
        # generate the source code file
        source_html = self.sourceHtml()
        if ( source_html ):
            fpath, fname = os.path.split(filename)
            fname = fname.split('.')[0] + '-source.html'
            sfilesource = os.path.join(fpath, fname)
            doc_environ['contents'] = source_html
            
            # create the crumbs
            crumbs = self.breadcrumbs(includeSelf = True)
            opts = {'url': '#', 'text': 'Source Code'}
            crumbs += templates.template('link_breadcrumbs.html') % opts
            
            doc_environ['breadcrumbs'] = crumbs
            
            # save the source file
            sourcefile = open(sfilesource, 'w')
            sourcefile.write( page % doc_environ )
            sourcefile.close()
        
        # generate the children
        for child in self.children():
            child.export(basepath, page)
    
    def findData( self, dtype ):
        """
        Looks up the inputed data objects based on the given data type.
        
        :param      dataType  |  <str>
        
        :return     <str>
        """
        self.parseData()
        
        output = []
        for data in self._data.values():
            if ( data.dataType == dtype or
                 (data.privacy + ' ' + data.dataType) == dtype ):
                output.append(data)
        return output
    
    def groupedData( self ):
        """
        Groups the data together based on their data types and returns it.
        
        :return     { <str> grp: [ <DocumentData>, .. ], .. }
        """
        output = {}
        values = self._data.values()
        values.sort( lambda x, y: cmp(x.name, y.name) )
        for data in values:
            dtype = '%s %s' % (data.privacy, data.dataType)
            output.setdefault(dtype, [])
            output[dtype].append(data)
        
        return output
    
    def html( self ):
        """
        Returns the generated html for this document.
        
        :return     <str>
        """
        if ( not self._html ):
            self._html = self._generateHtml()
        
        return self._html
    
    def isNull( self ):
        """
        Returns whether or not this document has any data associated with it.
        
        :return     <bool>
        """
        return self._object == None
    
    def object( self ):
        """
        Returns the object that this document represents.
        
        :return     <object> || None
        """
        return self._object
    
    def objectName( self ):
        """
        Returns the object name that this object will represent.  This will
        be similar to a URL, should be unique per document.
        
        :return     <str>
        """
        return self._objectName
    
    def parent( self ):
        """
        Returns the parent document of this instance.
        
        :return     <Document> || None
        """
        return self._parent
    
    def parseData( self ):
        """
        Parses out all the information that is part of this item's object.
        This is the method that does the bulk of the processing for the 
        documents.
        
        :return     <bool> success
        """
        if ( self.isNull() or self._data ):
            return False
            
        class_attrs = []
        obj         = self.object()
        
        # parse out class information
        cls_kind_map = {}
        if ( inspect.isclass( obj ) ):
            contents = self._collectMembers(obj)
            for const in contents:
                if ( const[2] == obj ):
                    class_attrs.append( const[0] )
                    cls_kind_map[const.name] = const.kind
        
        # try to load all the items
        try:
            members = dict(inspect.getmembers(obj))
            
        except AttributeError:
            members = {}
            
        for key in dir(obj):
            if ( not key in members ):
                try:
                    members[key] = getattr(obj, key)
                    
                except AttributeError:
                    pass
        
        modname = ''
        if ( inspect.ismodule(obj) ):
            modname = obj.__name__
        
        for name, value in members.items():
            # ignore inherited items
            if ( class_attrs and not name in class_attrs ):
                continue
            
            varType  = 'variable'
            funcType = 'function'
            kind     = 'data'
            if ( inspect.isclass( self._object ) ):
                varType  = 'member'
                funcType = 'static method'
                kind     = cls_kind_map.get(name, 'data')
            
            docdata = DocumentData.create( name,
                                           value,
                                           kind,
                                           varType,
                                           funcType )
            
            if ( modname and hasattr(value, '__module__') and 
                 modname != getattr(value, '__module__') ):
                docdata.privacy = 'imported ' + docdata.privacy
                
            
            self._data[name] = docdata
    
    def setObject( self, obj ):
        """
        Sets the object instance for this document to the inputed object.  This
        will be either a module, package, class, or enum instance.  This will
        clear the html information and title data.
        
        :param      obj  |  <variant>
        """
        self._object            = obj
        self._html              = ''
        self._allMembersHtml    = ''
        self._title = str(obj.__name__)
        
        if ( inspect.isclass( obj ) ):
            self.setObjectName( '%s-%s' % (obj.__module__, obj.__name__) )
        else:
            self.setObjectName( obj.__name__ )
    
    def setObjectName( self, objectName ):
        """
        Sets the object name for this document to the given name.
        
        :param      objectName | <str>
        """
        self._objectName = objectName
    
    def setTitle( self, title ):
        """
        Sets the title string for this document to the inputed string.
        
        :param      title | <str>
        """
        self._title = title
    
    def sourceHtml( self ):
        """
        Returns the source file html for this document.  This method only
        applies to module documents.
        
        :return     <str>
        """
        if ( not inspect.ismodule(self._object) ):
            return ''
        
        if ( not self._sourceHtml ):
            self._sourceHtml = self._generateSourceDocs()
        
        return self._sourceHtml
    
    def title( self ):
        """
        Returns the title string for this document.
        
        :return     <str>
        """
        return self._title
    
    def url( self, relativeTo = None ):
        """
        Returns the path to this document's html file.  If the optional
        relativeTo keyword is specified, then the generated url will be made
        in relation to the local path for the current document.
        
        :param      relativeTo      <Document> || None
        
        :return     <str>
        """
        modname = self.objectName()
        if ( inspect.ismodule( self._object ) ):
            if ( '__init__' in self._object.__file__ ):
                modname += '.__init__'
        
        if ( not relativeTo ):
            return modname.replace('.','/') + '.html'
        
        relmodule = relativeTo.objectName()
        relobject = relativeTo.object()
        if ( inspect.ismodule( relobject ) ):
            if ( '__init__' in relobject.__file__ ):
                relmodule += '.__init__'
        
        relpath = relmodule.split('.')
        mypath  = modname.split('.')
        
        go_up   = '/..' * (len(relpath)-1)
        go_down = '/'.join([ part for part in mypath if part ])
        
        return (go_up + '/' + go_down + '.html').strip('/')