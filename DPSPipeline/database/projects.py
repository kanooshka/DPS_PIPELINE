
from DPSPipeline.database.connection import Connection
from DPSPipeline.database import sequences
import sharedDB
#from DPSPipeline.projectview import ProjectView
#from PyQt4 import Qt
#import sys
#timestamp
from datetime import datetime

class Projects():

	def __init__(self,_idprojects = 0, _name = '', _folderLocation = '', _idstatus = 0, _fps = 25,_renderWidth = 1280,_renderHeight = 720,_due_date = '',_renderPriority = 50, _phases = [], _sequences = [],_updated = 0,_new = 1,_description = ''):
		
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
		self._description	     = _description
		
		self._updated                = _updated
		self._type                   = "project"
		self._hidden                 = False
		
		self._phases                 = _phases
		self._sequences              = _sequences
		
		self._new		     = _new
		
		self._lastSelectedSequenceNumber = '-1'
		
		self.GetSequencesFromProject()
		
		if self._idstatus == 3 or self._idstatus == 5:
			self._hidden = True
			
	def Save(self,timestamp):
		
		if self._updated:
			if self._new:
				self._new = 0
				
				print self._name+" Added to Database!"
			else:
				#print self._name+" Updated!"
				self.UpdateProject()
				
			self._updated = 0
			
		for seq in self._sequences:
			seq.Save(timestamp)
		
	def GetSequencesFromProject(self):
		self._sequences = []
		
		if not sharedDB.noDB:
			rows = sharedDB.mySQLConnection.query("SELECT idsequences, number, idstatuses, description, timestamp FROM sequences WHERE idprojects = '"+str(self._idprojects)+"'")
			
			for row in rows:
				#print row[0]
				self._sequences.append(sequences.Sequences(_idsequences = row[0],_number = row[1],_idstatus = row[2],_description = row[3],_timestamp = row[4],_new = 0,_idprojects = self._idprojects))
	
		else:
			self._sequences.append(sequences.Sequences(_idsequences = 1,_idprojects = self._idprojects ,_number = '010',_idstatus = 1,_description = 'This is the sequence where things go BOOM',_timestamp = datetime.now(),_new = 0))
	
	def UpdateProject (self):

		sharedDB.mySQLConnection.query("UPDATE projects SET name = '"+str(self._name)+"', folderLocation = '"+str(self._folderLocation)+"', idstatuses = '"+str(self._idstatus)+"', fps = '"+str(self._fps)+"', renderWidth = '"+str(self._renderWidth)+"', renderHeight = '"+str(self._renderHeight)+"', due_date = '"+str(self._due_date)+"', renderPriority = '"+str(self._renderPriority)+"', description = '"+str(self._description)+"' WHERE idprojects = "+str(self._idprojects)+";","commit")

		
def GetActiveProjects():
	activeProjects = []
	
	if not sharedDB.noDB:
		rows = sharedDB.mySQLConnection.query("SELECT idprojects, name, due_date, idstatuses, renderWidth, renderHeight, description FROM projects WHERE idstatuses != 4")
		
		for row in rows:
			#print row[0]
			activeProjects.append(Projects(_idprojects = row[0],_name = row[1],_due_date = row[2],_idstatus = row[3],_renderWidth = row[4],_renderHeight = row[5],_description = row[6],_new = 0))

	else:
		activeProjects.append(Projects(_idprojects = 1,_name = 'TW15-11  Rebel Raw Deal',_idstatus = 1,_new = 0,_fps = 400,_due_date = datetime.today(),_description = 'Blahty Blahty test test WEEEEEEE!!!'))

	return activeProjects

def AddProject(_name = '', _folderLocation = '', _idstatus = 0, _fps = 25,_renderWidth = 1280,_renderHeight = 720,_due_date = '',_renderPriority = 50,_description = '', phases = []):
	
	sharedDB.mySQLConnection.query("INSERT INTO projects (name, idstatuses, due_date, renderWidth, renderHeight, description) VALUES ('"+str(_name)+"', '"+str(1)+"', '"+str(_due_date)+"', '"+str(_renderWidth)+"', '"+str(_renderHeight)+"', '"+str(_description)+"');","commit")

	projectid = sharedDB.mySQLConnection._lastInsertId
	
	#connect phases to projectid
	for phase in phases:
		phase._idprojects = projectid

	#Add new project to list
	newProj = Projects(_idprojects = projectid, _name = _name, _folderLocation = '', _idstatus = 1, _fps = _fps,_renderWidth = _renderWidth,_renderHeight = _renderHeight,_due_date = _due_date,_renderPriority = _renderPriority, _description = _description,_phases = phases)
	sharedDB.projectList.append(newProj)
	
	sharedDB.calendarview.AddProject(project=newProj,phases=phases)
