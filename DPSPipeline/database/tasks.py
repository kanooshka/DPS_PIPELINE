from DPSPipeline.database.connection import Connection
import sharedDB

#timestamp
from datetime import datetime

from PyQt4 import QtCore
from PyQt4.QtCore import QObject

class Tasks(QObject):

	taskChanged = QtCore.pyqtSignal(QtCore.QString)
	taskAdded = QtCore.pyqtSignal(QtCore.QString)
	
	def __init__(self,_idtasks = 0, _idphaseassignments = 0, _idprojects = 0, _idshots = 0, _idusers = 0, _idphases = 0, _timealotted = 0, _idsequences = 0, _duedate = datetime.now(), _percentcomplete = 0, _done = 0, _status = 0,_parenttaskid = None,_timestamp = datetime.now(), _updated = 0, _new = 0):
		
		super(QObject, self).__init__()
		
		# define custom properties
		self._idtasks                = _idtasks
		self._idphaseassignments     = _idphaseassignments
		self._idprojects	     = _idprojects		
		self._idshots                = _idshots
		self._idusers		     = _idusers
		self._idphases		     = _idphases
		self._timealotted            = _timealotted
		self._idsequences	     = _idsequences
		self._duedate		     = _duedate
		self._percentcomplete	     = _percentcomplete
		self._done		     = _done
		self._status		     = _status
		self._timestamp		     = _timestamp
		self._parenttaskid	     = _parenttaskid
		self._updated		     = _updated
		self._new		     = _new

		self._type                   = "task"
		self._hidden                 = False
		
		self._new		     = _new
		
		if self._new:
			if str(self._idphases) in sharedDB.myPhases:				
				self._status = sharedDB.myPhases[str(self._idphases)]._defaultTaskStatus

		
		self.statusButton	= ''
		self.phaseAssignment = ''
		self.projects = ''

		#self.user = sharedDB.users.getUserByID(self._idusers)
		if str(self._idusers) in sharedDB.myUsers:
			self.user = sharedDB.myUsers[str(self._idusers)]
		else:
			self.user = None
		self.childTasks = {}

		#if self._idstatuses == 3 or self._idstatuses == 5:
			#self._hidden = True
			
	def __eq__(self, another):
		return hasattr(another, '_idtasks') and self._idtasks == another._idtasks
	
	def __hash__(self):
		return hash(self._idtasks)
	
	def id(self):
		return self._idtasks
	
	def Save(self):

		if self._new:	
			self.AddTaskToDB()
			print "Task '"+str(self._idtasks)+"' Added to Database!"
			self._new = 0
		elif self._updated:
			#print self._number+" Updated!"
			self.UpdateTaskInDB()
			print "Task '"+str(self._idtasks)+"' Updated in Database!"
			self._updated = 0		
	
	def AddTaskToDB(self):
	
		sharedDB.mySQLConnection.query("INSERT INTO tasks (idphaseassignments, idprojects, idshots, idusers, idphases, timealotted, idsequences, duedate, percentcomplete, done, status, lasteditedbyname, lasteditedbyip, appsessionid) VALUES ('"+str(self._idphaseassignments)+"', '"+str(self._idprojects)+"', '"+str(self._idshots)+"', '"+str(self._idusers)+"', '"+str(self._idphases)+"', '"+str(self._timealotted)+"', '"+str(self._idsequences)+"', '"+str(self._duedate)+"', '"+str(self._percentcomplete)+"', '"+str(self._done)+"', '"+str(self._status)+"', '"+str(sharedDB.currentUser._name)+"', '"+str(sharedDB.mySQLConnection.myIP)+"', '"+str(sharedDB.app.sessionId())+"');","commit")	
	
		self._idtasks = sharedDB.mySQLConnection._lastInsertId
		
		sharedDB.myTasks.append(self)
		self.taskAdded.emit(str(self._idtasks))
	
	def UpdateTaskInDB (self):
		
		sharedDB.mySQLConnection.query("UPDATE tasks SET idphaseassignments = '"+str(self._idphaseassignments)+"', idprojects = '"+str(self._idprojects)+"', idshots = '"+str(self._idshots)+"', idusers = '"+str(self._idusers)+"', idphases = '"+str(self._idphases)+"', timealotted = '"+str(self._timealotted)+"', idsequences = '"+str(self._idsequences)+"', duedate = '"+str(self._duedate)+"', percentcomplete = '"+str(self._percentcomplete)+"', done = '"+str(self._done)+"', status = '"+str(self._status)+"', lasteditedbyname = '"+str(sharedDB.currentUser._name)+"', lasteditedbyip = '"+str(sharedDB.mySQLConnection.myIP)+"', appsessionid = '"+str(sharedDB.app.sessionId())+"' WHERE idtasks = "+str(self._idtasks)+";","commit")

	def SetValues(self,_idtasks = 0, _idphaseassignments = 0, _idprojects = 0, _idshots = 0, _idusers = 0, _idphases = 0, _timealotted = 0, _idsequences = 0, _duedate = datetime.now(), _percentcomplete = 0, _done = 0, _status = 0, _timestamp = datetime.now()):
		print ("Downloaded updated for Task '"+str(self._idtasks)+"'")
		
		self._idtasks             = _idtasks
		self._idphaseassignments	      = _idphaseassignments
		self._idprojects		= _idprojects		
		self._idshots                   = _idshots
		self._idusers		=_idusers
		self._idphases			=_idphases
		self._timealotted             = _timealotted
		self._idsequences	     = _idsequences
		self._duedate		     = _duedate
		self._percentcomplete		     = _percentcomplete
		self._done		     = _done
		self._status		     = _status
		self._timestamp		     = _timestamp
		
		#update views containing project
		#update calendar view
		#self.UpdateCalendarView()
		self.emitTaskChanged()
		#self.UpdateProjectView()
		##if current project changed, update values
		##else just update project list
	
	def setStatus(self,newStatus):
		#print "TASK STATUS CHANGED"
		self._status = newStatus
		self._updated = 1
	
	def setUserId(self, newid):
		self._idusers = newid
		self._updated = 1
	
	def emitTaskChanged( self ):
		if ( not self.signalsBlocked() ):
		    self.taskChanged.emit(str(self._idtasks))
	
	'''
	def AddTaskToList(self, task):
		if str(self._idtasks) == str(task._parenttaskid):			
			self.childTasks.append(task)
	'''		
