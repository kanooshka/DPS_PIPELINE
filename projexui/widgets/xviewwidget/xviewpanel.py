#!/usr/bin python

""" Defines the main panel widget. """

# define authorship information
__authors__     = ['Eric Hulser']
__author__      = ','.join(__authors__)
__credits__     = []
__copyright__   = 'Copyright (c) 2011, Projex Software'

# maintanence information
__maintainer__  = 'Projex Software'
__email__       = 'team@projexsoftware.com'

from projexui.qt.QtCore   import Qt,\
                                 QMimeData,\
                                 QSize
                           
from projexui.qt.QtGui    import QApplication,\
                                 QBoxLayout, \
                                 QCursor, \
                                 QDrag,\
                                 QGridLayout, \
                                 QMenu, \
                                 QPixmap,\
                                 QScrollArea, \
                                 QSizePolicy, \
                                 QStyleOptionTabWidgetFrame,\
                                 QTabBar,\
                                 QWidget

from projexui.widgets.xtabwidget                 import XTabWidget
from projexui.widgets.xviewwidget.xviewpanelmenu import XViewPanelMenu
from projexui.widgets.xviewwidget.xview          import XView
from projexui.widgets.xsplitter                  import XSplitter

MAX_INT = 2**16

class XViewPanel(XTabWidget):
    def __init__(self, parent):
        # initialize the super class
        super(XViewPanel,self).__init__( parent )
        
        # create custom properties
        self._locked = False
        
        # set the size policy for this widget to always maximize space
        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(1)
        
        self.setSizePolicy(sizePolicy)
        self.setTabsClosable(True)
        self.setMovable(True)
        self.setAcceptDrops(True)
        
        # update the tab bar
        self.tabBar().installEventFilter(self)
        self.tabBar().setAcceptDrops(True)
        
        # create connections
        self.tabCloseRequested.connect( self.closeView )
        self.addRequested.connect( self.showAddMenu )
        self.currentChanged.connect( self.markCurrentChanged )
        self.optionsRequested.connect( self.showOptionsMenu )
        
        self.tabBar().customContextMenuRequested.connect( self.showTabMenu )
    
    def addPanel( self ):
        parent = self.parent()
        if not isinstance(parent, XSplitter):
            return False
        
        ewidgets = (self, self.parentWidget(), self.window())
        for w in ewidgets:
            w.setUpdatesEnabled(False)
        
        sizes = parent.sizes()
        total = sum(sizes)
        if ( total == 0 ):
            total = 1
            
        percents    = [float(size)/total for size in sizes]
        newpercent  = 1.0/(len(sizes)+1)
        newsize     = newpercent * total
        newsizes    = []
        
        for i, percent in enumerate(percents):
            newsizes.append((total * percent) - sizes[i] * newpercent)
        
        newsizes.append(newsize)
        
        panel = XViewPanel(parent)
        panel.setLocked(self.isLocked())
        
        parent.addWidget( panel )
        parent.setSizes(newsizes)
        
        for w in ewidgets:
            w.setUpdatesEnabled(True)
    
    def addTab( self, view, title ):
        """
        Adds a new view tab to this panel.
        
        :param      view    | <XView>
                    title   | <str>
        
        :return     <bool> | success
        """
        if ( not isinstance(view, XView) ):
            return False
        
        super(XViewPanel, self).addTab(view, title)
        
        # create connections
        view.windowTitleChanged.connect( self.refreshTitles )
        view.sizeConstraintChanged.connect( self.adjustSizeConstraint )
        
        self.setCurrentIndex(self.count() - 1)
        
        return True
    
    def addView(self, viewType):
        """
        Adds a new view of the inputed view type.
        
        :param      viewType | <subclass of XView>
        
        :return     <XView> || None
        """
        if not viewType:
            return None
        
        view = viewType.createInstance(self)
        self.addTab(view, view.windowTitle())
        return view
    
    def adjustSizeConstraint(self):
        """
        Adjusts the min/max size based on the current tab.
        """
        widget = self.currentWidget()
        if not widget:
            return
            
        offw = 4
        offh = 4
        
        if self.tabBar().isVisible():
            offh += 20 # tab bar height
        
        minw = min(widget.minimumWidth() + offw,   MAX_INT)
        minh = min(widget.minimumHeight() + offh,  MAX_INT)
        maxw = min(widget.maximumWidth() + offw,   MAX_INT)
        maxh = min(widget.maximumHeight() + offh,  MAX_INT)
        
        self.setMinimumSize(minw, minh)
        self.setMaximumSize(maxw, maxh)
        self.setSizePolicy(widget.sizePolicy())
    
    def closeView( self, view=None):
        if view == None:
            view = self.currentView()
        
        if type(view) == int:
            view = self.widget(view)
        
        if not view:
            return False
        
        index = self.indexOf(view)
        if index == -1:
            return False
        
        if not view.canClose():
            return False
        
        self.removeTab(index)
        view.destroyInstance(view)
        
        if not self.count():
            self.closePanel()
        
        return True
    
    def closePanel(self):
        """
        Closes a full view panel.
        """
        from projexui.widgets.xviewwidget.xviewdialog    import XViewDialog
        from projexui.widgets.xviewwidget.xviewwidget    import XViewWidget
        
        # make sure we can close all the widgets in the view first
        for i in range(self.count()):
            if not self.widget(i).canClose():
                return False
        
        # check to see if the panel is directly parented to the view widget,
        # if it is, then its the only panel remaining and cannot be closed.
        parentWidget = self.parentWidget()
        if not isinstance(parentWidget, XSplitter):
            
            # unless, its being used in an XViewDialog, in which case an empty
            # panel will close out the whole dialog
            window = self.window()
            if isinstance(window, XViewDialog):
                window.close()
                return True
                
            return False
        
        # if there is more than 1 panel in a splitter, then we can just close
        # this panel and not worry about it
        if parentWidget.count() > 2:
            self.close()
            self.deleteLater()
            return True
        
        # otherwise, we need to manipulate the splitters up the chain
        window = self.window()
        window.setUpdatesEnabled(False)
        
        oindex = int(not parentWidget.indexOf(self))
        other  = parentWidget.widget(oindex)
        
        # unsplit this widget
        superparent = parentWidget.parentWidget()
        superlayout = superparent.layout()
        
        remove = [parentWidget]
        supersizes = None
        
        # reset a splitter area
        if isinstance(superparent, XSplitter):
            supersizes  = superparent.sizes()
            index       = superparent.indexOf(parentWidget)
            
            other.setParent(superparent)
            
            superparent.insertWidget(index, other)
            
        # reset the scroll area
        elif isinstance(superparent, QWidget) and \
             isinstance(superparent.parent(), QScrollArea):
            
            area = superparent.parent()
            widget = area.takeWidget()
            
            other.setParent(superparent)
            area.setWidget(other)
            
            remove.append(widget)
        
        # clear out the old widgets
        for widget in remove:
            widget.close()
            widget.deleteLater()
        
        if supersizes:
            superparent.setSizes(supersizes)
        
        # close this panel, and mark it ready for removal
        self.close()
        self.deleteLater()
        
        # allow for ui updates
        window.setUpdatesEnabled(True)
    
    def currentView(self):
        """
        Returns the current view for this panel.
        
        :return     <XView> || None
        """
        widget = self.currentWidget()
        if isinstance(widget, XView):
            return widget
        return None
    
    def dragEnterEvent( self, event ):
        if ( str(event.mimeData().text()).startswith('move view:') and
             event.source() != self ):
            event.acceptProposedAction()
    
    def dropEvent( self, event ):
        text = str(event.mimeData().text())
        splt = text.split(':')
        self.snagViewFromPanel(event.source(), int(splt[1]))
    
    def eventFilter( self, object, event ):
        if event.type() == event.MouseButtonPress:
            if self.isLocked():
                return False
                
            if event.button() == Qt.MidButton or \
               (event.button() == Qt.LeftButton and \
                event.modifiers() == Qt.ShiftModifier):
                index = self.tabBar().tabAt(event.pos())
                view  = self.widget(index)
                pixmap = QPixmap.grabWidget(view)
                drag = QDrag(self)
                data = QMimeData()
                data.setText('move view:{}'.format(index))
                drag.setMimeData(data)
                drag.setPixmap(pixmap)
                drag.exec_()
                
                return True
            return False
            
        elif event.type() == event.DragEnter:
            if ( str(event.mimeData().text()).startswith('move view:') and
                 event.source() != self ):
                event.acceptProposedAction()
            return True
        
        elif event.type() == event.Drop:
            text = str(event.mimeData().text())
            splt = text.split(':')
            self.snagViewFromPanel(event.source(), int(splt[1]))
            return True
        
        return False
        
    def insertView( self, index, viewType ):
        if ( not viewType ):
            return False
            
        self.insertTab(index, 
                       viewType.createInstance(self), 
                       viewType.viewName())
        return True
    
    def isLocked( self ):
        """
        Returns whether or not this panel is currently locked from user editing.
        
        :return     <bool>
        """
        return self._locked
    
    def markCurrentChanged( self ):
        """
        Marks that the current widget has changed.
        """
        view = self.currentView()
        if view:
            view.setCurrent()
        
        self.adjustSizeConstraint()
    
    def refreshTitles( self ):
        """
        Refreshes the titles for each view within this tab panel.
        """
        for index in range(self.count()):
            widget = self.widget(index)
            self.setTabText(index, widget.windowTitle())
            
        self.adjustButtons()
    
    def removeTab( self, index ):
        """
        Removes the view at the inputed index and disconnects it from the \
        panel.
        
        :param      index | <int>
        """
        view = self.widget(index)
        if ( isinstance(view, XView) ):
            try:
                view.windowTitleChanged.disconnect(self.refreshTitles)
                view.sizeConstraintChanged.disconnect(self.adjustSizeConstraint)
            except:
                pass
        
        return super(XViewPanel, self).removeTab(index)
    
    def split( self, orientation ):
        parent = self.parent()
        if not parent:
            return False
        
        # split from a parent's layout
        layout  = parent.layout()
        w       = self.width()
        h       = self.height()
        
        if ( orientation == Qt.Horizontal ):
            size = w / 2
        else:
            size = h / 2
        
        window = self.window()
        window.setUpdatesEnabled(False)
        
        curr_view = self.currentView()
        
        # split a splitter
        if isinstance(parent, XSplitter):
            # remove the widget from the splitter
            psizes = parent.sizes()
            index = parent.indexOf(self)
            
            # create the splitter
            splitter = XSplitter(orientation, parent)
            self.setParent(splitter)
            splitter.addWidget(self)
            
            # split with a new view
            new_panel = XViewPanel(splitter)
            new_panel.setLocked(self.isLocked())
            
            if curr_view:
                new_view = curr_view.duplicate(new_panel)
                new_panel.addTab(new_view, new_view.windowTitle())
            
            splitter.addWidget(new_panel)
            
            sizePolicy = QSizePolicy(QSizePolicy.Expanding, 
                                     QSizePolicy.Expanding)
            sizePolicy.setHorizontalStretch(1)
            sizePolicy.setVerticalStretch(1)
            
            splitter.setSizePolicy(sizePolicy)
            splitter.setSizes( [size, size] )
            
            # insert the splitter into the parent
            parent.insertWidget(index, splitter)
            parent.setSizes(psizes)
        
        # split a scroll area
        elif isinstance( parent, QWidget ) and \
             isinstance( parent.parent(), QScrollArea ):
            
            area = parent.parent()
            area.takeWidget()
            
            # create the splitter
            splitter = XSplitter(orientation, parent)
            splitter.addWidget(self)
            
            # split with a new view
            new_panel = XViewPanel(splitter)
            new_panel.setLocked(self.isLocked())
            if curr_view:
                new_view = curr_view.duplicate(new_panel)
                new_panel.addTab(new_view, new_view.windowTitle())
            
            splitter.addWidget(new_panel)
            splitter.setSizes( [size, size] )
            
            sizePolicy = QSizePolicy(QSizePolicy.Expanding, 
                                     QSizePolicy.Expanding)
            sizePolicy.setHorizontalStretch(1)
            sizePolicy.setVerticalStretch(1)
            
            splitter.setSizePolicy(sizePolicy)
            
            area.setWidget(splitter)
        
        window.setUpdatesEnabled(True)
        
    def splitVertical( self ):
        self.split( Qt.Vertical )
        
    def splitHorizontal( self ):
        self.split( Qt.Horizontal )
    
    def setLocked(self, state):
        """
        Sets the locked state for this panel to the inputed state.
        
        :param      state | <bool>
        """
        self._locked = state
        
        tabbar = self.tabBar()
        
        tabbar.setVisible(self.count() > 1 or not state)
        self.addButton().setVisible(not state)
        self.optionsButton().setVisible(not state)
        self.setTabsClosable(not state)
        self.setMovable(not state)
        
        self.adjustButtons()
        self.adjustSizeConstraint()
    
    def setView( self, viewType ):
        self.setUpdatesEnabled(False)
        
        curr_view = self.currentView()
        
        if ( self.insertView( self.currentIndex(), curr_view ) and curr_view ):
            curr_view.destroyInstance(curr_view)
            
        self.setUpdatesEnabled(True)
    
    def setVisible( self, state ):
        super(XViewPanel, self).setVisible(state)
        
        if ( state ):
            self.adjustSizeConstraint()
    
    def showAddMenu( self, point ):
        if ( self.isLocked() ):
            return
            
        self.viewWidget().showInterfaceMenu(self, point)
    
    def showTabMenu( self ):
        self.showOptionsMenu()
    
    def showOptionsMenu( self, point = None ):
        if ( self.isLocked() ):
            return
            
        if ( not point ):
            point = QCursor.pos()
            
        self.viewWidget().showPanelMenu(self, point)
    
    def snagViewFromPanel( self, panel, index = None ):
        """
        Removes the view from the inputed panel and adds it to this panel.
        
        :param      panel | <XViewPanel>
                    view  | <XView>
        """
        if index == None:
            index = panel.currentIndex()
            
        view = panel.widget(index)
        if not view:
            return
        
        count = panel.count()
        self.addTab(view, view.windowTitle())
        
        # when the panel gets moved and there are no more widgets within the 
        # panel, we'll close it out - but we cannot close it directly or we 
        # run into a segmentation fault here.  Better to provide a timer and
        # close it in a second.  It depends on which thread triggers this call
        # that sometimes causes it to error out. - EKH 01/25/12
        if count == 1:
            panel.closePanel()
    
    def viewWidget( self ):
        from projexui.widgets.xviewwidget.xviewwidget import XViewWidget
        
        parent = self.parent()
        while (parent and not isinstance(parent, XViewWidget)):
            parent = parent.parent()
        return parent