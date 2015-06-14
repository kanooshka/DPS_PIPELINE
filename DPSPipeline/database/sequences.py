from DPSPipeline.database.connection import Connection
import sharedDB

#timestamp
from datetime import datetime

class Sequences():

	def __init__(self,_idsequences = 0,_idprojects = 1 , _number = '010',_idstatuses = 0, _shots = [],_updated = 0,_new = 1,_description = '',_timestamp = datetime.now()):
		
		# define custom properties
		self._idsequences             = _idsequences
		self._idprojects	      = _idprojects
		self._number                   = _number
		self._idstatuses             = _idstatuses
		self._description	     = _description
		self._timestamp		     = _timestamp
		
		self._shots                 = _shots
		self._updated                = _updated
		self._type                   = "sequence"
		self._hidden                 = False
		
		self._new		     = _new
		
		if self._idstatuses == 3 or self._idstatuses == 5:
			self._hidden = True
			
	def Save(self,timestamp):
		
		self._timestamp = timestamp
		if self._new:	
			self.AddSequenceToDB()
			#print self._number+" Added to Database!"
		
		elif self._updated:
			#print self._number+" Updated!"
			self.UpdateSequenceInDB()
	
		self._new = 0
		self._updated = 0
	
	def AddSequenceToDB(self):
	
		sharedDB.mySQLConnection.query("INSERT INTO sequences (number, idprojects, description, timestamp, idstatuses) VALUES ('"+str(self._number)+"', '"+str(self._idprojects)+"', '"+str(self._description)+"', '"+str(self._timestamp)+"', '"+str(self._idstatuses)+"');","commit")	
	
		self._idsequences = sharedDB.mySQLConnection._lastInsertId
	
	def UpdateSequenceInDB (self):

		sharedDB.mySQLConnection.query("UPDATE sequences SET number = '"+str(self._number)+"', idstatuses = '"+str(self._idstatuses)+"', description = '"+str(self._description)+"', timestamp = '"+str(self._timestamp)+"' WHERE idsequences = "+str(self._idsequences)+";","commit")

	
		


