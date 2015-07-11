import mysql.connector
import sharedDB
#import threading
from datetime import datetime,timedelta

from PyQt4 import QtCore,QtGui
from PyQt4.QtCore import QObject,QTimer



class Connection(QObject):
	
	newProjectSignal = QtCore.pyqtSignal(QtCore.QString)
	newSequenceSignal = QtCore.pyqtSignal()
	newShotSignal = QtCore.pyqtSignal()	

	def __init__(self,_user = '', _password = ''):
		
		super(QObject, self).__init__()
		
		# define custom properties
		sharedDB.mySQLConnection = self
		self._cnx = mysql.connector.connect()
		self._user = _user
		self._password = _password
		self._localhost = '10.9.21.12'
		self._remotehost = '174.79.161.184'
		self._cursor = ''
		self._host = self._localhost
		self._remote = 0
		
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
			print "FAILED TO connect if trying to connect remotely make sure to enable the remote access checkbox"
			'''
			print "FAILED TO connect locally, attempting WAN connection"
			try:
				self._host = '174.79.161.184'
				self.openConnection()
				return True
			except:
				self._host = '10.9.21.12'
				print "FAILED TO connect over WAN"
			'''
		return False
	
	def openConnection(self):
		if not self._cnx.is_connected():
			self._cnx = mysql.connector.connect(user = self._user, password = self._password, host = self._host, database = self._database)
	def closeConnection(self):
		self._cnx.close()

	def query(self, query = "", queryType = "fetchAll"):
		rows = ""
		self.openConnection()
		self._cursor = self._cnx.cursor()
		self._cursor.execute(query)
		self._lastInsertId = self._cursor.lastrowid
		if queryType == "fetchAll":
			rows = self._cursor.fetchall()
		elif queryType == "commit":
			self._cnx.commit()
		
		
		self._cursor.close()
		
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
		try:
			if (not sharedDB.noSaving):
				
				if sharedDB.myVersion.CheckVersion():
			
					try:
						#threading.Timer(2.0, self.SaveToDatabase).start()
						#print "Checking database for update..."
						
						
						if not sharedDB.pauseSaving:
						
							#timestamp = datetime.now()
							
							for proj in sharedDB.myProjects :
					
							    proj.Save()
							
							
							self.UpdateFromDatabase()
							self.closeConnection()
					except:
						errorMessage = QtGui.QMessageBox()
						errorMessage.setWindowTitle("ERROR!")
						errorMessage.setText("An error occured when save / loading from database, please contact support.")
						errorMessage.exec_()
				else:
					timer = QTimer()
					timer.timeout.connect(self.exit)
					timer.start(15000)
					
					sharedDB.pauseSaving = 1
					sharedDB.noSaving = 1
					
					versionError = QtGui.QMessageBox()
					versionError.setWindowTitle("OUT OF DATE!")
					versionError.setText("A New version of Sludge is ready to be implemented, please close Sludge and wait a few minutes to reopen. Sludge will autoclose in 15 seconds.")
					#versionError.button().setText("EXIT")
					
					versionError.exec_()
					
					QTimer.singleShot(10,sharedDB.app.exit())
		finally:
			QTimer.singleShot(3000,self.SaveToDatabase)
	def GetTimestamp(self):
		rows = ""
		self.openConnection()
		self._cursor = self._cnx.cursor()
		self._cursor.execute("SELECT NOW()")
		rows = self._cursor.fetchall()		
		
		self._cursor.close()
		
		self.closeConnection()

		return rows[0]
	
	def UpdateFromDatabase(self):
	
		"""
		Checks the database for any updated entries
		"""

		newdatetime = self.GetTimestamp();
		newdatetime = newdatetime[0]
		self.CheckForNewEntries()
		#print type(newdatetime)
		sharedDB.lastUpdate = newdatetime - timedelta(seconds=4)

	def CheckForNewEntries (self):

		projrows = sharedDB.mySQLConnection.query("SELECT idprojects, name, due_date, idstatuses, renderWidth, renderHeight, description, folderLocation, fps FROM projects WHERE timestamp > \""+str(sharedDB.lastUpdate)+"\"")
		
		#if len(rows):
		#	print "Loading 'Project' Changes from Database"
			
		for row in projrows:
			existed = False		
			#iterate through project list
			for proj in sharedDB.myProjects:
				#if id exists update entry
				if str(proj._idprojects) == str(row[0]):
					proj.SetValues(_idprojects = row[0],_name = row[1],_due_date = row[2],_idstatuses = row[3],_renderWidth = row[4],_renderHeight = row[5],_description = row[6],_folderLocation = row[7],_fps = row[8])
					existed = True
					break
			if not existed:
				#create project
				print "New PROJECT found in database CREATING project (NOT YET IMPLEMENTED)"
				#sharedDB.myProjects.append(sharedDB.projects.Projects(_idprojects = row[0],_name = row[1],_due_date = row[2],_idstatuses = row[3],_renderWidth = row[4],_renderHeight = row[5],_description = row[6],_folderLocation = row[7],_fps = row[8],_new = 0))
				myProj =sharedDB.projects.Projects(_idprojects = row[0],_name = row[1],_due_date = row[2],_idstatuses = row[3],_renderWidth = row[4],_renderHeight = row[5],_description = row[6],_folderLocation = row[7],_fps = row[8],_new = 0)
				#add sequence to sequence list
				sharedDB.myProjects.append(myProj)
				#iterate through projects

				#emit new sequence signal
				self.newProjectSignal.emit(str(myProj._idprojects))

		
		
		
		seqrows = sharedDB.mySQLConnection.query("SELECT idsequences, number, idstatuses, description, timestamp, idprojects FROM sequences WHERE timestamp > \""+str(sharedDB.lastUpdate)+"\"")
				
		for row in seqrows:
			existed = False
			for seq in sharedDB.mySequences:			
				#if id exists update entry
				if str(seq._idsequences) == str(row[0]):
					seq.SetValues(_idsequences = row[0],_number = row[1],_idstatuses = row[2],_description = row[3],_timestamp = row[4])
					existed = True
					break
		
				
			if existed == False:
			#create project
				print "New SEQUENCE found in database CREATING sequence"
				#create instance of sequence class				
				mySeq =sharedDB.sequences.Sequences(_idsequences = row[0],_number = row[1],_idstatuses = row[2],_description = row[3],_timestamp = row[4], _idprojects = row[5], _new = 0)
				#add sequence to sequence list
				sharedDB.mySequences.append(mySeq)
				#iterate through projects
				for proj in sharedDB.myProjects:
					##if idprojects matches
					if proj._idprojects == mySeq._idprojects:
						###add to project's sequences
						proj._sequences.append(mySeq)
						###if current project in projectview update
						if sharedDB.myProjectViewWidget._currentProject._idprojects == mySeq._idprojects:
							#emit new sequence signal
							self.newSequenceSignal.emit()
						break				
				
		shotrows = sharedDB.mySQLConnection.query("SELECT idshots, number, startframe, endframe, description, idstatuses, timestamp, idprojects, idsequences FROM shots WHERE timestamp > \""+str(sharedDB.lastUpdate)+"\"")
				
		for row in shotrows:
			existed = False
			for shot in sharedDB.myShots:			
				#if id exists update entry
				#if str(shot._number) == str(row[1]) and str(shot._idprojects) == str(row[7]) and str(shot._idsequences) == str(row[8]):
				if str(shot._idshots) == str(row[0]):
					shot.SetValues(_idshots = row[0],_number = row[1],_startframe = row[2],_endframe = row[3],_description = row[4],_idstatuses = row[5],_timestamp = row[6])
					existed = True
					break
				
			if existed == False:
			#create project
				print "New SHOT found in database CREATING shot"
				#create instance of shot class				
				myShot =sharedDB.shots.Shots(_idshots = row[0],_number = row[1],_startframe = row[2],_endframe = row[3],_description = row[4],_idstatuses = row[5],_timestamp = row[6],_idprojects = row[7],_idsequences = row[8], _new = 0)
				#add shot to shot list
				sharedDB.myShots.append(myShot)
				#iterate through sequences
				for seq in sharedDB.mySequences:
					##if idsequences matches
					if seq._idsequences == myShot._idsequences:
						###add to sequence's shot list
						seq._shots.append(myShot)
						###if current sequence in projectview update
						if sharedDB.myProjectViewWidget._currentSequence._idsequences == myShot._idsequences:
							#emit new shot signal
							self.newShotSignal.emit()
						break
					
	def setHost(self, typeString):
		if typeString == "local":
			self._host = self._localhost
			self._remote = 0
		elif typeString == "remote":
			self._host = self._remotehost
			self._remote = 1
			
	def exit(self):
		sharedDB.app.exit()