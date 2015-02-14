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

import logging
import os.path

from projexui import qt #import wrapVariant, unwrapVariant
from PyQt4 import QtGui

# used to register saving and loading systems
from projexui.xcolorset                import XColorSet, XPaletteColorSet

_dataValueTypes     = {}
logger = logging.getLogger(__name__)

def registerDataType( dataType, encoder, decoder ):
    """
    Registers a encoder/decoder for saving and restoring data from a QVariant.
    
    :param      dataType  | <str>
                encoder   | <method>
                decoder   | <method>
    """
    _dataValueTypes[str(dataType)] = (encoder, decoder)

def restoreDataSet( settings, key, dataSet ):
    """
    Restores the dataset settings to the inputed data set for the given key.
    
    :param      settings | <QSettings>
                key      | <str>
                dataSet  | <projex.dataset.DataSet>
    """
    for datakey in dataSet.keys():
        vtype = qt.unwrapVariant(settings.value('%s/%s/type' % (key, datakey)))
        value = qt.unwrapVariant(settings.value('%s/%s/value' % (key, datakey)))
        
        if ( vtype is None ):
            continue
        
        vtype = str(vtype)
        
        if ( vtype in _dataValueTypes ):
            datavalue = _dataValueTypes[vtype][1](value)
        else:
            logger.warning('Could not restore %s' % vtype)
            continue
        
        if ( type(datavalue).__name__ == 'QString' ):
            datavalue = unicode(datavalue)
        
        dataSet.setValue(datakey, datavalue)

def saveDataSet( settings, key, dataSet ):
    """
    Records the dataset settings to the inputed data set for the given key.
    
    :param      settings | <QSettings>
                key      | <str>
                dataSet  | <projex.dataset.DataSet>
    """
    for datakey, value in dataSet.items():
        datatype  = type(value).__name__
        
        if ( datatype in _dataValueTypes ):
            datavalue = _dataValueTypes[datatype][0](value)
        else:
            datavalue = value
        
        settings.setValue('%s/%s/type' % (key, datakey), qt.wrapVariant(datatype))
        settings.setValue('%s/%s/value' % (key, datakey), qt.wrapVariant(datavalue))

#-------------------------------------------------------------------------------

# register getter/setter value types
registerDataType('bool',
                 lambda pyvalue:  int(pyvalue),
                 lambda qvariant: qt.unwrapVariant(qvariant, False))

registerDataType('int',
                 lambda pyvalue:  int(pyvalue),
                 lambda qvariant: qt.unwrapVariant(qvariant, 0))

registerDataType('float',
                 lambda pyvalue:  float(pyvalue),
                 lambda qvariant: qt.unwrapVariant(qvariant, 0.0))

registerDataType('str',
                 lambda pyvalue:  str(pyvalue),
                 lambda qvariant: str(qt.unwrapVariant(qvariant, '')))
                 
registerDataType('unicode',
                 lambda pyvalue:  unicode(pyvalue),
                 lambda qvariant: unicode(qt.unwrapVariant(qvariant, '')))

def decodeFont(qvariant):
    font = QtGui.QFont()
    font.fromString(qt.unwrapVariant(qvariant))
    return font

registerDataType('QFont',
                 lambda pyvalue:  str(pyvalue.toString()),
                 decodeFont)

registerDataType('XColorSet',
                lambda pyvalue:  pyvalue.toString(),
                lambda qvariant: XColorSet.fromString(qt.unwrapVariant(qvariant, '')))

registerDataType('XPaletteColorSet',
            lambda pyvalue:  pyvalue.toString(),
            lambda qvariant: XPaletteColorSet.fromString(qt.unwrapVariant(qvariant, '')))
