import sys
import weakref
import projexui
import sharedDB

from datetime import timedelta,datetime
#from projexui import qt import Signal
from DPSPipeline.widgets.mytaskswidgetitem import mytaskswidgetitem
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
	
	self.showAllUsersEnabled = 0
	self.showUnassignedEnabled = 0
	self.showNotStartedEnabled = 1
	self.showInProgressEnabled = 1
	self.showOnHoldEnabled = 0
	self.showFinishedEnabled = 0
	self.showCancelledEnabled = 0
	self.showDeletedEnabled = 0
	self.showOutForApprovalEnabled = 0
	
	self.allowedStatuses = [1,2]
	
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
	self.unassignedItems = []
	
	sharedDB.mySQLConnection.newUserAssignmentSignal.connect(self.AddUserAssignment)
	
	#self.currentCellChanged.connect(self.sendSelection)
	self.cellClicked.connect(self.sendSelection)
    
    def propogateUI(self):
	#self.clear()
	#for x in range(0,self.rowCount()):
	#    self.removeRow(x)
	
	self.setSortingEnabled(0)
	
	for i in range(0,self.rowCount()):
	    self.setRowHidden(i,1)	
	
	for user in sharedDB.myUsers:
	    if user == sharedDB.currentUser or self.showAllUsersEnabled:	
		for userassignment in user._assignments:	    
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
			    phase.addUserAssignmentTaskItem(taskItem)
			    #taskItem.setText(phase.name())
			    
			    #userassignItem = QtGui.QTableWidgetItem()	
			    #userassignItem.setText(self._userassignment.idUserAssignment)
			    
			    self.setCellWidget(self.rowCount()-1,0,taskItem)
			    self.setItem(self.rowCount()-1,1,dateitem)
			    taskItem.SetVisibility()
			    #self.setItem(self.rowCount()-1,2,userassignItem)
	
	if self.showUnassignedEnabled:
	    for phase in sharedDB.myPhaseAssignments:
		skip = 0
		if len(phase.userAssignmentTaskItems()):		    
		    for ua in phase.userAssignmentTaskItems():		    
			if hasattr(ua, '_userassignment'):
			    if int(ua._userassignment.hours()) > 0:
				skip = 1			    
				break

		#if len(phase.userAssignment()) == 0:
		if not skip:
		    found = 0
		    
		    if self.unassignedItems is not None:
			for p in self.unassignedItems:
			    if p.phaseAssignment() == phase:
				p.UpdateValues()
				found = 1
				break
		    
		    if not found:
			if phase.project is not None and phase.name().upper() != "DUE" and phase.name().upper() != "APPROVAL":
			    self.insertRow(self.rowCount())
	    
			    dateitem = QtGui.QTableWidgetItem()	
			    dateitem.setText(phase.endDate().strftime('%Y/%m/%d'))
			
			    taskItem = mytaskswidgetitem.MyTasksWidgetItem(parent = self, _project = phase.project, _phaseassignment = phase, _rowItem = dateitem)	
			    self.unassignedItems.append(taskItem)
		    
			    self.setCellWidget(self.rowCount()-1,0,taskItem)
			    self.setItem(self.rowCount()-1,1,dateitem)
			    taskItem.SetVisibility()

	self.setSortingEnabled(1)

	self.setEnabled(1)
    
    def AddUserAssignment(self,sentIdUserAssignment):

	userassignment = sharedDB.userassignments.getUserAssignmentByID(sentIdUserAssignment)
	    
	if userassignment.idUsers() == sharedDB.currentUser.idUsers() or self.showAllUsersEnabled:	    
	    if str(userassignment.assignmentType()) == "phase_assignment":

		#add phase assignment to widget
		phase = sharedDB.phaseAssignments.getPhaseAssignmentByID(userassignment._assignmentid)
		
		self.insertRow(self.rowCount())

		dateitem = QtGui.QTableWidgetItem()	
		dateitem.setText(phase.endDate().strftime('%Y/%m/%d'))
		
		taskItem = mytaskswidgetitem.MyTasksWidgetItem(parent = self, _project = phase.project, _userassignment = userassignment, _phaseassignment = phase, _rowItem = dateitem)	
		self.myTaskItems.append(taskItem)
		phase.addUserAssignmentTaskItem(taskItem)
		
		self.setCellWidget(self.rowCount()-1,0,taskItem)
		self.setItem(self.rowCount()-1,1,dateitem)
		taskItem.SetVisibility()
    
    def CheckPhaseForUnassigned(self, phase):
	if self.showUnassignedEnabled:

	    skip = 0
	    if len(phase.userAssignmentTaskItems()):		    
		for ua in phase.userAssignmentTaskItems():		    
		    if hasattr(ua, '_userassignment'):
			if int(ua._userassignment.hours()) > 0:
			    skip = 1			    
			    break

	    #if len(phase.userAssignment()) == 0:
	    if not skip:
		if phase.project is not None and phase.name().upper() != "DUE" and phase.name().upper() != "APPROVAL":
		    self.insertRow(self.rowCount())
    
		    dateitem = QtGui.QTableWidgetItem()	
		    dateitem.setText(phase.endDate().strftime('%Y/%m/%d'))
		
		    taskItem = mytaskswidgetitem.MyTasksWidgetItem(parent = self, _project = phase.project, _phaseassignment = phase, _rowItem = dateitem)	
		    self.unassignedItems.append(taskItem)
	    
		    self.setCellWidget(self.rowCount()-1,0,taskItem)
		    self.setItem(self.rowCount()-1,1,dateitem)
		    taskItem.SetVisibility()
    
    
    def contextMenuEvent(self, ev):
        
        #if self.isEnabled():
        activeIps = []
        activeClients = []

        for proj in sharedDB.myProjects:
            if not proj._hidden or self.showAllUsersEnabled:
                if str(proj._idclients) not in activeClients or self.showAllUsersEnabled:
                    activeClients.append(str(proj._idclients))
                if str(proj._idips) not in activeIps or self.showAllUsersEnabled:
                    activeIps.append(str(proj._idips))
        
        menu	 = QtGui.QMenu()
        
        showAllUsersAction = menu.addAction('Show All User Assignments')
        showAllUsersAction.setCheckable(True)
        showAllUsersAction.setChecked(self.showAllUsersEnabled)
        showAllUsersAction.triggered.connect(self.toggleShowAllUsersAction)       
        
	showUnassignedAction = menu.addAction('Show Unassigned')
        showUnassignedAction.setCheckable(True)
        showUnassignedAction.setChecked(self.showUnassignedEnabled)
        showUnassignedAction.triggered.connect(self.toggleShowUnassignedAction)
	
	menu.addSeparator()
	
	#self.showNotStartedEnabled = 1
	showNotStartedAction = menu.addAction('Show Not Started')
        showNotStartedAction.setCheckable(True)
        showNotStartedAction.setChecked(self.showNotStartedEnabled)
        showNotStartedAction.triggered.connect(self.toggleShowNotStartedAction)
	
	#self.showInProgressEnabled = 1
	showInProgressAction = menu.addAction('Show In Progress')
        showInProgressAction.setCheckable(True)
        showInProgressAction.setChecked(self.showInProgressEnabled)
        showInProgressAction.triggered.connect(self.toggleShowInProgressAction)
	
	#self.showOnHoldEnabled = 0
	showOnHoldAction = menu.addAction('Show On Hold')
        showOnHoldAction.setCheckable(True)
        showOnHoldAction.setChecked(self.showOnHoldEnabled)
        showOnHoldAction.triggered.connect(self.toggleShowOnHoldAction)
	
	#self.showFinishedEnabled = 0
	showFinishedAction = menu.addAction('Show Finished')
        showFinishedAction.setCheckable(True)
        showFinishedAction.setChecked(self.showFinishedEnabled)
        showFinishedAction.triggered.connect(self.toggleShowFinishedAction)
	
	#self.showCancelledEnabled = 0
	showCancelledAction = menu.addAction('Show Cancelled')
        showCancelledAction.setCheckable(True)
        showCancelledAction.setChecked(self.showCancelledEnabled)
        showCancelledAction.triggered.connect(self.toggleShowCancelledAction)
	
	#self.showDeletedEnabled = 0
	showDeletedAction = menu.addAction('Show Deleted')
        showDeletedAction.setCheckable(True)
        showDeletedAction.setChecked(self.showDeletedEnabled)
        showDeletedAction.triggered.connect(self.toggleShowDeletedAction)
	
	#self.showOutForApprovalEnabled = 0
	showOutForApprovalAction = menu.addAction('Show Out For Approval')
        showOutForApprovalAction.setCheckable(True)
        showOutForApprovalAction.setChecked(self.showOutForApprovalEnabled)
        showOutForApprovalAction.triggered.connect(self.toggleShowOutForApprovalAction)

        menu.exec_(ev.globalPos())
    
    def toggleShowUnassignedAction(self):
	self.showUnassignedEnabled = not self.showUnassignedEnabled
	self.showAllUsersEnabled = self.showUnassignedEnabled
	self.propogateUI()
    
    def toggleShowAllUsersAction(self):
	self.showAllUsersEnabled = not self.showAllUsersEnabled
	self.propogateUI()
	
    def toggleShowNotStartedAction(self):
	self.showNotStartedEnabled = not self.showNotStartedEnabled
	if self.showNotStartedEnabled:
	    self.allowedStatuses.append(1)
	else:
	    self.allowedStatuses.remove(1)
	self.propogateUI()
    def toggleShowInProgressAction(self):
	self.showInProgressEnabled = not self.showInProgressEnabled
	if self.showInProgressEnabled:
	    self.allowedStatuses.append(2)
	else:
	    self.allowedStatuses.remove(2)
	self.propogateUI()
    def toggleShowOnHoldAction(self):
	self.showOnHoldEnabled = not self.showOnHoldEnabled
	if self.showOnHoldEnabled:
	    self.allowedStatuses.append(3)
	else:
	    self.allowedStatuses.remove(3)
	self.propogateUI()
    def toggleShowFinishedAction(self):
	self.showFinishedEnabled = not self.showFinishedEnabled
	if self.showFinishedEnabled:
	    self.allowedStatuses.append(4)
	else:
	    self.allowedStatuses.remove(4)
	self.propogateUI()
    def toggleShowCancelledAction(self):
	self.showCancelledEnabled = not self.showCancelledEnabled
	if self.showCancelledEnabled:
	    self.allowedStatuses.append(5)
	else:
	    self.allowedStatuses.remove(5)
	self.propogateUI()
    def toggleShowDeletedAction(self):
	self.showDeletedEnabled = not self.showDeletedEnabled
	if self.showDeletedEnabled:
	    self.allowedStatuses.append(6)
	else:
	    self.allowedStatuses.remove(6)
	self.propogateUI()
    def toggleShowOutForApprovalAction(self):
	self.showOutForApprovalEnabled = not self.showOutForApprovalEnabled
	if self.showOutForApprovalEnabled:
	    self.allowedStatuses.append(7)
	else:
	    self.allowedStatuses.remove(7)
	self.propogateUI()
    
    def sendSelection(self, row, column):
	if self.cellWidget(row,column) is not None:
	    sharedDB.sel.select(self.cellWidget(row,column)._phaseassignment)
    