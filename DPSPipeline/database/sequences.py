from DPSPipeline.database.connection import Connection
import sharedDB
from DPSPipeline.database import shots
#timestamp
from datetime import datetime

from PyQt4 import QtCore
from PyQt4.QtCore import QObject

class Sequences(QObject):

	sequenceChanged = QtCore.pyqtSignal(QtCore.QString)
	sequenceAdded = QtCore.pyqtSignal(QtCore.QString)
	
	def __init__(self,_idsequences = 0,_idprojects = 1 , _number = '010',_idstatuses = 1,_updated = 0,_new = 1,_description = '',_timestamp = datetime.now()):
		
		super(QObject, self).__init__()
		
		# define custom properties
		self._idsequences             = _idsequences
		self._idprojects	      = _idprojects
		self._number                   = _number
		self._idstatuses             = _idstatuses
		self._description	     = _description
		self._timestamp		     = _timestamp
		
		self._shots                 = {}
		self._updated                = _updated
		self._type                   = "sequence"
		self._hidden                 = False
		self._project               = self.GetProjectById()
		
		self._new		     = _new
		self._lastSelectedShotNumber = '-1'
	
	def __eq__(self, another):
		return hasattr(another, '_idsequences') and self._idsequences == another._idsequences
	
	def __hash__(self):
		return hash(self._idsequences)
	
	def id(self):
		return self._idsequences
		
	def Save(self):
		
		if self._new:	
			self.AddSequenceToDB()
			print "Sequence '"+self._number+"' Added to Database!"
			self._new = 0
		elif self._updated:
			#print self._number+" Updated!"
			self.UpdateSequenceInDB()
			print "Sequence '"+self._number+"' Updated in Database!"
			self._updated = 0
	
		for shot in self._shots:
			self._shots[str(shot)].Save()
	
	def AddSequenceToDB(self):
		if isinstance(self._description, QtCore.QString):
			self._description = unicode(self._description.toUtf8(), encoding="UTF-8")
			
		self._description = self._description.replace("\\","/")
		descr = self._description.replace("\'","\'\'")
		
		rows,self._idsequences = sharedDB.mySQLConnection.query("INSERT INTO sequences (number, idprojects, description, idstatuses, lasteditedbyname, lasteditedbyip, appsessionid) VALUES ('"+str(self._number)+"', '"+str(self._idprojects)+"', '"+descr+"', '"+str(self._idstatuses)+"', '"+str(sharedDB.currentUser._name)+"', '"+str(sharedDB.mySQLConnection.myIP)+"', '"+str(sharedDB.app.sessionId())+"');","commit")	
	
		#self._idsequences = sharedDB.mySQLConnection._lastInsertId
	
		sharedDB.mySequences[str(self.id())] = self
	
		self.sequenceAdded.emit(str(self._idsequences))
		
	def UpdateSequenceInDB (self):
		if self._description is None:
			self._description = "None"
		
		if isinstance(self._description, QtCore.QString):
			self._description = unicode(self._description.toUtf8(), encoding="UTF-8")
			
		self._description = self._description.replace("\\","/")
		descr = self._description.replace("\'","\'\'")

		sharedDB.mySQLConnection.query("UPDATE sequences SET number = '"+str(self._number)+"', idstatuses = '"+str(self._idstatuses)+"', description = '"+descr+"', lasteditedbyname = '"+str(sharedDB.currentUser._name)+"', lasteditedbyip = '"+str(sharedDB.mySQLConnection.myIP)+"', appsessionid = '"+str(sharedDB.app.sessionId())+"' WHERE idsequences = "+str(self._idsequences)+";","commit")
		#print ("Updating sequence in DB: "+str(self._idsequences))
	
	def AddShotToSequence(self, newName):
		
		shot = shots.Shots(_idshots = None,_number = newName,_idstatuses = 1,_description = '',_timestamp = None,_new = 1,_idprojects = self._idprojects, _idsequences = self._idsequences, _startframe = 101, _endframe = 101)
		shot.Save()
		
		self._shots[str(shot.id())] = shot
		#sharedDB.myShots.append(shot)
		
		return shot
	
	def SetValues(self,_idsequences = 0, _number = '', _idstatuses = 1, _description = '', _timestamp = ''):
		print ("Downloaded updated for Sequence '"+str(self._number)+"'")
		
		self._idsequences             = _idsequences
		self._number                   = _number
		self._idstatuses         = _idstatuses
		self._description               = _description
		self._timestamp                    = _timestamp

		self.emitSequenceChanged()
	
	
	def GetProjectById(self):
		if str(self._idprojects) in sharedDB.myProjects:
			return sharedDB.myProjects[str(self._idprojects)]
	
	def emitSequenceChanged( self ):
		if ( not self.signalsBlocked() ):
		    self.sequenceChanged.emit(str(self._idsequences))