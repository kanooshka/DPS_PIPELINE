""" Sets up the Qt environment to work with various Python Qt wrappers """

# define authorship information
__authors__         = ['Eric Hulser']
__author__          = ','.join(__authors__)
__credits__         = []
__copyright__       = 'Copyright (c) 2012, Projex Software'
__license__         = 'LGPL'

# maintenance information
__maintainer__      = 'Projex Software'
__email__           = 'team@projexsoftware.com'

__all__ = [# helpers
           'uic',
           'wrapVariant',
           'unwrapVariant',
           'PyObject',
            
           # modules
           'QtCore',
           'QtGui',
           'QtXml',
           'Qsci',
           'QtWebKit',
           'QtDesigner',
           'QtNetwork',
           
           # variables
           'Signal',
           'Slot',
           'Property',
           'QStringList']

import logging
import os
import sys

logger = logging.getLogger(__name__)

QT_WRAPPER = os.environ.get('PROJEXUI_QT_WRAPPER', 'PyQt4')

# load the specific wrapper from the environment
package = 'projexui.qt.%s_wrapper' % QT_WRAPPER.lower()
__import__(package)

# define the globals we're going to use
glbls = globals()
for name in __all__:
    glbls[name] = None

#----------------------------------------------------------

# define global methods
def wrapVariant(variant):
    if hasattr(QtCore, 'QVariant'):
        return QtCore.QVariant(variant)
    return variant

def unwrapVariant(variant, default=None):
    if type(variant).__name__ == 'QVariant':
        if not variant.isNull():
            return variant.toPyObject()
        return default
    
    if variant is None:
        return default
    return variant

def wrapNone(value):
    """
    Handles any custom wrapping that needs to happen for Qt to process
    None values properly (PySide issue)
    
    :param      value | <variant>
    
    :return     <variant>
    """
    return value

def unwrapNone(value):
    """
    Handles any custom wrapping that needs to happen for Qt to process
    None values properly (PySide issue)
    
    :param      value | <variant>
    
    :return     <variant>
    """
    return value

# setup the globals that are going to be wrapped
if package:
    sys.modules[package].createMap(globals())
    
    # define the modules for importing
    sys.modules['projexui.qt.QtCore']     = QtCore
    sys.modules['projexui.qt.QtDesigner'] = QtDesigner
    sys.modules['projexui.qt.QtGui']      = QtGui
    sys.modules['projexui.qt.Qsci']       = Qsci
    sys.modules['projexui.qt.QtWebKit']   = QtWebKit
    sys.modules['projexui.qt.QtNetwork']  = QtNetwork
    sys.modules['projexui.qt.QtXml']      = QtXml