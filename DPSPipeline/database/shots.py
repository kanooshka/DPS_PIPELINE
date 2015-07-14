from DPSPipeline.database.connection import Connection
import sharedDB

#timestamp
from datetime import datetime

from PyQt4 import QtCore
from PyQt4.QtCore import QObject

class Shots(QObject):

	shotChanged = QtCore.pyqtSignal(QtCore.QString)

	def __init__(self,_idshots = 0,_idsequences = 0,_idprojects = 1 , _number = '010',_startframe = 100,_endframe = 200,_idstatuses = 0,_updated = 0,_new = 1,_description = '',_timestamp = datetime.now(),_shotnotes = ''):
		
		super(QObject, self).__init__()
		
		# define custom properties
		self._idshots             = _idshots
		self._idprojects	      = _idprojects
		self._idsequences		= _idsequences		
		self._number                   = _number
		self._startframe		=_startframe
		self._endframe			=_endframe
		self._idstatuses             = _idstatuses
		self._description	     = _description
		self._timestamp		     = _timestamp
		self._shotnotes		     = _shotnotes
		
		#self._tasks                 = _tasks
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
		elif self._updated:
			#print self._number+" Updated!"
			self.UpdateShotInDB()
			print "Shot '"+self._number+"' Updated in Database!"
	
		self._new = 0
		self._updated = 0
	
	def AddShotToDB(self):
	
		sharedDB.mySQLConnection.query("INSERT INTO shots (number, startframe, endframe, idsequences, idprojects, description, idstatuses, lasteditedbyname, lasteditedbyip, shotnotes) VALUES ('"+str(self._number)+"', '"+str(self._startframe)+"', '"+str(self._endframe)+"', '"+str(self._idsequences)+"', '"+str(self._idprojects)+"', '"+str(self._description)+"', '"+str(self._idstatuses)+"', '"+str(sharedDB.currentUser[0]._name)+"', '"+str(sharedDB.mySQLConnection.myIP)+"', '"+str(self._shotnotes)+"');","commit")	
	
		self._idshots = sharedDB.mySQLConnection._lastInsertId
	
	def UpdateShotInDB (self):

		sharedDB.mySQLConnection.query("UPDATE shots SET number = '"+str(self._number)+"', startframe = '"+str(self._startframe)+"', endframe = '"+str(self._endframe)+"', idsequences = '"+str(self._idsequences)+"', idstatuses = '"+str(self._idstatuses)+"', description = '"+str(self._description)+"', lasteditedbyname = '"+str(sharedDB.currentUser[0]._name)+"', lasteditedbyip = '"+str(sharedDB.mySQLConnection.myIP)+"', shotnotes = '"+str(self._shotnotes)+"' WHERE idshots = "+str(self._idshots)+";","commit")

	def SetValues(self,_idshots = 0,_idsequences = 0,_idprojects = 1 , _number = '010',_startframe = 100,_endframe = 200,_idstatuses = 0,_description = '',_timestamp = datetime.now(),_shotnotes=''):
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

		
		#update views containing project
		#update calendar view
		#self.UpdateCalendarView()
		self.emitShotChanged()
		#self.UpdateProjectView()
		##if current project changed, update values
		##else just update project list
	
	def emitShotChanged( self ):
		if ( not self.signalsBlocked() ):
		    self.shotChanged.emit(str(self._idshots))
