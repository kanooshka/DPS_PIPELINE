#!/usr/bin/python

""" Provides a library of reusable user interface components. """

# define authorship information
__authors__         = ['Eric Hulser']
__author__          = ','.join(__authors__)
__credits__         = [
    ('Yusuke Kamiyamane',
     'Fuque icon pack from findicons.com under Creative Commons.'),
    ('Alexey Egorov',
     'Checkbox icons for XTreeWidget from findicons.com under Freeware.'),
    ('Moment Icons',
     'Folder icons from findicons.com under Creative Commons.'),
]
__copyright__       = 'Copyright (c) 2011, Projex Software'
__license__         = 'LGPL'

# maintanence information
__maintainer__      = 'Projex Software'
__email__           = 'team@projexsoftware.com'

#------------------------------------------------------------------------------

# define version information (major,minor,maintanence)
__depends__ = ['projex', 'PyQt4', 'PySide']
__major__   = 0
__minor__   = 13

try:
    from __revision__ import __revision__
except:
    __revision__ = 0

__version_info__   = (__major__, __minor__, __revision__)
__version__        = '%s.%s' % (__major__, __minor__)

#------------------------------------------------------------------------------

from projexui.xcommands     import *
from projexui.xwidgetvalue  import *
from projexui.xdatatype     import *