#!/usr/bin/python

""" Parses through the python source code to generate HTML documentation.  """

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

import logging
from projex.docgen.commands import generate, \
                                   generateModuleDocument

from projex.docgen.doxfile import DoxFile,\
                                  DoxSource

logger = logging.getLogger(__name__)