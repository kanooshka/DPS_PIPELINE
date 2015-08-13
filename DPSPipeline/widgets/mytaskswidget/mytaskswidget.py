import sys
import weakref
import projexui
import sharedDB

from datetime import timedelta,datetime
#from projexui import qt import Signal
from DPSPipeline.widgets.mytaskswidget import projectTreeWidgetItem
from PyQt4 import QtGui,QtCore
#from PyQt4 import QtCore
from PyQt4.QtGui    import QWidget
from PyQt4.QtCore   import QDate,QTime,QVariant,Qt

class MyTasksWidget(QWidget):
    
    def __init__( self, parent = None ):
    
	super(MyTasksWidget, self).__init__( parent )
	
	# load the user interface# load the user interface
	if getattr(sys, 'frozen', None):
	    projexui.loadUi(sys._MEIPASS, self, uifile = (sys._MEIPASS+"/ui/mytaskswidget.ui"))
	    
	else:
	    projexui.loadUi(__file__, self)

	self._blockUpdates = 0
	
	sharedDB.myTasksWidget = self
	
	if sharedDB.initialLoad:
	    self.propogateUI
	else:
	    sharedDB.mySQLConnection.firstLoadComplete.connect(self.propogateUI)
	
	self.projectTaskItems = []
	self.setEnabled(0)
	self.myTaskList.setColumnHidden(1,True)
    
    def propogateUI(self):
	#self.projectTaskItems.clear()
	for userassignment in sharedDB.currentUser._assignments:	    
	    if str(userassignment._assignmenttype) == "phase":
		#add phase assignment to widget
		phase = sharedDB.phaseAssignments.getPhaseAssignmentByID(userassignment._assignmentid)
		projectWidgetItem = projectTreeWidgetItem.ProjectTreeWidgetItem(phase = phase, parent = self.myTaskList)
		self.myTaskList.insertTopLevelItem(0,projectWidgetItem)
		self.projectTaskItems.append(projectWidgetItem)
	
	self.myTaskList.sortItems(1,QtCore.Qt.AscendingOrder)

	self.setEnabled(1)