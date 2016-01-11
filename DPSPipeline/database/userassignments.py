import sharedDB

#timestamp
from datetime import datetime

from PyQt4 import QtCore
from PyQt4.QtCore import QObject

'''
	Group by project/phase
	order by due date
	For percentage completed Get the number of unfinished tasks / total number of tasks
	To get estimated hours per assignment, take (8 hr * work days left in phase) / number of incomplete tasks under phase
'''


class UserAssignment(QObject):

	userAssignmentChanged = QtCore.pyqtSignal(QtCore.QString)
	userAssignmentAdded = QtCore.pyqtSignal(QtCore.QString)
	
	def __init__(self,_iduserassignments = -1, _idusers = -1, _assignmentid = -1, _assignmenttype = '', _idstatuses = 1, _timestamp = datetime.now(), _hours = 0, _updated = 0, _new = 0):
		
		super(QObject, self).__init__()
		
		# define custom properties
		self._iduserassignments      = _iduserassignments
		self._idusers     	     = _idusers
		self._assignmentid	     = _assignmentid		
		self._assignmenttype         = _assignmenttype
		self._idstatuses	     = _idstatuses
		self._hours                  = _hours
		self._timestamp		     = _timestamp
		self._updated		     = _updated
		self._new		     = _new

		self._type                   = "userassignment"
		self._hidden                 = False
		
		self._new		     = _new
		
		self.statusButton	= ''
		#if self._idstatuses == 3 or self._idstatuses == 5:
			#self._hidden = True
			
		self.connectToDBClasses()
			
	def Save(self):

		if self._new:	
			self.AddUserAssignmentToDB()
			print "User Assignment '"+str(self._iduserassignments)+"' Added to Database!"
			self._new = 0
		elif self._updated:
			#print self._number+" Updated!"
			self.UpdateUserAssignmentInDB()
			print "User Assignment '"+str(self._iduserassignments)+"' Updated in Database!"
			self._updated = 0	
	
	def AddUserAssignmentToDB(self):
	
		sharedDB.mySQLConnection.query("INSERT INTO userassignments (idusers, assignmentid, assignmenttype, idstatuses, lasteditedbyname, lasteditedbyip, appsessionid, hours) VALUES ('"+str(self._idusers)+"', '"+str(self._assignmentid)+"', '"+str(self._assignmenttype)+"', '"+str(self._idstatuses)+"', '"+str(sharedDB.currentUser._name)+"', '"+str(sharedDB.mySQLConnection.myIP)+"', '"+str(sharedDB.app.sessionId())+"', '"+str(self._hours)+"');","commit")	
	
		self._iduserassignments = sharedDB.mySQLConnection._lastInsertId
		
		sharedDB.myUserAssignments.append(self)
		self.userAssignmentAdded.emit(str(self._iduserassignments))
	
	def UpdateUserAssignmentInDB (self):
		
		sharedDB.mySQLConnection.query("UPDATE userassignments SET idusers = '"+str(self._idusers)+"', assignmentid = '"+str(self._assignmentid)+"', assignmenttype = '"+str(self._assignmenttype)+"', idstatuses = '"+str(self._idstatuses)+"', lasteditedbyname = '"+str(sharedDB.currentUser._name)+"', lasteditedbyip = '"+str(sharedDB.mySQLConnection.myIP)+"', appsessionid = '"+str(sharedDB.app.sessionId())+"', hours = '"+str(self._hours)+"' WHERE iduserassignments = "+str(self._iduserassignments)+";","commit")

	def SetValues(self,_iduserassignments = -1, _idusers = -1, _assignmentid = -1, _assignmenttype = '', _idstatuses = 1, _hours = 0, _timestamp = datetime.now()):
		print ("Downloaded update for UserAssignment '"+str(self._iduserassignments)+"'")
		
		self._iduserassignments         = _iduserassignments
		self._idusers			= _idusers
		self._assignmentid		= _assignmentid		
		self._assignmenttype            = _assignmenttype
		self._idstatuses		= _idstatuses
		self._hours                     = _hours
		self._timestamp		     	= _timestamp
		
		#update views containing project
		#update calendar view
		#self.UpdateCalendarView()
		self.userAssignmentChanged.emit(str(self._iduserassignments))
		#self.UpdateProjectView()
		##if current project changed, update values
		##else just update project list
	
	def setStatus(self,newStatus):
		self._status = newStatus
		self._updated = 1
	
	def setHours(self, hours):
		#if hours <1 delete assignment?
		self._hours = hours
		self.userAssignmentChanged.emit(str(self._iduserassignments))
		self._updated = 1
	
		
	def connectToDBClasses(self):
		
		#connect to users
		for user in sharedDB.myUsers:
			if str(user._idusers) == str(self._idusers):
				user._assignments.append(self)
				break
		if self.assignmentType() == "phase_assignment":
			for phase in sharedDB.myPhaseAssignments:
				if phase.idphaseassignments() == self.assignmentID():
					phase.addUserAssignment(self)
					if self.hours():
						if not phase.assigned():
							phase.setAssigned(1)
					
				
	def assignmentID(self):
		return self._assignmentid	
		
	def assignmentType(self):
		return self._assignmenttype
	
	def idUsers(self):
		return self._idusers
	

	def idUserAssignment(self):
		return self._iduserassignments
	
	def hours(self):
		return self._hours
	
def getUserAssignmentByID(sentid):
	for userAssignment in sharedDB.myUserAssignments:		
		if str(userAssignment._iduserassignments) == str(sentid):
			return userAssignment

	
		#
		
		'''if self._assignmenttype = 'phaseassignment':
		
		#iterate through shots
		for shot in sharedDB.myShots:
			##if idsequences matches
			#print "Shot id:" +str(shot._idshots)+" Task Id shots: "+str(myTask._idshots)
			if shot._idshots == myUserAssignment._idshots:
				
				###add to shot's task list
				if shot._tasks is not None:
					#print "Appending shot: "+str(shot._idshots)+"'s task list"
					shot._tasks.append(myUserAssignment)
				else:
					#print "Creating shot: "+str(shot._idshots)+"'s task list"
					shot._tasks = [myUserAssignment]

				sharedDB.mySQLConnection.newTaskSignal.emit(str(myUserAssignment._idtasks))
				
				break
		'''
