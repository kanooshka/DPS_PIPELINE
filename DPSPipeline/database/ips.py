
from DPSPipeline.database.connection import Connection
import sharedDB


from projexui import qt

from PyQt4 import QtCore
from PyQt4.QtCore import QObject
#import sys
#timestamp
from datetime import datetime


class Ips(QObject):

	ipChanged = QtCore.pyqtSignal(QtCore.QString)
	ipAdded = QtCore.pyqtSignal(QtCore.QString)
	
	def __init__(self,_idips = -1,_idclients = -1, _name = '', _updated = 0,_new = 1):
		super(QObject, self).__init__()
		
		# define custom properties
		self._idips                 = _idips
		self._idclients             = _idclients
		self._name                  = _name
		
		self._updated               = _updated

		self._type                   = "ip"
		self._hidden                 = False
		
		self._new		     = _new
		
		self._projects		     = []
		
		if self._new:
			self.AddIpToDB()
			self._new = 0
			sharedDB.myIps.append(self)
			
			sharedDB.mySQLConnection.newIpSignal.emit(str(self._idips))
			print "IP '"+self._name+"' Added to Database!"
		
		#if self._idstatuses == 4 or self._idstatuses == 5 or self._idstatuses == 6:
			#self._hidden = True
			
	def Save(self):
		
		#print self._name
		if self._updated:
			#print self._name+" Updated in DB!"			
			self.UpdateIpInDB()
			self._updated = 0
			print "IP '"+self._name+"' Updated in Database!"
		elif self._new:			
			self.AddIpToDB()
			self._new = 0
			print "IP '"+self._name+"' Added to Database!"
	
	def UpdateIpInDB (self):

		sharedDB.mySQLConnection.query("UPDATE ips SET name = '"+name+"', idclients = '"+str(self.idclients)+"', lasteditedbyname = '"+str(sharedDB.currentUser._name)+"', lasteditedbyip = '"+str(sharedDB.mySQLConnection.myIP)+"', appsessionid = '"+str(sharedDB.app.sessionId())+"' WHERE idips = '"+str(self._idips)+"';","commit")
	
	def AddIpToDB (self):

		sharedDB.mySQLConnection.query("INSERT INTO ips (name, idclients, lasteditedbyname, lasteditedbyip, appsessionid) VALUES ('"+self._name+"', '"+str(self._idclients)+"', '"+str(sharedDB.currentUser._name)+"', '"+str(sharedDB.mySQLConnection.myIP)+"', '"+str(sharedDB.app.sessionId())+"');","commit")
		
		self._idips = sharedDB.mySQLConnection._lastInsertId
		
		self.ipAdded.emit(str(self._idips))

	def SetValues(self,_idips ,_idclients , _name = ''):
		print ("Downloaded update for IP '"+str(self._name)+"'")
		self._idips             = _idips
		self._idclients             = _idclients
		self._name                   = _name

		self.ipChanged.emit(str(self._idips))
	