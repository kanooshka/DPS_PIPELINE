import projexui
import sharedDB
import sys

from PyQt4 import QtGui,QtCore

from DPSPipeline.widgets import UserAssignmentSpinBox

class UserAssignmentWidget(QtGui.QTableWidget):
    
    totalHoursChanged = QtCore.pyqtSignal()
    
    def __init__( self, parent = None ):
    
	super(UserAssignmentWidget, self).__init__( parent )
        
	self._parent = parent
	
        self.showAllEnabled = 0
        
	self.aephaseAssignment = None
	
	self.setShowGrid(1)
	
	self.horizontalHeaderLabels = ["Name","Availability","Hours"]
	for x in range(0,len(self.horizontalHeaderLabels)):
	    self.insertColumn(x)
	self.setHorizontalHeaderLabels(self.horizontalHeaderLabels)

	self.verticalHeader().setVisible(False)
	self.setSortingEnabled(1)
	self.sortByColumn(0,QtCore.Qt.AscendingOrder)
	
	
	self.totalAssignedHours = 0
	
	self.userlist = []
	
    def UpdateWidget(self):
        self.setSortingEnabled(0)
	for x in range(0,self.rowCount()):
		self.removeRow(0)
        
	self.userList = []
        for user in sharedDB.myUsers:
            #if in department
            #if self.showAllEnabled:
            #    userList.append(user._name)
            #else:
            if user._active and (str(sharedDB.phases.getPhaseByID(self.aephaseAssignment._currentPhaseAssignment._idphases)._iddepartments) in user.departments() or user._idusers in self._parent._currentPhaseAssignment.idusers()):
                self.userList.append(user)
                
        #userList.sort(reverse=False)
	
        for user in self.userList:
            if user._active:
                self.AddUserToList(user, hours = "0")
	self.setSortingEnabled(1)
	
	self.totalHoursChanged.connect(self._parent.UpdateHourValues)
	self.setTotalAssignedHours()
	
    def AddUserToList(self, user, availhours = 8, hours = 0):
	name = user._name
	nameitem = QtGui.QTableWidgetItem()	
	nameitem.setText(name)
	nameitem.setFlags( nameitem.flags() ^ QtCore.Qt.ItemIsEditable ^ QtCore.Qt.ItemIsSelectable)
        #nameitem.setReadOnly(1)
        
        availhoursItem = QtGui.QTableWidgetItem()
        availhoursItem.setText(str(int(availhours)*self._parent.workDays.value()))
	availhoursItem.setFlags( availhoursItem.flags() ^ QtCore.Qt.ItemIsEditable ^ QtCore.Qt.ItemIsSelectable)
        #availhoursItem.setValidator(validator)
	#availhoursItem.setReadOnly(1)
	
	#hoursItem = IntQTableWidgetItem.IntQTableWidgetItem()
	hoursItem = UserAssignmentSpinBox.UserAssignmentSpinBox(_phaseAssignment = self._parent._currentPhaseAssignment,_user = user,_parent = self)
        #hoursItem.setValue(int(hours))
	hoursItem.setMaximum(int(availhoursItem.text()))
	hoursItem.setKeyboardTracking(0)
	#hoursItem.setToolTip(name)
        #hoursItem.setFrame(0)
        #validator = QtGui.QIntValidator()
        #hoursItem.setValidator(validator)
        hoursItem.valueChanged.connect(self.setTotalAssignedHours)
	#hoursItem.valueChanged.connect(self.setUserAssignment)
	if sharedDB.currentUser._idPrivileges > 2:
            hoursItem.setReadOnly(1)
	
        self.insertRow(self.rowCount())
        self.setItem(self.rowCount()-1,0,nameitem)
	self.setItem(self.rowCount()-1,1,availhoursItem)
        self.setCellWidget(self.rowCount()-1,2,hoursItem)
    
    def setTotalAssignedHours(self):
	totalhours = 0
	
	for i in range(0,self.rowCount()):
	    item = self.cellWidget(i,2)
	    if item is not None:
		totalhours = totalhours + int(item.value())
		#print item.text()
	    
	self.totalAssignedHours = totalhours
	
	#if totalhours greater than alotted set red else green
	if totalhours > self._parent.hoursalotted.value():
	    self.setHoursColor(0)
	else:
	    self.setHoursColor(1)
	self.totalHoursChanged.emit()
	
    def setHoursColor(self,status):
	for i in range(0,self.rowCount()):
	    item = self.cellWidget(i,2)
	    if item is not None:
		if status:
		    item.setStyleSheet('color: green')
		else:
		    item.setStyleSheet('color: red')
    
    def mActions(self, username):
        for u in sharedDB.myUsers:
            if str(u._name) == username.text():
                print u._name
		#add user assignment with 0 hours
		self.userList.append(u)
		
		self._userAssignment =sharedDB.userassignments.UserAssignment(_idusers = u._idusers,_assignmentid = self._parent._currentPhaseAssignment._idphaseassignments,_assignmenttype = "phase_assignment",_idstatuses = 1, _hours = 0, _new = 1)
		self._userAssignment.userAssignmentAdded.connect(sharedDB.myTasksWidget.AddUserAssignment)
		#sharedDB.myTasksWidget.AddUserAssignment(ua = self._userAssignment)
		sharedDB.myUserAssignments.append(self._userAssignment)
		#connect to update
		#self._userAssignment.userAssignmentChanged.connect(self.getHours)
		
                break
    
    def contextMenuEvent(self, ev):
        
        
	menu	 = QtGui.QMenu()
	
	userList = []
	for user in sharedDB.myUsers:
	    #if in department
	    if user not in self.userList:
		userList.append(user._name)
	    '''if self.showAllEnabled:
		userList.append(user._name)
	    else:
		if user._active and str(sharedDB.phases.getPhaseByID(self._parent._currentPhaseAssignment._idphases)._iddepartments) in user.departments() and user not in self.userList:
		    userList.append(user._name)
	    '''
	userList.sort(reverse=False)
	'''
	showAllDepartmentsAction = menu.addAction('Show All Departments')
	showAllDepartmentsAction.setCheckable(True)
	showAllDepartmentsAction.setChecked(self.showAllEnabled)
	showAllDepartmentsAction.triggered.connect(self.toggleShowAllAction)    
	   
	menu.addSeparator()
	'''
	for user in userList:
	    menu.addAction(str(user))     
	
	menu.triggered.connect(self.mActions)
	
	menu.exec_(ev.globalPos())
        
    def toggleShowAllAction(self):
        self.showAllEnabled = not self.showAllEnabled