#!/usr/bin/python

""" Defines the scheme class type for interfaces. """

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

from projexui.qt import QtCore, Signal

class XHistoryStack(QtCore.QObject):
    currentIndexChanged = Signal(int)
    currentUrlChanged   = Signal(str)
    
    def __init__( self, parent = None ):
        super(XHistoryStack, self).__init__(parent)
        self._blockStack    = False
        self._stack         = []
        self._titles        = {}
        self._homeUrl       = ''
        self._currentIndex  = -1
        self._maximum       = 20
    
    def backUrl(self, count=1):
        """
        Returns the url that will be used when traversing backward.
        
        :return     <str>
        """
        try:
            return self._stack[self._currentIndex + count]
        except IndexError:
            return ''
    
    def clear( self ):
        """
        Clears the current history.
        """
        self._stack         = []
        self._titles        = {}
        self._currentIndex  = -1
        self.emitCurrentChanged()
    
    def count( self ):
        """
        Returns the count for all the urls in the system.
        
        :return     <int>
        """
        return len(self._stack)
    
    def currentIndex( self ):
        """
        Returns the current index for the history stack.
        
        :return     <int>
        """
        return self._currentIndex
    
    def currentUrl( self ):
        """
        Returns the current url path for the history stack.
        
        :return     <str>
        """
        return self.urlAt(self.currentIndex())
    
    def emitCurrentChanged( self ):
        """
        Emits the current index changed signal provided signals are not blocked.
        """
        if ( not self.signalsBlocked() ):
            self.currentIndexChanged.emit(self.currentIndex())
            self.currentUrlChanged.emit(self.currentUrl())
    
    def forwardUrl(self, count=1):
        """
        Returns the url that will be used when traversing backward.
        
        :return     <str>
        """
        try:
            return self._stack[self._currentIndex - count]
        except IndexError:
            return ''
    
    def future( self ):
        """
        Shows all the future - all the urls from after the current index \
        in the stack.
        
        :return     [ <str>, .. ]
        """
        return self._stack[:self._currentIndex]
    
    def goBack( self ):
        """
        Goes up one level if possible and returns the url at the current level.
        If it cannot go up, then a blank string will be returned.
        
        :return     <str>
        """
        index = self._currentIndex + 1
        if ( index == len(self._stack) ):
            return ''
        
        self._blockStack = True
        self._currentIndex = index
        self.emitCurrentChanged()
        self._blockStack = False
        return self.currentUrl()
    
    def goHome( self ):
        """
        Goes to the home url.  If there is no home url specifically set, then \
        this will go to the first url in the history.  Otherwise, it will \
        look to see if the home url is in the stack and go to that level, if \
        the home url is not found, then it will be pushed to the top of the \
        stack using the push method.
        """
        self._blockStack = True
        url = self.homeUrl()
        if ( url and url in self._stack ):
            self._currentIndex = self._stack.index(url)
            self.emitCurrentChanged()
        elif ( url ):
            self.push(url)
        else:
            self._currentIndex = len(self._stack) - 1
            self.emitCurrentChanged()
        self._blockStack = False
    
    def goForward( self ):
        """
        Goes down one level if possible and returns the url at the current \
        level.  If it cannot go down, then a blank string will be returned.
        
        :return     <str>
        """
        index = self._currentIndex - 1
        if ( index < 0 ):
            return ''
        
        self._blockStack = True
        self._currentIndex = index
        self.emitCurrentChanged()
        self._blockStack = False
        return self.currentUrl()
    
    def history( self ):
        """
        Shows all the history - all the urls from before the current index \
        in the stack.
        
        :return     [ <str>, .. ]
        """
        return self._stack[self._currentIndex+1:]
    
    def hasHistory( self ):
        """
        Returns whether or not there is currently history in the system.
        
        :return     <bool>
        """
        return self._currentIndex < (len(self._stack) - 1)
    
    def hasFuture( self ):
        """
        Returns whether or not there are future urls in the system.
        
        :return     <bool>
        """
        return self._currentIndex > 0
    
    def homeUrl( self ):
        """
        Returns the home url for this stack instance.
        
        :return     <str>
        """
        return self._homeUrl
    
    def indexOf( self, url ):
        """
        Returns the index of the inputed url for this stack.  If the url is \
        not found, then -1 is returned.
        
        :param      url | <str>
        
        :return     <int>
        """
        url = str(url)
        if ( url in self._stack ):
            return self._stack.index(url)
        return -1
    
    def maximum( self ):
        """
        Returns the maximum number of urls that should be stored in history.
        
        :return     <int>
        """
        return self._maximum
    
    def push( self, url, title='' ):
        """
        Pushes the url into the history stack at the current index.
        
        :param      url | <str>
        
        :return     <bool> | changed
        """
        # ignore refreshes of the top level
        if self.currentUrl() == url or self._blockStack:
            return False
        
        new_stack           = self._stack[self._currentIndex:]
        new_stack.insert(0, str(url))
        self._stack         = new_stack[:self.maximum()]
        self._currentIndex  = 0
        self._titles[str(url)] = title
        self.emitCurrentChanged()
        return True
        
    def setCurrentIndex( self, index ):
        """
        Sets the current index for the history stack.
        
        :param      index | <int>
        
        :return     <bool> | success
        """
        if ( 0 <= index and index < len(self._stack) ):
            self._currentIndex = index
            self.emitCurrentChanged()
            return True
        return False
    
    def setCurrentUrl( self, url ):
        """
        Sets the current url from within the history.  If the url is not \
        found, then nothing will happen.  Use the push method to add new \
        urls to the stack.
        
        :param      url | <str>
        """
        url = str(url)
        if ( not url in self._stack ):
            return False
        
        self._blockStack = True
        self.setCurrentIndex(self._stack.index(url))
        self._blockStack = False
        
        return True
    
    def setHomeUrl( self, url ):
        """
        Defines the home url for this history stack.
        
        :param      url | <str>
        """
        self._homeUrl = url
    
    def setMaximum( self, maximum ):
        """
        Sets the maximum number of urls to store in history.
        
        :param      maximum | <str>
        """
        self._maximum   = maximum
        self._stack     = self._stack[:maximum]
        
        if ( maximum <= self._currentIndex ):
            self._currentIndex = maximum - 1
    
    def urlAt( self, index ):
        """
        Returns the url at the inputed index wihtin the stack.  If the index \
        is invalid, then a blank string is returned.
        
        :return     <str>
        """
        if ( 0 <= index and index < len(self._stack) ):
            return self._stack[index]
        return ''
        
    def urls( self ):
        """
        Returns a list of the urls in this history stack.
        
        :return     [<str>, ..]
        """
        return self._stack
    
    def titleOf(self, url):
        """
        Returns the title for the inputed url.
        
        :param      url | <str>
        
        :return     <str>
        """
        title = self._titles.get(str(url))
        if not title:
            title = str(url).split('/')[-1]
        
        return title