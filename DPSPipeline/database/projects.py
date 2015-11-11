
from DPSPipeline.database.connection import Connection
from DPSPipeline.database import sequences
from DPSPipeline.database import shots
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
	#projectAdded = QtCore.pyqtSignal(QtCore.QString)
	
	def __init__(self,_idprojects = -1,_idips = -1,_idclients = -1, _name = '', _folderLocation = '', _idstatuses = 1, _fps = 25,_renderWidth = 1280,_renderHeight = 720,_due_date = '',_renderPriority = 50, _updated = 0,_new = 1,_description = ''):
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
		self._idips		     = _idips
		self._idclients		     = _idclients
		
		self._updated                = _updated
		#self._loadedChanges	     = 0
		self._type                   = "project"
		self._hidden                 = False
		
		self._phases                 = []
		#self._duePhase 		= []
		self._sequences              = []
		self._images		     = []
		
		self._new		     = _new
		
		self._lastSelectedSequenceNumber = '-1'
		self._calendarWidgetItem = None
		
		#else:
			#self._phases = sharedDB.phaseAssignments.GetPhaseAssignmentsFromProject(self._idprojects)
		#self.GetSequencesFromProject()
		
		if self._idstatuses == 4 or self._idstatuses == 5 or self._idstatuses == 6:
			self._hidden = True
			
		#self.projectAdded.emit(str(self._idprojects))
			
	def Save(self):
		
		#print self._name
		if self._updated:
			#print self._name+" Updated in DB!"			
			self.SetDueDate()
			self.UpdateProjectInDB()
			self._updated = 0
			print "Project '"+self._name+"' Updated in Database!"		
		
		if self._new:
			self.AddProjectToDB()
			self._new = 0			
			self.SetDueDate()			
			sharedDB.mySQLConnection.newProjectSignal.emit(str(self._idprojects))
			print "Project '"+self._name+"' Added to Database!"
		'''elif self._new:			
			self.AddProjectToDB()
			self._new = 0
			print "Project '"+self._name+"' Added to Database!"'''
		for seq in self._sequences:
			seq.Save()
			
		for shot in self._images:
			shot.Save()
		
			
		for phase in self._phases:
			phase.Save()
		
		#sharedDB.mySQLConnection.closeConnection()

	def AddSequenceToProject(self, newName):

		seq = sequences.Sequences(_idsequences = None,_number = newName,_idstatuses = 1,_description = '',_timestamp = None,_new = 1,_idprojects = self._idprojects)
		self._sequences.append(seq)
		sharedDB.mySequences.append(seq)
		return seq
	
	def AddShotToProject(self, newName):
		shot = shots.Shots(_idshots = None,_number = newName,_idstatuses = 1,_description = '',_timestamp = None,_new = 1,_idprojects = self._idprojects, _idsequences = 0, _startframe = 101, _endframe = 101)
		self._images.append(shot)
		sharedDB.myShots.append(shot)
		
		return shot
	
	def UpdateProjectInDB (self):		
		if self._description is None:
			self._description = "None"		
		
		if isinstance(self._description, QtCore.QString):
			self._description = unicode(self._description.toUtf8(), encoding="UTF-8")
		
		if isinstance(self._name, QtCore.QString):
			self._name = unicode(self._name.toUtf8(), encoding="UTF-8")
		
		self._description = self._description.replace("\\","/")
		self._name = self._name.replace("\\","/")
		
		descr = self._description.replace("\'","\'\'")
		name = self._name.replace("\'","\'\'")

		sharedDB.mySQLConnection.query("UPDATE projects SET name = '"+str(name)+"', folderLocation = '"+str(self._folderLocation).replace("\\", "\\\\")+"', idstatuses = '"+str(self._idstatuses)+"', fps = '"+str(self._fps)+"', renderWidth = '"+str(self._renderWidth)+"', renderHeight = '"+str(self._renderHeight)+"', due_date = '"+str(self._due_date)+"', renderPriority = '"+str(self._renderPriority)+"', description = '"+descr+"', idips = '"+str(self._idips)+"', idclients = '"+str(self._idclients)+"', lasteditedbyname = '"+str(sharedDB.currentUser._name)+"', lasteditedbyip = '"+str(sharedDB.mySQLConnection.myIP)+"', appsessionid = '"+str(sharedDB.app.sessionId())+"' WHERE idprojects = '"+str(self._idprojects)+"';","commit")
		#print ("Updating project in DB: "+str(self._idprojects))
	
	def AddProjectToDB (self):
		self.SetDueDate()
		
		if isinstance(self._description, QtCore.QString):
			self._description = unicode(self._description.toUtf8(), encoding="UTF-8")
		
		if isinstance(self._name, QtCore.QString):
			self._name = unicode(self._name.toUtf8(), encoding="UTF-8")
			
		self._description = self._description.replace("\\","/")
		self._name = self._name.replace("\\","/")
		
		descr = self._description.replace("\'","\'\'")
		name = self._name.replace("\'","\'\'")
		#print ("Adding project to DB: "+str(self._idprojects))

		sharedDB.mySQLConnection.query("INSERT INTO projects (name, idstatuses, due_date, renderWidth, renderHeight, description, fps, idips, idclients, lasteditedbyname, lasteditedbyip, appsessionid) VALUES ('"+name+"', '"+str(self._idstatuses)+"', '"+str(self._due_date)+"', '"+str(self._renderWidth)+"', '"+str(self._renderHeight)+"', '"+descr+"', '"+str(self._fps)+"', '"+str(self._idips)+"', '"+str(self._idclients)+"', '"+str(sharedDB.currentUser._name)+"', '"+str(sharedDB.mySQLConnection.myIP)+"', '"+str(sharedDB.app.sessionId())+"');","commit")
		
		self._idprojects = sharedDB.mySQLConnection._lastInsertId
	
		#connect phases to projectid
		for phase in self._phases:
			phase._idprojects = self._idprojects
			phase._new = 1
			
		
		
	
	def SetValues(self,_idprojects , _name = '', _folderLocation = '', _idstatuses = 1, _fps = 25,_renderWidth = 1280,_renderHeight = 720,_due_date = '', _description = '' ):
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
		
		if self._idstatuses == 3 or self._idstatuses == 4 or self._idstatuses == 5:
			self._hidden = True
		else:
			self._hidden = False
		
		#update views containing project
		#update calendar view
		#self.UpdateCalendarView()
		self.emitProjectChanged()
		#self.UpdateProjectView()
		##if current project changed, update values
		##else just update project list		
		
		
	#def UpdateCalendarView(self):
	#	self._calendarWidgetItem.setName(self._name)
		
	def SetDueDate(self):
		for phase in self._phases:
			#print phase._idphases
			if str(phase._idphases) == "16":
				self._due_date = phase._enddate
				print self._due_date
				break
	
	def setProperty(self,propertyname,value):
		if (propertyname == "Name"):
			if (value != self._name):
				print ("Updating project name to "+value)
				self._name = value
				self._updated = 1
					
	def emitProjectChanged( self ):
		if ( not self.signalsBlocked() ):
		    self.projectChanged.emit(str(self._idprojects))
		    
	def getPhaseAssignmentByIDPhases(self, idrequest):
		for phase in phases:
			if phase._idphases == idrequest:
				return phase
			
		return 0