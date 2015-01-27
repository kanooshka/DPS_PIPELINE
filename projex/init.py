#!/usr/bin/python

""" 
This is the core Python package for all of the projex software
projects.  At the bare minimum, this package will be required, and 
depending on which software you are interested in, other packages 
will be required and updated.
"""

# define authorship information
__authors__         = ['Eric Hulser']
__author__          = ','.join(__authors__)
__credits__         = []
__copyright__       = 'Copyright (c) 2011, Projex Software'
__license__         = 'LGPL'

__maintainer__      = 'Projex Software'
__email__           = 'team@projexsoftware.com'

#------------------------------------------------------------------------------

import importlib
import logging
import os
import pkgutil
import sys

# initialize the main projex logger class
logger       = logging.getLogger(__name__)

WEBSITES     = {
    'home': 'http://www.projexsoftware.com',
    'docs': 'http://docs.projexsoftware.com',
    'blog': 'http://blog.projexsoftware.com',
    'dev':  'http://dev.projexsoftware.com'
}

SUBCONTEXT_MAP = {
    ('home', 'Product'):      '%(base_url)s/products/%(app)s',
    ('docs', 'UserGuide'):    '%(base_url)s/userguide/%(app)s',
    ('docs', 'APIReference'): 'http://api.projexsoftware.com/static/'\
                              '%(app)s/current/index.html',
    ('dev',  'Project'):      '%(base_url)s/projects/%(app)s',
    ('dev',  'NewIssue'):     '%(base_url)s/projects/%(app)s/'\
                              'issues/new?tracker_id=1',
    ('dev',  'NewFeature'):   '%(base_url)s/projects/%(app)s/'\
                              'issues/new?tracker_id=2',
}

class attrdict(object):
    def __init__(self, data):
        self.__dict__.update(data)

#------------------------------------------------------------------------------

def environ():
    """
    Returns the current environment that is being used.
    
    :return     <projex.envmanager.EnvManager> || None
    """
    from projex.envmanager import EnvManager
    return EnvManager.current()

def importmodules(package_or_toc):
    """
    Imports all the sub-modules of a package, a useful technique for developing
    plugins.  By default, this method will walk the directory structure looking
    for submodules and packages.  You can also specify a __toc__ attribute
    on the package to define the sub-modules that you want to import.
    
    :param      package_or_toc | <package> || <str> filename
    
    :usage      |>>> import projex
                |>>> import projex.docgen
                |>>> projex.importmodules(projex.docgen)
                |[<projex.docgen.commands>, <projex.docgen.default_config>, ..]
    
    :return     [<module> || <package>, ..]
    """
    output = []
    
    # import from a set toc file
    if type(package_or_toc) in (str, unicode):
        f = open(package_or_toc, 'r')
        toc = f.readlines()
        f.close()
    
    # import from a given package
    else:
        toc = getattr(package_or_toc, '__toc__', [])
        if not toc:
            path = os.path.dirname(package_or_toc.__file__)
            name = packageFromPath(path)
            toc = [modname for _, modname, _ in pkgutil.iter_modules([path])]
            toc = filter(lambda x: not '__init__' in x and \
                                   not '__plugins__' in x,
                         toc)
            setattr(package_or_toc, '__toc__', toc)
            
            toc = map(lambda x: '{0}.{1}'.format(name, x), toc)
    
    # import using standard means (successful for when dealing with 
    for modname in toc:
        if not modname:
            continue
        
        logger.debug('Importing: %s' % modname)
        try:
            __import__(modname)
            sub_module = sys.modules[modname]
        except ImportError, KeyError:
            logger.exception('Error importing module: %s' % modname)
            continue
        
        output.append(sub_module)
    
    return output

def importobject( module_name, object_name ):
    """
    Imports the object with the given name from the inputed module.
    
    :param      module_name | <str>
                object_name | <str>
    
    :usage      |>>> import projex
                |>>> modname = 'projex.envmanager'
                |>>> attr = 'EnvManager'
                |>>> EnvManager = projex.importobject(modname, attr)
    
    :return     <object> || None
    """
    if ( not module_name in sys.modules ):
        try:
            __import__(module_name)
        except ImportError:
            logger.exception('Could not import module: %s' % module_name)
            return None
    
    module = sys.modules.get(module_name)
    if ( not module ):
        logger.warning('No module %s found.' % module_name)
        return None
    
    if ( not hasattr(module, object_name) ):
        logger.warning('No object %s in %s.' % (object_name, module_name))
        return None
    
    return getattr(module, object_name)

def packageRootPath( path ):
    """
    Retruns the root file path that defines a Python package from the inputed
    path.
    
    :param      path | <str>
    
    :return     <str>
    """
    path = str(path)
    if ( os.path.isfile(path) ):
        path = os.path.dirname(path)
        
    parts = os.path.normpath(path).split(os.path.sep)
    package_parts = []
    
    for i in range(len(parts), 0, -1):
        filename = os.path.sep.join(parts[:i] + ['__init__.py'])
        
        if ( not os.path.isfile(filename) ):
            break
        
        package_parts.insert(0, parts[i-1])
    
    return os.path.abspath(os.path.sep.join(parts[:-len(package_parts)]))

def packageFromPath( path ):
    """
    Determines the python package path based on the inputed path.
    
    :param      path | <str>
    
    :return     <str>
    """
    path = str(path)
    if ( os.path.isfile(path) ):
        path = os.path.dirname(path)
        
    parts = os.path.normpath(path).split(os.path.sep)
    package_parts = []
    
    for i in range(len(parts), 0, -1):
        filename = os.path.sep.join(parts[:i] + ['__init__.py'])
        
        if ( not os.path.isfile(filename) ):
            break
        
        package_parts.insert(0, parts[i-1])
    
    return '.'.join(package_parts)

def refactor( module, name, repl ):
    """
    Convenience method for the EnvManager.refactor 
    """
    environ().refactor( module, name, repl )

def requires( *modules ):
    """
    Convenience method to the EnvManager.current().requires method.
    
    :param      *modules    | (<str>, .. )
    """
    environ().requires(*modules)

def website( app = None, mode = 'home', subcontext = 'UserGuide' ):
    """
    Returns the website location for projex software.
    
    :param      app  | <str> || None
                mode | <str> (home, docs, blog, dev)
    
    :return     <str>
    """
    base_url = WEBSITES.get(mode, '')
    
    if ( app and base_url ):
        opts      = {'app': app, 'base_url': base_url}
        base_url  = SUBCONTEXT_MAP.get((mode, subcontext), base_url)
        base_url %= opts
        
    return base_url