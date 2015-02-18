import projexui
import projex
import datetime
from projexui.widgets.xganttwidget.xganttwidget     import XGanttWidget
from projexui.widgets.xganttwidget.xganttviewitem   import XGanttViewItem
from projexui.widgets.xganttwidget.xganttwidgetitem import XGanttWidgetItem 
from PyQt4.QtCore import QDate

import sharedDB

from PyQt4.QtGui import QColor

class GanttTest():

	def __init__(self):
		#global myXGanttWidget
		
		self._myXGanttWidget = XGanttWidget()
		self._myXGanttWidget.hide()
		#self.app=app
		reload(projex)
		reload(projexui)


	def AddProject(self, project,phases = []):
		#global myXGanttWidget

		projectXGanttWidgetItem = XGanttWidgetItem(self._myXGanttWidget)
		projectXGanttWidgetItem.setName(project._name)
		projectXGanttWidgetItem.phases = phases
		
		projectXGanttWidgetItem._dbEntry = project
		self._myXGanttWidget.addTopLevelItem(projectXGanttWidgetItem)
		#projectXGanttWidgetItem.setDateStart(QDate(2014,11,4))
		#projectXGanttWidgetItem.setDateStart(QDate(2015,2,21))

		#for phase in project
		
		for phase in phases:
			#print phase._idphases
			self.AddPhase(projectXGanttWidgetItem, phase)
		
		projectXGanttWidgetItem.adjustRange()
		#projectXGanttWidgetItem.setDateEnd(QDate(project._due_date.year,project._due_date.month,project._due_date.day))

		self._myXGanttWidget.SaveToDatabase()
		sharedDB.freezeDBUpdates = 0;
		self._myXGanttWidget._dateStart = QDate(sharedDB.earliestDate.year,sharedDB.earliestDate.month,sharedDB.earliestDate.day)
		#self.AddPhase(projectXGanttWidgetItem, 'Storyboard', project._story_board_start, project._story_board_end, QColor(220,0,0))
				
		#if project starts before view start date
		
		#if project ends after view end date
		#myXGanttWidgetItem.setProperty("Start",QDate(2014,11,6))
		#myXGanttWidgetItem.setProperty("End",QDate(2014,11,7))
		#myXGanttWidgetItem.setProperty("Calendar Days",2)
		#myXGanttWidgetItem.setProperty("Work Days",2)
		
		#self._myXGanttWidget.setDateStart(QDate(2014,11,1))	
	
	def AddPhase(self, parent, phase):	
		
		for myPhase in sharedDB.myPhases:
			if myPhase._idphases == phase._idphases:
				name = myPhase._name
				
				BGcolor = myPhase._ganttChartBGColor.split(',')
				#print BGcolor[0]
				BGcolor = QColor(int(BGcolor[0]),int(BGcolor[1]),int(BGcolor[2]))
				
				textColor = myPhase._ganttChartTextColor.split(',')
				#print textColor[0]
				textColor = QColor(int(textColor[0]),int(textColor[1]),int(textColor[2]))
		
		
		startDate = phase._startdate
		endDate = phase._enddate
		
		if (startDate<sharedDB.earliestDate):
			sharedDB.earliestDate = startDate
			#print (startDate)
		
		
		childItem = XGanttWidgetItem(self._myXGanttWidget)
		childItem.setName(name)
		childItem._dbEntry = phase
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

	