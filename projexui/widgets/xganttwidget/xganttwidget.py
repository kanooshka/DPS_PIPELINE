#!/usr/bin/python

""" Defines a gantt chart widget for use in scheduling applications. """

# define authorship information
__authors__         = ['Eric Hulser']
__author__          = ','.join(__authors__)
__credits__         = []
__copyright__       = 'Copyright (c) 2012, Projex Software'
__license__         = 'LGPL'

# maintenance information
__maintainer__      = 'Projex Software'
__email__           = 'team@projexsoftware.com'

#------------------------------------------------------------------------------

import weakref
import sys
import operator

import sharedDB

from projexui import qt

from PyQt4    import QtCore,QtGui
from PyQt4.QtCore   import QDate,\
				 QSize,\
				 QDateTime,\
				 Qt, QString

from PyQt4.QtGui    import QWidget,\
				 QPen,\
				 QBrush,\
				 QPalette,\
				 QColor, QMenuBar, QCursor

from projex.enum import enum

import projexui

#from projexui.qt import unwrapVariant, wrapVariant
from projexui.widgets.xganttwidget.xganttscene   import XGanttScene
from DPSPipeline.widgets.createprojectwidget import createprojectwidget


from datetime import datetime 

class XGanttWidget(QWidget):
    dateRangeChanged = qt.Signal()
    
    Timescale = enum('Week', 'Month', 'Year')
    
    def __init__( self, parent = None, _availabilityEnabled = 0):
	super(XGanttWidget, self).__init__( parent )
	
	'''
	menubar = QMenuBar(self)
	#menubar.sizeHint(QSize.setHeight(10))
	
	fileMenu = menubar.addMenu('&File')
	
	fileMenu.addAction('Create Project')
	fileMenu.addSeparator()
	fileMenu.addAction('Save')
	fileMenu.addSeparator()
	fileMenu.addAction('Exit')
	fileMenu.triggered.connect( self.fileMenuActions )
	'''
	
	# load the user interface
	if getattr(sys, 'frozen', None):
	    #print (sys._MEIPASS+"/ui/xganttwidget.ui");
	    projexui.loadUi(sys._MEIPASS, self, uifile = (sys._MEIPASS+"/ui/xganttwidget.ui"))
	    
	else:
	    projexui.loadUi(__file__, self)
	
	# define custom properties
	self._backend               = None
	self._dateStart             = QDate.currentDate()
	self._dateEnd               = QDate.currentDate().addMonths(12)
	self._alternatingRowColors  = False
	self._cellWidth             = 15
	self._cellHeight            = 15
	self._first                 = True
	self._dateFormat            = 'M/d/yy'
	self._timescale             = XGanttWidget.Timescale.Year
	self._scrolling             = False
	
	# setup the palette colors
	palette = self.palette()
	color   = palette.color(palette.Base)
	
	self._gridPen           = QPen(color.darker(135))
	self._brush             = QBrush(color)
	self._alternateBrush    = QBrush(color.darker(105))	
	self._currentDayBrush   = QBrush(QColor(146,252,186))
	self._holidayBrush      = QBrush(QColor(166,46,46))
	self._bookedBrush      = QBrush(QColor(20,250,0))
	self._unavailableBrush = QBrush(QColor(75,75,75))
	self._underbookedBrush = QBrush(QColor(255,255,20))
	self._overbookedBrush = QBrush(QColor(255,25,25))
	self._overbookedAmount = {}
	self._unassignedBrush = QBrush(QColor(25,25,255))
	
	weekendColor            = color.darker(148)
	
	
	
	self._availabilityEnabled = _availabilityEnabled
	
	self._weekendBrush      = QBrush(weekendColor)
	
	# setup the columns for the tree
	if _availabilityEnabled:
	    self.setColumns(['Name'])
	else:
	    self.setColumns(['Name', 'Start', 'End', 'Calendar Days', 'Work Days'])
	header = self.uiGanttTREE.header()
	header.setFixedHeight(self._cellHeight * 2)
	header.setResizeMode(0, header.ResizeToContents)
	header.setDefaultSectionSize(60)
	headerItem = self.uiGanttTREE.headerItem()
	headerItem.setSizeHint(0, QSize(10, header.height()))
	
	self.uiGanttTREE.setContextMenuPolicy( Qt.CustomContextMenu )
        
        # connect signals
        self.uiGanttTREE.customContextMenuRequested.connect( self.showProjectMenu)
	
	# initialize the tree widget
	self.uiGanttTREE.setShowGrid(False)
	
	#enable drag and drop
	self.uiGanttTREE.setDragDropFilter(self.uiGanttTREE.setDragDropFilter(XGanttWidget.handleDragDrop))
	
	if (sharedDB.currentUser._idPrivileges==3):
	    self.uiGanttTREE.setEditable(False)
	for act in sharedDB.mainWindow._fileMenu.actions():
	    if act.text() == "Save" or act.text() == "Create Project":
		act.setEnabled(False)
	    
	else:
	    self.uiGanttTREE.setEditable(True)
	    
	self.uiGanttTREE.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
	self.uiGanttTREE.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
	self.uiGanttTREE.setVerticalScrollMode(self.uiGanttTREE.ScrollPerPixel)

	#left half size
	self.uiGanttTREE.resize(400, 20)
	
	# initialize the view widget
	#self.uiGanttVIEW.setDragMode( self.uiGanttVIEW.RubberBandDrag )
	self.uiGanttVIEW.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
	self.uiGanttVIEW.setAlignment(Qt.AlignTop | Qt.AlignLeft)
	self.uiGanttVIEW.setScene(XGanttScene(self))
	self.uiGanttVIEW.installEventFilter(self)
	#self.uiGanttVIEW.horizontalScrollBar().setValue(50)
	
	# create connections
	self.uiGanttTREE.itemExpanded.connect(self.syncView)
	self.uiGanttTREE.itemCollapsed.connect(self.syncView)
	
	# connect scrollbars
	tree_bar = self.uiGanttTREE.verticalScrollBar()
	view_bar = self.uiGanttVIEW.verticalScrollBar()
	
	tree_bar.rangeChanged.connect(self.__updateViewRect)
	tree_bar.valueChanged.connect(self.__scrollView)
	view_bar.valueChanged.connect(self.__scrollTree)
	
	# connect selection
	self.uiGanttTREE.itemSelectionChanged.connect(self.__selectView)
	self.uiGanttVIEW.scene().selectionChanged.connect(self.__selectTree)
	self.uiGanttTREE.itemChanged.connect(self.updateItemData)
    
	if self._availabilityEnabled:
	    self._currentDayBrush   = None
	    self._holidayBrush      = QBrush(QColor(75,75,75))
	    weekendColor	= QBrush(QColor(75,75,75))
	    self.uiGanttTREE.setEditable(False)
	    #self._cellHeight = 12
    
    def __del__(self):
	self.uiGanttVIEW.scene().selectionChanged.disconnect(self.__selectTree)
    
    def __scrollTree( self, value ):
	"""
	Updates the tree view scrolling to the inputed value.
	
	:param      value | <int>
	"""
	if ( self._scrolling ):
	    return
	
	tree_bar = self.uiGanttTREE.verticalScrollBar()
	self._scrolling = True
	tree_bar.setValue(value)
	self._scrolling = False
	
    def __scrollView( self, value ):
	"""
	Updates the gantt view scrolling to the inputed value.
	
	:param      value | <int>
	"""
	if ( self._scrolling ):
	    return
	
	view_bar = self.uiGanttVIEW.verticalScrollBar()
	self._scrolling = True
	view_bar.setValue(value)
	self._scrolling = False
    
    def __selectTree( self ):
	"""
	Matches the tree selection to the views selection.
	"""
	self.uiGanttTREE.blockSignals(True)
	self.uiGanttTREE.clearSelection()
	for item in self.uiGanttVIEW.scene().selectedItems():
	    item.treeItem().setSelected(True)
	    sharedDB.sel.select([item.treeItem()._dbEntry])
	self.uiGanttTREE.blockSignals(False)
	
    
    def __selectView( self ):
	"""
	Matches the view selection to the trees selection.
	"""
	self.uiGanttVIEW.scene().blockSignals(True)
	self.uiGanttVIEW.scene().clearSelection()
	for item in self.uiGanttTREE.selectedItems():
	    item.viewItem().setSelected(True)
	    sharedDB.sel.select([item._dbEntry])
	self.uiGanttVIEW.scene().blockSignals(False)
    
    def __updateViewRect( self ):
	"""
	Updates the view rect to match the current tree value.
	"""
	header_h    = self._cellHeight * 2
	rect        = self.uiGanttVIEW.scene().sceneRect()
	sbar_max    = self.uiGanttTREE.verticalScrollBar().maximum()
	sbar_max   += self.uiGanttTREE.viewport().height() + header_h
	widget_max  = self.uiGanttVIEW.height()
	widget_max -= (self.uiGanttVIEW.horizontalScrollBar().height() + 10)
	
	rect.setHeight(max(widget_max, sbar_max))
	self.uiGanttVIEW.scene().setSceneRect(rect)
    
    def addTopLevelItem( self, item ):
	"""
	Adds the inputed item to the gantt widget.
	
	:param      item | <XGanttWidgetItem>
	"""
	vitem = item.viewItem()
	
	self.treeWidget().addTopLevelItem(item)
	if not self._availabilityEnabled:
	    self.viewWidget().scene().addItem(vitem)
	    
	    item._viewItem = weakref.ref(vitem)
	
	#set scrollbar offset
	#item.treeWidget._scrollBar = self.uiGanttTREE.verticalScrollBar()
	
	item.sync(recursive = True)
	
    def alternateBrush( self ):
	"""
	Returns the alternate brush to be used for the grid view.
	
	:return     <QBrush>
	"""
	return self._alternateBrush
    
    def alternatingRowColors( self ):
	"""
	Returns whether or not this widget should show alternating row colors.
	
	:return     <bool>
	"""
	return self._alternatingRowColors
    
    def brush( self ):
	"""
	Returns the background brush to be used for the grid view.
	
	:return     <QBrush>
	"""
	return self._brush
    
    def cellHeight( self ):
	"""
	Returns the height for the cells in this gantt's views.
	
	:return     <int>
	"""
	return self._cellHeight
    
    def cellWidth( self ):
	"""
	Returns the width for the cells in this gantt's views.
	
	:return     <int>
	"""
	return self._cellWidth
    
    def clear( self ):
	"""
	Clears all the gantt widget items for this widget.
	"""
	self.uiGanttTREE.clear()
	self.uiGanttVIEW.scene().clear()
    
    def closeEvent(self, event):
	if sharedDB.changesToBeSaved and sharedDB.users.currentUser._idPrivileges != 3:
	    quit_msg = "Save before exit?"
	    reply = QtGui.QMessageBox.question(self, 'Message', 
			     quit_msg, QtGui.QMessageBox.Yes, QtGui.QMessageBox.No,QtGui.QMessageBox.Cancel)
	
	    if reply == QtGui.QMessageBox.Yes:
		self.SaveToDatabase()
		event.accept()
	    elif reply == QtGui.QMessageBox.No:
		event.accept()
	    else:
		event.ignore()
		
    
    def columns( self ):
	"""
	Returns a list of the columns being used in the treewidget of this gantt
	chart.
	
	:return     [<str>, ..]
	"""
	return self.treeWidget().columns()
    
    '''def CreateProject(self):
	#self._myCreateProjectWidget = CreateProjectWidget()
	#self._myCreateProjectWidget.show()
	sharedDB.app.CreateProjectWidget() 
    '''
    def dateEnd( self ):
	"""
	Returns the date end for this date range of this gantt widget.
	
	:return     <QDate>
	"""
	return self._dateEnd
    
    def dateFormat( self ):
	"""
	Returns the date format that will be used when rendering items in the
	view.
	
	:return     <str>
	"""
	return self._dateFormat
    
    def dateStart( self ):
	"""
	Returns the date start for the date range of this gantt widget.
	
	:return     <QDate>
	"""
	return self._dateStart

    def emitDateRangeChanged( self ):
	"""
	Emits the date range changed signal provided signals aren't being
	blocked.
	"""
	if ( not self.signalsBlocked() ):
	    self.dateRangeChanged.emit()
    
    def collapseAllTrees(self):
	self.uiGanttTREE.blockSignals(True)
	#for x in range(0,self.treeWidget().topLevelItemCount()):
	    #self.treeWidget().topLevelItem(x).setExpanded(True)
	self.treeWidget().collapseAll()
	self.uiGanttTREE.blockSignals(False)
	self.syncView()
	
    def expandAllTrees(self):
	self.uiGanttTREE.blockSignals(True)
	#for x in range(0,self.treeWidget().topLevelItemCount()):
	    #self.treeWidget().topLevelItem(x).setExpanded(True)
	self.treeWidget().expandAll()
	self.uiGanttTREE.blockSignals(False)
	self.syncView()
    
    def eventFilter( self, object, event ):
	if ( event.type() == event.Resize ):
	    self.__updateViewRect()
	return False
    
    def frameCurrentDate(self):
	# Subtract start date from current date
	prerollDays = self._dateStart.day() - QDate.currentDate().day()
	#set scroll to multiply difference against cel width
	
	view_bar = self.uiGanttVIEW.horizontalScrollBar()
	self._scrolling = True
	view_bar.setMaximum(1)
	view_bar.setMinimum(0)
	#print view_bar.maximum()
	view_bar.setValue(1)
	#view_bar.update()
	#self.update()
	#self.uiGanttVIEW.update()
	self._scrolling = False
	
	#self.__scrollView(self._cellWidth * prerollDays)
    
    def gridPen( self ):
	"""
	Returns the pen that this widget uses to draw in the view.
	
	:return     <QPen>
	"""
	return self._gridPen
    
    @staticmethod
    def handleDragDrop(object, event):
	if ( event.type() == QEvent.DragEnter ):
	    event.acceptProposedActions()
	elif ( event.type() == QEvent.Drop ):
	    print 'dropping'
    
    
    def indexOfTopLevelItem( self, item ):
	"""
	Returns the index for the inputed item from the tree.
	
	:return     <int>
	"""
	return self.treeWidget().indexOfTopLevelItem(item)
    
    def insertTopLevelItem( self, index, item ):
	"""
	Inserts the inputed item at the given index in the tree.
	
	:param      index   | <int>
		    item    | <XGanttWidgetItem>
	"""
	self.treeWidget().insertTopLevelItem(index, item)
	
	item.sync(recursive = True)

    def setAlternateBrush( self, brush ):
	"""
	Sets the alternating brush used for this widget to the inputed brush.
	
	:param      brush | <QBrush> || <QColor>
	"""
	self._alternateBrush = QBrush(brush)
    
    def setAlternatingRowColors( self, state ):
	"""
	Sets the alternating row colors state for this widget.
	
	:param      state | <bool>
	"""
	self._alternatingRowColors = state
	
	self.treeWidget().setAlternatingRowColors(state)
    
    def setBrush( self, brush ):
	"""
	Sets the main background brush used for this widget to the inputed
	brush.
	
	:param      brush | <QBrush> || <QColor>
	"""
	self._brush = QBrush(brush)
    
    def setCellHeight( self, cellHeight ):
	"""
	Sets the height for the cells in this gantt's views.
	
	:param      cellHeight | <int>
	"""
	self._cellHeight = cellHeight
    
    def setCellWidth( self, cellWidth ):
	"""
	Sets the width for the cells in this gantt's views.
	
	:param      cellWidth | <int>
	"""
	self._cellWidth = cellWidth
    
    def setColumns( self, columns ):
	"""
	Sets the columns for this gantt widget's tree to the inputed list of
	columns.
	
	:param      columns | {<str>, ..]
	"""
	self.treeWidget().setColumns(columns)
	item = self.treeWidget().headerItem()
	for i in range(item.columnCount()):
	    item.setTextAlignment(i, Qt.AlignBottom | Qt.AlignHCenter)
    
    def setDateEnd( self, dateEnd ):
	"""
	Sets the end date for the range of this gantt widget.
	
	:param      dateEnd | <QDate>
	"""
	self._dateEnd = dateEnd
	self.emitDateRangeChanged()
    
    def setDateFormat( self, format ):
	"""
	Sets the date format that will be used when rendering in the views.
	
	:return     <str>
	"""
	return self._dateFormat
    
    def setDateStart( self, dateStart ):
	"""
	Sets the start date for the range of this gantt widget.
	
	:param      dateStart | <QDate>
	"""
	self._dateStart = dateStart
	self.emitDateRangeChanged()
    
    def setGridPen( self, pen ):
	"""
	Sets the pen used to draw the grid lines for the view.
	
	:param      pen | <QPen> || <QColor>
	"""
	self._gridPen = QPen(pen)
    
    def setTimescale( self, timescale ):
    
	"""
	Sets the timescale value for this widget to the inputed value.
	
	:param      timescale | <XGanttWidget.Timescale>
	"""
	self._timescale = timescale

    #def setupUserView(self, privileges, department):
	#sif department
    
    
    def setWeekendBrush( self, brush ):
	"""
	Sets the brush to be used when coloring weekend columns.
	
	:param      brush | <QBrush> || <QColor>
	"""
	self._weekendBrush = QBrush(brush)
    
    def syncView( self ):
	"""
	Syncs all the items to the view.
	"""
	if ( not self.signalsBlocked() ):	
	    for i in range(self.topLevelItemCount()):
		item = self.topLevelItem(i)
		item.syncView(recursive = True)
    
    def takeTopLevelItem( self, index ):
	"""
	Removes the top level item at the inputed index from the widget.
	
	:param      index | <int>
	
	:return     <XGanttWidgetItem> || None
	"""
	item = self.topLevelItem(index)
	if ( item ):
	    self.viewWidget().scene().removeItem(item.viewItem())
	    self.treeWidget().takeTopLevelItem(index)
	    
	    return item
	return None
    
    def timescale( self ):
	"""
	Returns the timescale that is being used for this widget.
	
	:return     <XGanttWidget.Timescale>
	"""
	return self._timescale
    
    def topLevelItem( self, index ):
	"""
	Returns the top level item at the inputed index.
	
	:return     <XGanttWidgetItem>
	"""
	return self.treeWidget().topLevelItem(index)
    
    def topLevelItemCount( self ):
	"""
	Returns the number of top level items for this widget.
	
	:return     <int>
	"""
	return self.treeWidget().topLevelItemCount()
    
    def treeWidget( self ):
	"""
	Returns the tree widget for this gantt widget.
	
	:return     <QTreeWidget>
	"""
	return self.uiGanttTREE
    
    def updateItemData(self, item, index):
	"""
	Updates the item information from the tree.
	
	:param      item    | <XGanttWidgetItem>
		    index   | <int>
	"""
	value = qt.unwrapVariant(item.data(index, Qt.EditRole))
	
	if type(value) == QDateTime:
	    value = value.date()
	    item.setData(index, Qt.EditRole, qt.wrapVariant(value))
	
	if type(value) == QDate:
	    value = value.toPython()
	
	columnName = self.treeWidget().columnOf(index)
	item.setProperty(columnName, value)
	item.sync()
    
    def updatePhaseVisibility(self, visibility, phaseName = ''):
	
	if (phaseName != ''):
	    #print ("Changing "+ phaseName + " to : "+ str(visibility))	    
	    #iterate through all projects
	    for x in range(0,self.treeWidget().topLevelItemCount()):
		projectWidgetItem = self.treeWidget().topLevelItem(x)
		keepVisible = False
		for c in range(projectWidgetItem.childCount()):
		    child = projectWidgetItem.child(c)
		    if (child._dbEntry._phase._name == phaseName):
			#projectWidgetItem.setHidden(not visibility)
			child.setHidden(not visibility)
			if (visibility):
			    keepVisible = True
		    
		    elif (visibility == False and not child.isHidden() and keepVisible == False):
			keepVisible = True
			
			#print child._name
		#print ("item: " + str(x))
		    #iterate through all phases
		
		
		if (keepVisible):
		    if (projectWidgetItem.isHidden()):
			projectWidgetItem.setHidden(False)
		elif (not visibility):
		    if (not projectWidgetItem.isHidden()):
			#self.syncView()
			projectWidgetItem.setHidden(True)
		    
	    #if phase matches, change visibility
	    
	    for phase in sharedDB.myPhases.values():
		if (phase._name == phaseName):
		    phase._visible = visibility
	    
	else:
	    #iterate through all projects
	    #iterate through all phases
	    #change visibility
	    if visibility == False:
		self.collapseAllTrees()
	    
	    for x in range(0,self.treeWidget().topLevelItemCount()):
		projectWidgetItem = self.treeWidget().topLevelItem(x)		
		for c in range(projectWidgetItem.childCount()):
		    child = projectWidgetItem.child(c)
		    child.setHidden(not visibility)
		#self.syncView()
		projectWidgetItem.setHidden(not visibility)
		
	    
	    for phase in sharedDB.myPhases.values():
		phase._visible = visibility
	    #print ("Changing all phases to: "+ str(visibility))
	    
	self.syncView()

    def updateUserVisibility(self, visibility, username = ''):
	if (username != ''):
	    #print ("Changing "+ phaseName + " to : "+ str(visibility))
	    #iterate through all projects
	    for x in range(0,self.treeWidget().topLevelItemCount()):
		projectWidgetItem = self.treeWidget().topLevelItem(x)
		keepProjectVisible = False
		for c in range(projectWidgetItem.childCount()):
		    child = projectWidgetItem.child(c)

		    if (child._dbEntry.type() == "phaseassignment"):
		   	print "keeping "+ username + " visible."
			
			if self.CheckUserAssignmentForUser(child._dbEntry._userAssignments.values(),username):
			    child.setHidden(not visibility)
			    if (visibility):
				keepProjectVisible = True			
			    
		    
		    if (visibility == False and not child.isHidden() and keepProjectVisible == False):
			keepProjectVisible = True
		
		if (keepProjectVisible):
		    if (projectWidgetItem.isHidden()):
			projectWidgetItem.setHidden(False)
		elif (not visibility):
		    if (not projectWidgetItem.isHidden()):
			#self.syncView()			
			for c in range(projectWidgetItem.childCount()):
			    projectWidgetItem.child(c).setHidden(True)
			
			projectWidgetItem.setHidden(True)
				
	    #if phase matches, change visibility
	    
	    for user in sharedDB.myUsers.values():
		if (user.name() == username):
		    user._calendarVisibility = visibility
	    
	else:
	    #iterate through all projects
	    #iterate through all phases
	    #change visibility
	    if visibility == False:
		self.collapseAllTrees()
	    
	    for x in range(0,self.treeWidget().topLevelItemCount()):
		projectWidgetItem = self.treeWidget().topLevelItem(x)		
		for c in range(projectWidgetItem.childCount()):
		    child = projectWidgetItem.child(c)
		    child.setHidden(not visibility)
		#self.syncView()
		projectWidgetItem.setHidden(not visibility)
		
	    
	    for phase in sharedDB.myPhases.values():
		phase._visible = visibility
		
	    for user in sharedDB.myUsers.values():
		user._calendarVisibility = visibility
	    
		
	    #print ("Changing all phases to: "+ str(visibility))
  
	self.syncView()
    
    def CheckUserAssignmentForUser(self, userAssignments, username):
	for ua in userAssignments:
	    if ua._hours > 1 and ua.idUsers() is not None:
		if (sharedDB.myUsers[str(ua.idUsers())].name() == username):			
		    return True
	
	return False

    def viewWidget( self ):
	"""
	Returns the view widget for this gantt widget.
	
	:return     <QGraphicsView>
	"""
	return self.uiGanttVIEW
    
    def weekendBrush( self ):
	"""
	Returns the weekend brush to be used for coloring in weekends.
	
	:return     <QBrush>
	"""
	return self._weekendBrush

    def bookedBrush( self ):
	"""
	Returns the booked brush to be used for coloring in booked days.
	
	:return     <QBrush>
	"""
	return self._bookedBrush
    
    def unavailableBrush( self ):
	"""
	Returns the unavailable brush to be used for coloring in unavailable days.
	
	:return     <QBrush>
	"""
	return self._unavailableBrush
    
    def underbookedBrush( self ):
	"""
	Returns the underbookedBrush brush to be used for coloring in underbooked days.
	
	:return     <QBrush>
	"""
	return self._underbookedBrush
    
    def overbookedBrush( self ):
	"""
	Returns the overbookedBrush brush to be used for coloring in overbooked days.
	
	:return     <QBrush>
	"""
	return self._overbookedBrush
    
    def unassignedBrush( self ):
	"""
	Returns the unassignedBrush brush to be used for coloring in unassigned days.
	
	:return     <QBrush>
	"""
	return self._unassignedBrush

    def showProjectMenu( self, pos):
        """
        Displays the header menu for this tree widget.
        
        :param      pos | <QPoint> || None
        """
        '''
	
	header = self.header()
        index  = header.logicalIndexAt(pos)
        self._headerIndex = index
        
        # show a pre-set menu
        if self._headerMenu:
            menu = self._headerMenu
        else:
            menu = self.createHeaderMenu(index)
        '''
        # determine the point to show the menu from
        #if pos is not None:
        #    point = header.mapToGlobal(pos)
        #else:
        index = self.uiGanttTREE.indexAt(pos)
	
	typ = "None"
	if index.isValid():	    
	    dbentry = self.uiGanttTREE.itemFromIndex(index)._dbEntry
	    if hasattr(dbentry, '_type'):
		typ = dbentry._type

	
	point = QCursor.pos()
        
        #self.headerMenuAboutToShow.emit(menu, index)
	
	menu	 = QtGui.QMenu()
        
	if typ == "phaseassignment":
	    statusMenu = menu.addMenu("TEST")
	elif typ == "project":
	    statusAction = menu.addAction("Open in Project View")
	    statusAction.setData(dbentry.id())
	    menu.addSeparator()
	    if sharedDB.currentUser._idPrivileges < 2:
		addPhaseMenu = menu.addMenu("Add Phase")
		
		phases = sharedDB.myPhases.values()        
		phases.sort(key=operator.attrgetter('_name'))
		
		middleChar = phases[len(phases)/2]._name[0]
		
		AMMenu = addPhaseMenu.addMenu('A - '+middleChar)
		NZMenu = addPhaseMenu.addMenu(chr(ord(middleChar) + 1)+' - Z')
		
		for x in range(0,len(phases)):
		    phase = phases[x]
		    
		    if phase._name == "DUE":
			continue
		    
		    #col    = self.column(column)
		    if x<len(phases)/2 or phase._name[0] == middleChar:
			action = AMMenu.addAction(phase._name)
			action.setData("addphase_"+str(phase.id())+"_"+str(dbentry.id()))
		    else:
			action = NZMenu.addAction(phase._name)
			action.setData("addphase_"+str(phase.id())+"_"+str(dbentry.id()))
		'''
		for phase in sharedDB.myPhases.values():
		    if phase._name != "DUE":
			addPhaseAction = addPhaseMenu.addAction(phase._name)
			addPhaseAction.setData("addphase_"+str(phase.id())+"_"+str(dbentry.id()))
		'''
	    if sharedDB.currentUser._idPrivileges == 1:
		archiveAction = menu.addAction("Archive Project")
		archiveAction.setData(dbentry.id())
	else:
	    if sharedDB.currentUser._idPrivileges < 2:
		menu.addAction("Create Project")
	    
	menu.triggered.connect(self.mActions)
	    
        menu.exec_(point)
    
    def mActions(self, action):
	act = action.text()
	
	if act == "Open in Project View":
	    self.loadinprojectview(sharedDB.myProjects[str(action.data().toPyObject())])
	    #print sharedDB.myProjects[str(projectId)]._name
	elif act == "Archive Project":
	    sharedDB.myProjects[str(action.data().toPyObject())].setArchived(1)
	elif act == "Create Project":
	    if not hasattr(sharedDB, 'myCreateProjectWidget'):
		sharedDB.myCreateProjectWidget = createprojectwidget.CreateProjectWidget(sharedDB.mainWindow)
		
	    sharedDB.myCreateProjectWidget.setDefaults()
	    sharedDB.myCreateProjectWidget.dockWidget.show()
	elif "addphase" in str(action.data().toPyObject()):
	    phaseId = str(action.data().toPyObject()).split("_")[1]
	    proj = sharedDB.myProjects[str(action.data().toPyObject()).split("_")[2]]
	    phase = sharedDB.phaseAssignments.PhaseAssignments(_idphases = phaseId, _startdate = proj._startdate,_enddate = proj._startdate,_updated = 0)
	    proj.AddPhase(phase)
	    
	    #iterate through shots for
	    for image in proj._images.values():
		currentTask = sharedDB.tasks.Tasks(_idphaseassignments = phase._idphaseassignments, _idprojects = proj._idprojects, _idshots = image._idshots, _idphases = phase._idphases, _new = 1)
		currentTask.Save()
		image._tasks[str(currentTask.id())] = (currentTask)

		currentTask.Save()
	    for seq in proj._sequences.values():
		for shot in seq._shots.values():
		    currentTask = sharedDB.tasks.Tasks(_idphaseassignments = phase._idphaseassignments, _idprojects = proj._idprojects, _idshots = shot._idshots, _idphases = phase._idphases, _new = 1)
		    currentTask.Save()
		    shot._tasks[str(currentTask.id())] = (currentTask)
    
		    

    def loadinprojectview(self, project):
	#print "Loading Project"+self.cellWidget(row,column)._phaseassignment._name
	sharedDB.mainWindow.centralTabbedWidget.setCurrentIndex(0)
        sharedDB.myProjectViewWidget._currentProject = project            
        
	sharedDB.myProjectViewWidget.LoadProjectValues()
	
	sharedDB.myProjectViewWidget.projectPartWidget.setCurrentIndex(0)