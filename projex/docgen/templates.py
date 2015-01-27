#!/usr/bin/python

""" 
Defines the different HTML templates that will be used for generating
the documentation.
"""

# define authorship information
__authors__         = ['Eric Hulser']
__author__          = ','.join(__authors__)
__credits__         = ['Eric Hulser']
__copyright__       = 'Copyright (c) 2011, Projex Software'
__license__         = 'LGPL'

# maintanence information
__maintainer__      = 'Projex Software'
__email__           = 'team@projexsoftware.com'

#------------------------------------------------------------------------------

import os.path

from projex import resources

_cache = {}
_theme = 'base'
_theme_path = ''

def clear():
    """
    Clears the template cache.
    """
    _cache.clear()

def path( name ):
    """
    Looks up the given filepath.
    
    :param      name | <str>
    
    :return     <str>
    """
    # use a standard theme
    if ( not _theme_path ):
        return resources.find('docgen/%s/%s' % (_theme, name))
    
    # use a custom theme
    else:
        return os.path.join(_theme_path, name)

def template( name ):
    """
    Returns the template from the inputed name from the template files in the
    templ path.
    
    :return     <str>
    """
    cached = _cache.get(name)
    if ( cached != None ):
        return cached
    
    filename = path('templ/' + name)
    if ( os.path.exists(filename) ):
        templ_file = open(filename, 'r')
        cached = templ_file.read()
        templ_file.close()
    else:
        cached = ''
    
    _cache[str(name)] = cached
    return cached

def setTheme( theme ):
    """
    Sets the HTML & CSS theme that will be used for the docgen documentation.
    
    :return     <str>
    """
    global _theme
    _theme = str(theme)

def setThemePath( theme_path ):
    """
    Sets the path to a custom theme system.
    
    :param      theme_path | <str>
    """
    global _theme_path
    _theme_path = str(theme_path)

def theme():
    """
    Returns the theme that will be used for the docgen.
    
    :return     <str>
    """
    return _theme

def themePath():
    """
    Returns the custom theme path defined for this system.
    
    :return     <str>
    """
    return _theme_path