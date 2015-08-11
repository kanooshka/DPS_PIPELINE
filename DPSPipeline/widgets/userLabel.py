from PyQt4 import QtCore,QtGui
import sharedDB

class UserLabel(QtGui.QLabel):
    
    def __init__(self,task = ''):
        super(UserLabel, self).__init__()
        
        self.task       = task
        #self._currentUserId = ''
        #self._iddepartments = 'tasks.'
        self.showAllEnabled = 0
        
        self.user = ''
        
        self.setFixedWidth(50)
        self.getUserFromTask()

    def getUserFromTask(self):
        if str(self.task._idusers) == "0":
            self.setText("----")
        else:
            self.setText(sharedDB.users.getUserByID(self.task._idusers)._name)
        
    def mActions(self, username):
        for u in sharedDB.myUsers:
            if str(u._name) == username.text():
                self.setText(username.text())
                self.task.setUserId(u._idusers)
                break
    
    def contextMenuEvent(self, ev):
        
        menu	 = QtGui.QMenu()
        
        userList = []
        for user in sharedDB.myUsers:
            #if in department
            if self.showAllEnabled:
                userList.append(user._name)
            else:
                if user._active and str(user._iddepartments) == str(sharedDB.phases.getPhaseByID(self.task._idphases)._iddepartments):
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