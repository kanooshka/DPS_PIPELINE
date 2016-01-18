
from DPSPipeline.database.connection import Connection
import sharedDB


from projexui import qt

from PyQt4 import QtCore
from PyQt4.QtCore import QObject
#import sys
#timestamp
from datetime import datetime


class Clients(QObject):

	clientChanged = QtCore.pyqtSignal(QtCore.QString)
	clientAdded = QtCore.pyqtSignal(QtCore.QString)
	
	def __init__(self,_idclients = -1, _name = '', _updated = 0,_new = 1):
		super(QObject, self).__init__()
		
		# define custom properties
		self._idclients             = _idclients
		self._name                   = _name
		
		self._updated                = _updated

		self._type                   = "client"
		self._hidden                 = False
		
		self._new		     = _new
		self._ips		     = {}
		
		if self._new:
			self.AddClientToDB()
			self._new = 0
			sharedDB.myClients.append(self)
			
			sharedDB.mySQLConnection.newClientSignal.emit(str(self._idclients))
			print "Client '"+self._name+"' Added to Database!"
		
		#if self._idstatuses == 4 or self._idstatuses == 5 or self._idstatuses == 6:
			#self._hidden = True
	
	def __eq__(self, another):
		return hasattr(another, '_idclients') and self._idclients == another._idclients
	
	def __hash__(self):
		return hash(self._idclients)
		
	def id(self):
		return self._idclients
	
	def Save(self):
		
		#print self._name
		if self._updated:
			#print self._name+" Updated in DB!"			
			self.UpdateClientInDB()
			self._updated = 0
			print "Client '"+self._name+"' Updated in Database!"
		elif self._new:			
			self.AddClientToDB()
			self._new = 0
			print "Client '"+self._name+"' Added to Database!"
	
	def UpdateClientInDB (self):

		sharedDB.mySQLConnection.query("UPDATE clients SET name = '"+name+"', lasteditedbyname = '"+str(sharedDB.currentUser._name)+"', lasteditedbyip = '"+str(sharedDB.mySQLConnection.myIP)+"', appsessionid = '"+str(sharedDB.app.sessionId())+"' WHERE idclients = '"+str(self._idclients)+"';","commit")
	
	def AddClientToDB (self):

		sharedDB.mySQLConnection.query("INSERT INTO clients (name, lasteditedbyname, lasteditedbyip, appsessionid) VALUES ('"+self._name+"', '"+str(sharedDB.currentUser._name)+"', '"+str(sharedDB.mySQLConnection.myIP)+"', '"+str(sharedDB.app.sessionId())+"');","commit")
		
		self._idclients = sharedDB.mySQLConnection._lastInsertId
		
		self.clientAdded.emit(str(self._idclients))

	def SetValues(self,_idclients , _name = ''):
		print ("Downloaded updated for Client '"+str(self._name)+"'")
		
		self._idclients             = _idclients
		self._name                   = _name

		self.clientChanged.emit(str(self._idclients))
	