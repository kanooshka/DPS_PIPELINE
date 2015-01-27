#!/usr/bin/python

""" Defines the base commands module for this system.  """

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

import datetime
import distutils.dir_util
import glob
import inspect
import logging
import os
import sys
import shutil
import zipfile

from xml.etree import ElementTree

import projex
from projex              import text
from projex              import errors
from projex              import wikitext
from projex.enum         import enum
from projex.envmanager   import EnvManager
from projex.cli          import climethod

from projex              import resources
from projex.docgen       import templates
from projex.docgen       import default_config

logger = logging.getLogger(__name__)

ENVIRON = {}
RENDER_OPTIONS = {}

class DocgenUrlHandler(wikitext.UrlHandler):
    def resolveClass( self, cls ):
        """
        Resolves the class path for the given class instance.
        
        :param      cls | <str>
        
        :return     <str>
        """
        cls_opts = cls.split('.')
        module   = cls_opts[0]
        page     = '/'.join(cls_opts[:-1])
        page    += '-' + cls_opts[-1]
        
        url = '$DOCS_ROOT/%s/current/api/%s' % (module, page)
        return self.resolve(url)
    
    def resolve( self, key ):
        """
        Resolves the given key to a url.
        
        :param      key | <str>
        
        :return     (<str> url, <bool> exists)
        """
        path, ext = os.path.splitext(key)
        if ( not ext ):
            key += '.html'
        elif ext == '.wiki' and self.replaceWikiSuffix():
            key = key.replace('.wiki', '.html')
        
        # replace a key with a root value
        if ( key.startswith('$ROOT') ):
            return (key.replace('$ROOT', self.rootUrl()), True)
        
        # replace a key with a document value
        elif ( key.startswith('$DOCS_ROOT') ):
            # standard doc style is <package>/current/<root>
            # so defualt documentation is 2 folders up from the current
            # however, can be hardcoded using the PROJEX_DOCGEN_ROOT variable
            # in the environment
            url = os.environ.get('PROJEX_DOCGEN_ROOT', self.rootUrl() + '/../..')
            
            return (key.replace('$DOCS_ROOT', url), True)
        
        # replace a key with an API value
        elif ( key.startswith('$API') ):
            return (key.replace('$API', self.rootUrl() + '/api'), True)
        
        # replace a static lookup
        elif ( key.startswith('$STATIC') ):
            return (key.replace('$STATIC', self.staticUrl()), True)
        
        # treat the key as a local reference
        return ('./%s' % key, True)
    
    def resolveImage( self, key ):
        """
        Resolves the image location for the given key.
        
        :param      key | <str>
        
        :return     (<str> url, <bool> exists)
        """
        return self.resolve('$STATIC/images/%s' % key)

url_handler = DocgenUrlHandler()
url_handler.setCurrent()

#------------------------------------------------------------------------------

def breadcrumbs( crumbs ):
    """
    Creates a breadcrumb string for the inputed crumbs.
    
    :param      crumbs | [(<str> relative url, <str> title), ..]
    """
    crumb_str = []
    crumb_templ = templates.template('link_breadcrumbs.html')
    for url, text in crumbs:
        if ( url != '' ):
            crumb_str.append(crumb_templ % {'url': url, 'text': text})
        else:
            crumb_str.append(crumb_templ % {'url': '#', 'text': text})
    
    return ''.join(crumb_str)

def defaultValueType( value, default = 'data', functionType = 'function' ):
    """
    Returns the default value type the inputed value.
    
    :param      value           |  <variant>
    :param      default         |  <str>
    :param      functionType    |  <str>
    
    :return     <str>
    """
    if ( type(value).__name__ == 'pyqtSignal' ):
        return 'signal'
    elif ( type(value).__name__ == 'pyqtSlot' ):
        return 'slot'
    elif ( type(value).__name__ == 'pyqtProperty' ):
        return 'property'
    elif ( hasattr(value, 'func_type') ):
        return getattr(value, 'func_type')
    elif ( inspect.ismodule( value ) ):
        return 'module'
    elif ( inspect.isclass( value ) ):
        return 'class'
    elif ( isinstance( value, staticmethod ) ):
        return 'static method'
    elif ( isinstance( value, classmethod ) ):
        return 'class method'
    elif ( inspect.ismethod( value ) or inspect.ismethoddescriptor( value ) ):
        return 'method'
    elif ( inspect.isbuiltin( value ) ):
        return 'built-in'
    elif ( isinstance( value, enum ) ):
        return 'enum'
    elif ( inspect.isfunction( value ) ):
        return functionType
    
    # return the default type
    return default

def findDocument( obj ):
    """
    Returns the document that the inputed object is relating to.
    
    :return     <Document>
    """
    from projex.docgen.document import Document
    for doc in Document.cache.values():
        if ( doc.object() == obj ):
            return doc
    return None

@climethod
def generate(  module,
               outputpath   = './resources/docs/html',
               userpath     = '',
               config       = None ):
    """
    Generates documenation for the inputed filepath at the given output \
    location.  The system can also supply the root location for user \
    documentation that can be included in addition to the code by supplying \
    a root userdocs path.
    
    :param      module        | <module> || <str>
    :param      outputpath    | <str>
    :param      config        | <module> || None
    
    :return     <bool> success
    """
    from projex.docgen.document import Document
    
    if ( type(module) == str ):
        # extract from a specific filepath
        if ( os.path.exists(module) ):
            package = projex.packageFromPath(module)
            if ( not package ):
                msg = '%s is an invalid module.' % module
                raise errors.DocumentationError(msg)
            
            root_path = projex.packageRootPath(module)
            sys.path.insert(0, root_path)
        
        # otherwise, use it as the package name
        else:
            projex.requires(module)
            package = module.split('-')[0]
        
        try:
            __import__(package)
            module = sys.modules[package]
        
        except ImportError:
            msg = 'Could not import the %s module' % package
            raise errors.DocumentationError(msg)
        
        except KeyError:
            msg = 'Could not import the %s module' % package
            raise errors.DocumentationError(msg)
    
    # initialize the global environ
    if ( config is None ):
        config = default_config
    
    init_environ(module, config)
    
    logger.info('Generating module documentation %s...' % module.__name__)
    
    # load the base page and style information
    page  = templates.template('page.html')
    
    # start generating the documents
    Document.cache.clear()
    
    # generate the module documentation
    try:
        ignore = config.IGNORE
    except AttributeError:
        ignore = None
    
    doc = generateModuleDocument(module, ignore = ignore)
    
    modpath = os.path.dirname(module.__file__)
    outpath = outputpath.replace( './', modpath + '/' )
    
    # clear the docs path
    if ( os.path.exists( outpath ) ):
        shutil.rmtree( outpath )
    
    if ( not os.path.exists( outpath ) ):
        logger.info( 'Making doc path: ' + outpath )
        os.makedirs(outpath)
    
    # make the root api documentation
    api_path = outpath.rstrip('/') + '/api/'
    if not os.path.exists(api_path):
        logger.info( 'Making doc path:' + api_path )
        os.mkdir(api_path)
    
    # generate the api docs
    doc.export(api_path, page = page)
    
    # generate the all classes page
    generateClassDocs( outpath, page, module.__name__ )
    generateModuleDocs( outpath, page, module.__name__)
    generateFunctionDocs( outpath, page, module.__name__)
    generateApiIndex( outpath, page )
    generateDocumentIndex( outpath, page)
    
    # create the user docs
    if ( userpath ):
        userdocs = os.path.abspath(userpath)
    elif ( config != default_config ):
        userdocs = os.path.dirname(config.__file__)
    else:
        userdocs = os.path.abspath('./docs')
    
    if ( os.path.exists(userdocs) ):
        targetuserdocs = outpath
        templ  = templates.template('link_breadcrumbs.html')
        
        generateUserDocs( userdocs, targetuserdocs, page )
    
    # copy the syntaxhighlighter code
    targetpath = os.path.join(outpath,'_static')
    
    paths = []
    paths.append(resources.find('ext/prettify'))
    paths.append(templates.path('javascript'))
    paths.append(templates.path('css'))
    paths.append(templates.path('images'))
    paths.append(templates.path('img'))
    
    logger.info('Copying static resources...')
    
    # python26+
    try:
        ignore = shutil.ignore_patterns('.svn')
    except AttributeError:
        ignore = None
        
    for path in paths:
        if ( not os.path.exists(path) ):
            continue
        
        basename = os.path.basename(path)
        instpath = os.path.join(targetpath, basename)
        
        if ( ignore is not None ):
            shutil.copytree( path, instpath, ignore = ignore )
        else:
            shutil.copytree(path, instpath)
    
    # create a compressed xdk file
    logger.info('Creating XDK file...')
    zfilename = os.path.join(outpath, '../%s.xdk' % module.__name__)
    zfilename = os.path.abspath(zfilename)
    
    generateXdk(outpath, zfilename)

def generateApiIndex(outpath, page ):
    """
    Generates the main API index document.
    """
    
    # generate the indexes and global files
    environ = ENVIRON.copy()
    environ['base_url'] = '..'
    environ['static_url'] = '../_static'
    contents = templates.template('index.html') % environ
    
    environ = ENVIRON.copy()
    environ['title']    = 'API Main Page'
    environ['base_url'] = '..'
    environ['static_url'] = '../_static'
    environ['breadcrumbs'] = breadcrumbs([('../index.html', 'Home'),
                                           ('', 'API')])
    environ['contents'] = contents
    environ['navigation'] %= environ
    
    html = page % environ
    
    # save to the base location
    indexfilename = os.path.join(outpath, 'api/index.html')
    indexfile = open(indexfilename, 'w')
    indexfile.write(html)
    indexfile.close()

def generateDocumentIndex(outpath, page ):
    """
    Generates the main API index document.
    """
    
    # generate the indexes and global files
    environ = ENVIRON.copy()
    environ['base_url'] = '.'
    environ['static_url'] = './_static'
    environ['navigation'] %= environ
    contents = templates.template('index.html') % environ
    
    environ = ENVIRON.copy()
    environ['title']    = 'Documentation Main Page'
    environ['base_url'] = '.'
    environ['static_url'] = './_static'
    environ['breadcrumbs'] = breadcrumbs([('', 'Home')])
    environ['contents'] = contents
    environ['navigation'] %= environ
    
    html = page % environ
    
    indexfile = open(os.path.join(outpath, 'index.html'), 'w')
    indexfile.write(html)
    indexfile.close()

def generateClassDocs(outpath, page, basemod):
    """
    Generates the class index html document based on the currently loaded
    class documents.
    """
    from projex.docgen.document import Document
    
    classes = {}
    for doc in Document.cache.values():
        obj = doc.object()
        if ( inspect.isclass(obj) and obj.__module__.startswith(basemod) ):
            first = obj.__name__[0].upper()
            classes.setdefault(first, [])
            classes[first].append(doc)
    
    class_html = []
    letters = []
    keys = classes.keys()
    keys.sort()
    for key in keys:
        docs = classes[key]
        docs.sort( lambda x, y: cmp( x.title(), y.title() ) )
        
        contents = []
        for doc in docs:
            opts = {}
            opts['text'] = doc.title()
            opts['url']  = './' + doc.url()
            contents.append( templates.template('link_standard.html') % opts )
        
        letter_opts = {}
        letter_opts['text'] = key
        letter_opts['url'] = '#%s' % key
        
        letters.append( templates.template('link_standard.html') % letter_opts )
        
        class_opts = {}
        class_opts['letter'] = key
        class_opts['contents'] = '' + '<br/>'.join(contents)
        class_html.append( templates.template('letter_group.html') % class_opts )
    
    cls_data = {}
    cls_data['contents'] = '\n'.join(class_html)
    cls_data['letters'] = ' . '.join(letters)
    
    cls_html = templates.template('classes.html') % cls_data
    
    classes_opt = ENVIRON.copy()
    classes_opt['title'] = 'API Classes'
    classes_opt['base_url'] = '..'
    classes_opt['static_url'] = '../_static'
    classes_opt['contents'] = cls_html
    classes_opt['navigation'] %= classes_opt
    classes_opt['breadcrumbs'] = breadcrumbs([('../index.html', 'Home'),
                                              ('./index.html', 'API'),
                                              ('', 'All Classes')])
    
    html = page % classes_opt
    
    classesfile = open(os.path.join(outpath, 'api/classes.html'), 'w')
    classesfile.write(html)
    classesfile.close()

def generateModuleDocs(outpath, page, basemod):
    """
    Generates the module index html document based on the currently loaded
    module documents.
    """
    from projex.docgen.document import Document
    
    modules = {}
    for doc in Document.cache.values():
        obj = doc.object()
        if ( inspect.ismodule(obj) and obj.__name__.startswith(basemod) ):
            first = obj.__name__.split('.')[-1][0].upper()
            modules.setdefault(first, [])
            modules[first].append(doc)
    
    module_html = []
    letters = []
    keys = modules.keys()
    keys.sort()
    for key in keys:
        docs = modules[key]
        docs.sort( lambda x, y: cmp( x.title(), y.title() ) )
        
        contents = []
        for doc in docs:
            opts = {}
            opts['text'] = doc.title()
            opts['url']  = './' + doc.url()
            contents.append( templates.template('link_standard.html') % opts )
        
        letter_opts = {}
        letter_opts['text'] = key
        letter_opts['url'] = '#%s' % key
        
        letters.append( templates.template('link_standard.html') % letter_opts )
        
        modules_opts = {}
        modules_opts['letter'] = key
        modules_opts['contents'] = '' + '<br/>'.join(contents)
        module_text = templates.template('letter_group.html') % modules_opts
        module_html.append( module_text )
    
    cls_data = ENVIRON.copy()
    cls_data['base_url'] = '..'
    cls_data['static_url'] = '../_static'
    cls_data['contents'] = '\n'.join(module_html)
    cls_data['letters'] = ' . '.join(letters)
    cls_data['navigation'] %= cls_data
    
    cls_html = templates.template('modules.html') % cls_data
    
    modules_opt = ENVIRON.copy()
    modules_opt['title'] = 'API Modules'
    modules_opt['base_url'] = '..'
    modules_opt['static_url'] = '../_static'
    modules_opt['contents'] = cls_html
    modules_opt['navigation'] %= modules_opt
    modules_opt['breadcrumbs'] = breadcrumbs([('../index.html', 'Home'),
                                              ('./index.html', 'API'),
                                              ('', 'All Modules')])
    
    html = page % modules_opt
    
    modulesfile = open(os.path.join(outpath, 'api/modules.html'), 'w')
    modulesfile.write(html)
    modulesfile.close()

def generateFunctionDocs(outpath, page, basemod):
    """
    Generates the module index html document based on the currently loaded
    module documents.
    """
    from projex.docgen.document import Document
    
    functions = {}
    for doc in Document.cache.values():
        obj = doc.object()
        if ( inspect.ismodule(obj) and 
             not obj.__name__.startswith(basemod) ):
            continue
        elif ( inspect.isclass(obj) and 
               not obj.__module__.startswith(basemod) ):
            continue
            
        for data in doc.data().values():
            if ( 'function' in data.dataType ):
                first = data.name.strip('_')[0].upper()
                functions.setdefault(first, [])
                functions[first].append((doc, data))
                
            elif ( 'method' in data.dataType ):
                first = data.name.strip('_')[0].upper()
                functions.setdefault(first, [])
                functions[first].append((doc, data))
                
    function_html = []
    letters = []
    keys = functions.keys()
    keys.sort()
    for key in keys:
        docs = functions[key]
        docs.sort( lambda x, y: cmp( x[1].name, y[1].name ) )
        
        contents = []
        for doc, data in docs:
            opts = {}
            opts['class'] = doc.title()
            opts['text'] = data.name
            opts['url']  = './%s#%s' % (doc.url(), data.name)
            contents.append( templates.template('link_function.html') % opts )
        
        letter_opts = {}
        letter_opts['text'] = key
        letter_opts['url'] = '#%s' % key
        
        letters.append( templates.template('link_standard.html') % letter_opts )
        
        functions_opts = {}
        functions_opts['letter'] = key
        functions_opts['contents'] = '' + '<br/>'.join(contents)
        function_text = templates.template('letter_group.html') % functions_opts
        function_html.append( function_text )
    
    cls_data = {}
    cls_data['contents'] = '\n'.join(function_html)
    cls_data['letters'] = ' . '.join(letters)
    
    cls_html = templates.template('functions.html') % cls_data
    
    functions_opt = ENVIRON.copy()
    functions_opt['title'] = 'API Functions'
    functions_opt['base_url'] = '..'
    functions_opt['static_url'] = '../_static'
    functions_opt['contents'] = cls_html
    functions_opt['navigation'] %= functions_opt
    functions_opt['breadcrumbs'] = breadcrumbs([('../index.html', 'Home'),
                                                 ('./index.html', 'API'),
                                                 ('', 'All Functions')])
    
    html = page % functions_opt
    
    functionsfile = open(os.path.join(outpath, 'api/functions.html'), 'w')
    functionsfile.write(html)
    functionsfile.close()

def generateClassDocument( cls, alias = '' ):
    """
    Generates documentation for a class based on the inputed source path.
    
    :param      cls   |  <class>
    :param      alias |  <str>
    
    :return     <Document> || None
    """
    from projex.docgen.document import Document
    
    logger.info('Generating class documentation %s...' % cls.__name__)
    
    objectName = '%s-%s' % (cls.__module__, cls.__name__)
    classdoc = None
    
    # load the object into the cache
    if ( not objectName in Document.cache ):
        classdoc = Document()
        classdoc.setObject( cls )
        Document.cache[ str(classdoc.objectName()) ] = classdoc
        
        # make sure the base classes are documented
        bases = cls.__bases__
        if ( bases != None ):
            for base in bases:
                child = generateClassDocument( base )
                if ( child ):
                    classdoc.addChild(child)
    
    # include aliases
    if ( alias and alias != objectName ):
        Document.aliases[ alias ] = objectName
        Document.reverseAliases.setdefault( objectName, [] )
        Document.reverseAliases[objectName].append(alias)
    
    return classdoc

def generateModuleDocument( module, ignore = None ):
    """
    Generates documentation for a module based on the inputed source path,
    and module name and scope.
    
    :param      module | <module>
                ignore | [<str>, ..] || None
    
    :return     <Document> || None
    """
    from projex.docgen.document import Document
    
    logger.info('Generating module documentation %s...' % module.__name__)
    
    # load the module
    newdoc = Document()
    newdoc.setObject( module )
    Document.cache[ newdoc.objectName() ] = newdoc
    
    # load sub-modules and packages
    if ( os.path.basename( module.__file__ ).split('.')[0] == '__init__' ):
        modpath = os.path.dirname( module.__file__ )
        
        submodpaths = glob.glob( modpath + '/*.py' )
        for submodpath in submodpaths:
            # for a package, this is the __init__ file
            if ( '__init__.py' in submodpath ):
                continue
            
            submodule = EnvManager.fileImport(submodpath, ignore = ignore)
            if ( submodule ):
                subdoc = generateModuleDocument( submodule, ignore = ignore )
                if ( subdoc ):
                    newdoc.addChild(subdoc)
                    
        
        subpakgpaths = glob.glob( modpath + '/*/__init__.py' )
        for subpackgpath in subpakgpaths:
            subpackg = EnvManager.fileImport(subpackgpath, ignore = ignore)
            if ( subpackg ):
                subdoc = generateModuleDocument( subpackg, ignore = ignore )
                if ( subdoc ):
                    newdoc.addChild( subdoc )
    
    # load the class documentation
    modname = module.__file__
    newdoc.parseData()
    for data in newdoc.data().values():
        alias = ('%s-%s' % (modname, data.name))
        
        # genearte documentation for a class within the module
        if ( data.dataType == 'class' ):
            subdoc = generateClassDocument( data.value, alias = alias )
            if ( subdoc ):
                newdoc.addChild( subdoc )
    
    return newdoc
    
def generateUserDocs(path,
                     target,
                     page=None,
                     breadcrumbs=None,
                     basepath='.',
                     title=''):
    """
    Generates the user documentation for the inputed path by \
    rendering any wiki text files to html and saving it out to the doc \
    root.
    
    :param      path            |  <str>
                target          |  <str>
                page            |  <str>
                source          |  <str>
                breadcrumbs     |  [<str>, .. ] || None
    """
    logger.info('Generating user documentation...')
    
    if page is None:
        page = templates.template('page.html')
    
    if not os.path.exists(target):
        os.mkdir(target)
    
    if breadcrumbs == None:
        breadcrumbs = []
    
    crumb_templ = templates.template('link_breadcrumbs.html')
    
    # setup the base crumbs
    base_url = basepath + '/..' * len(breadcrumbs)
    static_url = base_url + '/_static'    url_handler.setRootUrl(base_url)
    
    # setup the title
    if not title:
        main_title = 'Home'
        if breadcrumbs:
            main_title = os.path.normpath(path).split(os.path.sep)[-1]
            main_title = text.pretty(main_title)
    else:
        main_title = title
    
    entry_contents = []
    has_index_file = False
    
    for entry in sorted(os.listdir(path)):
        filepath = os.path.join(path, entry)
        
        # skip the svn information
        if ( entry == '.svn' ):
            continue
        
        # check for manual index overrides
        elif ( entry == 'index.wiki' ):
            has_index_file = True
        
        # add wiki pages to the system
        elif ( entry.endswith('.wiki') ):
            filename    = os.path.join(path, entry)
            outfilename = os.path.join(target, entry.replace('.wiki','.html'))
            
            wiki_file = open(filename, 'r')
            wiki_contents = wiki_file.read()
            wiki_file.close()
            
            crumbs = []
            count  = len(breadcrumbs)
            for i, crumb in enumerate(breadcrumbs):
                crumbs.append(crumb % (basepath + '/..' * count))
            
            # add the base crumb
            crumb  = crumb_templ % {'url': '%s/index.html' % basepath,
                                    'text': main_title}
            crumbs.append(crumb)
            
            # add the page crumb
            crumb = crumb_templ % {'url': '#', 'text': title}
            crumbs.append( crumb )
            crumbstr = ''.join(crumbs)
            
            # generate the contents
            title    = text.capitalizeWords(entry.split('.')[0])
            options = RENDER_OPTIONS.copy()
            options['FILENAME'] = filepath
            options['ROOT'] = base_url
            contents = wikitext.render(wiki_contents,
                                       url_handler,
                                       options=options)
            
            # update the environ
            environ = ENVIRON.copy()
            environ['title']        = title
            environ['contents']     = contents
            environ['base_url']     = base_url
            environ['static_url']   = static_url
            environ['breadcrumbs']  = crumbstr
            environ['navigation'] %= environ
            
            url = entry.replace('.wiki', '.html')
            entry_item = '<a href="%s/%s">%s</a>' % (basepath, url, title)
            entry_contents.append( entry_item )
            
            html = page % environ
            
            html_file = open(outfilename, 'w')
            html_file.write(html)
            html_file.close()
            
            continue
        
        # copy static paths
        elif ( entry == '_static' ):
            targetpath = os.path.join(target, '_static')
            
            # python26+
            try:
                ignore   = shutil.ignore_patterns('.svn')
                shutil.copytree(filepath, targetpath, ignore=ignore)
            
            # python25-
            except AttributeError:
                shutil.copytree(filepath, targetpath)
            continue
        
        # include sub-documents that contain index.wiki
        elif ( os.path.isdir(filepath) and \
             os.path.exists(os.path.join(filepath, 'index.wiki')) ):
            base_name   = os.path.normpath(path).split(os.path.sep)[-1]
            title       = text.capitalizeWords(base_name)
            
            newtarget   = os.path.join(target, entry)
            newcrumb    = crumb_templ % {'url': '%s/index.html', 
                                         'text': main_title}
            newcrumbs   = breadcrumbs[:] + [newcrumb]
            
            entry_title = text.capitalizeWords(entry)
            opts = (basepath, entry, entry_title)
            entry_item = '<a href="%s/%s/index.html">%s</a>' % opts
            entry_contents.append( entry_item )
            
            generateUserDocs(filepath, newtarget, page, newcrumbs, basepath)
    
    # generate the main index file
    indexfilename   = os.path.join(target, 'index.html')
    base_name       = os.path.normpath(path).split(os.path.sep)[-1]
    
    # generate the entry html
    entry_html = ['<ul class=entries>']
    for entry in entry_contents:
        entry_html.append('<li>%s</li>' % entry)
    entry_html.append('</ul>')
    
    # base crumbs
    crumbs = []
    count  = len(breadcrumbs)
    for i, crumb in enumerate(breadcrumbs):
        crumbs.append(crumb % (basepath + '/..' * count))
    
    url_handler.setRootUrl(basepath + '/..' * count)
    
    # add the parent crumb
    crumb = crumb_templ % {'url': '#', 'text': main_title}
    crumbs.append(crumb)
    
    # generate the environ
    environ = ENVIRON.copy()
    environ['title']        = main_title
    environ['base_url']     = base_url
    environ['static_url']   = static_url
    environ['breadcrumbs']  = ''.join(crumbs)
    environ['sub_pages']    = ''.join(entry_html)
    environ['navigation'] %= environ
    
    # include a base template
    if ( not has_index_file ):
        wiki_templ = templates.template('userguide.html')
    else:
        f = open(os.path.join(path, 'index.wiki'), 'r')
        wiki_txt = f.read()
        f.close()
        
        options = RENDER_OPTIONS.copy()
        options['FILENAME'] = indexfilename
        options['ROOT'] = base_url
        wiki_templ = wikitext.render(wiki_txt,
                                     url_handler,
                                     options=options)
    
    # generate the contents
    environ['contents'] = wiki_templ % environ
    
    html = page % environ
    
    # generate the index HTML
    index_file = open(indexfilename, 'w')
    index_file.write(html)
    index_file.close()

def generateXdk(srcpath, destfile):
    """
    Generates an XDK file based on the inputed src path of documentation.
    
    An XDK file is a ZIP file that can be used with the XDK browser for
    looking up documentation.
    
    :param      srcpath | <str>
                destfile | <str>
    """
    srcpath = os.path.normpath(srcpath)
    zfile = zipfile.ZipFile(destfile, 'w')
    
    for path, folders, files in os.walk(srcpath):
        if ( '.svn' in path ):
            continue
            
        arcpath = path.replace(srcpath, '')
        for filename in files:
            arcfilename = os.path.join(arcpath, filename)
            logger.info('Compressing %s...' % arcfilename)
            
            zfile.write(os.path.join(path, filename), 
                        os.path.join(arcpath, filename))
    
    zfile.close()

def init_environ( module, config ):
    """
    Initializes the global environ with the given config module.  If the given
    module is None, then the default_config will be used.
    
    :param      module | <module>
    :param      config | <module> || None
    """
    if ( not config ):
        config = default_config
    
    #---------------------------------------------------------------------------
    
    # genrate module information
    try:
        module_title = config.MODULE_TITLE
    except AttributeError:
        module_title = module.__name__
    
    try:
        module_version = config.MODULE_VERSION
    except AttributeError:
        try:
            module_version = module.__version__
        except AttributeError:
            module_version = '0.0.0'
    
    #---------------------------------------------------------------------------
    
    # generate copyright information
    copyright = []
    try:
        show_docgen_link = config.SHOW_DOCGEN_LINK
    except AttributeError:
        show_docgen_link = True
    
    if ( show_docgen_link ):
        link = projex.website()
        copyright.append('generated by <a href="%s">docgen</a>' % link)
    
    try:
        title = config.COMPANY_TITLE
    except AttributeError:
        title = 'Projex Software, LLC'
    
    try:
        url = config.COMPANY_URL
    except AttributeError:
        url = projex.website()
    
    year = datetime.date.today().year
    opts = (year, url, title)
    copyright.append('copyright &copy; %i <a href="%s">%s</a>' % opts)
    
    #---------------------------------------------------------------------------
    
    # grab the theme information
    try:
        theme = config.THEME
    except AttributeError:
        theme = 'base'
    
    try:
        theme_path = config.THEME_PATH
    except AttributeError:
        theme_path = ''
    
    #---------------------------------------------------------------------------
    
    # generate the title bar links
    try:
        links = config.NAVIGATION_LINKS
    except AttributeError:
        links = []
    
    templ = templates.template('link_navigation.html')
    navigation_links = []
    for title, url in links:
        navigation_links.append(templ % {'title': title, 'url': url})
    
    #---------------------------------------------------------------------------
    
    ENVIRON.clear()
    ENVIRON['navigation']           = ''.join(navigation_links)
    ENVIRON['copyright']            = ' '.join(copyright)
    ENVIRON['module_title']         = module_title
    ENVIRON['module_version']       = module_version
    
    templates.setTheme(theme)
    templates.setThemePath(theme_path)

if ( __name__ == '__main__' ):
    logging.basicConfig()
    generate.run(sys.argv)