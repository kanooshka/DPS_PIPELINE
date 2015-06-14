from DPSPipeline.database.connection import Connection
import sharedDB

#timestamp
from datetime import datetime

class Sequences():

	def __init__(self,_idsequences = 0,_idprojects = 1 , _number = '010',_idstatus = 0, _shots = [],_updated = 0,_new = 1,_description = '',_timestamp = datetime.now()):
		
		# define custom properties
		self._idsequences             = _idsequences
		self._idprojects	      = _idprojects
		self._number                   = _number
		self._idstatus               = _idstatus
		self._description	     = _description
		self._timestamp		     = _timestamp
		
		self._shots                 = _shots
		self._updated                = _updated
		self._type                   = "sequence"
		self._hidden                 = False
		
		self._new		     = _new
		
		if self._idstatus == 3 or self._idstatus == 5:
			self._hidden = True
			
	def Save(self,timestamp):
		
		self._timestamp = timestamp
		if self._updated:
			if self._new:
				self._new = 0
				
				print self._number+" Added to Database!"
			else:
				#print self._number+" Updated!"
				self.UpdateSequenceInDB()
				
			self._updated = 0
		'''
	def AddSequenceToDB(self):
	
	sharedDB.mySQLConnection.query("INSERT INTO sequences (idprojects, name, idstatuses, due_date, renderWidth, renderHeight, description) VALUES ('"+str(maxidprojects)+"', '"+str(_number)+"', '"+str(1)+"', '"+str(_due_date)+"', '"+str(_renderWidth)+"', '"+str(_renderHeight)+"', '"+str(_description)+"');","commit")

	#connect phases to projectid
	for phase in phases:
		phase._idsequences = maxidprojects

	#Add new project to list
	newProj = Projects(_idsequences = maxidprojects, _number = _number, _folderLocation = '', _idstatus = 1, _fps = _fps,_renderWidth = _renderWidth,_renderHeight = _renderHeight,_due_date = _due_date,_renderPriority = _renderPriority, _description = _description,phases = phases)
	sharedDB.projectList.append(newProj)
	
	sharedDB.projectView.AddProject(project=newProj,phases=phases)
	
	'''
	def UpdateSequenceInDB (self):

		sharedDB.mySQLConnection.query("UPDATE sequences SET number = '"+str(self._number)+"', idstatuses = '"+str(self._idstatus)+"', description = '"+str(self._description)+"', timestamp = '"+str(self._timestamp)+"' WHERE idsequences = "+str(self._idsequences)+";","commit")

	
		


