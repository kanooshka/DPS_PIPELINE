#!/usr/bin/python

""" 
Provides additional utilities for data transfer using REST interfaces,
specifically helpers for converting between Python and JSON formats.
"""

# define authorship information
__authors__         = ['Eric Hulser']
__author__          = ','.join(__authors__)
__credits__         = []
__copyright__       = 'Copyright (c) 2011, Projex Software'
__license__         = 'LGPL'

__maintainer__      = 'Projex Software'
__email__           = 'team@projexsoftware.com'

import datetime
import logging
import re

try:
    import json
except ImportError:
    try:
        import simplejson as json
    except ImportError:
        json is None

logger = logging.getLogger(__name__)

_encoders = []
_decoders = []

def json2py(json_obj):
    """
    Converts the inputed JSON object to a python value.
    
    :param      json_obj | <variant>
    """
    for key, value in json_obj.items():
        if type(value) not in (str, unicode):
            continue
                
        # restore a datetime
        if re.match('^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}:\d+$', value):
            value = datetime.datetime.strptime(value, '%Y-%m-%d %H:%M:%S:%f')
        elif re.match('^\d{4}-\d{2}-\d{2}$', value):
            year, month, day = map(int, value.split('-'))
            value = datetime.date(year, month, day)
        elif re.match('^\d{2}:\d{2}:\d{2}:\d+$', value):
            hour, minute, second, micro = map(int, value.split(':'))
            value = datetime.time(hour, minute, second, micro)
        else:
            found = False
            for decoder in _decoders:
                success, new_value = decoder(value)
                if success:
                    value = new_value
                    found = True
                    break
            
            if not found:
                continue
        
        json_obj[key] = value
    return json_obj

def jsonify(py_data):
    """
    Converts the inputed Python data to JSON format.
    
    :param      py_data | <variant>
    """
    return json.dumps(py_data, default=py2json)

def py2json(py_obj):
    """
    Converts the inputed python object to JSON format.
    
    :param      py_obj | <variant>
    """
    if type(py_obj) == datetime.datetime:
        return py_obj.strftime('%Y-%m-%d %H:%M:%S:%f')
    elif type(py_obj) == datetime.date:
        return py_obj.strftime('%Y-%m-%d')
    elif type(py_obj) == datetime.time:
        return py_obj.strftime('%H:%M:%S:%f')
    else:
        # look through custom plugins
        for encoder in _encoders:
            success, value = encoder(py_obj)
            if success:
                return value
        
        opts = (py_obj, type(py_obj))
        raise TypeError('Unserializable object {} of type {}'.format(*opts))

def unjsonify(json_data):
    """
    Converts the inputed JSON data to Python format.
    
    :param      json_data | <variant>
    """
    return json.loads(json_data, object_hook=json2py)

def register(encoder=None, decoder=None):
    """
    Registers an encoder method and/or a decoder method for processing
    custom values.  Encoder and decoders should take a single argument
    for the value to encode or decode, and return a tuple of (<bool>
    success, <variant> value).  A successful decode or encode should
    return True and the value.
    
    :param      encoder | <callable> || None
                decoder | <callable> || None
    """
    if encoder:
        _encoders.append(encoder)
    if decoder:
        _decoders.append(decoder)