import sharedDB
from PyQt4 import QtCore,QtGui

class UserAssignmentSpinBox(QtGui.QSpinBox):

    def __init__(self, _phaseAssignment = None, _user = None):
        super(QtGui.QSpinBox, self).__init__()
        
        self._userAssignment = None
        self._phaseAssignment = _phaseAssignment
        self._user = _user
        
        self.setValue(0)
        self.getUserAssignment()
        
        self.valueChanged.connect(self.setHours)
        sharedDB.mySQLConnection.newUserAssignmentSignal.connect(self.CheckForUserAssignment)
        
    def getUserAssignment(self):
        for UA in sharedDB.myUserAssignments:
            if UA._idusers == self._user._idusers and UA._assignmenttype == "phase_assignment" and UA._assignmentid == self._phaseAssignment._idphaseassignments:
                self._userAssignment = UA
                self.getHours()
                #connect to update
                self._userAssignment.userAssignmentChanged.connect(self.getHours)
                break
      
    def CheckForUserAssignment(self, iduserassignment):
        for UA in sharedDB.myUserAssignments:
            if str(iduserassignment) == str(UA._iduserassignments):
                if UA._idusers == self._user._idusers and UA._assignmenttype == "phase_assignment" and UA._assignmentid == self._phaseAssignment._idphaseassignments:
                    self._userAssignment = UA
                    self.getHours()
                    #connect to update
                    self._userAssignment.userAssignmentChanged.connect(self.getHours)
                break    
      
    def getHours(self):
        self.blockSignals(1)
        self.setValue(self._userAssignment._hours)
        self.blockSignals(0)
    def setHours(self):
        if self._userAssignment is not None:
            self._userAssignment.setHours(self.value())
        elif self.value()>0:
            self._userAssignment =sharedDB.userassignments.UserAssignment(_idusers = self._user._idusers,_assignmentid = self._phaseAssignment._idphaseassignments,_assignmenttype = "phase_assignment",_idstatuses = 1, _hours = self.value(), _new = 1)
	    sharedDB.myUserAssignments.append(self._userAssignment)
            #connect to update
            self._userAssignment.userAssignmentChanged.connect(self.getHours)
        