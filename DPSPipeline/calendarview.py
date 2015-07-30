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
		
		time.sleep(.5)

class CalendarView(QObject):
	AddProjectSignal = QtCore.pyqtSignal()
	
	def __init__(self):
		#global myXGanttWidget
		super(QObject, self).__init__()
		
		dockWidget = QtGui.QDockWidget(sharedDB.mainWindow)
		#sharedDB.widgetList.Append(dockWidget)
		self._myXGanttWidget = XGanttWidget(sharedDB.mainWindow)
		#sharedDB.mainWindow.setCentralWidget(self._myXGanttWidget)
		dockWidget.setWidget(self._myXGanttWidget)
		dockWidget.setWindowTitle("Calendar View")
		sharedDB.leftWidget = dockWidget
		sharedDB.mainWindow.addDockWidget(QtCore.Qt.LeftDockWidgetArea, dockWidget)

		reload(projex)
		reload(projexui)
		
		self._projectQueue = []
		self.myWaitTimer = WaitTimer()
		self.myWaitTimer.daemon = True
		self.myWaitTimer.finished.connect(self.myWaitTimer.start)
		self.myWaitTimer.start()
		atexit.register(self.closeThreads)
		
		self.AddProjectSignal.connect(self.AddProject)
		sharedDB.mySQLConnection.newProjectSignal.connect(self.AddNewProjects)
	
	def closeThreads(self):
		self.myWaitTimer.quit()
	
	def AddNewProjects(self, idprojects):
		for project in sharedDB.myProjects:
			if str(project._idprojects) == str(idprojects):
				if project._phases:
					myPhaseAssignments = project._phases
				
				if (not project._hidden):
				    #self.AddProject(project,myPhaseAssignments)
				    #tmp = []
				   # tmp.append(project)
				    #tmp.append(myPhaseAssignments)
				    #self._projectQueue.append(project)
				    #self._projectQueue.append(myPhaseAssignments)
				    self._projectQueue.append(project)
				    self._projectQueue.sort(key=operator.attrgetter('_due_date'),reverse=True)
				
	
	
	#def AddProject(self, project,phases = []):
	def AddProject(self):
		#global myXGanttWidget
		if len(self._projectQueue)>0:
			project = self._projectQueue[0]
			phases = project._phases
			
			projectXGanttWidgetItem = XGanttWidgetItem(self._myXGanttWidget)
			
			projectXGanttWidgetItem._dbEntry = project
			project.projectChanged.connect(projectXGanttWidgetItem.projectChanged)
			
			projectXGanttWidgetItem.setName(project._name)
			
			
			project._calendarWidgetItem = projectXGanttWidgetItem
			
			viewItem = projectXGanttWidgetItem.viewItem()
			#viewItem.setText(project._name)
			
			projectXGanttWidgetItem.phases = phases
			
			
			#projectXGanttWidgetItem.setHidden(True)
			
			#find where to insert item
			index = 0
			'''duedate = QDate(project._due_date)
			#print phases
			for p in phases:
				#print p._idphases
				if str(p._idphases) == "16":
					#print duedate
					duedate = QDate(p._enddate)
					#print duedate
					break
			'''
			#print self._myXGanttWidget.topLevelItemCount()
			for x in range(0,self._myXGanttWidget.topLevelItemCount()):
				index = x
				if self._myXGanttWidget.topLevelItem(x)._dateEnd >= project._due_date:
					#print  duedate.toString("MM.dd.yyyy") + " less than " + self._myXGanttWidget.topLevelItem(x)._dateEnd.toString("MM.dd.yyyy")					
					break				
				
			#print "Inserting "+project._name+" into index "+ str(index) + " " + duedate.toString("MM.dd.yyyy")
			self._myXGanttWidget.insertTopLevelItem(index,projectXGanttWidgetItem)
			#self._myXGanttWidget.addTopLevelItem(projectXGanttWidgetItem)
			
			#projectXGanttWidgetItem.setDateStart(QDate(2014,11,4))
			#projectXGanttWidgetItem.setDateStart(QDate(2015,2,21))
	
			project._phases = phases
			
			#for phase in project
			
			for phase in phases:
				#if str(phase._idphases) == "16":
				self.AddPhase(projectXGanttWidgetItem, phase)
			
			projectXGanttWidgetItem.adjustRange()
	
			self._myXGanttWidget._dateStart = QDate(sharedDB.earliestDate.year,sharedDB.earliestDate.month,sharedDB.earliestDate.day)		
			projectXGanttWidgetItem.setExpanded(1)
			
			del self._projectQueue[0]
		
		#if project starts before view start date
		
		#if project ends after view end date

	
	def AddPhase(self, parent, phase):	
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
				
				department = myPhase._idDepartment
		
		startDate = phase._startdate
		endDate = phase._enddate
		
		if (startDate<sharedDB.earliestDate):
			sharedDB.earliestDate = startDate
			#print (startDate)
		
		
		childItem = XGanttWidgetItem(self._myXGanttWidget)
		childItem._dbEntry = phase
		
		childItem.setName(name)		
		childItem._name = name
			
		#if (qStartDate.isValid()):
		childItem.setDateStart(QDate(startDate.year,startDate.month,startDate.day))
		childItem.setDateEnd(QDate(endDate.year,endDate.month,endDate.day))
		#sets view Item
		viewItem = childItem.viewItem()
		viewItem.setText(name)
		viewItem.setColor(BGcolor)
		viewItem.setTextColor(textColor)
		
		parent.addChild(childItem)
		
		if (sharedDB.currentUser[0]._idDepartment == 0 or department == sharedDB.currentUser[0]._idDepartment):
			childItem.setHidden(False)
			parent.setHidden(False)
		else:
			childItem.setHidden(True)
		
	