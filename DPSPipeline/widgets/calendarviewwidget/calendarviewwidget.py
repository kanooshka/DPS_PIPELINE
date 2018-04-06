import projexui
import projex
import datetime
from projexui.widgets.xganttwidget.xganttwidget     import XGanttWidget
from projexui.widgets.xganttwidget.xganttviewitem   import XGanttViewItem
from projexui.widgets.xganttwidget.xganttwidgetitem import XGanttWidgetItem 
from PyQt4.QtCore import QDate, QObject, Qt
from PyQt4 import QtGui, QtCore

import sharedDB
import operator
import time
import atexit

from PyQt4.QtGui import QColor


class WaitTimer(QtCore.QThread):

	def run(self):
		
		if sharedDB.calendarview is not None:
			sharedDB.calendarview.AddProjectSignal.emit()
			#sharedDB.calendarview.AddPhaseAssignmentSignal.emit()
		
		time.sleep(.5)

class CalendarViewWidget(QtGui.QWidget):
	AddProjectSignal = QtCore.pyqtSignal()
	AddPhaseAssignmentSignal = QtCore.pyqtSignal()
	def __init__(self):
		#global myXGanttWidget
		super(CalendarViewWidget, self).__init__()
		
		sharedDB.calendarview = self
		
		#dockWidget = QtGui.QDockWidget(sharedDB.mainWindow)
		#sharedDB.widgetList.Append(dockWidget)
		vLayout = QtGui.QHBoxLayout()
		self.setLayout(vLayout)
		
		#Add Splitter
		splitter = QtGui.QSplitter(QtCore.Qt.Vertical)
		vLayout.addWidget(splitter)
		
		
		self._myXGanttWidget = XGanttWidget()
		splitter.addWidget(self._myXGanttWidget)
		
		self._departmentXGanttWidget = XGanttWidget(_availabilityEnabled = 1)
		#self._departmentXGanttWidget._availabilityEnabled = 1
		splitter.addWidget(self._departmentXGanttWidget)
		#CONNECT SLIDERS
		self._departmentXGanttWidget.uiGanttVIEW.horizontalScrollBar().valueChanged.connect(self._myXGanttWidget.uiGanttVIEW.horizontalScrollBar().setValue)
		self._myXGanttWidget.uiGanttVIEW.horizontalScrollBar().valueChanged.connect(self._departmentXGanttWidget.uiGanttVIEW.horizontalScrollBar().setValue)
		self._departmentXGanttWidget.uiGanttSPLT.splitterMoved.connect(self.syncSplitters)
		self._myXGanttWidget.uiGanttSPLT.splitterMoved.connect(self.syncSplitters)
		 
		#connect date range changed
		self._myXGanttWidget.dateRangeChanged.connect(self.UpdateDepartmentGanttDateRange)
		sharedDB.mySQLConnection.newPhaseSignal.connect(self.AddPhaseToDepartment)
		
		#resize splitter
		sizes = [275,50000]
		self._myXGanttWidget.uiGanttSPLT.setSizes(sizes)
		self._myXGanttWidget.uiGanttSPLT.setStretchFactor(0,0)
		self._departmentXGanttWidget.uiGanttSPLT.setSizes(sizes)
		self._departmentXGanttWidget.uiGanttSPLT.setStretchFactor(0,0)
		
		#insert context menu for availability info
		# setup header
		self._departmentXGanttWidget.setContextMenuPolicy( Qt.CustomContextMenu )
		
		# connect signals
		self._departmentXGanttWidget.customContextMenuRequested.connect( self.showAvailabilityContextMenu )
		
		#sharedDB.mainWindow.setCentralWidget(self._myXGanttWidget)
		#dockWidget.setWidget(self._myXGanttWidget)
		#dockWidget.setWindowTitle("Calendar View")
		#sharedDB.leftWidget = dockWidget
		#sharedDB.mainWindow.addDockWidget(QtCore.Qt.LeftDockWidgetArea, dockWidget)

		self.availabilityPhasesSkip = ["DUE","Revision 1","Revision 2","Approval","Delivery","Rendering","Internal Review"]

		reload(projex)
		reload(projexui)
		
		self._projectQueue = []
		self._phaseassignmentQueue = []
		self.myWaitTimer = WaitTimer()
		self.myWaitTimer.daemon = True
		self.myWaitTimer.finished.connect(self.myWaitTimer.start)
		self.myWaitTimer.start()
		atexit.register(self.closeThreads)
		
		self.AddProjectSignal.connect(self.AddProject)
		self.AddPhaseAssignmentSignal.connect(self.AddPhase)
		sharedDB.mySQLConnection.newProjectSignal.connect(self.AddNewProjects)
		sharedDB.mySQLConnection.newPhaseAssignmentSignal.connect(self.AddNewPhaseAssignment)
		
		sharedDB.mySQLConnection.dateChanged.connect(self.updateDate)
		
	def closeThreads(self):
		self.myWaitTimer.quit()
	
	def AddNewProjects(self, idprojects):
		if str(idprojects) in sharedDB.myProjects:
			project = sharedDB.myProjects[str(idprojects)]				
			#if project._phases:
					#myPhaseAssignments = project._phases	
			if (not project._hidden):
			    self._projectQueue.append(project)
			    #self._projectQueue.sort(key=operator.attrgetter('_due_date'),reverse=True)
				
	def AddNewPhaseAssignment(self, idphaseassignments):
		if str(idphaseassignments) in sharedDB.myPhaseAssignments:
			self.AddPhase(sharedDB.myPhaseAssignments[str(idphaseassignments)])
		'''
		for phase in sharedDB.myPhaseAssignments:
			if str(phase._idphaseassignments) == str(idphaseassignments):
				#find project with same id
				self.AddPhase(phase)				
		'''				
	
	#def AddProject(self, project,phases = []):
	def AddProject(self):
		#global myXGanttWidget
		if len(self._projectQueue)>0:
			project = self._projectQueue[0]
			#phases = project._phases
			
			projectXGanttWidgetItem = XGanttWidgetItem(self._myXGanttWidget)
			
			projectXGanttWidgetItem._dbEntry = project
			project.projectChanged.connect(projectXGanttWidgetItem.projectChanged)
			
			projectXGanttWidgetItem.setName(project._name)
			
			viewItem = projectXGanttWidgetItem.viewItem()
			viewItem._locked = True
			viewItem.setPrivelages()
			#viewItem.setText(project._name)
			
			#projectXGanttWidgetItem.setHidden(True)
			
			#find where to insert item
			index = 0

			#print self._myXGanttWidget.topLevelItemCount()
			for x in range(0,self._myXGanttWidget.topLevelItemCount()):
				index = x+1
				if self._myXGanttWidget.topLevelItem(x)._dbEntry._due_date > project._due_date:
					#print  str(self._myXGanttWidget.topLevelItem(x)._dbEntry._due_date) + " less than " + self._myXGanttWidget.topLevelItem(x)._dateEnd.toString("MM.dd.yyyy")					
					break				
				
			#print "Inserting "+project._name+" into index "+ str(index) + " " + duedate.toString("MM.dd.yyyy")
			self._myXGanttWidget.insertTopLevelItem(index,projectXGanttWidgetItem)
			#self._myXGanttWidget.addTopLevelItem(projectXGanttWidgetItem)
			
			project._calendarWidgetItem = projectXGanttWidgetItem
			
			projectXGanttWidgetItem.setHidden(True)
			
			phaselist = project._phases.values()
				
			phaselist.sort(key=operator.attrgetter('_startdate'))

			for phase in phaselist:
				self.AddPhase(phase)
			
			#print project._calendarWidgetItem			
	
			self._myXGanttWidget.setDateStart(QDate(sharedDB.earliestDate.year,sharedDB.earliestDate.month,sharedDB.earliestDate.day))	
			projectXGanttWidgetItem.setExpanded(0)
			self._myXGanttWidget.syncView()
			projectXGanttWidgetItem.sync()
			del self._projectQueue[0]
		
		#if project starts before view start date
		
		#if project ends after view end date

	
	def AddPhase(self, phase):
		
		if phase.project is not None and phase.project._calendarWidgetItem is not None and int(phase._idstatuses) != 6 and int(phase._idstatuses) != 5:

			#if not already attached
			for c in range(0,phase.project._calendarWidgetItem.childCount()):
				if phase.project._calendarWidgetItem.child(c)._dbEntry == phase:
					return
			
			parentItem = phase.project._calendarWidgetItem
			
			department = 0
			
			if str(phase._idphases) in sharedDB.myPhases:
				myPhase = sharedDB.myPhases[str(phase._idphases)]
	
				name = myPhase._name
				
				BGcolor = myPhase._ganttChartBGColor.split(',')
				#print BGcolor[0]
				BGcolor = QColor(int(BGcolor[0]),int(BGcolor[1]),int(BGcolor[2]))
				
				textColor = myPhase._ganttChartTextColor.split(',')
				#print textColor[0]
				textColor = QColor(int(textColor[0]),int(textColor[1]),int(textColor[2]))
				
				department = myPhase._iddepartments
	
			
			startDate = phase._startdate
			endDate = phase._enddate
			
			if (startDate<sharedDB.earliestDate):
				sharedDB.earliestDate = startDate
				#print (startDate)
			
			
			childItem = XGanttWidgetItem(self._myXGanttWidget)
			childItem._dbEntry = phase
			phase._calendarWidgetItem = childItem
			
			childItem.setName(name)		
			childItem._name = name
				
			#if (qStartDate.isValid()):
			#childItem.setDateStart(QDate(startDate.year,startDate.month,startDate.day))
			#childItem.setDateEnd(QDate(endDate.year,endDate.month,endDate.day))
			#sets view Item
			viewItem = childItem.viewItem()
			viewItem.setText(name)
			viewItem.setColor(BGcolor)
			viewItem.setTextColor(textColor)			
			
			childItem.RefreshFromDB()
			phase.phaseAssignmentChanged.connect(childItem.RefreshFromDB)
			
			parentItem.addChild(childItem)
			
			if "0" in sharedDB.currentUser.departments() or (str(phase._idphases) in sharedDB.myPhases and sharedDB.myPhases[str(phase._idphases)].isVisible()):
				childItem.setHidden(False)
				parentItem.setHidden(False)
			else:
				childItem.setHidden(True)
	
	
			parentItem.adjustRange()
	def updateDate(self):
		
		#self._myXGanttWidget.frameCurrentDate()
		
		#redraw background
		self._myXGanttWidget.uiGanttVIEW.scene().rebuild()
		pass
	
	def AddPhaseToDepartment(self, phaseid):
		if str(phaseid) in sharedDB.myPhases:
			phase = sharedDB.myPhases[str(phaseid)]		

			if phase._name not in self.availabilityPhasesSkip:
			
				phaseXGanttWidgetItem = XGanttWidgetItem(self._departmentXGanttWidget)
				
				phaseXGanttWidgetItem.setFlags(phaseXGanttWidgetItem.flags() ^ Qt.ItemIsSelectable)
				
				phaseXGanttWidgetItem._dbEntry = phase
				
				phaseXGanttWidgetItem.setName(phase._name)
				
				#viewItem = phaseXGanttWidgetItem.viewItem()
				
				#find where to insert item
				index = 0						
				for x in range(0,self._departmentXGanttWidget.topLevelItemCount()):
					if min(self._departmentXGanttWidget.topLevelItem(x)._dbEntry._name , phase._name) == phase._name:
						break
					index = x+1
				
				#print "Inserting "+project._name+" into index "+ str(index) + " " + duedate.toString("MM.dd.yyyy")
				
				self._departmentXGanttWidget.insertTopLevelItem(index,phaseXGanttWidgetItem)
				#self._myXGanttWidget.addTopLevelItem(projectXGanttWidgetItem)
				
				#project._calendarWidgetItem = projectXGanttWidgetItem
				
				#projectXGanttWidgetItem.setHidden(True)
				
				#for phase in project._phases:
				#	self.AddPhase(phase)
				
				#print project._calendarWidgetItem			
		
				phaseXGanttWidgetItem.setDateStart(QDate.currentDate().addYears(-12),True)
				phaseXGanttWidgetItem.setDateEnd(QDate.currentDate().addYears(-12),True)
		
				#self._myXGanttWidget.setDateStart(QDate(sharedDB.earliestDate.year,sharedDB.earliestDate.month,sharedDB.earliestDate.day))	
				phaseXGanttWidgetItem.setExpanded(0)
				self._departmentXGanttWidget.syncView()
				phaseXGanttWidgetItem.sync()

	def syncSplitters(self,x, index):
		self._departmentXGanttWidget.uiGanttSPLT.blockSignals(1)
		self._myXGanttWidget.uiGanttSPLT.blockSignals(1)
		self._departmentXGanttWidget.uiGanttSPLT.moveSplitter(x,index)
		self._myXGanttWidget.uiGanttSPLT.moveSplitter(x,index)
		self._departmentXGanttWidget.uiGanttSPLT.blockSignals(0)
		self._myXGanttWidget.uiGanttSPLT.blockSignals(0)

	def UpdateDepartmentGanttDateRange(self):
		self._departmentXGanttWidget.setDateStart(self._myXGanttWidget.dateStart())
		self._departmentXGanttWidget.setDateEnd(self._myXGanttWidget.dateEnd())
	
	def showAvailabilityContextMenu(self, pos):
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
		
		menu = QtGui.QMenu(self)
	       
		mappedPos = self._departmentXGanttWidget.viewWidget().mapFromParent(pos)
		
		horscrollOffset = self._departmentXGanttWidget.uiGanttVIEW.horizontalScrollBar().value()-10
		verscrollOffset = self._departmentXGanttWidget.uiGanttVIEW.verticalScrollBar().value()-20
		headerHeight = self._departmentXGanttWidget.treeWidget().header().height()			
				
		datestring = self._departmentXGanttWidget.viewWidget().scene().dateAt(mappedPos.x()+horscrollOffset).toString("yyyy-MM-dd")
		item = self._departmentXGanttWidget.topLevelItem((verscrollOffset+mappedPos.y()-headerHeight)/self._departmentXGanttWidget.cellHeight())
		
		#date = self._departmentXGanttWidget.viewWidget().scene().dateAt(mappedPos.x()+horscrollOffset))
		#Take date and grab booking info for that date
	       
		#expandAll = menu.addAction( "Hor POS: " + str(mappedPos.x()))
		#expandAll = menu.addAction( "DATE: " + str(date))
		#expandAll = menu.addAction( "Ver Scroll Offset: " + str(verscrollOffset))
		#expandAll = menu.addAction( "Ver Pos: " + str(mappedPos.y()))
		
		#go through the users
		#if date in booking dict
		#if booking dict phase assignment in phase
		#add Project - Phase assignment
		
		use = sharedDB.myUsers.values()
		use.sort(key=operator.attrgetter('_name'),reverse=False)
		for i in xrange(0, len(use)):
		    if datestring in use[i]._bookingDict.keys():
			bookings = use[i]._bookingDict[str(datestring)]
			
			skip = 1
			
			for b in bookings:
				if item._dbEntry.id() == sharedDB.myPhaseAssignments[str(b.idphaseassignments())]._idphases:
					skip = 0
					exec("user_menu%d = QtGui.QMenu(use[i]._name)" % (i + 1))
					exec("menu.addMenu(user_menu%d)" % (i + 1))
					break
			if skip is not 1:
				for j in xrange(0, len(bookings)):
					exec("user_menu%d.addAction(%s)" % (i + 1,repr(str(sharedDB.myProjects[str(bookings[j].idprojects())].name()) + ": "+str(sharedDB.myPhaseAssignments[str(bookings[j].idphaseassignments())].name()))))
		
		#List Unassigned phase assignments
		unassigned_menu = QtGui.QMenu("UNASSIGNED")
		
		
		
		for pa in item._dbEntry._phaseAssignments.values():
			#if unassigned and date in phase range
			if not pa.assigned() and pa.visibility() and pa.startDate() <= self._departmentXGanttWidget.viewWidget().scene().dateAt(mappedPos.x()+horscrollOffset).toPython() <= pa.endDate():
				menu.addMenu(unassigned_menu)
				exec("unassigned_menu.addAction(%s)" % repr(str(sharedDB.myProjects[str(pa.idprojects())].name())+": " + pa.name()))			
		
		'''
		for user in sharedDB.myUsers.values():
			#print date
			#print user._bookingDict.keys() 
			if date in user._bookingDict.keys():
				#print date
				expandAll = menu.addAction(user.name() + ": " + str(sum(user._bookingDict[str(date)])))		
		'''
		#if item._dbEntry._type == "phase":
		#	phase = item._dbEntry
		#	for key in phase._availability.keys():			    
		#		if QDate.fromString(key,"yyyy-MM-dd") == date:		
		#			expandAll = menu.addAction( "Item: " + str(item._dbEntry.name()))
		# determine the point to show the menu from
		#if pos is not None:
		#    point = header.mapToGlobal(pos)
		#else:
		point = QtGui.QCursor.pos()
		
		#self.headerMenuAboutToShow.emit(menu)
		menu.exec_(point)