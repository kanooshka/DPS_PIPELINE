
from DPSPipeline.database.connection import Connection
from DPSPipeline.database import sequences
import sharedDB
#from DPSPipeline.projectview import ProjectView

from projexui import qt

from PyQt4 import QtCore
from PyQt4.QtCore import QObject
#import sys
#timestamp
from datetime import datetime

class Projects(QObject):

	projectChanged = QtCore.pyqtSignal(QtCore.QString)
	
	def __init__(self,_idprojects = 0, _name = '', _folderLocation = '', _idstatuses = 0, _fps = 25,_renderWidth = 1280,_renderHeight = 720,_due_date = '',_renderPriority = 50, _phases = [], _sequences = [],_updated = 0,_new = 1,_description = ''):
		super(QObject, self).__init__()
		
		# define custom properties
		self._idprojects             = _idprojects
		self._name                   = _name
		self._folderLocation         = _folderLocation
		self._idstatuses               = _idstatuses
		self._fps                    = _fps
		self._renderWidth            = _renderWidth
		self._renderHeight           = _renderHeight
		self._due_date               =_due_date
		self._renderPriority         = _renderPriority
		self._description	     = _description
		
		self._updated                = _updated
		#self._loadedChanges	     = 0
		self._type                   = "project"
		self._hidden                 = False
		
		self._phases                 = _phases
		self._sequences              = _sequences
		
		self._new		     = _new
		
		self._lastSelectedSequenceNumber = '-1'
		self._calendarWidgetItem = ''
		
		self.GetSequencesFromProject()
		
		if self._idstatuses == 3 or self._idstatuses == 5:
			self._hidden = True
			
	def Save(self):
		
		if self._updated:
			#print self._name+" Updated in DB!"
			self._updated = 0
			self.UpdateProjectInDB()
			print "Project '"+self._name+"' Updated in Database!"
		elif self._new:
			self._new = 0
			self.AddProjectToDB()
			#print self._name+" Added to Database!"
			print "Project '"+self._name+"' Added to Database!"
		for seq in self._sequences:
			seq.Save()
			
		for phase in self._phases:
			phase.Save()
		
		sharedDB.mySQLConnection.closeConnection()
		
	def GetSequencesFromProject(self):
		self._sequences = []
		
		if not sharedDB.noDB:
			rows = sharedDB.mySQLConnection.query("SELECT idsequences, number, idstatuses, description, timestamp FROM sequences WHERE idprojects = '"+str(self._idprojects)+"'")
			
			for row in rows:
				#print row[0]
				seq = sequences.Sequences(_idsequences = row[0],_number = row[1],_idstatuses = row[2],_description = row[3],_timestamp = row[4],_new = 0,_idprojects = self._idprojects)
				self._sequences.append(seq)
				sharedDB.mySequences.append(seq)
		else:
			self._sequences.append(sequences.Sequences(_idsequences = 1,_idprojects = self._idprojects ,_number = '010',_idstatuses = 1,_description = 'This is the sequence where things go BOOM',_timestamp = datetime.now(),_new = 0))
	
	def AddSequenceToProject(self, newName):
		if not sharedDB.noDB:
			seq = sequences.Sequences(_idsequences = None,_number = newName,_idstatuses = 1,_description = '',_timestamp = None,_new = 1,_idprojects = self._idprojects)
			self._sequences.append(seq)
			sharedDB.mySequences.append(seq)
			#self._sequences[len(self._sequences)-1].Save(datetime.now())
			#sharedDB.mySQLConnection.closeConnection()
	
	
	def UpdateProjectInDB (self):

		sharedDB.mySQLConnection.query("UPDATE projects SET name = '"+str(self._name)+"', folderLocation = '"+str(self._folderLocation).replace("\\", "\\\\")+"', idstatuses = '"+str(self._idstatuses)+"', fps = '"+str(self._fps)+"', renderWidth = '"+str(self._renderWidth)+"', renderHeight = '"+str(self._renderHeight)+"', due_date = '"+str(self._due_date)+"', renderPriority = '"+str(self._renderPriority)+"', description = '"+str(self._description)+"' WHERE idprojects = "+str(self._idprojects)+";","commit")
		#print ("Updating project in DB: "+str(self._idprojects))
	
	def AddProjectToDB (self):
		
		#print ("Adding project to DB: "+str(self._idprojects))

		sharedDB.mySQLConnection.query("INSERT INTO projects (name, idstatuses, due_date, renderWidth, renderHeight, description, fps) VALUES ('"+str(self._name)+"', '"+str(self._idstatuses)+"', '"+str(self._due_date)+"', '"+str(self._renderWidth)+"', '"+str(self._renderHeight)+"', '"+str(self._description)+"', '"+str(self._fps)+"');","commit")
		
		self._idprojects = sharedDB.mySQLConnection._lastInsertId
	
		#connect phases to projectid
		for phase in self._phases:
			phase._idprojects = self._idprojects
			phase._updated = 1
		
		
	
	def SetValues(self,_idprojects , _name = '', _folderLocation = '', _idstatuses = 0, _fps = 25,_renderWidth = 1280,_renderHeight = 720,_due_date = '', _description = '' ):
		print ("Downloaded updated for Project '"+str(self._name)+"'")
		
		self._idprojects             = _idprojects
		self._name                   = _name
		self._folderLocation         = _folderLocation
		self._idstatuses               = _idstatuses
		self._fps                    = _fps
		self._renderWidth            = _renderWidth
		self._renderHeight           = _renderHeight
		self._due_date               =_due_date
		self._description	     = _description
		#self._loadedChanges	     = 1
		
		#update views containing project
		#update calendar view
		#self.UpdateCalendarView()
		self.emitProjectChanged()
		#self.UpdateProjectView()
		##if current project changed, update values
		##else just update project list		
		
		
	#def UpdateCalendarView(self):
	#	self._calendarWidgetItem.setName(self._name)
		
	def setProperty(self,propertyname,value):
		if (propertyname == "Name"):
			if (value != self._name):
				print ("Updating project name to "+value)
				self._name = value
				self._updated = 1
					
	def emitProjectChanged( self ):
		if ( not self.signalsBlocked() ):
		    self.projectChanged.emit(str(self._idprojects))
			
def GetActiveProjects():
	activeProjects = []
	
	if not sharedDB.noDB:
		rows = sharedDB.mySQLConnection.query("SELECT idprojects, name, due_date, idstatuses, renderWidth, renderHeight, description, folderLocation, fps FROM projects WHERE idstatuses != 4")
		
		for row in rows:
			#print row[0]
			activeProjects.append(Projects(_idprojects = row[0],_name = row[1],_due_date = row[2],_idstatuses = row[3],_renderWidth = row[4],_renderHeight = row[5],_description = row[6],_folderLocation = row[7],_fps = row[8],_new = 0))

	else:
		activeProjects.append(Projects(_idprojects = 1,_name = 'TW15-11  Rebel Raw Deal',_idstatuses = 1,_new = 0,_fps = 400,_due_date = datetime.today(),_description = 'Blahty Blahty test test WEEEEEEE!!!'))

	return activeProjects