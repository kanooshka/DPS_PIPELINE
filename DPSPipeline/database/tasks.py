import mysql.connector
import sharedDB
from DPSPipeline.database.connection import Connection


class Task():

	def __init__(self,_idtasks = 0,_parentType = 'Project',_parentId = '0',_tasktype = 'assignment',_assignedUserId = 0,_statusId = 0,_updated=0):
		
		# define custom properties
		self._idtasks           = _idtasks
		self._parentType               = _parentType
		self._parentId    = _parentId
		self._tasktype    = _tasktype
		self._assignedUserId    = _assignedUserId
		self._statusId = _statusId
		
		self._updated = _updated

	def Save(self,timestamp):		
		if self._updated:
			connection = sharedDB.mySQLConnection
			connection.openConnection()
			cnx = connection._cnx
			cursor = connection._cnx.cursor()
			
			updatedBy = socket.gethostbyname(socket.gethostname())
			
			#cnx = mysql.connector.connect(user='root', database='dpstudio', password='poop')
			#cursor = cnx.cursor()
			
			#print (self._name+" Updated!")
			query = "INSERT INTO tasks (idtasks, parentType, parentId, taskType, assignedUserId, statusId, timestamp) VALUES ('"+str(self._idtasks)+"', '"+str(self._parentType)+"', '"+str(self._parentId) +"', '"+str(self._tasktype) +"', '"+str(_assignedUserId)+str(_statusId) + str(timestamp) + "');"
			
			#print query
			
			#connection._cnx.commit()
			
			cursor.execute(query)
			cnx.commit()
			cursor.close()
			#connection.closeConnection()
			cnx.close()
			self._updated = 0
			
	

def GetTasks():
	tasks = []
	
	if not sharedDB.testing:
		connection = sharedDB.mySQLConnection
		connection.openConnection()
		cursor = connection._cnx.cursor()
		query = "SELECT idtasks, parentType, parentId, taskType, assignedUserId, statusId FROM tasks"
		
		cursor.execute(query)
		rows = cursor.fetchall()
		
		for row in rows:
			#print row[0]
			tasks.append(Phases(_idtasks = row[0],_parentType = row[1],_parentId = row[2],_tasktype = row[3],_assignedUserId = row[4],statusId = row[5]))
		cursor.close()
		connection.closeConnection()
	
	else:
		tasks.append(Task(_idtasks = 1,_parentType = 'Project',_parentId = '1',_tasktype = 'Assignment',_assignedUserId = 1,_statusId = 2))
	
	return tasks
