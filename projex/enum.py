#!/usr/bin/python

""" 
Defines the enum class type that can be used to generate 
enumerated types 
"""

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

# use the text module from projex
from projex import text

class enum(dict):
    """ 
    Class for generating enumerated types. 
    
    :usage      |>>> from projex.enum import enum
                |>>> TestType = enum( 'Value1', 'Value2', 'Value3' )
                |>>> TestType.Value1 | TestType.Value2
                |3
                |>>> (3 & TestType.Value1) != 0
                |True
                |>>> TestType['Value1']
                |1
                |>>> TestType[3]
                |'Value1'
                |>>> TestType.Value1
                |1
                |>>> TestType.keys()
                |[1,2,4]
    """
    
    def __getitem__(self, key):
        """
        Overloads the base dictionary functionality to support
        lookups by value as well as by key.  If the inputed
        type is an integer, then a string is returned.   If the
        lookup is a string, then an integer is returned
        
        :param      key     <str> || <int>
        :return     <int> || <key>
        """
        # lookup the key for the inputed value
        if type(key) in (int, long):
            result = self.text(key)
            if not result:
                raise AttributeError, key
            return result
        
        # lookup the value for the inputed key
        else:
            return super(enum, self).__getitem__( key )
    
    def __init__(self, *args, **kwds):
        """
        Initializes the enum type by assigning a binary
        value to the inputed arguments in the order they
        are supplied.
        """
        super(enum, self).__init__()
        
        # store the base types for different values
        self._bases = {}
        
        # update based on the inputed arguments
        kwds.update(dict([(key, 2**index) for index, key in enumerate(args)]))
        
        # set the properties
        for key, value in kwds.items():
            setattr(self, key, value)
        
        # update the keys based on the current keywords
        self.update(kwds)
    
    def add(self, key, value=None):
        """
        Adds the new key to this enumerated type.
        
        :param      key | <str>
        """
        if value is None:
            value = 2**(len(self))
        
        self[key] = value
        setattr(self, key, self[key])
        return value
    
    def all(self):
        """
        Returns all the values joined together.
        
        :return     <int>
        """
        out = 0
        for key, value in self.items():
            out |= value
        return out
    
    def base(self, value, recurse=True):
        """
        Returns the root base for the given value from this enumeration.
        
        :param      value   | <variant>
                    recurse | <bool>
        """
        while value in self._bases:
            value = self._bases[value]
            if not recurse:
                break
        return value
    
    def extend(self, base, key, value=None):
        """
        Adds a new definition to this enumerated type, extending the given
        base type.  This will create a new key for the type and register
        it as a new viable option from the system, however, it will also
        register its base information so you can use enum.base to retrieve
        the root type.
        
        :param      base  | <variant> | value for this enumeration
                    key   | <str>     | new key for the value
                    value | <variant> | if None is supplied, it will be auto-assigned
        
        :usage      |>>> from projex.enum import enum
                    |>>> Types = enum('Integer', 'Boolean')
                    |>>> Types.Integer
                    |1
                    |>>> Types.Boolean
                    |2
                    |>>> Types.extend(Types.Integer, 'BigInteger')
                    |>>> Types.BigInteger
                    |4
                    |>>> Types.base(Types.BigInteger)
                    |1
        """
        new_val = self.add(key, value)
        self._bases[new_val] = base
    
    def labels(self):
        """
        Return a list of "user friendly" labels.
        
        :return     <list> [ <str>, .. ]
        """
        keys = self.keys()
        keys.sort(lambda x, y: cmp(self[x], self[y]))
        return [ text.pretty(key) for key in keys ]
    
    def text(self, value, default=''):
        """
        Returns the text for the inputed value.
        
        :return     <str>
        """
        for key, val in self.items():
            if ( val == value ):
                return key
        return default
    
    def valueByLabel(self, label):
        """
        Determine a given value based on the inputed label.

        :param      label   <str>
        
        :return     <int>
        """
        keys    = self.keys()
        labels  = [ text.pretty(key) for key in keys ]
        if ( label in labels ):
            return self[keys[labels.index(label)]]
        return 0