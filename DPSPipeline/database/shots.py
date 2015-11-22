from DPSPipeline.database.connection import Connection
import sharedDB

#timestamp
from datetime import datetime

from PyQt4 import QtCore
from PyQt4.QtCore import QObject

class Shots(QObject):
	shotAdded = QtCore.pyqtSignal(QtCore.QString)
	shotChanged = QtCore.pyqtSignal()
	startFrameChanged = QtCore.pyqtSignal()
	endFrameChanged = QtCore.pyqtSignal()
	descriptionChanged = QtCore.pyqtSignal()
	
	
	def __init__(self,_idshots = -1,_idsequences = -1,_idprojects = -1, _number = '010',_startframe = 100,_endframe = 200,_idstatuses = 1,_updated = 0,_new = 1,_description = '',_timestamp = datetime.now(),_shotnotes = '',_tasks=None):
		
		super(QObject, self).__init__()
		
		# define custom properties
		self._idshots                = _idshots
		self._idprojects	     = _idprojects
		self._idsequences	     = _idsequences		
		self._number                 = _number
		self._startframe	     =_startframe
		self._endframe		     =_endframe
		self._idstatuses             = _idstatuses
		self._description	     = _description
		self._timestamp		     = _timestamp
		self._shotnotes		     = _shotnotes
		
		self._sequence               = self.GetSequenceById()
		self._project		     = self.GetProjectById()
		self._tasks                  = _tasks
		self._taskButtons            = []
		self._updated                = _updated
		self._type                   = "shot"
		self._hidden                 = False
		
		self._new		     = _new
		
		#if self._idstatuses == 3 or self._idstatuses == 5:
			#self._hidden = True
			
	def Save(self):
		if self._new:	
			self.AddShotToDB()
			print "Shot '"+self._number+"' Added to Database!"
			self._new = 0
		elif self._updated:
			#print self._number+" Updated!"
			self.UpdateShotInDB()
			print "Shot '"+self._number+"' Updated in Database!"
			self._updated = 0

		if self._tasks is not None:
			for task in self._tasks:
				task.Save()
		
	def GetSequenceById(self):
		for seq in sharedDB.mySequences:
			if seq._idsequences == self._idsequences:
				return seq
			
	def GetProjectById(self):
		for proj in sharedDB.myProjects:
			if proj._idprojects == self._idprojects:
				return proj
	
	def AddShotToDB(self):
		if isinstance(self._description, QtCore.QString):
			self._description = unicode(self._description.toUtf8(), encoding="UTF-8")
		
		self._description =self._description.replace("\\","/")		
		descr = self._description.replace("\'","\'\'")
		
		if isinstance(self._shotnotes, QtCore.QString):
			self._shotnotes = unicode(self._shotnotes.toUtf8(), encoding="UTF-8")
			
		notes = self._shotnotes.replace("\'","\'\'")
		
		#descr = descr.replace("\"","\"\"")
	
		sharedDB.mySQLConnection.query("INSERT INTO shots (number, startframe, endframe, idsequences, idprojects, description, idstatuses, lasteditedbyname, lasteditedbyip, shotnotes, appsessionid) VALUES ('"+str(self._number)+"', '"+str(self._startframe)+"', '"+str(self._endframe)+"', '"+str(self._idsequences)+"', '"+str(self._idprojects)+"', '"+descr+"', '"+str(self._idstatuses)+"', '"+str(sharedDB.currentUser._name)+"', '"+str(sharedDB.mySQLConnection.myIP)+"', '"+notes+"', '"+str(sharedDB.app.sessionId())+"');","commit")	
	
		self._idshots = sharedDB.mySQLConnection._lastInsertId
		
		self.shotAdded.emit(str(self._idshots))
	
	def UpdateShotInDB (self):	
		if self._description is None:
			self._description = "None"
		
		if isinstance(self._description, QtCore.QString):
			self._description = unicode(self._description.toUtf8(), encoding="UTF-8")		
		
		self._description =self._description.replace("\\","/")
		descr = self._description.replace("\'","\'\'")
		
		if isinstance(self._shotnotes, QtCore.QString):
			self._shotnotes = unicode(self._shotnotes.toUtf8(), encoding="UTF-8")
			
		notes = self._shotnotes.replace("\'","\'\'")
		
		sharedDB.mySQLConnection.query("UPDATE shots SET number = '"+str(self._number)+"', startframe = '"+str(self._startframe)+"', endframe = '"+str(self._endframe)+"', idsequences = '"+str(self._idsequences)+"', idstatuses = '"+str(self._idstatuses)+"', description = '"+descr+"', lasteditedbyname = '"+str(sharedDB.currentUser._name)+"', lasteditedbyip = '"+str(sharedDB.mySQLConnection.myIP)+"', shotnotes = '"+notes+"', appsessionid = '"+str(sharedDB.app.sessionId())+"' WHERE idshots = "+str(self._idshots)+";","commit")

	def SetValues(self,_idshots = 0,_idsequences = 0,_idprojects = 1 , _number = '010',_startframe = 100,_endframe = 200,_idstatuses = 1,_description = '',_timestamp = datetime.now(),_shotnotes=''):
		print ("Downloaded updated for Shot '"+str(self._number)+"'")
		
		self._idshots                 = _idshots
		self._idprojects	      = _idprojects
		self._idsequences	      = _idsequences		
		self._number                  = _number
		self._startframe	      = _startframe
		self._endframe		      = _endframe
		self._idstatuses              = _idstatuses		
		self._description	      = _description
		self._shotnotes	              = _shotnotes
		self._timestamp		      = _timestamp

		self.shotChanged.emit()

	def AddTaskToList(self, task):
		if str(self._idshots) == str(task._idshots):			
			###add to shot's task list
			if self._tasks is not None:
				self._tasks.append(task)
			else:
				self._tasks = [task]
	
	
	def emitShotChanged( self ):
		if ( not self.signalsBlocked() ):
		    self.shotChanged.emit(str(self._idshots))
