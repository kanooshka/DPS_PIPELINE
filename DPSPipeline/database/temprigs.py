from DPSPipeline.database.connection import Connection
import sharedDB

#timestamp
from datetime import datetime

from PyQt4 import QtCore
from PyQt4.QtCore import QObject

class TempRigs(QObject):
	rigAdded = QtCore.pyqtSignal(QtCore.QString)
	rigChanged = QtCore.pyqtSignal()
	descriptionChanged = QtCore.pyqtSignal()	
	
	def __init__(self,_idtemprigs = -1,_idprojects = -1, _name = '',_setnumber = 0,_typ = 0,_status = 0,_description = '', _folderLocation = '',_updated = 0,_new = 1,_timestamp = datetime.now()):
		
		super(QObject, self).__init__()
		
		# define custom properties
		self._idtemprigs                = _idtemprigs
		self._idprojects	     = _idprojects
	
		self._name                 = _name
		self._setnumber	     =_setnumber
		self._typ		     =_typ
		
		self._status             = _status
		self._description	     = _description
		self._folderLocation         = _folderLocation
		
		self._timestamp		     = _timestamp
		
		self._updated                = _updated
		self._type                   = "temprigs"
		self._hidden                 = False
		
		self._new		     = _new
		
	def __eq__(self, another):
		return hasattr(another, '_idtemprigs') and self._idtemprigs == another._idtemprigs
	
	def __hash__(self):
		return hash(self._idtemprigs)
		
	def id(self):
		return self._idtemprigs
			
	def Save(self):
		if self._new:	
			self.AddRigToDB()
			print "Rig '"+self._name+"' Added to Database!"
			self._new = 0
		elif self._updated:
			#print self._name+" Updated!"
			self.UpdateRigInDB()
			print "Rig '"+self._name+"' Updated in Database!"
			self._updated = 0
			
	
	def AddRigToDB(self):
		if isinstance(self._description, QtCore.QString):
			self._description = unicode(self._description.toUtf8(), encoding="UTF-8")
		
		self._description =self._description.replace("\\","/")		
		descr = self._description.replace("\'","\'\'")
		
				
		#descr = descr.replace("\"","\"\"")
	
		sharedDB.mySQLConnection.query("INSERT INTO temprigs (idprojects, name, setNumber, type, status, description, folderlocation, lasteditedbyname, lasteditedbyip, appsessionid) VALUES ('"+str(self._idprojects)+"', '"+str(self._name)+"', '"+str(self._setnumber)+"', '"+str(self._typ)+"', '"+str(self._status)+"', '"+descr+"', '"+str(self._folderLocation)+"', '"+str(sharedDB.currentUser._name)+"', '"+str(sharedDB.mySQLConnection.myIP)+"', '"+str(sharedDB.app.sessionId())+"');","commit")	
	
		self._idtemprigs = sharedDB.mySQLConnection._lastInsertId
		
		sharedDB.myTempRigs[str(self.id())] = self
		
		self.rigAdded.emit(str(self._idtemprigs))
	
	def UpdateRigInDB (self):	
		if self._description is None:
			self._description = "None"
		
		if isinstance(self._description, QtCore.QString):
			self._description = unicode(self._description.toUtf8(), encoding="UTF-8")		
		
		self._description =self._description.replace("\\","/")
		descr = self._description.replace("\'","\'\'")		
		
		sharedDB.mySQLConnection.query("UPDATE temprigs SET name = '"+str(self._name)+"', setNumber = '"+str(self._setnumber)+"', type = '"+str(self._typ)+"', idprojects = '"+str(self._idprojects)+"', status = '"+str(self._status)+"', description = '"+descr+"', folderLocation = '"+str(self._folderLocation)+"', lasteditedbyname = '"+str(sharedDB.currentUser._name)+"', lasteditedbyip = '"+str(sharedDB.mySQLConnection.myIP)+"', appsessionid = '"+str(sharedDB.app.sessionId())+"' WHERE idtemprigs = "+str(self._idtemprigs)+";","commit")

	def SetValues(self,_idtemprigs = 0,_idprojects = 0 , _name = '',_setnumber = 0,_typ = 0,_status = 0,_description = '', _folderLocation = '',_timestamp = datetime.now()):
		print ("Downloaded updated for Rig '"+str(self._name)+"'")
		
		self._idtemprigs                 = _idtemprigs
		self._idprojects	      = _idprojects
		self._name                  = _name
		self._setnumber	      = _setnumber
		self._typ		      = _typ
		self._status              = _status		
		self._description	      = _description
		self._timestamp		      = _timestamp
		self._folderLocation           =_folderLocation

		self.rigChanged.emit()

	
	def emitRigChanged( self ):
		if ( not self.signalsBlocked() ):
		    self.rChanged.emit(str(self._idtemprigs))


	def setName(self, name):
		self._name = name
		self._updated = 1
	
	def setSetNumber(self, number):
		self._setnumber = number
		self._updated = 1
		
	def setType(self, typ):
		self._typ = typ
		self._updated = 1
    
	def setStatus(self, status):
		self._status = status
		self._updated = 1
	
	def setDescription(self, descr):
		self._description = descr
		self._updated = 1