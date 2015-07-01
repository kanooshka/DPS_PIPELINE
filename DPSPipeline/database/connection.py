import mysql.connector
import sharedDB
import threading
from datetime import datetime

class Connection():

	def __init__(self,_user = '', _password = ''):
		
		# define custom properties
		sharedDB.mySQLConnection = self
		self._cnx = mysql.connector.connect()
		self._user = _user
		self._password = _password
		self._host = '10.9.21.12'
		#self._host = '174.79.161.184'
		
		self._lastInsertId = ''
		if sharedDB.localDB:
			self._host = 'localhost'
		if sharedDB.testing and not sharedDB.localDB:
			self._database = 'testDB'
		else:
			self._database = 'dpstudio'
		#print "connection initiated"
	
	def testConnection(self):
		try:
			self.openConnection()
			return True
		except:
			print "FAILED TO connect locally, attempting WAN connection"
			try:
				self._host = '174.79.161.184'
				self.openConnection()
				return True
			except:
				self._host = '10.9.21.12'
				print "FAILED TO connect over WAN"
		return False
	
	def openConnection(self):
		if not self._cnx.is_connected():
			self._cnx = mysql.connector.connect(user = self._user, password = self._password, host = self._host, database = self._database)
	def closeConnection(self):
		self._cnx.close()

	def query(self, query = "", queryType = "fetchAll"):
		rows = ""
		self.openConnection()
		cursor = self._cnx.cursor()
		cursor.execute(query)
		self._lastInsertId = cursor.lastrowid
		if queryType == "fetchAll":
			rows = cursor.fetchall()
		elif queryType == "commit":
			self._cnx.commit()
		
		
		cursor.close()
		
		#self.closeConnection()

		return rows

	def UpdateDatabaseClasses(self):
		sharedDB.myStatuses = sharedDB.statuses.GetStatuses()
		sharedDB.myPhases = sharedDB.phases.GetPhaseNames()
		sharedDB.myProjects = sharedDB.projects.GetActiveProjects()
		sharedDB.myUsers = sharedDB.users.GetAllUsers()
		
	
	def SaveToDatabase(self):
	
		"""
		Saves the updated entries to the database
		"""
		if (not sharedDB.noSaving):
			threading.Timer(5.0, self.SaveToDatabase).start()
			
			if not sharedDB.pauseSaving:
			
				#timestamp = datetime.now()
				
				for proj in sharedDB.myProjects :
		
				    proj.Save()
				
				
				self.UpdateFromDatabase()
		
	def GetTimestamp(self):
		rows = ""
		self.openConnection()
		cursor = self._cnx.cursor()
		cursor.execute("SELECT NOW()")
		rows = cursor.fetchall()		
		
		cursor.close()
		
		self.closeConnection()

		return rows[0]
	
	def UpdateFromDatabase(self):
	
		"""
		Checks the database for any updated entries
		"""

		newdatetime = self.GetTimestamp();
		newdatetime = newdatetime[0]
		sharedDB.projects.CheckForNewEntries()
		sharedDB.lastUpdate = newdatetime
		print sharedDB.lastUpdate
		
		#sharedDB.myProjectViewWidget.CheckForDBUpdates()
		#for p in sharedDB.myProjects:
		#	p.ChangesLoaded()