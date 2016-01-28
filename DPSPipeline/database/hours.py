from DPSPipeline.database.connection import Connection
import sharedDB

#timestamp
from datetime import datetime

from PyQt4 import QtCore
from PyQt4.QtCore import QObject

class Hours(QObject):
	hoursAdded = QtCore.pyqtSignal(QtCore.QString)
	hoursChanged = QtCore.pyqtSignal()	
	
	def __init__(self,_idhours = -1,_idusers = -1,_idphaseassignments = -1,_idprojects = -1, _description = '010',_hours = 0,_date = datetime.now(), _updated = 0,_new = 1,_timestamp = datetime.now()):
		
		super(QObject, self).__init__()
		
		# define custom properties
		self._idhours                = _idhours
		self._idusers		     = _idusers
		self._idphaseassignments     = _idphaseassignments
		self._idprojects	     = _idprojects		
		self._description            = _description
		self._hours	     	     =_hours
		self._date		     =_date
		
		self._timestamp		     = _timestamp
		
		self._user               = self.GetUsersById()
		self._taskButtons            = []
		self._updated                = _updated
		self._type                   = "hours"
		self._hidden                 = False
		
		self._new		     = _new
	
	def __eq__(self, another):
		return hasattr(another, '_idhours') and self._idhours == another._idhours
	
	def __hash__(self):
		return hash(self._idhours)
		
	def id(self):
		return self._idhours
			
	def Save(self):
		if self._new:	
			self.AddHoursToDB()
			print "Hours '"+self._idhours+"' Added to Database!"
			self._new = 0
		elif self._updated:
			self.UpdateHoursInDB()
			print "Hours '"+self._idhours+"' Updated in Database!"
			self._updated = 0
		
	def GetUsersById(self):
		for user in sharedDB.myUsers:
			if user._idusers == self._idusers:
				return user	
	
	def AddHoursToDB(self):
		if isinstance(self._description, QtCore.QString):
			self._description = unicode(self._description.toUtf8(), encoding="UTF-8")
		
		self._description =self._description.replace("\\","/")		
		descr = self._description.replace("\'","\'\'")
	
		sharedDB.mySQLConnection.query("INSERT INTO hours (idusers, idphaseassignments, idprojects, description, hours, date, lasteditedbyname, lasteditedbyip, appsessionid) VALUES ('"+str(self._idusers)+"', '"+str(self._idphaseassignments)+"', '"+str(self._idprojects)+"', '"+str(descr)+"', '"+str(self._hours)+"', '"+str(self._date)+"', '"+descr+"', '"+str(sharedDB.currentUser._name)+"', '"+str(sharedDB.mySQLConnection.myIP)+"', '"+str(sharedDB.app.sessionId())+"');","commit")	
	
		self._idhours = sharedDB.mySQLConnection._lastInsertId
		
		self.hoursAdded.emit(str(self._idhours))
	
	def UpdateHoursInDB (self):	
		if self._description is None:
			self._description = "None"
		
		if isinstance(self._description, QtCore.QString):
			self._description = unicode(self._description.toUtf8(), encoding="UTF-8")		
		
		self._description =self._description.replace("\\","/")
		descr = self._description.replace("\'","\'\'")
		
		#idusers, idphaseassignments, idprojects, description, hours, lasteditedbyname, lasteditedbyip, appsessionid
		
		sharedDB.mySQLConnection.query("UPDATE hours SET idusers = '"+str(self._idusers)+"', idphaseassignments = '"+str(self._idphaseassignments)+"', idprojects = '"+str(self._idprojects)+"', description = '"+descr+"', hours = '"+str(self._hours)+"', date = '"+str(self._date)+"', lasteditedbyname = '"+str(sharedDB.currentUser._name)+"', lasteditedbyip = '"+str(sharedDB.mySQLConnection.myIP)+"', appsessionid = '"+str(sharedDB.app.sessionId())+"' WHERE idhours = "+str(self._idhours)+";","commit")

	def SetValues(self,_idhours = 0,_idusers = 0,_idphaseassignments = 0,_idprojects = 1 , _description = '',_hours = 0, _date = datetime.now(), _timestamp = datetime.now()):
		print ("Downloaded update for Hours '"+str(self._idhours)+"'")
		
		self._idhours                = _idhours
		self._idusers		     = _idusers
		self._idphaseassignments     = _idphaseassignments
		self._idprojects	     = _idprojects		
		self._description            = _description
		self._hours	     	     = _hours
		self._date		     = _date
		self._timestamp		      = _timestamp

		self.emitHoursChanged()
	
	def emitHoursChanged( self ):
		if ( not self.signalsBlocked() ):
		    self.hoursChanged.emit(str(self._idhours))
