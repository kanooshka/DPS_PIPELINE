#!/usr/bin/python

""" Creates reusable resources for the gui systems """

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

import os

_BASE_PATH   = os.path.dirname(__file__)
_BASE_THEME  = 'default'

USE_COMPILED = os.environ.get('PROJEXUI_USE_COMPILED', '').lower() == 'true'

def basePath():
    """
    Returns the base path that will be used when looking up resources for this
    module.
    
    :return     <str>
    """
    return _BASE_PATH

def baseTheme():
    """
    Returns the current base theme name for icons for this resource group.
    
    :return     <str>
    """
    return _BASE_THEME

def find(relpath, root=None, theme=None):
    """
    Returns the path name for the inputed relative path from this base. \
    If no root is supplied, then the current base path will be used.  \
    If no theme is supplied, then the current base theme will be used.
    
    :param      relpath | <str>
    :param      root    | <str> || None
    :param      theme   | <str> || None
    
    :return     <str>
    """
    
    if root is None:
        root = _BASE_PATH
        
    if theme is None:
        theme = _BASE_THEME
    
    if USE_COMPILED:
        __import__('projexui.resources.%s_rc' % theme)
        
        return ':' + relpath
    
    if relpath.startswith('img'):
        return os.path.join(root, theme, relpath)
    
    return os.path.join(root, relpath)

def setBasePath( path ):
    """
    Sets the path for the resources to pull from.
    
    :param      path | <str>
    """
    global _BASE_PATH
    _BASE_PATH = str(path)

def setBaseTheme( theme ):
    """
    Sets the name for the current base theme to be used.
    
    :param      theme | <str>
    """
    global _BASE_THEME
    _BASE_THEME = str(theme)

def stylesheet( name ):
    """
    Loads the inputed stylesheet from the inputed path.
    
    :return     <str>
    """
    filename = find('styles/%s.css' % name)
    if ( not os.path.exists(filename) ):
        return ''
    
    f = open(filename, 'r')
    style = f.read()
    f.close()
    
    return style