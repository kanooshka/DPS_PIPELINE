import mysql.connector
import sharedDB
#import threading
from datetime import datetime,timedelta
import time
import socket

import atexit

from PyQt4 import QtCore,QtGui
from PyQt4.QtCore import QObject,QTimer

'''
Start
'''

class AutoParseProjectsThread(QtCore.QThread):

    def run(self):

	#sharedDB.blockSignals = 1
	
	if sharedDB.mySQLConnection is not None:
		while True:
			#print "Queue Lenght: "+str(x)
			if len(sharedDB.mySQLConnection._projectsToBeParsed)>0:
				row = sharedDB.mySQLConnection._projectsToBeParsed[0]
				#print "Adding project "+str(row[1])
				existed = False		
				#iterate through project list
				for proj in sharedDB.myProjects:
					#if id exists update entry
					if str(proj._idprojects) == str(row[0]):
						if not str(sharedDB.mySQLConnection.myIP) == str(row[10]) or sharedDB.testing:
							proj.SetValues(_idprojects = row[0],_name = row[1],_due_date = row[2],_idstatuses = row[3],_renderWidth = row[4],_renderHeight = row[5],_description = row[6],_folderLocation = row[7],_fps = row[8])
						existed = True
						break
				if not existed:
					#create project
					print "New PROJECT found in database CREATING project: "+str(row[0])
					#sharedDB.myProjects.append(sharedDB.projects.Projects(_idprojects = row[0],_name = row[1],_due_date = row[2],_idstatuses = row[3],_renderWidth = row[4],_renderHeight = row[5],_description = row[6],_folderLocation = row[7],_fps = row[8],_new = 0))
					myProj =sharedDB.projects.Projects(_idprojects = row[0],_name = row[1],_due_date = row[2],_idstatuses = row[3],_renderWidth = row[4],_renderHeight = row[5],_description = row[6],_folderLocation = row[7],_fps = row[8],_new = 0)
					#add project to project list
					sharedDB.myProjects.append(myProj)
					#iterate through projects
		
					#emit new sequence signal
					sharedDB.mySQLConnection.newProjectSignal.emit(str(myProj._idprojects))
					
				#remove row from list
				del sharedDB.mySQLConnection._projectsToBeParsed[0]
			else:
				break
	
		while True:
			#print "Queue Lenght: "+str(x)
			if len(sharedDB.mySQLConnection._sequencesToBeParsed)>0:
				row = sharedDB.mySQLConnection._sequencesToBeParsed[0]
				
				existed = False
				for seq in sharedDB.mySequences:			
					#if id exists update entry

					if str(seq._idsequences) == str(row[0]):
						if not str(sharedDB.mySQLConnection.myIP) == str(row[7]) or sharedDB.testing:
							seq.SetValues(_idsequences = row[0],_number = row[1],_idstatuses = row[2],_description = row[3],_timestamp = row[4])
						existed = True
						break
			
					
				if existed == False:
				#create project
					print "New SEQUENCE found in database CREATING sequence: "+str(row[0])
					#create instance of sequence class				
					mySeq =sharedDB.sequences.Sequences(_idsequences = row[0],_number = row[1],_idstatuses = row[2],_description = row[3],_timestamp = row[4], _idprojects = row[5], _new = 0)
					#add sequence to sequence list
					sharedDB.mySequences.append(mySeq)
					#iterate through projects
					for proj in sharedDB.myProjects:
						##if idprojects matches
						if proj._idprojects == mySeq._idprojects:
							###add to project's sequences
							#print "Adding Sequence "+str(mySeq._idsequences)+ " in Project " + str(proj._idprojects)
							proj._sequences.append(mySeq)
							###if current project in projectview update
							sharedDB.mySQLConnection.newSequenceSignal.emit(str(mySeq._idsequences))
							'''if sharedDB.myProjectViewWidget._currentProject is not None:
								if sharedDB.myProjectViewWidget._currentProject._idprojects == mySeq._idprojects:
									#emit new sequence signal
									
									#print "emitSignal"'''
									
							
							break
					
				#remove row from list
				del sharedDB.mySQLConnection._sequencesToBeParsed[0]
			else:
				break
		
		while True:
			#print "Queue Lenght: "+str(x)
			if len(sharedDB.mySQLConnection._shotsToBeParsed)>0:
				row = sharedDB.mySQLConnection._shotsToBeParsed[0]
	
				existed = False
				for shot in sharedDB.myShots:			
					#if id exists update entry
					#if str(shot._number) == str(row[1]) and str(shot._idprojects) == str(row[7]) and str(shot._idsequences) == str(row[8]):

					if str(shot._idshots) == str(row[0]):						
						if not str(sharedDB.mySQLConnection.myIP) == str(row[10]) or sharedDB.testing:
							shot.SetValues(_idshots = row[0],_number = row[1],_startframe = row[2],_endframe = row[3],_description = row[4],_idstatuses = row[5],_timestamp = row[6],_idprojects = row[7],_idsequences = row[8], _shotnotes = row[11])
						existed = True
						break
					
				if existed == False:
				#create project
					print "New SHOT found in database CREATING shot: "+str(row[0])
					#create instance of shot class				
					myShot =sharedDB.shots.Shots(_idshots = row[0],_number = row[1],_startframe = row[2],_endframe = row[3],_description = row[4],_idstatuses = row[5],_timestamp = row[6],_idprojects = row[7],_idsequences = row[8], _new = 0, _shotnotes = row[11])
					#add shot to shot list
					sharedDB.myShots.append(myShot)
					#iterate through sequences
					for seq in sharedDB.mySequences:
						##if idsequences matches
						if seq._idsequences == myShot._idsequences:
							###add to sequence's shot list
							seq._shots.append(myShot)
							###if current sequence in projectview update
							sharedDB.mySQLConnection.newShotSignal.emit(str(myShot._idshots))
							break
					
				#remove row from list
				del sharedDB.mySQLConnection._shotsToBeParsed[0]
			else:
				break

		
		while True:
			#print "Queue Lenght: "+str(x)
			if len(sharedDB.mySQLConnection._tasksToBeParsed)>0:
				row = sharedDB.mySQLConnection._tasksToBeParsed[0]
	
				existed = False
				for task in sharedDB.myTasks:
					if str(task._idtasks) == str(row[0]):						
						if not str(sharedDB.mySQLConnection.myIP) == str(row[13]) or sharedDB.testing:
							#idtasks, idphaseassignments, idprojects, idshots, idusers, idphases, timealotted, idsequences, duedate, percentcomplete, done, timestamp
							task.SetValues(_idtasks = row[0],_idphaseassignments = row[1],_idprojects = row[2],_idshots = row[3],_idusers = row[4],_idphases = row[5],_timealotted = row[6], _idsequences = row[7], _duedate = row[8], _percentcomplete = row[9], _done = row[10], _timestamp = row[11], _status = row[14])
						existed = True
						break
					
				if existed == False:
				#create project
					print "New TASK found in database CREATING task: "+str(row[0])
					#create instance of shot class				
					myTask =sharedDB.tasks.Tasks(_idtasks = row[0],_idphaseassignments = row[1],_idprojects = row[2],_idshots = row[3],_idusers = row[4],_idphases = row[5],_timealotted = row[6], _idsequences = row[7], _duedate = row[8], _percentcomplete = row[9], _done = row[10], _timestamp = row[11], _status = row[14])
					#add task to task list
					sharedDB.myTasks.append(myTask)
					#iterate through shots
					for shot in sharedDB.myShots:
						##if idsequences matches
						#print "Shot id:" +str(shot._idshots)+" Task Id shots: "+str(myTask._idshots)
						if shot._idshots == myTask._idshots:
							
							###add to shot's task list
							if shot._tasks is not None:
								#print "Appending shot: "+str(shot._idshots)+"'s task list"
								shot._tasks.append(myTask)
							else:
								#print "Creating shot: "+str(shot._idshots)+"'s task list"
								shot._tasks = [myTask]

							sharedDB.mySQLConnection.newTaskSignal.emit(str(myTask._idtasks))
							
							break
					
				#remove row from list
				del sharedDB.mySQLConnection._tasksToBeParsed[0]
			else:
				if len(sharedDB.myProjects) and sharedDB.initialLoad == 0:
					#print "First Load Complete!"
					sharedDB.initialLoad=1
					sharedDB.mySQLConnection.firstLoadComplete.emit()
				break
				

	time.sleep(2)
	
class AutoCheckDatabase(QtCore.QThread):

    def run(self):

	if (not sharedDB.noSaving):
				
		if sharedDB.myVersion.CheckVersion():
	
			#try:				
			if not sharedDB.pauseSaving:
			
				#timestamp = datetime.now()
				
				for proj in sharedDB.myProjects :
		
				    proj.Save()
				
				#print "Updating from Database!"
				sharedDB.mySQLConnection.UpdateFromDatabase()
				#sharedDB.mySQLConnection.closeConnection()
			'''except:
				errorMessage = QtGui.QMessageBox()
				errorMessage.setWindowTitle("ERROR!")
				errorMessage.setText("An error occured when save / loading from database, please contact support.")
				errorMessage.exec_()'''
		else:
			sharedDB.mySQLConnection.wrongVersionSignal.emit()
			
	#print "Checking for update"
	sharedDB.blockSignals = 0
	time.sleep(sharedDB.mySQLConnection._autoUpdateFrequency)
	    
class Connection(QObject):
	
	newProjectSignal = QtCore.pyqtSignal(QtCore.QString)
	newSequenceSignal = QtCore.pyqtSignal(QtCore.QString)
	newShotSignal = QtCore.pyqtSignal(QtCore.QString)
	newTaskSignal = QtCore.pyqtSignal(QtCore.QString)
	wrongVersionSignal = QtCore.pyqtSignal()
	firstLoadComplete = QtCore.pyqtSignal()

	def __init__(self,_user = '', _password = ''):
		
		super(QObject, self).__init__()
		
		# define custom properties
		#sharedDB.mySQLConnection = self
		self._cnx = mysql.connector.connect()
		self._user = _user
		self._password = _password
		self._localhost = '10.9.21.12'
		self._remotehost = '174.79.161.184'
		
		if sharedDB.localDB:
			self._localhost = 'localhost'
		
		self._cursor = ''
		self._host = self._localhost
		self._remote = 0
		self._autoUpdateFrequency = 2
	
		self.myIP = socket.gethostbyname(socket.gethostname())
		
		self._lastInsertId = ''
		
		self._projectsToBeParsed = []
		self._sequencesToBeParsed = []
		self._shotsToBeParsed = []
		self._phaseAssignmentsToBeParsed = []
		self._tasksToBeParsed = []
		
		if sharedDB.localDB:
			self._host = 'localhost'
		if sharedDB.testing and not sharedDB.localDB:
			self._database = 'testDB'
		else:
			self._database = 'dpstudio'
			
		self._autoCheckDatabaseThread = AutoCheckDatabase()
		self._autoCheckDatabaseThread.daemon = True
		
		self.wrongVersionSignal.connect(self.wrongVersion)
		
		self._projectParser = AutoParseProjectsThread()
		self._projectParser.finished.connect(self._projectParser.start)
		self._projectParser.start()
		self._projectParser.daemon = True
		
		atexit.register(self.closeThreads)
		#self._sequenceParser = AutoParseSequencesThread()
		#self._sequenceParser.finished.connect(self._sequenceParser.start)
		#self._sequenceParser.start()

		#print "connection initiated"
	
	def closeThreads(self):
		self._autoCheckDatabaseThread.quit()
		self._projectParser.quit()
		
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
		
		self.closeConnection()

		return rows

	def UpdateDatabaseClasses(self):
		#newdatetime = self.GetTimestamp();
		#sharedDB.lastUpdate = newdatetime[0]
		sharedDB.myStatuses = sharedDB.statuses.GetStatuses()
		sharedDB.myPhases = sharedDB.phases.GetPhaseNames()
		#sharedDB.myProjects = sharedDB.projects.GetActiveProjects()
		sharedDB.myUsers = sharedDB.users.GetAllUsers()
	
	def SaveToDatabase(self):
		self._autoCheckDatabaseThread.finished.connect(self._autoCheckDatabaseThread.start)
		self._autoCheckDatabaseThread.start()
	
	'''
	def SaveToDatabaseOLD(self):
	
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
			QTimer.singleShot(self._autoUpdateFrequency,self.SaveToDatabase)
	'''
	def GetTimestamp(self):
		rows = ""
		self.openConnection()
		self._cursor = self._cnx.cursor()
		self._cursor.execute("SELECT NOW()")
		rows = self._cursor.fetchall()		
		
		self._cursor.close()
		
		#self.closeConnection()

		return rows[0]
	
	def UpdateFromDatabase(self):
	
		"""
		Checks the database for any updated entries
		"""

		newdatetime = self.GetTimestamp();
		#newdatetime = datetime.now()- timedelta(years=4);
		newdatetime = newdatetime[0]
		self.CheckForNewEntries()
		#print type(newdatetime)
		sharedDB.lastUpdate = newdatetime - timedelta(seconds=4)

	def CheckForNewEntries (self):

		projrows = self.query("SELECT idprojects, name, due_date, idstatuses, renderWidth, renderHeight, description, folderLocation, fps, lasteditedbyname, lasteditedbyip FROM projects WHERE timestamp > \""+str(sharedDB.lastUpdate)+"\"")
		projrows.sort(key=lambda x: x[2])
		self._projectsToBeParsed.extend(projrows)		
			
		seqrows = sharedDB.mySQLConnection.query("SELECT idsequences, number, idstatuses, description, timestamp, idprojects, lasteditedbyname, lasteditedbyip FROM sequences WHERE timestamp > \""+str(sharedDB.lastUpdate)+"\"")
		self._sequencesToBeParsed.extend(seqrows)		
						
				
		shotrows = sharedDB.mySQLConnection.query("SELECT idshots, number, startframe, endframe, description, idstatuses, timestamp, idprojects, idsequences, lasteditedbyname, lasteditedbyip, shotnotes FROM shots WHERE timestamp > \""+str(sharedDB.lastUpdate)+"\"")
		self._shotsToBeParsed.extend(shotrows)
		
		taskrows = sharedDB.mySQLConnection.query("SELECT idtasks, idphaseassignments, idprojects, idshots, idusers, idphases, timealotted, idsequences, duedate, percentcomplete, done, timestamp, lasteditedbyname, lasteditedbyip, status FROM tasks WHERE timestamp > \""+str(sharedDB.lastUpdate)+"\"")
		self._tasksToBeParsed.extend(taskrows)
		
		'''for proj in sharedDB.myProjectList:
			phaseAssignmentRows = sharedDB.mySQLConnection.query("SELECT a.idphaseassignments,a.idphases,a.idprojects,a.startdate,a.enddate,a.progress,a.archived,a.idstatuses, b.MaxTimeStamp FROM phaseassignments a JOIN (SELECT idphases,idprojects , Max(Timestamp) AS MaxTimeStamp FROM phaseassignments WHERE idprojects = %s GROUP BY idphases) b ON a.idphases = b.idphases AND a.idprojects = b.idprojects AND a.Timestamp = b.MaxTimeStamp" % proj._idprojects)
			self._phaseAssignmentsToBeParsed.extend(phaseAssignmentRows)
		'''
	def setHost(self, typeString):
		if typeString == "local":
			self._host = self._localhost
			self._remote = 0
			self._autoUpdateFrequency = 2
		elif typeString == "remote":
			self._host = self._remotehost
			self._remote = 1
			self._autoUpdateFrequency = 2
			
	def exit(self):
		sharedDB.app.exit()
		
	def wrongVersion(self):
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
		
		sharedDB.app.exit()
	