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
        self.noUserText = "----"
        
        self.setFixedWidth(50)
        self.getUserFromTask()
        
        
        

    def getUserFromTask(self):
        
        if self.task == None:
            self.setText(self.noUserText)
        else:
            self.task.taskChanged.connect(self.getUserFromTask)
            if str(self.task._idusers) == "0":
                self.setText(self.noUserText)
            elif str(self.task._status) == "4":
                self.setText("")
            else:
                self.setText(sharedDB.myUsers[str(self.task._idusers)]._name)
                
        
    def mActions(self, username):
        if username.text() == " NONE":
            self.task.setUserId("0")
            self.getUserFromTask()
            return
        
        for u in sharedDB.myUsers.values():
            if str(u._name) == username.text():
                #self.setText(username.text())
                self.task.setUserId(u._idusers)
                self.getUserFromTask()
                return
    
    def contextMenuEvent(self, ev):
        
        if self.task is not None and not self.task._status == 4 :
            menu	 = QtGui.QMenu()
            
            userList = [" NONE"]
            
            #get phase assignment id from task
            phaseAssignmentid = self.task._idphaseassignments
            #get user assignments from phase assignment
            uas = sharedDB.myPhaseAssignments[str(phaseAssignmentid)]._userAssignments.values()
            
            #get user from user assignment
            userids = []
            for ua in uas:
                if ua.hours()>0:
                    userids.append(str(ua._idusers))
            
            for user in sharedDB.myUsers.values():
                #if in department
                if self.showAllEnabled:
                    userList.append(user._name)
                else:
                    if user._active:
                        #if str(sharedDB.myPhases[str(self.task._idphases)]._iddepartments) in user.departments():
                        if str(user.id()) in userids:
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