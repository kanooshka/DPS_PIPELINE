#!/usr/bin/python

""" Compiles and defines commonly used regular expressions. """

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

EMAIL           = '^[\w\-_\.]+@\w+\.\w+$'
EMAIL_HELP      = 'Requires email to contain only letters, numbers, '\
                  'dashes, underscores, and periods.  Must be in the '\
                  'format of "address@domain.type"'

PASSWORD        = '^[\w\.\-_@#$%^&+=]{5,10}$'
PASSWORD_HELP   = 'Passwords must be between 5-10 characters long, contain '\
                  'at least 1 letter, 1 number, and 1 special character, '\
                  'like a period or underscore.'

DATETIME        = '(?P<month>\d{1,2})[/-:\.](?P<day>\d{1,2})[/-:\.]'\
                  '(?P<year>\d{2,4}) (?P<hour>\d{1,2}):(?P<min>\d{2}):?'\
                  '(?P<second>\d{2})?\s?(?P<ap>[ap]m?)?'

DATE            = '(?P<month>\d{1,2})[/-:\.](?P<day>\d{1,2})[/-:\.]'\
                  '(?P<year>\d{2,4})'

TIME            = '(?P<hour>\d{1,2}):(?P<min>\d{2}):?'\
                  '(?P<second>\d{2})?\s?(?P<ap>[ap]m?)?'

def fromSearch(text):
    """
    Generates a regular expression from 'simple' search terms.
    
    :param      text | <str>
    
    :usage      |>>> import projex.regex
                |>>> projex.regex.fromSearch('*cool*')
                |'^.*cool.*$'
                |>>> projex.projex.fromSearch('*cool*,*test*')
                |'^.*cool.*$|^.*test.*$'
    
    :return     <str>
    """
    terms = []
    for term in str(text).split(','):
        # assume if no *'s then the user wants to search anywhere as keyword
        if not '*' in term:
            term = '*%s*' % term
        
        term = term.replace('*', '.*')
        terms.append('^%s$' % term)
    
    return '|'.join(terms)