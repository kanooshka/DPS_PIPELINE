import projexui
import projex
import datetime
from projexui.widgets.xganttwidget.xganttwidget     import XGanttWidget
from projexui.widgets.xganttwidget.xganttviewitem   import XGanttViewItem
from projexui.widgets.xganttwidget.xganttwidgetitem import XGanttWidgetItem 
from PyQt4.QtCore import QDate, QObject
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
		self._myXGanttWidget = XGanttWidget()
		vLayout.addWidget(self._myXGanttWidget)
		
		#resize splitter
		sizes = [275,50000]
		self._myXGanttWidget.uiGanttSPLT.setSizes(sizes)
		self._myXGanttWidget.uiGanttSPLT.setStretchFactor(0,0)
		
		#sharedDB.mainWindow.setCentralWidget(self._myXGanttWidget)
		#dockWidget.setWidget(self._myXGanttWidget)
		#dockWidget.setWindowTitle("Calendar View")
		#sharedDB.leftWidget = dockWidget
		#sharedDB.mainWindow.addDockWidget(QtCore.Qt.LeftDockWidgetArea, dockWidget)

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
		
	def closeThreads(self):
		self.myWaitTimer.quit()
	
	def AddNewProjects(self, idprojects):
		for project in sharedDB.myProjects:
			if str(project._idprojects) == str(idprojects):
				#if project._phases:
					#myPhaseAssignments = project._phases				
				if (not project._hidden):
				    self._projectQueue.append(project)
				    #self._projectQueue.sort(key=operator.attrgetter('_due_date'),reverse=True)
				
	def AddNewPhaseAssignment(self, idphaseassignments):
		for phase in sharedDB.myPhaseAssignments:
			if str(phase._idphaseassignments) == str(idphaseassignments):
				#find project with same id
				self.AddPhase(phase)				
						
	
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
			
			for phase in project._phases:
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
		
		if phase.project is not None:
			if phase.project._calendarWidgetItem is not None:

				parentItem = phase.project._calendarWidgetItem
				
				department = 0
				
				for myPhase in sharedDB.myPhases:
					if myPhase._idphases == phase._idphases:
						name = myPhase._name
						
						BGcolor = myPhase._ganttChartBGColor.split(',')
						#print BGcolor[0]
						BGcolor = QColor(int(BGcolor[0]),int(BGcolor[1]),int(BGcolor[2]))
						
						textColor = myPhase._ganttChartTextColor.split(',')
						#print textColor[0]
						textColor = QColor(int(textColor[0]),int(textColor[1]),int(textColor[2]))
						
						department = myPhase._iddepartments
						continue
				
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
				
				childItem.GetDatesFromDBEntry()
				phase.phaseAssignmentChanged.connect(childItem.GetDatesFromDBEntry)
				
				parentItem.addChild(childItem)
				
				if 0 in sharedDB.currentUser.departments() or str(department) in sharedDB.currentUser.departments():
					childItem.setHidden(False)
					parentItem.setHidden(False)
				else:
					childItem.setHidden(True)

				parentItem.adjustRange()
