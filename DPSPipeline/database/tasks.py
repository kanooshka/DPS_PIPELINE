from DPSPipeline.database.connection import Connection
import sharedDB

#timestamp
from datetime import datetime
# idtasks, parenttasksid, idphaseassignments, idprojects, idshots, idusers, idphases, timealotted, idsequences, duedate, percentcomplete, done, timestamp

class Tasks():

	def __init__(self,_idtasks = 1,_parenttasksid = 1,_idphaseassignments = 1 , _idprojects = 1, _idshots = 1, _idusers = 1, _idphases = 1, _timealotted = 0, _idsequences = 1, _duedate = datetime.now(), _percentcomplete = 0, _done = 0, _timestamp = datetime.now(), _updated = 0, _new = 1):
		
		# define custom properties
		self._idtasks                = _idtasks
		self._parenttasksid	     = _parenttasksid
		self._parenttasksid	     = _parenttasksid		
		self._idprojects             = _idprojects
		self._idshots		     =_idshots
		self._idusers		     =_idusers
		self._idphases               = _idphases
		self._timealotted	     = _timealotted
		self._idsequences	     = _idsequences
		self._duedate	       	     = _duedate
		self._percentcomplete	     = _percentcomplete
		self._done	     	     = _done
		self._timestamp		     = _timestamp
		
		#self._tasks                 = _tasks
		self._updated                = _updated
		self._type                   = "task"
		self._hidden                 = False
		
		self._new		     = _new
		
		#if self._idstatuses == 3 or self._idstatuses == 5:
			#self._hidden = True
			
	def Save(self,timestamp):
		
		self._timestamp = timestamp
		if self._new:	
			self.AddTaskToDB()
		
		elif self._updated:
			#print self._number+" Updated!"
			self.UpdateTaskInDB()
	
		self._new = 0
		self._updated = 0
	
	def AddTaskToDB(self):
	
		sharedDB.mySQLConnection.query("INSERT INTO tasks (idtasks, parenttasksid, idphaseassignments, idprojects, idshots, idusers, idphases, timealotted, idsequences, duedate, percentcomplete, done, timestamp) VALUES ('"+str(self._idtasks)+"', '"+str(self._parenttasksid)+"', '"+str(self._idphaseassignments)+"', '"+str(self._idprojects)+"', '"+str(self._idshots)+"', '"+str(self._idusers)+"', '"+str(self._idphases)+"', '"+str(self._timealotted)+"', '"+str(self._idsequences)+"', '"+str(self._duedate)+"', '"+str(self._percentcomplete)+"', '"+str(self._done)+"', '"+str(self._timestamp)+"');","commit")	
	
		self._idtasks = sharedDB.mySQLConnection._lastInsertId
	
	def UpdateShotInDB (self):

		sharedDB.mySQLConnection.query("UPDATE tasks SET parenttasksid = '"+str(self._parenttasksid)+"', idphaseassignments = '"+str(self._idphaseassignments)+"', idprojects = '"+str(self._idprojects)+"', idshots = '"+str(self._idshots)+"', idusers = '"+str(self._idusers)+"', idphases = '"+str(self._idphases)+"', timealotted = '"+str(self._timealotted)+"', idsequences = '"+str(self._idsequences)+"', duedate = '"+str(self._duedate)+"', percentcomplete = '"+str(self._percentcomplete)+"', done = '"+str(self._done)+"', timestamp = '"+str(self._timestamp)+";","commit")

def GetTasks():
	tasks = []
	
	if not sharedDB.noDB:
		rows = sharedDB.mySQLConnection.query("SELECT idtasks, parenttasksid, idphaseassignments, idprojects, idshots, idusers, idphases, timealotted, idsequences, duedate, percentcomplete, done, timestamp FROM tasks")
		
		for row in rows:
			#print row[0]
			tasks.append(Tasks(_idtasks = row[0],_parenttasksid = row[1],_idphaseassignments = row[2],_idprojects = row[3],_idshots = row[4],_idusers = row[5],_idphases = row[6],_timealotted = row[7],_idsequences = row[8],_duedate = row[9],_percentcomplete = row[10],_done = row[11],_timestamp = row[12],_new = 0))

	#else:
		#activeProjects.append(Projects(_idprojects = 1,_name = 'TW15-11  Rebel Raw Deal',_idstatuses = 1,_new = 0,_fps = 400,_due_date = datetime.today(),_description = 'Blahty Blahty test test WEEEEEEE!!!'))

	return tasks
