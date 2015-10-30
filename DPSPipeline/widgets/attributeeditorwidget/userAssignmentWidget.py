import projexui
import sharedDB
import sys

from PyQt4 import QtGui,QtCore

class UserAssignmentWidget(QtGui.QTableWidget):
    
    def __init__( self, parent = None ):
    
	super(UserAssignmentWidget, self).__init__( parent )
        
        self.showAllEnabled = 0
        
	self.aephaseAssignment = None
	
        self.insertColumn(0)
	self.insertColumn(1)
	self.setShowGrid(0)
	self.setHorizontalHeaderLabels(["Name","Hours"])
	self.verticalHeader().setVisible(False)
	self.setSortingEnabled(0)
	self.sortByColumn(1,QtCore.Qt.DescendingOrder)
	
    def UpdateWidget(self):
        for x in range(0,self.rowCount()):
		self.removeRow(0)
        '''
        for x in range(0,len(sharedDB.myUsers)):
            if sharedDB.myUsers[x]._active:
                self.AddUserToList(name = sharedDB.myUsers[x]._name, hours = "0")
        '''
    def AddUserToList(self, name = "", hours = "0"):
        nameitem = QtGui.QLineEdit()
        nameitem.setText(name)
        nameitem.setFrame(0)
        nameitem.setReadOnly(1)
        
        hoursItem = QtGui.QLineEdit()
        hoursItem.setText(hours)
        hoursItem.setFrame(0)
        validator = QtGui.QIntValidator()
        hoursItem.setValidator(validator)
        
        self.insertRow(self.rowCount())
        self.setCellWidget(self.rowCount()-1,0,nameitem)
        self.setCellWidget(self.rowCount()-1,1,hoursItem)
    
    def mActions(self, username):
        for u in sharedDB.myUsers:
            if str(u._name) == username.text():
                self.AddUserToList(u._name)
                break
    
    def contextMenuEvent(self, ev):

        menu	 = QtGui.QMenu()
        
        userList = []
        for user in sharedDB.myUsers:
            #if in department
            if self.showAllEnabled:
                userList.append(user._name)
            else:
                if user._active and str(user._iddepartments) == str(sharedDB.phases.getPhaseByID(self.aephaseAssignment._currentPhaseAssignment._idphases)._iddepartments):
                    userList.append(user._name)
                
        userList.sort(reverse=False)
         
        showAllDepartmentsAction = menu.addAction('Show All Departments')
        showAllDepartmentsAction.setCheckable(True)
        showAllDepartmentsAction.setChecked(self.showAllEnabled)
        showAllDepartmentsAction.triggered.connect(self.toggleShowAllAction)    
           
        menu.addSeparator()
        
        for user in userList:
            menu.addAction(str(user))     
        
        menu.triggered.connect(self.mActions)
        
        menu.exec_(ev.globalPos())
        
    def toggleShowAllAction(self):
        self.showAllEnabled = not self.showAllEnabled