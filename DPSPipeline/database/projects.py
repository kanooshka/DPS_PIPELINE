from DPSPipeline.database.connection import Connection
import sharedDB
from DPSPipeline.ganttTest import GanttTest
#from PyQt4 import Qt
#import sys
#timestamp
'''from datetime import datetime
source.date = datetime.now()
'''
class Projects():

	def __init__(self,_idprojects = 0, _name = '', _folderLocation = '', _idstatus = 0, _fps = 25,_renderWidth = 1280,_renderHeight = 720,_due_date = '',_renderPriority = 50, phases = [],_updated = 0):
		
		# define custom properties
		self._idprojects             = _idprojects
		self._name                   = _name
		self._folderLocation         = _folderLocation
		self._idstatus               = _idstatus
		self._fps                    = _fps
		self._renderWidth            = _renderWidth
		self._renderHeight           = _renderHeight
		self._due_date               =_due_date
		self._renderPriority         = _renderPriority
		self._phases                 = phases
		self._updated                = _updated
		self._type                   = "project"
	
	def Save(self,timestamp):
		
		if self._updated:
			print self._name+" Updated!"
		
		
def GetActiveProjects():
	activeProjects = []
	connection = Connection()
	connection.openConnection()
	cursor = connection._cnx.cursor()
	query = ("SELECT idprojects, name, due_date FROM projects WHERE idstatuses != 4")            
	cursor.execute(query)
	rows = cursor.fetchall()
	
	for row in rows:
		#print row[0]
		activeProjects.append(Projects(_idprojects = row[0],_name = row[1],_due_date = row[2]))
	cursor.close()
	connection.closeConnection()
	
	return activeProjects

def AddProject(_name = '', _folderLocation = '', _idstatus = 0, _fps = 25,_renderWidth = 1280,_renderHeight = 720,_due_date = '',_renderPriority = 50, phases = []):
	#print (_name+" Updated!")
	maxidprojects = QueryLatestID()
	
	connection = Connection()
	connection.openConnection()
	cnx = connection._cnx
	cursor = connection._cnx.cursor()
	
	query = "INSERT INTO projects (idprojects, name, idstatuses, due_date) VALUES ('"+str(maxidprojects)+"', '"+str(_name)+"', '"+str(1)+"', '"+str(_due_date)+"');"
	
	#print query
	
	
	cursor.execute(query)
	cnx.commit()
	connection.closeConnection()
	cnx.close()

	#connect phases to projectid
	for phase in phases:
		phase._idprojects = maxidprojects

	#Add new project to list
	newProj = Projects(_idprojects = maxidprojects, _name = _name, _folderLocation = '', _idstatus = 1, _fps = _fps,_renderWidth = _renderWidth,_renderHeight = _renderHeight,_due_date = _due_date,_renderPriority = _renderPriority, phases = phases)
	sharedDB.projectList.append(newProj)
	
	sharedDB.GanttTest.AddProject(project=newProj,phases=phases)	
		
def QueryLatestID():
	connection = Connection()
	connection.openConnection()
	cnx = connection._cnx
	cursor = connection._cnx.cursor()
	
	query = "SELECT MAX(idprojects) FROM projects;"
	cursor.execute(query)
	rows = cursor.fetchall()
	
	for row in rows:
		maxidprojects = row[0]+1
	
	connection.closeConnection()
	cnx.close()
	return maxidprojects
