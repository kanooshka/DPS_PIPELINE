from DPSPipeline.database.connection import Connection
import sharedDB
from DPSPipeline.projectview import ProjectView
#from PyQt4 import Qt
#import sys
#timestamp
'''from datetime import datetime
source.date = datetime.now()
'''
class Projects():

	def __init__(self,_idprojects = 0, _name = '', _folderLocation = '', _idstatus = 0, _fps = 25,_renderWidth = 1280,_renderHeight = 720,_due_date = '',_renderPriority = 50, phases = [],_updated = 0,_new = 1):
		
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
		self._hidden                 = False
		
		self._new		     = 1
		
		if self._idstatus == 3 or self._idstatus == 5:
			self._hidden = True
			
	def Save(self,timestamp):
		
		if self._updated:
			if self._new:
				self._new = 0
				
				print self._name+" Added to Database!"
			else:
				print self._name+" Updated!"
		
		
def GetActiveProjects():
	activeProjects = []
	
	if not sharedDB.testing:
		rows = sharedDB.mySQLConnection.query("SELECT idprojects, name, due_date, idstatuses FROM projects WHERE idstatuses != 4")
		
		for row in rows:
			#print row[0]
			activeProjects.append(Projects(_idprojects = row[0],_name = row[1],_due_date = row[2],_idstatus = row[3],_new = 0))

	else:
		activeProjects.append(Projects(_idprojects = 1,_name = 'TW15-11  Rebel Raw Deal',_idstatus = 1,_new = 0))

	return activeProjects

def AddProject(_name = '', _folderLocation = '', _idstatus = 0, _fps = 25,_renderWidth = 1280,_renderHeight = 720,_due_date = '',_renderPriority = 50, phases = []):
	#print (_name+" Updated!")
	maxidprojects = QueryLatestID()
	
	sharedDB.mySQLConnection.query("INSERT INTO projects (idprojects, name, idstatuses, due_date) VALUES ('"+str(maxidprojects)+"', '"+str(_name)+"', '"+str(1)+"', '"+str(_due_date)+"');","commit")
	#query = "INSERT INTO projects (idprojects, name, idstatuses, due_date) VALUES ('"+str(maxidprojects)+"', '"+str(_name)+"', '"+str(1)+"', '"+str(_due_date)+"');"
	
	#print query

	#connect phases to projectid
	for phase in phases:
		phase._idprojects = maxidprojects

	#Add new project to list
	newProj = Projects(_idprojects = maxidprojects, _name = _name, _folderLocation = '', _idstatus = 1, _fps = _fps,_renderWidth = _renderWidth,_renderHeight = _renderHeight,_due_date = _due_date,_renderPriority = _renderPriority, phases = phases)
	sharedDB.projectList.append(newProj)
	
	sharedDB.projectView.AddProject(project=newProj,phases=phases)	
		
def QueryLatestID():
	rows = sharedDB.mySQLConnection.query("SELECT MAX(idprojects) FROM projects;")

	for row in rows:
		if (type(row[0])) is int:
			maxidprojects = row[0]+1
		else:
			maxidprojects = 1;
	
	return maxidprojects

