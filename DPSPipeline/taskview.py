import projexui
import projex
import datetime
from projexui.widgets.xganttwidget.xganttwidget     import XGanttWidget
from projexui.widgets.xganttwidget.xganttviewitem   import XGanttViewItem
from projexui.widgets.xganttwidget.xganttwidgetitem import XGanttWidgetItem 
from PyQt4.QtCore import QDate
from PyQt4 import QtGui, QtCore

import sharedDB
import operator

from PyQt4.QtGui import QColor

class TaskView():

	def __init__(self):
		#global myXGanttWidget
		
		sharedDB.myTasks = sharedDB.tasks.GetTasks()
		
		dockWidget = QtGui.QDockWidget(sharedDB.mainWindow)
		#sharedDB.widgetList.Append(dockWidget)
		self._myXGanttWidget = XGanttWidget(sharedDB.mainWindow)
		dockWidget.setWidget(self._myXGanttWidget)
		dockWidget.setWindowTitle("Project View")
		sharedDB.mainWindow.setCentralWidget(dockWidget)
		
		reload(projex)
		reload(projexui)
		
		#depending on privileges / department hide all and then unhide appropriate department
		#self._myXGanttWidget.setupUserView(sharedDB.users.currentUser[0]._idPrivelages,sharedDB.users.currentUser[0]._idDepartment)
		
		for task in sharedDB.myTasks:
			if (not task._hidden):
			    self.AddTasks(task)
			    
		
		self._myXGanttWidget.emitDateRangeChanged()
		self._myXGanttWidget.setCellWidth(15)
		
		self._myXGanttWidget.expandAllTrees()


	def AddTasks(self, task):
		#global myXGanttWidget

		taskXGanttWidgetItem = XGanttWidgetItem(self._myXGanttWidget)
		taskXGanttWidgetItem.setName(task._taskType)
		viewItem = taskXGanttWidgetItem.viewItem()
		viewItem.setText(project._name)		
		
		taskXGanttWidgetItem._dbEntry = project
		taskXGanttWidgetItem.setHidden(True)
		self._myXGanttWidget.addTopLevelItem(projectXGanttWidgetItem)
		#projectXGanttWidgetItem.setDateStart(QDate(2014,11,4))
		#projectXGanttWidgetItem.setDateStart(QDate(2015,2,21))

		#for phase in project
		
		for phase in phases:
			#print phase._idphases
			self.AddPhase(projectXGanttWidgetItem, phase)
		
		projectXGanttWidgetItem.adjustRange()
		#projectXGanttWidgetItem.setDateEnd(QDate(project._due_date.year,project._due_date.month,project._due_date.day))

		#self._myXGanttWidget.SaveToDatabase()
		#sharedDB.freezeDBUpdates = 0;
		self._myXGanttWidget._dateStart = QDate(sharedDB.earliestDate.year,sharedDB.earliestDate.month,sharedDB.earliestDate.day)		
		
		#self.AddPhase(projectXGanttWidgetItem, 'Storyboard', project._story_board_start, project._story_board_end, QColor(220,0,0))
				
		#if project starts before view start date
		
		#if project ends after view end date
		#myXGanttWidgetItem.setProperty("Start",QDate(2014,11,6))
		#myXGanttWidgetItem.setProperty("End",QDate(2014,11,7))
		#myXGanttWidgetItem.setProperty("Calendar Days",2)
		#myXGanttWidgetItem.setProperty("Work Days",2)
		
		#self._myXGanttWidget.setDateStart(QDate(2014,11,1))	


	