#!/usr/bin python

""" Defines a more robust tab widget. """

# define authorship information
__authors__     = ['Eric Hulser']
__author__      = ','.join(__authors__)
__credits__     = []
__copyright__   = 'Copyright (c) 2011, Projex Software'

# maintanence information
__maintainer__  = 'Projex Software'
__email__       = 'team@projexsoftware.com'

import projexui
from projexui import qt
#from cutie import Signal, SIGNAL, Property

from PyQt4.QtCore   import QPoint,\
                                 QSize,\
                                 Qt
                           
from PyQt4.QtGui    import QApplication,\
                                 QCursor, \
                                 QIcon, \
                                 QTabWidget,\
                                 QTabBar,\
                                 QPushButton

from projexui import resources

class XTabBar(QTabBar):
    resized = qt.Signal()
    
    def resizeEvent(self, event):
        """
        Updates the position of the additional buttons when this widget \
        resizes.
        
        :param      event | <QResizeEvet>
        """
        super(XTabBar, self).resizeEvent(event)
        self.resized.emit()

#------------------------------------------------------------------------------

class XTabWidget(QTabWidget):
    addRequested     = qt.Signal(QPoint)
    optionsRequested = qt.Signal(QPoint)
    
    def __init__(self, *args):
        super(XTabWidget, self).__init__(*args)
        
        # create the tab bar
        self.setTabBar(XTabBar(self))
        
        # create custom properties
        self._showAddButton = True
        self._showOptionsButton = True
        
        # create the add button
        self._addButton = QPushButton(self)
        self._addButton.setIcon(QIcon(resources.find('img/tab/add.png')))
        self._addButton.setFixedSize(18, 18)
        self._addButton.setIconSize(QSize(10, 10))
        
        # create the option button
        self._optionsButton = QPushButton(self)
        self._optionsButton.setFixedSize(22, 18)
        self._optionsButton.setIcon(QIcon(resources.find('img/tab/gear.png')))
        self._optionsButton.setIconSize(QSize(10, 10))
        
        # create connection
        self.connect(self.tabBar(),
                     SIGNAL('currentChanged(int)'),
                     self.adjustButtons)
        
        self.connect(self.tabBar(),
                     SIGNAL('resized()'),
                     self.adjustButtons)
        
        self.connect(self._optionsButton,
                     SIGNAL('clicked()'),
                     self.emitOptionsRequested)
        
        self.connect(self._addButton,
                     SIGNAL('clicked()'),
                     self.emitAddRequested)
    
    def __nonzero__( self ):
        """
        At somepoint, QTabWidget's nonzero became linked to whether it had
        children vs. whether it was none.  This returns the original
        functionality.
        """
        return self is not None
    
    def adjustButtons( self ):
        """
        Updates the position of the buttons based on the current geometry.
        """
        tabbar = self.tabBar()
        tabbar.adjustSize()
        
        w = self.width() - self._optionsButton.width() - 2
        self._optionsButton.move(w, 0)
        
        if self.count():
            if self.currentIndex() == self.count() - 1:
                self._addButton.move(tabbar.width() - 2, -1)
                self._addButton.setFixedHeight(tabbar.height() + 2)
            else:
                self._addButton.move(tabbar.width() - 4, 1)
                self._addButton.setFixedHeight(tabbar.height())
        else:
            self._addButton.move(tabbar.width() + 2, 1)
        
        self._addButton.stackUnder(self.currentWidget())
        
    def addButton(self):
        """
        Returns the add button linked with this tab widget.
        
        :return     <QPushButton>
        """
        return self._addButton
    
    def emitAddRequested(self, point=None):
        """
        Emitted when the option menu button is clicked provided the signals \
        are not being blocked for this widget.
        
        :param      point | <QPoint>
        """
        if self.signalsBlocked():
            return
        
        if not point:
            point = QCursor.pos()
        
        self.addRequested.emit(point)
    
    def emitOptionsRequested(self, point=None):
        """
        Emitted when the option menu button is clicked provided the signals \
        are not being blocked for this widget.
        
        :param      point | <QPoint>
        """
        if self.signalsBlocked():
            return
        
        if not point:
            point = QCursor.pos()
        
        self.optionsRequested.emit(point)
    
    def optionsButton(self):
        """
        Returns the options button linked with this tab widget.
        
        :return     <QPushButton>
        """
        return self._optionsButton
    
    def paintEvent(self, event):
        if not self.count():
            return
        
        super(XTabWidget, self).paintEvent(event)
    
    def resizeEvent(self, event):
        """
        Updates the position of the additional buttons when this widget \
        resizes.
        
        :param      event | <QResizeEvet>
        """
        super(XTabWidget, self).resizeEvent(event)
        self.adjustButtons()
    
    def setShowAddButton(self, state):
        """
        Sets whether or not the add button is visible.
        
        :param      state | <bool>
        """
        self._showAddButton = state
        self._addButton.setVisible(state)
    
    def setShowOptionsButton(self, state):
        """
        Sets whether or not the option button is visible.
        
        :param          state   | <bool>
        """
        self._showOptionsButton = state
        self._optionsButton.setVisible(state)
    
    def showAddButton(self):
        """
        Returns whether or not the add button is visible.
        
        :return     <bool>
        """
        return self._showAddButton
    
    def showOptionsButton(self):
        """
        Returns whether or not the option button should be visible.
        
        :return     <bool>
        """
        return self._showOptionsButton
    
    x_showAddButton = qt.Property(bool, showAddButton, setShowAddButton)
    x_showOptionsButton = qt.Property(bool, showOptionsButton, setShowOptionsButton)

__designer_plugins__ = [XTabWidget]