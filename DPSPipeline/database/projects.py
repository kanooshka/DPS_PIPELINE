
from DPSPipeline.database.connection import Connection
from DPSPipeline.database import temprigs
from DPSPipeline.database import sequences
from DPSPipeline.database import shots
import sharedDB
#from DPSPipeline.projectview import ProjectView

from projexui import qt

from PyQt4 import QtCore,QtGui
from PyQt4.QtCore import QObject
#import sys
#timestamp
from datetime import datetime


class Projects(QObject):

	projectChanged = QtCore.pyqtSignal(QtCore.QString)
	statusChanged = QtCore.pyqtSignal(QtCore.QString)
	projectAdded = QtCore.pyqtSignal(QtCore.QString)
	
	def __init__(self,_idprojects = -1,_idips = -1,_idclients = -1, _name = '', _folderLocation = '', _idstatuses = 1, _fps = 25,_renderWidth = 1280,_renderHeight = 720,_due_date = '',_renderPriority = 50, _updated = 0,_new = 1,_description = '',_budget = 0, _statusDescription = '',_archived = 0):
		super(QObject, self).__init__()
		
		# define custom properties
		self._idprojects             = _idprojects
		self._name                   = _name
		self._folderLocation         = _folderLocation
		self._idstatuses               = _idstatuses
		self._fps                    = _fps
		self._renderWidth            = _renderWidth
		self._renderHeight           = _renderHeight
		#self._startdate	
		self._due_date               =_due_date
		self._renderPriority         = _renderPriority
		self._description	     = _description
		self._statusDescription	     = _statusDescription
		self._idips		     = _idips
		self._idclients		     = _idclients
		self._archived		     = _archived
		self._budget		     = _budget
		
		self._updated                = _updated
		#self._loadedChanges	     = 0
		self._type                   = "project"
		self._hidden                 = False
		
		self._phases                 = {}
		#self._duePhase 		= []
		self._sequences              = {}
		self._images		     = {}
		self._rigs                   = {}
		
		self._new		     = _new
		
		self._lastSelectedSequenceNumber = '-1'
		self._calendarWidgetItem = None
		
		#else:
			#self._phases = sharedDB.phaseAssignments.GetPhaseAssignmentsFromProject(self._idprojects)
		#self.GetSequencesFromProject()
		
		self.UpdateVisibility()
		
		sharedDB.mySQLConnection.firstLoadComplete.connect(self.UpdateStartDate)
		
		if sharedDB.initialLoadComplete:
			self.UpdateStartDate()
		
		#Connect new project to UI elements
		#self.projectAdded.connect(sharedDB.calendarview.AddNewProjects)
	
	def __eq__(self, another):
		return hasattr(another, '_idprojects') and self._idprojects == another._idprojects
	
	def __hash__(self):
		return hash(self._idprojects)
		
	def id(self):
		return self._idprojects
		
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
			self._sequences[str(seq)].Save()
			
		for shot in self._images:
			self._images[str(shot)].Save()
		
			
		for phase in self._phases:
			self._phases[str(phase)].Save()
		
		
		for rig in self._rigs.values():
			rig.Save()
		#sharedDB.mySQLConnection.closeConnection()

	def UpdateStartDate(self):
		plist = self._phases.values()
		if plist:
			d = plist[0]._startdate
			for x in range(1,len(plist)):
				if d > plist[x]._startdate:
					d = plist[x]._startdate
			self._startdate = d

	def AddSequenceToProject(self, newName):

		seq = sequences.Sequences(_idsequences = None,_number = newName,_idstatuses = 1,_description = '',_timestamp = None,_new = 1,_idprojects = self._idprojects)
		seq.Save()
		
		self._sequences[str(seq.id())] = seq
		return seq
	
	def AddRigToProject(self, newName):

		rig = temprigs.TempRigs(_name = newName,_idprojects = self._idprojects,_new = 1)
		rig.Save()
		
		self._rigs[str(rig.id())] = rig
		return rig
	
	def AddShotToProject(self, newName):
		shot = shots.Shots(_idshots = None,_number = newName,_idstatuses = 1,_description = '',_timestamp = None,_new = 1,_idprojects = self._idprojects, _idsequences = 0, _startframe = 101, _endframe = 101)
		shot.Save()
		self._images[str(shot.id())] = shot
		
		return shot
	
	def UpdateProjectInDB (self):		
		if self._description is None:
			self._description = "None"		
		
		if self._statusDescription is None:
			self._statusDescription = ""
		
		if isinstance(self._description, QtCore.QString):
			self._description = unicode(self._description.toUtf8(), encoding="UTF-8")
		
		if isinstance(self._statusDescription, QtCore.QString):
			self._statusDescription = unicode(self._statusDescription.toUtf8(), encoding="UTF-8")
		
		if isinstance(self._name, QtCore.QString):
			self._name = unicode(self._name.toUtf8(), encoding="UTF-8")
		
		self._description = self._description.replace("\\","/")
		self._statusDescription = self._statusDescription.replace("\\","/")
		self._name = self._name.replace("\\","/")
		
		descr = self._description.replace("\'","\'\'")
		statdescr = self._statusDescription.replace("\'","\'\'")
		name = self._name.replace("\'","\'\'")

		self.UpdateVisibility()

		sharedDB.mySQLConnection.query("UPDATE projects SET name = '"+str(name)+"', folderLocation = '"+str(self._folderLocation).replace("\\", "\\\\")+"', idstatuses = '"+str(self._idstatuses)+"', fps = '"+str(self._fps)+"', renderWidth = '"+str(self._renderWidth)+"', renderHeight = '"+str(self._renderHeight)+"', due_date = '"+str(self._due_date)+"', archived = '"+str(self._archived)+"', budget = '"+str(self._budget)+"', renderPriority = '"+str(self._renderPriority)+"', description = '"+descr+"', statusDescription = '"+statdescr+"', idips = '"+str(self._idips)+"', idclients = '"+str(self._idclients)+"', lasteditedbyname = '"+str(sharedDB.currentUser._name)+"', lasteditedbyip = '"+str(sharedDB.mySQLConnection.myIP)+"', appsessionid = '"+str(sharedDB.app.sessionId())+"' WHERE idprojects = '"+str(self._idprojects)+"';","commit")
		#print ("Updating project in DB: "+str(self._idprojects))
	
	def AddProjectToDB (self):
		self.SetDueDate()
		
		if isinstance(self._description, QtCore.QString):
			self._description = unicode(self._description.toUtf8(), encoding="UTF-8")
		
		if isinstance(self._statusDescription, QtCore.QString):
			self._statusDescription = unicode(self._statusDescription.toUtf8(), encoding="UTF-8")
		
		if isinstance(self._name, QtCore.QString):
			self._name = unicode(self._name.toUtf8(), encoding="UTF-8")
			
		self._description = self._description.replace("\\","/")
		self._statusDescription = self._statusDescription.replace("\\","/")
		self._name = self._name.replace("\\","/")
		
		descr = self._description.replace("\'","\'\'")
		statdescr = self._statusDescription.replace("\'","\'\'")
		name = self._name.replace("\'","\'\'")
		#print ("Adding project to DB: "+str(self._idprojects))

		rows,self._idprojects = sharedDB.mySQLConnection.query("INSERT INTO projects (name, idstatuses, due_date, renderWidth, renderHeight, archived, budget, description, statusDescription, fps, idips, idclients, lasteditedbyname, lasteditedbyip, appsessionid) VALUES ('"+name+"', '"+str(self._idstatuses)+"', '"+str(self._due_date)+"', '"+str(self._renderWidth)+"', '"+str(self._renderHeight)+"', '"+str(self._archived)+"', '"+str(self._budget)+"', '"+descr+"', '"+statdescr+"', '"+str(self._fps)+"', '"+str(self._idips)+"', '"+str(self._idclients)+"', '"+str(sharedDB.currentUser._name)+"', '"+str(sharedDB.mySQLConnection.myIP)+"', '"+str(sharedDB.app.sessionId())+"');","commit")
		
		#self._idprojects = sharedDB.mySQLConnection._lastInsertId
	
		sharedDB.myProjects[str(self.id())] = self	
		
		#self.projectAdded.emit(str(self._idprojects))
		
	
	def SetValues(self,_idprojects , _idclients = 1, _idips = 1, _name = '', _folderLocation = '', _idstatuses = 1, _fps = 25,_renderWidth = 1280,_renderHeight = 720,_due_date = '', _description = '', _statusDescription = '', _archived = 0, _budget = 0):
		print ("Downloaded updated for Project '"+str(self._name)+"'")
		
		self._idprojects             = _idprojects
		self._name                   = _name
		self._idips		     = _idips
		self._idclients              = _idclients
		self._folderLocation         = _folderLocation
		self._idstatuses               = _idstatuses
		self._fps                    = _fps
		self._renderWidth            = _renderWidth
		self._renderHeight           = _renderHeight
		self._due_date               =_due_date
		self._description	     = _description
		self._statusDescription	     = _statusDescription
		self._archived		     = _archived
		self._budget		     = _budget
		#self._loadedChanges	     = 1
		
		self.UpdateVisibility()
		
		#update views containing project
		#update calendar view
		#self.UpdateCalendarView()
		self.emitProjectChanged()
		#self.UpdateProjectView()
		##if current project changed, update values
		##else just update project list		
		
	def setIdstatuses(self, value):
		self._idstatuses = value
		self._updated = 1
	
	def UpdateVisibility(self):
		#if self._idstatuses == 4 or self._idstatuses == 5 or self._idstatuses == 6:
		if self._archived:
			self._hidden = True
		else:
			self._hidden = False
	
	#def UpdateCalendarView(self):
	#	self._calendarWidgetItem.setName(self._name)
		
	def SetDueDate(self):
		for phase in self._phases.values():
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
	
	def setStartDate(self,d):
		self._startdate = d
		print d
		self._updated = 1
	
	def AddPhase(self, sentphase):
		sentphase._idprojects = self._idprojects
		sentphase.project = self
		sentphase._new = 1
		sentphase.Save()
		self._phases[str(sentphase.id())] = sentphase
	
	def name(self):
		return self._name
	
	
	def setArchived(self, a):
		msg = QtGui.QMessageBox()
		msg.setIcon(QtGui.QMessageBox.Warning)
	     
		msg.setText("Are you sure you wish to archive this project?")
		msg.setWindowTitle("Are you sure?")
		msg.setStandardButtons(QtGui.QMessageBox.Ok | QtGui.QMessageBox.Cancel)
		#msg.buttonClicked.connect(self.msgbtn)
		     
		retval = msg.exec_()
		
		if retval == QtGui.QMessageBox.Ok:
			#print "value of pressed message box button:", retval		
			self._archived = a
			self.UpdateVisibility()
			self._updated = 1
			self.emitProjectChanged()
		
	
	#def msgbtn(i):
	#	print "Button pressed is:",i.text()
	
	def setBudget(self, budget = 0):
		self._budget = budget
		self._updated = 1
	
	
def getProjectQuery():
	#self._queries.append(["SELECT","projects","SELECT idprojects, name, due_date, idstatuses, renderWidth, renderHeight, description, statusDescription, folderLocation, fps, lasteditedbyname, lasteditedbyip, idclients, idips, appsessionid FROM projects WHERE timestamp > \""+str(sharedDB.lastUpdate)+"\""])			
	pass