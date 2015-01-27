#!/usr/bin/python

""" Defines a view for the XViewWidget based on the XConsoleEdit. """

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

from projexui.qt.QtCore import Qt, QSize
from projexui.qt        import wrapVariant, unwrapVariant, Signal
from projexui.qt.QtGui  import QIcon

from projexui.widgets.xviewwidget   import XView
from projexui.widgets.xloggerwidget import XLoggerWidget

import projex.text
import projexui

ROOT_LOGGER_TEXT = 'root'

class XConsoleView(XView):
    """ """
    lockToggled = Signal()
    
    def __init__(self, parent=None):
        super(XConsoleView, self).__init__(parent, autoKillThreads=False)
        
        # load the user interface
        projexui.loadUi(__file__, self)
        
        # define custom properties
        self._locked        = False
        self._lastDetails   = True
        self._lastHeight    = None
        
        # set default properties
        self.uiConsoleEDIT.setLogger(logging.root)
        self.uiLoggerDDL.addItem(ROOT_LOGGER_TEXT)
        self.uiLoggerDDL.addItem('-----------')
        self.lockHeight()
        
        self.uiFindWIDGET.hide()
        
        all_loggers = logging.root.manager.loggerDict.keys()
        self.uiLoggerDDL.addItems(sorted(all_loggers))
        self.adjustLoggerIcons()
        
        # load level drop down list
        order = []
        size = QSize(120, 20)
        for i, item in enumerate(sorted(XLoggerWidget.LoggingMap.items())):
            level, data = item
            self.uiLevelDDL.addItem(projex.text.pretty(data[0]))
            self.uiLevelDDL.setItemIcon(i, QIcon(data[1]))
            self.uiLevelDDL.setItemData(i, wrapVariant(level))
            self.uiLevelDDL.setItemData(i, wrapVariant(size), Qt.SizeHintRole)
            
            if ( logging.root.getEffectiveLevel() == level ):
                self.uiLevelDDL.setCurrentIndex(i)
        
        # link the find widget with the text edit
        self.uiFindWIDGET.setTextEdit(self.uiConsoleEDIT)
        
        # create connections
        self.uiLevelDDL.currentIndexChanged.connect( self.adjustLevel )
        self.uiShowLevelCHK.toggled.connect( self.uiConsoleEDIT.setShowLevel )
        self.uiShowDetailsCHK.toggled.connect(self.uiConsoleEDIT.setShowDetails)
        self.uiShowDetailsCHK.clicked.connect(self.setLastDetails)
        self.uiLoggerDDL.currentIndexChanged.connect( self.updateLogger )
        self.uiMoreBTN.clicked.connect( self.unlockHeight )
        self.uiLessBTN.clicked.connect( self.lockHeight )
    
    def adjustLoggerIcons( self ):
        """
        Updates the logger icons for all the loggers in the system.
        """
        default = XLoggerWidget.LoggingMap.get(logging.root.getEffectiveLevel())
        if ( not default ):
            default = XLoggerWidget.LoggingMap[logging.DEBUG]
        
        size = QSize(120, 20)
        for i in range(self.uiLoggerDDL.count()):
            text = str(self.uiLoggerDDL.itemText(i))
            if ( text.startswith('---') ):
                continue
            
            if ( text == ROOT_LOGGER_TEXT ):
                logger = logging.root
            else:
                logger = logging.getLogger(text)
            
            level = logger.getEffectiveLevel()
            icon = XLoggerWidget.LoggingMap.get(level, default)[1]
            
            self.uiLoggerDDL.setItemIcon(i, QIcon(icon))
            self.uiLoggerDDL.setItemData(i, wrapVariant(size), Qt.SizeHintRole)
    
    def adjustLevel( self ):
        """
        Matches the current level to the level from the editor.
        """
        level = self.uiLevelDDL.itemData(self.uiLevelDDL.currentIndex())
        level = unwrapVariant(level)
        logger = self.uiConsoleEDIT.logger()
        logger.setLevel(level)
        
        self.adjustLoggerIcons()
    
    def closeEvent( self, event ):
        """
        Closes this view and its children.
        
        :param      event | <QCloseEvent>
        """
        self.uiConsoleEDIT.setLogger(None)
        
        super(XConsoleView, self).closeEvent(event)
    
    def console( self ):
        """
        Returns the XConsoleEdit instance that is being used by the view.
        
        :return     <XConsoleEdit>
        """
        return self.uiConsoleEDIT
    
    def isLocked( self ):
        """
        Returns whether or not this view is locked down.
        
        :return     <bool>
        """
        return self._locked
    
    def lastDetails( self ):
        """
        Sets whether or not the details were checked for the last state.
        
        :return     <bool>
        """
        return self._lastDetails
    
    def lastHeight( self ):
        """
        Returns the last height that this console view was in.
        
        :return     <int>
        """
        if ( self._lastHeight == None ):
            return 250
        
        return self._lastHeight
    
    def lockHeight( self ):
        """
        Forces the view to a particular size.
        """
        self._locked = True
        self.uiToolsWIDGET.hide()
        self.uiMoreBTN.show()
        
        self.setLastDetails(self.uiShowDetailsCHK.isChecked())
        self.setLastHeight(self.height())
        
        self.setMinimumHeight(24)
        self.setMaximumHeight(24)
        self.uiConsoleEDIT.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.uiConsoleEDIT.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.uiConsoleEDIT.setReadOnly(True)
        self.uiConsoleEDIT.setShowDetails(False)
        self.uiConsoleEDIT.scrollToEnd()
        
        if ( not self.signalsBlocked() ):
            self.lockToggled.emit()
        
    def restoreXml( self, xml ):
        """
        Restores the settings for this view to from the inputed xml node.
        
        :param      xml | <xml.etree.ElementTree.Element>
        """
        self.uiShowLevelCHK.setChecked(xml.get('show_level') != 'False')
        self.setLastDetails(xml.get('last_detail') != 'False')
        self.setLocked(xml.get('locked') != 'False')
        
        height = xml.get('last_height')
        if ( height ):
            self.setLastHeight(int(height))
        
    def saveXml( self, xml ):
        """
        Saves the settings for this console to the xml node.
        
        :param      xml | <xml.etree.ElementTree.Element>
        """
        show_level  = self.uiShowLevelCHK.isChecked()
        logger      = self.uiLoggerDDL.currentText()
        level       = self.uiLevelDDL.currentText()
        
        xml.set('show_level',   str(show_level))
        xml.set('locked',       str(self.isLocked()))
        xml.set('last_height',  str(self.lastHeight()))
        xml.set('last_detail',  str(self.lastDetails()))
        
    def setLastDetails( self, state ):
        """
        Sets if the details were set in the last console state.
        
        :param      state | <bool>
        """
        self._lastDetails = state
    
    def setLastHeight( self, height ):
        """
        Sets the last height for this console view to the inputed height.
        
        :param      height | <int>
        """
        self._lastHeight = height
    
    def setLocked( self, state ):
        """
        Sets whether or not this view is locked down.
        
        :param      state | <bool>
        """
        if ( state ):
            self.lockHeight()
        else:
            self.unlockHeight()
    
    def unlockHeight( self ):
        """
        Unlocks the view from the particular size.
        """
        self._locked = False
        self.uiToolsWIDGET.show()
        self.uiMoreBTN.hide()
        self.setMinimumHeight(150)
        self.setMaximumHeight(100000)
        self.uiConsoleEDIT.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.uiConsoleEDIT.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.resize(self.width(), self.lastHeight())
        self.uiConsoleEDIT.setReadOnly(False)
        self.uiConsoleEDIT.setShowDetails(True)
        
        self.uiShowDetailsCHK.setChecked(self.lastDetails())
        
        if ( not self.signalsBlocked() ):
            self.lockToggled.emit()
    
    def updateLogger( self ):
        """
        Updates which logger is being used by the system.
        """
        curr_text = str(self.uiLoggerDDL.currentText())
        
        if ( curr_text == ROOT_LOGGER_TEXT ):
            logger = logging.root
        elif ( not curr_text.startswith('---') ):
            logger = logging.getLogger(curr_text)
        else:
            logger = None
        
        self.uiConsoleEDIT.setLogger(logger)
        
        if ( not logger ):
            return
            
        level = logger.getEffectiveLevel()
        self.uiLevelDDL.blockSignals(True)
        
        for i in range(self.uiLevelDDL.count()):
            if ( unwrapVariant(self.uiLevelDDL.itemData(i)) == level ):
                self.uiLevelDDL.setCurrentIndex(i)
                break
                
        self.uiLevelDDL.blockSignals(False)
    
# initialize the view settings
XConsoleView.setViewName('Console')
XConsoleView.setViewIcon( projexui.resources.find('img/terminal.png') )