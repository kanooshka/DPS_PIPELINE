import sharedDB
from PyQt4 import QtCore,QtGui

class UserAssignmentSpinBox(QtGui.QSpinBox):

    def __init__(self, _phaseAssignment = None, _user = None, _parent = None):
        super(QtGui.QSpinBox, self).__init__()
        
        self._userAssignment = None
        self._phaseAssignment = _phaseAssignment
        self._user = _user
        self._parent = _parent
        
        self.setValue(0)
	self.setMaximum(99999)
        self.getUserAssignment()
        
	
	
        #self._parent.totalHoursChanged
        self.valueChanged.connect(self.setHours)
        sharedDB.mySQLConnection.newUserAssignmentSignal.connect(self.CheckForUserAssignment)
        
    def getUserAssignment(self):
        for UA in sharedDB.myUserAssignments.values():
            if UA._idusers == self._user._idusers and UA._assignmenttype == "phase_assignment" and UA._assignmentid == self._phaseAssignment._idphaseassignments:
                self._userAssignment = UA
                self.getHours()
                #connect to update
                self._userAssignment.userAssignmentChanged.connect(self.getHours)
                break
      
    def CheckForUserAssignment(self, iduserassignment):

	if str(iduserassignment) in sharedDB.myUserAssignments:
	    UA = sharedDB.myUserAssignments[str(iduserassignment)]
	    if UA._idusers == self._user._idusers and UA._assignmenttype == "phase_assignment" and UA._assignmentid == self._phaseAssignment._idphaseassignments:
		self._userAssignment = UA
		self.getHours()
		#connect to update
		self._userAssignment.userAssignmentChanged.connect(self.getHours)
		self._parent.setTotalAssignedHours()
 
      
    def getHours(self):
        self.blockSignals(1)
        self.setValue(self._userAssignment._hours)
        #update 
        self.blockSignals(0)
    
    def setHours(self):
        if self._userAssignment is not None:
            self._userAssignment.setHours(self.value())
            if self.value()>0:
                self._phaseAssignment.updateAssigned()
            else:
                #sharedDB.myTasksWidget.CheckForUnassigned(self._phaseAssignment._idphaseassignments)
                self._phaseAssignment.updateAssigned()
        elif self.value()>0:
            self._userAssignment =sharedDB.userassignments.UserAssignment(_idusers = self._user._idusers,_idprojects = self._phaseAssignment._idprojects, _assignmentid = self._phaseAssignment._idphaseassignments,_assignmenttype = "phase_assignment",_idstatuses = 1, _hours = self.value(), _new = 1)
	    
            self._userAssignment.userAssignmentAdded.connect(sharedDB.myTasksWidget.AddUserAssignment)
            #sharedDB.myUserAssignments.append(self._userAssignment)
            #connect to update
            self._userAssignment.userAssignmentChanged.connect(self.getHours)
	    self._userAssignment.Save()
	    self._userAssignment.connectToDBClasses()
	    
	    self._phaseAssignment.setAssigned(1)
            self._phaseAssignment.updateAssigned()
	    
    def wheelEvent(self, event):
        pass