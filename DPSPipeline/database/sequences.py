from DPSPipeline.database.connection import Connection
import sharedDB
from DPSPipeline.database import shots
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
		self._lastSelectedShotNumber = '-1'
		
		self.GetShotsFromSequence()
		
		
		#if self._idstatuses == 3 or self._idstatuses == 5:
			#self._hidden = True
			
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
	
		for shot in self._shots:
			shot.Save(timestamp)
	
	def AddSequenceToDB(self):
	
		sharedDB.mySQLConnection.query("INSERT INTO sequences (number, idprojects, description, timestamp, idstatuses) VALUES ('"+str(self._number)+"', '"+str(self._idprojects)+"', '"+str(self._description)+"', '"+str(self._timestamp)+"', '"+str(self._idstatuses)+"');","commit")	
	
		self._idsequences = sharedDB.mySQLConnection._lastInsertId
	
	def UpdateSequenceInDB (self):

		sharedDB.mySQLConnection.query("UPDATE sequences SET number = '"+str(self._number)+"', idstatuses = '"+str(self._idstatuses)+"', description = '"+str(self._description)+"', timestamp = '"+str(self._timestamp)+"' WHERE idsequences = "+str(self._idsequences)+";","commit")
		print ("Updating sequence in DB: "+str(self._idsequences))
	
		
	def GetShotsFromSequence(self):
		self._shots = []
		
		if not sharedDB.noDB:
			rows = sharedDB.mySQLConnection.query("SELECT idshots, number, startframe, endframe, description, idstatuses, timestamp FROM shots WHERE idsequences = '"+str(self._idsequences)+"'")
			
			for row in rows:
				#print row[0]
				self._shots.append(shots.Shots(_idshots = row[0],_number = row[1],_startframe = row[2],_endframe = row[3],_description = row[4],_idstatuses = row[5],_timestamp = row[6],_new = 0,_idprojects = self._idprojects,_idsequences = self._idsequences))
	
		else:
			self._shots.append(shots.Shots(_idshots = 1,_startframe = 10, _endframe= 230,_idsequences = self._idsequences,_idprojects = self._idprojects ,_number = '0010',_idstatuses = 1,_description = 'YES! THIS IS A SHOT!',_timestamp = datetime.now(),_new = 0))
	
	
	def AddShotToSequence(self, newName):
		if not sharedDB.noDB:
			self._shots.append(shots.Shots(_idshots = None,_number = newName,_idstatuses = 1,_description = '',_timestamp = None,_new = 1,_idprojects = self._idprojects, _idsequences = self._idsequences, _startframe = 101, _endframe = 101))
			self._shots[len(self._shots)-1].Save(datetime.now())
			sharedDB.mySQLConnection.closeConnection()
	
