""" 
Defines the LazyModule class which will delay loading of a python module until
it is accessed the first time.

doing:

scoped_name = LazyModule('package_name.module_name')

is equivalent as doing:

from package_name import module_name as scoped_name

Only the module will not actually load itself until the first time a value
is attempted to pull from the module.  Once loaded, it will be able to be
used like a standard python module.  This is very useful when dealing with
slow loading modules and import cycles.

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

import sys

class LazyModule(object):
    def __dir__(self):
        mod = self.__dict__['__module_inst__']
        if mod is None:
            mod_name = self.__dict__['__module_name__']
            
            # retrieve the module from the sys location, importing it if
            # necessary
            mod = sys.modules.get(mod_name)
            if mod is None:
                __import__(mod_name)
                mod = sys.modules.get(mod_name)
            
            self.__dict__['__module_inst__'] = mod
        
        return dir(mod)
    
    def __getattr__(self, key):
        """
        Retrieves the value from the module wrapped by this instance.
        
        :param      key | <str>
        
        :return     <variant>
        """
        mod = self.__dict__['__module_inst__']
        if mod is None:
            mod_name = self.__dict__['__module_name__']
            
            # retrieve the module from the sys location, importing it if
            # necessary
            mod = sys.modules.get(mod_name)
            if mod is None:
                __import__(mod_name)
                mod = sys.modules.get(mod_name)
            
            self.__dict__['__module_inst__'] = mod
        
        return getattr(mod, key)
    
    def __setattr__(self, key, value):
        """
        Sets the value within the module wrapped by this instance to the
        inputed value.
        
        :param      key | <str>
                    value | <variant>
        """
        mod = self.__dict__['__module_inst__']
        if mod is None:
            mod_name = self.__dict__['__module_name__']
            
            # retrieve the module from the sys location, importing it if
            # necessary
            mod = sys.modules.get(mod_name)
            if mod is None:
                __import__(mod_name)
                mod = sys.modules.get(mod_name)
            
            self.__dict__['__module_inst__'] = mod
        
        return setattr(mod, key, value)
    
    def __init__(self, module_name):
        self.__dict__['__module_name__'] = module_name
        self.__dict__['__module_inst__'] = None