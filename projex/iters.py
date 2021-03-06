#!/usr/bin/python

""" 
Defines iteration utilities
"""

# define authorship information
__authors__         = ['Eric Hulser']
__author__          = ','.join(__authors__)
__credits__         = []
__copyright__       = 'Copyright (c) 2011, Projex Software'
__license__         = 'LGPL'

__maintainer__      = 'Projex Software'
__email__           = 'team@projexsoftware.com'

import itertools

def batch(iterable, length):
    """
    Returns a series of iterators across the inputed iterable method, 
    broken into chunks based on the inputed length.
    
    :param      iterable | <iterable>  | (list, tuple, set, etc.)
                length   | <int> 
    
    :credit    http://en.sharejs.com/python/14362
    
    :return     <generator>
    
    :usage      |>>> import projex.iters
                |>>> for batch in projex.iters.batch(range(100), 10):
                |...    print list(batch)
                |[0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
                |[10, 11, 12, 13, 14, 15, 16, 17, 18, 19]
                |[20, 21, 22, 23, 24, 25, 26, 27, 28, 29]
                |[30, 31, 32, 33, 34, 35, 36, 37, 38, 39]
                |[40, 41, 42, 43, 44, 45, 46, 47, 48, 49]
                |[50, 51, 52, 53, 54, 55, 56, 57, 58, 59]
                |[60, 61, 62, 63, 64, 65, 66, 67, 68, 69]
                |[70, 71, 72, 73, 74, 75, 76, 77, 78, 79]
                |[80, 81, 82, 83, 84, 85, 86, 87, 88, 89]
                |[90, 91, 92, 93, 94, 95, 96, 97, 98, 99]
    """
    source_iter = iter(iterable)
    while True:
        batch_iter = itertools.islice(source_iter, length)
        yield itertools.chain([batch_iter.next()], batch_iter)