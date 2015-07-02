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
		newdatetime = self.GetTimestamp();
		sharedDB.lastUpdate = newdatetime[0]
		sharedDB.myStatuses = sharedDB.statuses.GetStatuses()
		sharedDB.myPhases = sharedDB.phases.GetPhaseNames()
		sharedDB.myProjects = sharedDB.projects.GetActiveProjects()
		sharedDB.myUsers = sharedDB.users.GetAllUsers()
		
	
	def SaveToDatabase(self):
	
		"""
		Saves the updated entries to the database
		"""
		if (not sharedDB.noSaving):
			threading.Timer(3.0, self.SaveToDatabase).start()
			
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
		self.CheckForNewEntries()
		#sharedDB.sequences.CheckForNewEntries()
		#sharedDB.shots.CheckForNewEntries()
		#sharedDB.phaseAssignments.CheckForNewEntries()
		
		sharedDB.lastUpdate = newdatetime
		#print sharedDB.lastUpdate
		
		#sharedDB.myProjectViewWidget.CheckForDBUpdates()
		#for p in sharedDB.myProjects:
		#	p.ChangesLoaded()
		
	def CheckForNewEntries (self):

		projrows = sharedDB.mySQLConnection.query("SELECT idprojects, name, due_date, idstatuses, renderWidth, renderHeight, description, folderLocation, fps FROM projects WHERE idstatuses != 4 AND timestamp > \""+str(sharedDB.lastUpdate)+"\"")
		
		#if len(rows):
		#	print "Loading 'Project' Changes from Database"
			
		for row in projrows:
			#print row[0]
			
			#iterate through project list
			for proj in sharedDB.myProjects:
				#if id exists update entry
				if str(proj._idprojects) == str(row[0]):
					proj.SetValues(_idprojects = row[0],_name = row[1],_due_date = row[2],_idstatuses = row[3],_renderWidth = row[4],_renderHeight = row[5],_description = row[6],_folderLocation = row[7],_fps = row[8])
	
		
		seqrows = sharedDB.mySQLConnection.query("SELECT idsequences, number, idstatuses, description, timestamp FROM sequences WHERE timestamp > \""+str(sharedDB.lastUpdate)+"\"")
				
		for row in seqrows:
			#print row[0]
			for seq in sharedDB.mySequences:			
				#if id exists update entry
				if str(seq._idsequences) == str(row[0]):
					seq.SetValues(_idsequences = row[0],_number = row[1],_idstatuses = row[2],_description = row[3],_timestamp = row[4])
	
					#else create new entry
	
