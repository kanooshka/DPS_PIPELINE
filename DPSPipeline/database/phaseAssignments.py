from DPSPipeline.database.connection import Connection
#import socket
import sharedDB
from PyQt4 import QtCore
from PyQt4.QtCore import QDate, QObject
from datetime import datetime
import operator

class PhaseAssignments(QObject):
	phaseAssignmentChanged = QtCore.pyqtSignal(QtCore.QString)
	phaseAssignmentAdded = QtCore.pyqtSignal(QtCore.QString)
	userAssigned = QtCore.pyqtSignal()
	
	def __init__(self,_idphaseassignments = 0,_idphases = 0,_idprojects = -1,_startdate = '',_enddate = '',_idstatuses = 1,_progress = 0.0,_archived = 0, _updated = 0, _new = 0, _hoursalotted = 0, _timestamp = datetime.now()):
		
		super(QObject, self).__init__()
		
		# define custom properties
		self._idphaseassignments           = _idphaseassignments
		self._idphases                     = _idphases
		self._idprojects                   = _idprojects
		self._startdate                    = _startdate
		self._enddate                      = _enddate
		self._progress                     = _progress
		self._idstatuses                   = _idstatuses
		self._hoursalotted		   = _hoursalotted
		self._archived                     = _archived
		self._timestamp		     	   = _timestamp
		
		self._updated                      = _updated
		self._new                    	   = _new
		self._name                         = ''
		self._taskPerShot		   = 1
		self._type                         = "phaseassignment"
		self.project                       = None
		self._calendarWidgetItem	   = None
		self._tasks			   = []
		self._iddepartments	           = 1
		
		self.phaseAssignmentAdded.emit(str(self._idphaseassignments))
		
		#sharedDB.mySQLConnection.newTaskSignal.connect(self.AddTaskToList)
		
		self.SetPhaseValues()
		
		self._userAssignments = []
		#self._unassigned = []
		
	def Save(self):		

		if self._new:	
			self.AddPhaseAssignmentToDB()
			print "Phase '"+str(self._idphaseassignments)+"' Added to Database!"
			sharedDB.mySQLConnection.newPhaseAssignmentSignal.emit(str(self._idphaseassignments))
			self._new = 0
		elif self._updated:
			#print self._number+" Updated!"
			self.UpdatePhaseAssignmentInDB()
			self.phaseAssignmentChanged.emit(str(self._idphaseassignments))
			if str(self._idphases) == '16':
				self.project._updated = 1
			print "Phase '"+str(self._idphaseassignments)+"' Updated in Database!"
			self._updated = 0
		
	def SetPhaseValues(self):
		for phase in sharedDB.myPhases:
			if phase._idphases == self._idphases:
				self._name = phase._name
				self._taskPerShot = phase._taskPerShot
				self._iddepartments = phase._iddepartments
				break
		
	def AddPhaseAssignmentToDB(self):
		sharedDB.mySQLConnection.query("INSERT INTO phaseassignments (idprojects, idphases, startdate, enddate, idstatuses, archived, lasteditedbyname, lasteditedbyip, appsessionid, hoursalotted) VALUES ('"+str(self._idprojects)+"', '"+str(self._idphases)+"', '"+str(self._startdate)+"', '"+str(self._enddate)+"', '"+str(self._idstatuses)+"', '"+str(self._archived)+"', '"+str(sharedDB.currentUser._name)+"', '"+str(sharedDB.mySQLConnection.myIP)+"', '"+str(sharedDB.app.sessionId())+"', '"+str(self._hoursalotted)+"');","commit")	
	
		self._idphaseassignments = sharedDB.mySQLConnection._lastInsertId
	
		self.phaseAssignmentAdded.emit(str(self._idphaseassignments))
		
	def UpdatePhaseAssignmentInDB (self):
		sharedDB.mySQLConnection.query("UPDATE phaseassignments SET idprojects = '"+str(self._idprojects)+"', idphases = '"+str(self._idphases)+"', startdate = '"+str(self._startdate)+"', enddate = '"+str(self._enddate)+"', idstatuses = '"+str(self._idstatuses)+"', archived = '"+str(self._archived)+"', lasteditedbyname = '"+str(sharedDB.currentUser._name)+"', lasteditedbyip = '"+str(sharedDB.mySQLConnection.myIP)+"', appsessionid = '"+str(sharedDB.app.sessionId())+"', hoursalotted = '"+str(self._hoursalotted)+"' WHERE idphaseassignments = "+str(self._idphaseassignments)+";","commit")
		#print ("Updating phase in DB: "+str(self._idphaseassignments))
		
		
	def SetValues(self,_idphaseassignments = 0, _idprojects = '', _idphases = 1, _startdate = '', _enddate = '',_idstatuses = 1 ,_archived = 0, _timestamp = '', _hoursalotted = 0):
		print ("Downloaded updated for PhaseAssignment '"+str(self._idphaseassignments)+"'")
		
		self._idphaseassignments             = _idphaseassignments
		self._idprojects                   = _idprojects
		self._idphases         = _idphases
		self._startdate               = _startdate
		self._enddate               = _enddate
		self._idstatuses               = _idstatuses
		self._hoursalotted               = _hoursalotted
		self._archived               = _archived
		self._timestamp                    = _timestamp

		self.phaseAssignmentChanged.emit(str(self._idphaseassignments))
		
	def AddTaskToList(self, task):
		if task._idphaseassignments == self._idphaseassignments:
			self._tasks.append(task)
			return
	def setHoursAlotted(self, sent):
		self._hoursalotted = sent
		self._updated = 1
	
	def hoursAlotted(self):
		return self._hoursalotted
	
	def name(self):
		return self._name
	
	def idstatuses(self):
		return self._idstatuses
	
	def setIdstatuses(self, value):
		self._idstatuses = value
		self._updated = 1

	def endDate(self):
		return self._enddate
	
	def addUserAssignmentTaskItem(self, taskitem):
		self._userAssignments.append(taskitem)
		#print "added user assignment"
		self.userAssigned.emit()
		
	def userAssignmentTaskItems(self):
		return self._userAssignments
	
	def iddepartments(self):
		return self._iddepartments

	def idusers(self):
		ids = []
		for ua in self._userAssignments:
			ids.append(ua.userAssignment()._idusers)
		return ids
		
	
def getPhaseAssignmentByID(sentid):
	for phase in sharedDB.myPhaseAssignments:		
		if str(phase._idphaseassignments) == str(sentid):
			return phase