import sys
import weakref
import projexui
import sharedDB

from datetime import timedelta,datetime
#from projexui import qt import Signal
from DPSPipeline.widgets.mytaskswidget import mytaskswidgetitem
from PyQt4 import QtGui,QtCore
#from PyQt4 import QtCore
from PyQt4.QtGui    import QWidget
from PyQt4.QtCore   import QDate,QTime,QVariant,Qt

class MyTasksWidget(QtGui.QTableWidget):
    
    def __init__( self, parent = None ):
    
	super(MyTasksWidget, self).__init__( parent )
	
	# load the user interface# load the user interface
	#if getattr(sys, 'frozen', None):
	#   projexui.loadUi(sys._MEIPASS, self, uifile = (sys._MEIPASS+"/ui/mytaskswidget.ui"))    
	#else:
	#    projexui.loadUi(__file__, self)

	self._blockUpdates = 0
	
	sharedDB.myTasksWidget = self
	
	if sharedDB.initialLoad:
	    self.propogateUI
	else:
	    sharedDB.mySQLConnection.firstLoadComplete.connect(self.propogateUI)
	
	#self.projectTaskItems = []
	self.setEnabled(0)
	
	self.horizontalHeaderLabels = ["Task","Due Date","ID User Assignment"]
	for x in range(0,len(self.horizontalHeaderLabels)):
	    self.insertColumn(x)
	self.setHorizontalHeaderLabels(self.horizontalHeaderLabels)

	self.setShowGrid(0)

	self.verticalHeader().setVisible(False)
	self.verticalHeader().setDefaultSectionSize(95)
	self.horizontalHeader().setVisible(False)
	self.horizontalHeader().setResizeMode( 0, QtGui.QHeaderView.Stretch )
	self.setSortingEnabled(1)
	self.setColumnHidden(1,True)
	self.setColumnHidden(2,True)
	
	self.sortByColumn(1,QtCore.Qt.AscendingOrder)
    
	#create listener for new user assignments
	
	self.myTaskItems = []
	
	sharedDB.mySQLConnection.newUserAssignmentSignal.connect(self.propogateUI)
    
    def propogateUI(self):
	#self.clear()
	#for x in range(0,self.rowCount()):
	#    self.removeRow(x)
	
	self.setSortingEnabled(0)
	for userassignment in sharedDB.currentUser._assignments:	    
	    if str(userassignment.assignmentType()) == "phase_assignment":
		found = 0
		
		#see if it already exists
		if self.myTaskItems is not None:
		    for t in self.myTaskItems:
			if t.userAssignment() == userassignment:
			    t.UpdateValues()
			    found = 1
			    break
		
		if not found:
		    #add phase assignment to widget
		    phase = sharedDB.phaseAssignments.getPhaseAssignmentByID(userassignment._assignmentid)
		    
		    #projectWidgetItem = projectTreeWidgetItem.ProjectTreeWidgetItem(phase = phase, parent = self.myTaskList)
		    #self.myTaskList.insertTopLevelItem(0,projectWidgetItem)		
		    #self.projectTaskItems.append(projectWidgetItem)
		    
		    self.insertRow(self.rowCount())
		    
		    #phase.phaseAssignmentChanged.connect(self.propogateUI)
		    dateitem = QtGui.QTableWidgetItem()	
		    dateitem.setText(phase.endDate().strftime('%Y/%m/%d'))
		    
		    taskItem = mytaskswidgetitem.MyTasksWidgetItem(parent = self, _project = phase.project, _userassignment = userassignment, _phaseassignment = phase, _rowItem = dateitem)	
		    self.myTaskItems.append(taskItem)
		    #taskItem.setText(phase.name())
		    
		    #userassignItem = QtGui.QTableWidgetItem()	
		    #userassignItem.setText(self._userassignment.idUserAssignment)
		    
		    self.setCellWidget(self.rowCount()-1,0,taskItem)
		    self.setItem(self.rowCount()-1,1,dateitem)
		    taskItem.SetVisibility()
		    #self.setItem(self.rowCount()-1,2,userassignItem)
		
	self.setSortingEnabled(1)

	self.setEnabled(1)