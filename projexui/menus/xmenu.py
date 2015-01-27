#!/usr/bin/python

"""
Extends the base QLineEdit class to support some additional features like \
setting hints on line edits.
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

import logging

from xml.etree          import ElementTree
from xml.parsers.expat  import ExpatError

from projexui.qt.QtCore import QPoint,\
                               QTimer,\
                               Qt
                           
from projexui.qt.QtGui  import QCursor,\
                               QFontMetrics,\
                               QIcon,\
                               QMenu, \
                               QPainter,\
                               QToolButton,\
                               QToolTip,\
                               QLabel,\
                               QAction,\
                               QWidgetAction,\
                               QPixmap,\
                               QStyle

from projexui import resources

logger = logging.getLogger(__name__)

LABEL_STYLE = """\
QLabel:hover {
    background: palette(Highlight);
    border: 1px solid palette(WindowText);
}"""

class XMenu(QMenu):
    def __init__(self, parent=None):
        super(XMenu, self).__init__(parent)
        
        # define custom parameters
        self._acceptedAction = None
        self._showTitle     = True
        self._advancedMap   = {}
        self._customData    = {}
        self._titleHeight   = 24
        self._yScroll       = 0
        self._toolTipAction = None
        self._toolTipTimer  = QTimer(self)
        self._toolTipTimer.setInterval(1000)
        self._toolTipTimer.setSingleShot(True)
#        self._scrollingTimer = QTimer(self)
#        self._scrollingTimer.setInterval(100)
        
        # setup scrolling options (coming soon)
#        down = QPixmap(resources.find('img/menu/down.png'))
#        up   = QPixmap(resources.find('img/menu/up.png'))
#        
#        self._scrollDownLabel = QLabel(self)
#        self._scrollDownLabel.setPixmap(down)
#        self._scrollDownLabel.setAlignment(Qt.AlignCenter)
#        self._scrollDownLabel.setAutoFillBackground(True)
#        self._scrollDownLabel.setStyleSheet(LABEL_STYLE)
#        self._scrollDownLabel.setFixedHeight(16)
#        self._scrollUpLabel = QLabel(self)
#        self._scrollUpLabel.setPixmap(up)
#        self._scrollUpLabel.setFixedHeight(16)
#        self._scrollUpLabel.setAlignment(Qt.AlignCenter)
#        self._scrollUpLabel.setAutoFillBackground(True)
#        self._scrollUpLabel.setStyleSheet(LABEL_STYLE)
#        
#        self._scrollDownLabel.hide()
#        self._scrollUpLabel.hide()
#        self._scrollUpLabel.installEventFilter(self)
#        self._scrollDownLabel.installEventFilter(self)
        
        # set default parameters
        self.setContentsMargins(0, self._titleHeight, 0, 0)
        self.setShowTitle(False)
        #self.setMaximumHeight(400)
        
        # create connections
        self.hovered.connect(self.startActionToolTip)
        self.aboutToShow.connect(self.clearAcceptedAction)
        self._toolTipTimer.timeout.connect(self.showActionToolTip)
#        self._scrollingTimer.timeout.connect(self.startScrolling)
    
    def acceptAdvanced(self):
        self._acceptedAction = self.sender().defaultAction()
        self.close()
    
    def acceptedAction(self):
        return self._acceptedAction
    
    def addMenu( self, submenu ):
        """
        Adds a new submenu to this menu.  Overloads the base QMenu addMenu \
        method so that it will return an XMenu instance vs. a QMenu when \
        creating a submenu by passing in a string.
        
        :param      submenu | <str> || <QMenu>
        
        :return     <QMenu>
        """
        # create a new submenu based on a string input
        if not isinstance(submenu, QMenu):
            title = str(submenu)
            submenu = XMenu(self)
            submenu.setTitle(title)
            submenu.setShowTitle(self.showTitle())
            super(XMenu, self).addMenu(submenu)
            return submenu
            
        else:
            return super(XMenu, self).addMenu(submenu)
    
    def addSection(self, section):
        """
        Adds a section to this menu.  A section will create a label for the
        menu to separate sections of the menu out.
        
        :param      section | <str>
        """
        label = QLabel(section, self)
        label.setMinimumHeight(self.titleHeight())
        
        # setup font
        font = label.font()
        font.setBold(True)
        
        # setup palette
        palette = label.palette()
        palette.setColor(palette.WindowText, palette.color(palette.Mid))
        
        # setup label
        label.setFont(font)
        label.setAutoFillBackground(True)
        label.setPalette(palette)
        
        # create the widget action
        action = QWidgetAction(self)
        action.setDefaultWidget(label)
        self.addAction(action)
        
        return action
    
    def adjustMinimumWidth( self ):
        """
        Updates the minimum width for this menu based on the font metrics \
        for its title (if its shown).  This method is called automatically \
        when the menu is shown.
        """
        if ( not self.showTitle() ):
            return
        
        metrics = QFontMetrics(self.font())
        width   = metrics.width(self.title()) + 20
        
        if ( self.minimumWidth() < width ):
            self.setMinimumWidth(width)
        
    def clearAdvancedActions( self ):
        """
        Clears out the advanced action map.
        """
        self._advancedMap.clear()
        margins     = list(self.getContentsMargins())
        margins[2]  = 0
        self.setContentsMargins(*margins)
    
    def clearAcceptedAction(self):
        self._acceptedAction = None
    
    def customData( self, key, default = None ):
        """
        Returns data that has been stored on this menu.
        
        :param      key     | <str>
                    default | <variant>
        
        :return     <variant>
        """
        key     = str(key)
        menu    = self
        while (not key in menu._customData and \
               isinstance(menu.parent(), XMenu)):
            menu = menu.parent()
        
        return menu._customData.get(str(key), default)
    
    def eventFilter(self, object, event):
        """
        Listens for the mouse hover event on the labels to know if the
        menu should scroll up or down.
        
        :param      object | <QObject>
                    event  | <QEvent>
        
        :return     <bool> | consumed
        """
#        # starts the scrolling
#        if event.type() == event.HoverEnter:
#            
#            if object == self._scrollDownLabel:
#                ydelta = -5
#            elif object == self._scrollUpLabel:
#                ydelta = 5
#            else:
#                ydelta = 0
#            
#            if ydelta != 0:
#                self._scrollingDelta = ydelta
#                self.startScrolling()
#            else:
#                self.stopScrolling()
#        
#        # cancel the scrolling
#        elif event.type() == event.HoverLeave:
#            self.stopScrolling()
        
        return False
    
    def paintEvent( self, event ):
        """
        Overloads the paint event for this menu to draw its title based on its \
        show title property.
        
        :param      event | <QPaintEvent>
        """
        super(XMenu, self).paintEvent(event)
        
        if ( self.showTitle() ):
            painter = QPainter()
            painter.begin(self)
            
            palette = self.palette()
            
            painter.setBrush(palette.color(palette.Button))
            painter.setPen(Qt.NoPen)
            painter.drawRect(1, 1, self.width() - 2, 22)
            
            painter.setBrush(Qt.NoBrush)
            painter.setPen(palette.color(palette.ButtonText))
            painter.drawText(1, 1, self.width() - 2, 22, 
                             Qt.AlignCenter, self.title())
            
            painter.end()
    
    def rebuildButtons( self ):
        """
        Rebuilds the buttons for the advanced actions.
        """
        for btn in self.findChildren(QToolButton):
            btn.close()
            btn.setParent(None)
            btn.deleteLater()
        
        for standard, advanced in self._advancedMap.items():
            rect    = self.actionGeometry(standard)
            btn     = QToolButton(self)
            btn.setFixedWidth(22)
            btn.setFixedHeight(rect.height())
            btn.setDefaultAction(advanced)
            btn.setAutoRaise(True)
            btn.move(rect.right() + 1, rect.top())
            
            if btn.icon().isNull():
                btn.setIcon(QIcon(resources.find('img/advanced.png')))
            
            btn.clicked.connect(self.acceptAdvanced)
    
    def resizeEvent(self, event):
        """
        Resizes this widget
        
        :param      event | <QResizeEvent>
        """
        super(XMenu, self).resizeEvent(event)
        
        # update the scrolling widgets
        self.updateScrollLabels()
    
    def setAdvancedAction(self, standardAction, advancedAction):
        """
        Links an advanced action with the inputed standard action.  This will \
        create a tool button alongside the inputed standard action when the \
        menu is displayed.  If the user selects the advanced action, then the \
        advancedAction.triggered signal will be emitted.
        
        :param      standardAction | <QAction>
                    advancedAction | <QAction>
        """
        if advancedAction:
            self._advancedMap[standardAction] = advancedAction
            margins     = list(self.getContentsMargins())
            margins[2]  = 22
            self.setContentsMargins(*margins)
            
        elif standardAction in self._advancedMap:
            self._advancedMap.pop(standardAction)
            if not self._advancedMap:
                margins     = list(self.getContentsMargins())
                margins[2]  = 22
                self.setContentsMargins(*margins)
    
    def setCustomData( self, key, value ):
        """
        Sets custom data for the developer on this menu instance.
        
        :param      key     | <str>
                    value | <variant>
        """
        self._customData[str(key)] = value
        
    def setShowTitle( self, state ):
        """
        Sets whether or not the title for this menu should be displayed in the \
        popup.
        
        :param      state | <bool>
        """
        self._showTitle = state
        
        margins = list(self.getContentsMargins())
        if state:
            margins[1] = self.titleHeight()
        else:
            margins[1] = 0
        
        self.setContentsMargins(*margins)
    
    def setVisible( self, state ):
        """
        Overloads the set visible method to update the advanced action buttons \
        to match their corresponding standard action location.
        
        :param      state | <bool>
        """
        if state:
            self.adjustMinimumWidth()
            self.rebuildButtons()
            self.updateScrollLabels()
        
        return super(XMenu, self).setVisible(state)
    
    def setTitleHeight(self, height):
        """
        Sets the height for the title of this menu bar and sections.
        
        :param      height | <int>
        """
        self._titleHeight = height
    
    def showActionToolTip( self ):
        """
        Shows the tool tip of the action that is currently being hovered over.
        
        :param      action | <QAction>
        """
        if ( not self.isVisible() ):
            return
            
        geom  = self.actionGeometry(self._toolTipAction)
        pos   = self.mapToGlobal(QPoint(geom.left(), geom.top()))
        pos.setY(pos.y() + geom.height())
        
        tip   = str(self._toolTipAction.toolTip()).strip().strip('.')
        text  = str(self._toolTipAction.text()).strip().strip('.')
        
        # don't waste time showing the user what they already see
        if ( tip == text ):
            return
        
        QToolTip.showText(pos, self._toolTipAction.toolTip())
    
    def showTitle( self ):
        """
        Returns whether or not this menu should show the title in the popup.
        
        :return     <bool>
        """
        return self._showTitle
    
    def startActionToolTip( self, action ):
        """
        Starts the timer to hover over an action for the current tool tip.
        
        :param      action | <QAction>
        """
        self._toolTipTimer.stop()
        QToolTip.hideText()
        
        if not action.toolTip():
            return
        
        self._toolTipAction = action
        self._toolTipTimer.start()
    
    def startScrolling(self):
        """
        Starts scrolling this widget based on the inputed delta amount.
        
        :param      delta | <int>
        """
        pass
#        self._yScroll += self._scrollingDelta
#        self.scroll(0, self._scrollingDelta)
#        self.repaint()
#        self.updateScrollLabels()
#        
#        if not self._scrollingTimer.isActive():
#            self._scrollingTimer.start()
    
    def stopScrolling(self):
        """
        Stops scrolling this widget.
        """
        pass
#        self._scrollingTimer.stop()
    
    def titleHeight(self):
        """
        Returns the height for the title of this menu bar and sections.
        
        :return     <int>
        """
        return self._titleHeight
    
    def updateCustomData( self, data ):
        """
        Updates the custom data dictionary with the inputed data.
        
        :param      data | <dict>
        """
        if ( not data ):
            return
            
        self._customData.update(data)
    
    def updateScrollLabels(self):
        """
        Updates the scrolling labels for this widget.
        """
        pass
#        size = self.size()
#        y = self.yScroll()
#        
#        max_h  = self.maximumHeight()
#        hint_h = self.sizeHint().height()
#        
#        # don't worry about it if the height is better than before
#        if hint_h <= max_h:
#            self._scrollUpLabel.hide()
#            self._scrollDownLabel.hide()
#            return
#        
#        if self.sizeHint().height() <= y:
#            self.scroll(0, y - self.sizeHint().height())
#            self.repaint()
#            self._scrollUpLabel.hide()
#        else:
#            self._scrollUpLabel.show()
#            self._scrollUpLabel.resize(size.width(), 16)
#            self._scrollUpLabel.move(0, 0)
#            self._scrollUpLabel.raise_()
#        
#        if y <= 0:
#            self.scroll(0, abs(y))
#            self.repaint()
#            self._scrollDownLabel.hide()
#        else:
#            self._scrollDownLabel.show()
#            self._scrollDownLabel.resize(size.width(), 16)
#            self._scrollDownLabel.move(0, self.height() - 16)
#            self._scrollDownLabel.raise_()
    
    def yScroll(self):
        """
        Returns the y-scroll amount for this widget.
        
        :return     <int>
        """
        return self._yScroll
    
    @staticmethod
    def fromString( parent, xmlstring, actions = None ):
        """
        Loads the xml string as xml data and then calls the fromXml method.
        
        :param      parent | <QWidget>
                    xmlstring | <str>
                    actions     | {<str> name: <QAction>, .. } || None
        
        :return     <XMenu> || None
        """
        try:
            xdata = ElementTree.fromstring(xmlstring)
            
        except ExpatError, e:
            logger.exception(e)
            return None
        
        return XMenu.fromXml(parent, xdata, actions)
    
    @staticmethod
    def fromXml( parent, xml, actions = None ):
        """
        Generates an XMenu from the inputed xml data and returns the resulting \
        menu.  If no action dictionary is supplied, it will be generated based \
        on the parents actions.
        
        :param      parent      | <QWidget>
                    xml         | <xml.etree.ElementTree.Element>
                    actions     | {<str> name: <QAction>, } || None
        
        :return     <XMenu> || None
        """
        # generate the actions off the parent
        if ( actions is None ):
            actions = {}
            for action in parent.actions():
                key = str(action.objectName())
                if ( not key ):
                    key = str(action.text())
                
                if ( not key ):
                    continue
                
                actions[key] = action
        
        # create a new menu
        menu = XMenu(parent)
        menu.setIcon(QIcon(resources.find('img/folder.png')))
        menu.setTitle(xml.get('title', '')) 
        
        for xaction in xml:
            if ( xaction.tag == 'separator' ):
                menu.addSeparator()
            elif ( xaction.tag == 'menu' ):
                menu.addMenu(XMenu.fromXml(menu, xaction, actions))
            else:
                action = actions.get(xaction.get('name', ''))
                if ( action ):
                    menu.addAction(action)
        
        return menu