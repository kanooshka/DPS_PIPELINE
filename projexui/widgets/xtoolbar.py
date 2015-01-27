#!/usr/bin python

""" Defines a more feature rich toolbar. """

# define authorship information
__authors__     = ['Eric Hulser']
__author__      = ','.join(__authors__)
__credits__     = []
__copyright__   = 'Copyright (c) 2011, Projex Software'

# maintanence information
__maintainer__  = 'Projex Software'
__email__       = 'team@projexsoftware.com'

from projexui.qt import Signal
from projexui.qt.QtCore   import Qt
from projexui.qt.QtGui    import QIcon,\
                                 QSizePolicy,\
                                 QToolBar,\
                                 QToolButton,\
                                 QWidget

from projexui       import resources

MAX_SIZE = 16777215

class XToolBar(QToolBar):
    collapseToggled = Signal(bool)
    
    def __init__( self, *args ):
        super(XToolBar, self).__init__( *args )
        
        # set custom properties
        self._collapseButton    = None
        self._collapsed         = True
        self._collapsedSize     = 14
        self._precollapseSize   = None
        
        # set standard options
        self.layout().setSpacing(0)
        self.layout().setContentsMargins(1, 1, 1, 1)
        self.setMovable(False)
        self.clear()
        self.setOrientation(Qt.Horizontal)
        self.setCollapsed(False)
    
    def clear( self ):
        """
        Clears out this toolbar from the system.
        """
        # preserve the collapse button
        super(XToolBar, self).clear()
        
        self._collapseButton = QToolButton(self)
        self._collapseButton.setAutoRaise(True)
        self._collapseButton.setSizePolicy( QSizePolicy.Expanding,
                                            QSizePolicy.Expanding )
        
        self.addWidget(self._collapseButton)
        self.refreshButton()
        
        # create connection
        self._collapseButton.clicked.connect( self.toggleCollapsed )
    
    def count( self ):
        """
        Returns the number of actions linked with this toolbar.
        
        :return     <int>
        """
        return len(self.actions())
    
    def collapseButton( self ):
        """
        Returns the collapsing button for this toolbar.
        
        :return     <QToolButton>
        """
        return self._collapseButton
    
    def isCollapsed( self ):
        """
        Returns whether or not this toolbar is in a collapsed state.
        
        :return     <bool>
        """
        return self._collapsed
    
    def refreshButton( self ):
        """
        Refreshes the button for this toolbar.
        """
        collapsed   = self.isCollapsed()
        btn         = self._collapseButton
        if ( not btn ):
            return
        
        btn.setMaximumSize(MAX_SIZE, MAX_SIZE)
        
        # set up a vertical scrollbar
        if ( self.orientation() == Qt.Vertical ):
            btn.setMaximumHeight(12)
        else:
            btn.setMaximumWidth(12)
            
        icon = ''
        
        # collapse/expand a vertical toolbar
        if ( self.orientation() == Qt.Vertical ):
            if ( collapsed ):
                self.setFixedWidth(self._collapsedSize)
                btn.setMaximumHeight(MAX_SIZE)
                btn.setArrowType(Qt.RightArrow)
            else:
                self.setMaximumWidth(1000)
                self._precollapseSize = None
                btn.setMaximumHeight(12)
                btn.setArrowType(Qt.LeftArrow)
                
        else:
            if ( collapsed ):
                self.setFixedHeight(self._collapsedSize)
                btn.setMaximumWidth(MAX_SIZE)
                btn.setArrowType(Qt.DownArrow)
            else:
                self.setMaximumHeight(1000)
                self._precollapseSize = None
                btn.setMaximumWidth(12)
                btn.setArrowType(Qt.UpArrow)
        
        for index in range(1, self.layout().count()):
            item = self.layout().itemAt(index)
            if ( not item.widget() ):
                continue
                
            if ( collapsed ):
                item.widget().setMaximumSize(0, 0)
            else:
                item.widget().setMaximumSize(MAX_SIZE, MAX_SIZE)
    
    def setCollapsed( self, state ):
        """
        Sets whether or not this toolbar is in a collapsed state.
        
        :return     <bool> changed
        """
        if ( state == self._collapsed ):
            return False
        
        self._collapsed = state
        self.refreshButton()
        
        if ( not self.signalsBlocked() ):
            self.collapseToggled.emit(state)
        
        return True
    
    def setOrientation( self, orientation ):
        """
        Sets the orientation for this toolbar to the inputed value, and \
        updates the contents margins and collapse button based on the vaule.
        
        :param      orientation | <Qt.Orientation>
        """
        super(XToolBar, self).setOrientation(orientation)
        self.refreshButton()
    
    def toggleCollapsed( self ):
        """
        Toggles the collapsed state for this toolbar.
        
        :return     <bool> changed
        """
        return self.setCollapsed(not self.isCollapsed())

__designer_plugins__ = [XToolBar]