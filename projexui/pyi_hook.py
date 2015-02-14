""" Defines the hook required for the PyInstaller to use projexui with it. """

# define authorship information
__authors__         = ['Eric Hulser']
__author__          = ','.join(__authors__)
__credits__         = []
__copyright__       = 'Copyright (c) 2011, Projex Software'
__license__         = 'LGPL'

# maintanence information
__maintainer__      = 'Projex Software'
__email__           = 'team@projexsoftware.com'

__all__ = ['hiddenimports', 'datas']

import os
import projex.pyi

hiddenimports, datas = projex.pyi.collect(os.path.dirname(__file__))

# determine which Qt version to include
wrapper = os.environ.get('PROJEXUI_QT_WRAPPER', 'PyQt4')

# include PySide Libraries
if wrapper == 'PySide':
    hiddenimports += ['PySide.QtUiTools', 'PySide.QtXml', 'PySide.QtWebKit']
    hiddenimports.remove('projexui.qt.pyqt4_wrapper')

# include PyQt4 Libraries
elif wrapper == 'PyQt4':
    hiddenimports += ['PyQt4.QtUiTools', 'PyQt4.QtXml', 'PyQt4.QtWebKit']
    hiddenimports.remove('projexui.qt.pyside_wrapper')
    
#print hiddenimports