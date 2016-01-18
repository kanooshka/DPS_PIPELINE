import sys
import weakref
import projexui
import sharedDB
import time

from datetime import timedelta,datetime,date
#from projexui import qt import Signal
from DPSPipeline.widgets.mytaskswidgetitem import mytaskswidgetitem
from PyQt4 import QtGui,QtCore
#from PyQt4 import QtCore
from PyQt4.QtGui    import QWidget
from PyQt4.QtCore   import QDate,QTime,QVariant,Qt
import atexit

class WaitTimer(QtCore.QThread):

	def run(self):
		
		if sharedDB.myTasksWidget is not None:
			sharedDB.myTasksWidget.AddTaskSignal.emit()
			#sharedDB.calendarview.AddPhaseAssignmentSignal.emit()
		
		time.sleep(.05)

class MyTasksWidget(QtGui.QTableWidget):
    AddTaskSignal = QtCore.pyqtSignal()
    
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
	self.showAllUsersInDepartmentEnabled = 0
	
	self.allowedStatuses = [1,2]
	
	# Set visibility defaults
	if sharedDB.currentUser._idPrivileges == 2:
	    self.showAllUsersInDepartmentEnabled = 1
	    self.showUnassignedEnabled = 1
	elif sharedDB.currentUser._idPrivileges == 1:
	    self.showAllUsersEnabled = 1
	    self.showUnassignedEnabled = 1
	    self.showOnHoldEnabled = 1
	    self.allowedStatuses.append(3)
	    self.showOutForApprovalEnabled = 1
	    self.allowedStatuses.append(7)

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
	
	sharedDB.mySQLConnection.newUserAssignmentSignal.connect(self.AppendToUserAssignmentQueue)
	sharedDB.mySQLConnection.newPhaseAssignmentSignal.connect(self.CheckForUnassigned)
	
	#self.currentCellChanged.connect(self.sendSelection)
	self.cellClicked.connect(self.sendSelection)
	self.cellDoubleClicked.connect(self.loadinprojectview)
    
	self.myWaitTimer = WaitTimer()
	self.myWaitTimer.daemon = True
	self.myWaitTimer.finished.connect(self.myWaitTimer.start)
	self.myWaitTimer.start()
	atexit.register(self.closeThreads)
	self.AddTaskSignal.connect(self.ProcessQueue)
	self._userAssignmentQueue = []
	self._unassignedTaskQueue = []
	
	self._connectedPhaseAssignments = []
	
    def closeThreads(self):
	self.myWaitTimer.quit()
    
    def propogateUI(self):
	#self.clear()
	#for x in range(0,self.rowCount()):
	#    self.removeRow(x)
	
	self.setSortingEnabled(0)
	
	for i in range(0,self.rowCount()):
	    self.setRowHidden(i,1)	
	
	for userids in sharedDB.myUsers:
	    user = sharedDB.myUsers[str(userids)]
	    #if user == sharedDB.currentUser or self.showAllUsersEnabled or self.showAllUsersInDepartmentEnabled:	
	    for userassignmentids in user._assignments:	    
		if str(userassignmentids) in user._assignments:
		    userassignment = user._assignments[str(userassignmentids)]
		    if str(userassignment.assignmentType()) == "phase_assignment":
			found = 0
			
			#see if it already exists
			if self.myTaskItems is not None:
			    for t in self.myTaskItems:
				if t.userAssignment() == userassignment:
				    t.UpdateValues()
				    found = 1
				    break
	
	self.CheckForUnassigned()

	self.setSortingEnabled(1)

	self.setEnabled(1)
    
    def CheckForUnassigned(self, sentphaseid = None):
	if sentphaseid is None:
	    phaselist = sharedDB.myPhaseAssignments.values()
	else:
	    #phaselist = [sharedDB.phaseAssignments.getPhaseAssignmentByID(sentphaseid)]
	    phaselist = [sharedDB.myPhaseAssignments[str(sentphaseid)]]
	    
	for phase in phaselist:
	    if phase is not None:
		#connect phase unassigned signal to widget
		if phase not in self._connectedPhaseAssignments:
		    phase.unassignedSignal.connect(self.AddToUnassignedQueue)
		    self._connectedPhaseAssignments.append(phase)
		
		if not phase.assigned():
		    found = 0
		    if self.unassignedItems is not None:
			for p in self.unassignedItems:
			    if p.phaseAssignment() == phase:
				p.UpdateValues()
				found = 1
				break
			
			if not found:
			    if phase.project is not None and phase.name().upper() != "DUE" and phase.name().upper() != "APPROVAL":
				if phase not in self._unassignedTaskQueue:
				    self._unassignedTaskQueue.append(phase)
    
    def AddToUnassignedQueue(self, sentID):
	if str(sentID) in sharedDB.myPhaseAssignments:
	    phase = sharedDB.myPhaseAssignments[str(sentID)]
	    if self.unassignedItems is not None:
		for p in self.unassignedItems:
		    if p.phaseAssignment() == phase:
			p.UpdateValues()
			return
			
	    self._unassignedTaskQueue.append(phase)
	    return
    
    def AppendToUserAssignmentQueue(self, assignmentid):
	self._userAssignmentQueue.append(assignmentid)
    
    def ProcessQueue(self):
	if len(self._userAssignmentQueue)>0:
	    self.AddUserAssignment(self._userAssignmentQueue[0])
	    del self._userAssignmentQueue[0]
	else:
	    if len(self._unassignedTaskQueue)>0:
		if not self._unassignedTaskQueue[0].assigned():
		    self.AddUnassigned(self._unassignedTaskQueue[0])
		del self._unassignedTaskQueue[0]
    
    def AddUserAssignment(self,sentIdUserAssignment):

	if str(sentIdUserAssignment) in sharedDB.myUserAssignments:
	    userassignment = sharedDB.myUserAssignments[str(sentIdUserAssignment)]
	    
	    if str(userassignment._assignmentid) in sharedDB.myPhaseAssignments:
		phase = sharedDB.myPhaseAssignments[str(userassignment._assignmentid)]
		
		#if userassignment.idUsers() == sharedDB.currentUser.idUsers() or self.showAllUsersEnabled or (sharedDB.currentUser._idPrivileges == 2 and phase._iddepartments in sharedDB.currentUser.departments()):	    
		if str(userassignment.assignmentType()) == "phase_assignment":
	
		    #add phase assignment to widget
		    
		    #phase.setAssigned(1)
		    
		    if sharedDB.currentUser._idPrivileges < 3 or date.today()+timedelta(days=5) >= phase._startdate:
			self.insertRow(self.rowCount())
	
			dateitem = QtGui.QTableWidgetItem()	
			dateitem.setText(phase.endDate().strftime('%Y/%m/%d'))
			
			taskItem = mytaskswidgetitem.MyTasksWidgetItem(parent = self, _project = phase.project, _userassignment = userassignment, _phaseassignment = phase, _rowItem = dateitem)	
			self.myTaskItems.append(taskItem)
			#phase.addUserAssignmentTaskItem(taskItem)
			
			self.setCellWidget(self.rowCount()-1,0,taskItem)
			self.setItem(self.rowCount()-1,1,dateitem)
			taskItem.SetVisibility()

    def AddUnassigned(self, phase):
	if self.showUnassignedEnabled:

	    self.insertRow(self.rowCount())

	    dateitem = QtGui.QTableWidgetItem()
	    dateitem.setText(date.today().strftime('%Y/%m/%d'))
	
	    taskItem = mytaskswidgetitem.MyTasksWidgetItem(parent = self, _project = phase.project, _phaseassignment = phase, _rowItem = dateitem)	
	    self.unassignedItems.append(taskItem)
    
	    self.setCellWidget(self.rowCount()-1,0,taskItem)
	    self.setItem(self.rowCount()-1,1,dateitem)
	    taskItem.SetVisibility()
    
    
    def contextMenuEvent(self, ev):
        
        #if self.isEnabled():
        activeIps = []
        activeClients = []
	
	'''
        for proj in sharedDB.myProjects:
            if not proj._hidden or self.showAllUsersEnabled:
                if str(proj._idclients) not in activeClients or self.showAllUsersEnabled:
                    activeClients.append(str(proj._idclients))
                if str(proj._idips) not in activeIps or self.showAllUsersEnabled:
                    activeIps.append(str(proj._idips))
        '''
        menu	 = QtGui.QMenu()
        
	if sharedDB.currentUser._idPrivileges < 3:
	    
	    justMyAssignmentsAction = menu.addAction('Show ONLY MY Assignments')
	    justMyAssignmentsAction.triggered.connect(self.toggleJustMyAssignmentsAction)
	    
	    showAllUsersAction = menu.addAction('Show All User Assignments')
	    showAllUsersAction.setCheckable(True)
	    showAllUsersAction.setChecked(self.showAllUsersEnabled)
	    showAllUsersAction.triggered.connect(self.toggleShowAllUsersAction)       
	    
	    showAllUsersInDepartmentAction = menu.addAction('Show Department')
	    showAllUsersInDepartmentAction.setCheckable(True)
	    showAllUsersInDepartmentAction.setChecked(self.showAllUsersInDepartmentEnabled)
	    showAllUsersInDepartmentAction.triggered.connect(self.toggleShowAllUsersInDepartmentAction)
	    
	    showUnassignedAction = menu.addAction('Show Unassigned')
	    showUnassignedAction.setCheckable(True)
	    showUnassignedAction.setChecked(self.showUnassignedEnabled)
	    showUnassignedAction.triggered.connect(self.toggleShowUnassignedAction)
	
	    menu.addSeparator()
	statusMenu = menu.addMenu("Status Visibility")
	
	#self.showNotStartedEnabled = 1
	showNotStartedAction = statusMenu.addAction('Show Not Started')
	showNotStartedAction.setCheckable(True)
	showNotStartedAction.setChecked(self.showNotStartedEnabled)
	showNotStartedAction.triggered.connect(self.toggleShowNotStartedAction)
	
	#self.showInProgressEnabled = 1
	showInProgressAction = statusMenu.addAction('Show In Progress')
	showInProgressAction.setCheckable(True)
	showInProgressAction.setChecked(self.showInProgressEnabled)
	showInProgressAction.triggered.connect(self.toggleShowInProgressAction)
	
	#self.showOnHoldEnabled = 0
	showOnHoldAction = statusMenu.addAction('Show On Hold')
	showOnHoldAction.setCheckable(True)
	showOnHoldAction.setChecked(self.showOnHoldEnabled)
	showOnHoldAction.triggered.connect(self.toggleShowOnHoldAction)
	
	#self.showFinishedEnabled = 0
	showFinishedAction = statusMenu.addAction('Show Finished')
	showFinishedAction.setCheckable(True)
	showFinishedAction.setChecked(self.showFinishedEnabled)
	showFinishedAction.triggered.connect(self.toggleShowFinishedAction)
	
	#self.showCancelledEnabled = 0
	showCancelledAction = statusMenu.addAction('Show Cancelled')
	showCancelledAction.setCheckable(True)
	showCancelledAction.setChecked(self.showCancelledEnabled)
	showCancelledAction.triggered.connect(self.toggleShowCancelledAction)
	
	#self.showDeletedEnabled = 0
	showDeletedAction = statusMenu.addAction('Show Deleted')
	showDeletedAction.setCheckable(True)
	showDeletedAction.setChecked(self.showDeletedEnabled)
	showDeletedAction.triggered.connect(self.toggleShowDeletedAction)
	
	#self.showOutForApprovalEnabled = 0
	showOutForApprovalAction = statusMenu.addAction('Show Out For Approval')
	showOutForApprovalAction.setCheckable(True)
	showOutForApprovalAction.setChecked(self.showOutForApprovalEnabled)
	showOutForApprovalAction.triggered.connect(self.toggleShowOutForApprovalAction)

        menu.exec_(ev.globalPos())
    
    def toggleJustMyAssignmentsAction(self):
	self.showAllUsersInDepartmentEnabled = 0
	self.showUnassignedEnabled = 0
	self.showAllUsersEnabled = 0
	self.propogateUI()
    
    
    def toggleShowAllUsersInDepartmentAction(self):
	self.showAllUsersInDepartmentEnabled = not self.showAllUsersInDepartmentEnabled
	self.propogateUI()
    
    
    def toggleShowUnassignedAction(self):
	self.showUnassignedEnabled = not self.showUnassignedEnabled
	#self.showAllUsersEnabled = self.showUnassignedEnabled
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
	    sharedDB.sel.select([self.cellWidget(row,column),self.cellWidget(row,column)._phaseassignment])
    
    def loadinprojectview(self, row, column):
	#print "Loading Project"+self.cellWidget(row,column)._phaseassignment._name
	sharedDB.mainWindow.centralTabbedWidget.setCurrentIndex(0)
        sharedDB.myProjectViewWidget._currentProject = self.cellWidget(row,column)._phaseassignment.project            
        
	sharedDB.myProjectViewWidget.LoadProjectValues()