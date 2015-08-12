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



class processQueries(QtCore.QThread):
	

	_currentDB = ''
	_currentQuery = ''
	_currentQueryType = ''
	
	_queries = []		
	
	
	def run(self):

		if sharedDB.myVersion.CheckVersion():
		
			#Check for database updates
			#sharedDB.mySQLConnection.CheckForNewEntries()
			
			if sharedDB.initialLoad:
		
				newdatetime = sharedDB.mySQLConnection.GetTimestamp();
				#newdatetime = datetime.now()- timedelta(years=4);
				newdatetime = newdatetime[0]
				sharedDB.lastUpdate = newdatetime - timedelta(seconds=4)
			else:
				print "Commencing initial Database load"
				
				sharedDB.myStatuses = sharedDB.statuses.GetStatuses()
				sharedDB.myPhases = sharedDB.phases.GetPhaseNames()
				#sharedDB.myUsers = sharedDB.users.GetAllUsers()
		
			self._queries.append(["SELECT","clients","SELECT idclients, name, lasteditedbyname, lasteditedbyip FROM clients WHERE timestamp > \""+str(sharedDB.lastUpdate)+"\""])			
			self._queries.append(["SELECT","ips","SELECT idips, name, idclients, lasteditedbyname, lasteditedbyip FROM ips WHERE timestamp > \""+str(sharedDB.lastUpdate)+"\""])			
			self._queries.append(["SELECT","projects","SELECT idprojects, name, due_date, idstatuses, renderWidth, renderHeight, description, folderLocation, fps, lasteditedbyname, lasteditedbyip, idclients, idips FROM projects WHERE timestamp > \""+str(sharedDB.lastUpdate)+"\""])			
			self._queries.append(["SELECT","phaseassignments","SELECT idphaseassignments,idprojects, idphases, startdate, enddate, idstatuses, archived, timestamp, lasteditedbyname, lasteditedbyip FROM phaseassignments WHERE timestamp > \""+str(sharedDB.lastUpdate)+"\""])			
			self._queries.append(["SELECT","sequences","SELECT idsequences, number, idstatuses, description, timestamp, idprojects, lasteditedbyname, lasteditedbyip FROM sequences WHERE timestamp > \""+str(sharedDB.lastUpdate)+"\""])			
			self._queries.append(["SELECT","shots","SELECT idshots, number, startframe, endframe, description, idstatuses, timestamp, idprojects, idsequences, lasteditedbyname, lasteditedbyip, shotnotes FROM shots WHERE timestamp > \""+str(sharedDB.lastUpdate)+"\""])			
			self._queries.append(["SELECT","tasks","SELECT idtasks, idphaseassignments, idprojects, idshots, idusers, idphases, timealotted, idsequences, duedate, percentcomplete, done, timestamp, lasteditedbyname, lasteditedbyip, status FROM tasks WHERE timestamp > \""+str(sharedDB.lastUpdate)+"\""])
			self._queries.append(["SELECT","userassignments","SELECT iduserassignments, idusers, assignmentid, assignmenttype, idstatuses, timestamp, lasteditedbyname, lasteditedbyip FROM userassignments WHERE timestamp > \""+str(sharedDB.lastUpdate)+"\""])
			
			while True:
				if len(self._queries)>0:
					self._currentQueryType =  self._queries[0][0]
					self._currentDB = self._queries[0][1]		
					self._currentQuery = self._queries[0][2]
					
					rows = sharedDB.mySQLConnection.query(self._currentQuery)

					if self._currentDB == "clients":						
						rows.sort(key=lambda x: x[2])
						sharedDB.mySQLConnection._clientsToBeParsed.extend(rows)
					elif self._currentDB == "ips":
						rows.sort(key=lambda x: x[2])
						sharedDB.mySQLConnection._ipsToBeParsed.extend(rows)
					elif self._currentDB == "projects":
						rows = sorted(rows, key=lambda x: x[2])
						sharedDB.mySQLConnection._projectsToBeParsed.extend(rows)
					elif self._currentDB == "phaseassignments":
						rows = sorted(rows, key=lambda x: x[3])
						sharedDB.mySQLConnection._phaseassignmentsToBeParsed.extend(rows)
					elif self._currentDB == "sequences":
						sharedDB.mySQLConnection._sequencesToBeParsed.extend(rows)
					elif self._currentDB == "shots":
						sharedDB.mySQLConnection._shotsToBeParsed.extend(rows)
					elif self._currentDB == "tasks":
						sharedDB.mySQLConnection._tasksToBeParsed.extend(rows)
					elif self._currentDB == "userassignments":
						sharedDB.mySQLConnection._userAssignmentsToBeParsed.extend(rows)
					
					del self._queries[0]		
				else:
					break
			
			#parse updates
			sharedDB.mySQLConnection.ParseUpdatesFromDB()
			
			#save changes				
			for proj in sharedDB.myProjects :		
			    proj.Save()
		else:
			sharedDB.mySQLConnection.wrongVersionSignal.emit()
			time.sleep(99999)
	
		time.sleep(sharedDB.mySQLConnection._autoUpdateFrequency)
		
	

    
class Connection(QObject):
	newClientSignal = QtCore.pyqtSignal(QtCore.QString)
	newIpSignal = QtCore.pyqtSignal(QtCore.QString)
	newProjectSignal = QtCore.pyqtSignal(QtCore.QString)
	newPhaseAssignmentSignal = QtCore.pyqtSignal(QtCore.QString)
	newSequenceSignal = QtCore.pyqtSignal(QtCore.QString)
	newShotSignal = QtCore.pyqtSignal(QtCore.QString)
	newTaskSignal = QtCore.pyqtSignal(QtCore.QString)
	newUserAssignmentSignal = QtCore.pyqtSignal(QtCore.QString)
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
		
		sharedDB.mySQLConnection = self
		
		if sharedDB.localDB:
			self._localhost = 'localhost'
		elif sharedDB.remote:
			self.localhost = self._remotehost
		
		self._cursor = ''
		self._host = self._localhost
		self._remote = 0
		self._autoUpdateFrequency = 2
	
		self.myIP = socket.gethostbyname(socket.gethostname())
		
		self._lastInsertId = ''		
		
		if sharedDB.localDB:
			self._host = 'localhost'
		if sharedDB.testDB:
			self._database = 'testDB'
		else:
			self._database = 'dpstudio'
		
		self.wrongVersionSignal.connect(self.wrongVersion)
		
		self._clientsToBeParsed = []
		self._ipsToBeParsed = []
		self._projectsToBeParsed = []
		self._phaseassignmentsToBeParsed = []
		self._sequencesToBeParsed = []
		self._shotsToBeParsed = []
		self._phaseAssignmentsToBeParsed = []
		self._tasksToBeParsed = []
		self._userAssignmentsToBeParsed = []
		
		self._queryProcessor = processQueries()
		self._queryProcessor.finished.connect(self._queryProcessor.start)
		self._queryProcessor.daemon = True
		
		atexit.register(self.closeThreads)
	def closeThreads(self):
		self._queryProcessor.quit()
		#self._projectParser.quit()
		
	def testConnection(self):
		try:
			self.openConnection()
			return True
		except:
			print "FAILED TO connect if trying to connect remotely make sure to enable the remote access checkbox"
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
			if not sharedDB.disableSaving:
				self._cnx.commit()
		
		
		self._cursor.close()
		
		self.closeConnection()

		return rows

	def GetTimestamp(self):
		rows = ""
		self.openConnection()
		self._cursor = self._cnx.cursor()
		self._cursor.execute("SELECT NOW()")
		rows = self._cursor.fetchall()		
		
		self._cursor.close()
		
		#self.closeConnection()

		return rows[0]		
	
	def ParseUpdatesFromDB(self):
		#sharedDB.blockSignals = 1
		

		#clients
		while True:
			if len(self._clientsToBeParsed)>0:
				row = self._clientsToBeParsed[0]
				
				existed = False		
				
				#iterate through ip list
				for client in sharedDB.myClients:
					#if id exists update entry
					if str(client._idclients) == str(row[0]):
						if not str(sharedDB.mySQLConnection.myIP) == str(row[3]) or sharedDB.testing:
							client.SetValues(_idclients = row[0],_name = row[1])
						existed = True
						break
				if not existed:
					#create client
					print "New Client found in database CREATING client: "+str(row[0])
					#sharedDB.myProjects.append(sharedDB.projects.Projects(_idprojects = row[0],_name = row[1],_due_date = row[2],_idstatuses = row[3],_renderWidth = row[4],_renderHeight = row[5],_description = row[6],_folderLocation = row[7],_fps = row[8],_new = 0))
					myClient =sharedDB.clients.Clients(_idclients = row[0],_name = row[1],_new = 0)
					#add ip to ip list
					sharedDB.myClients.append(myClient)	
		
					#emit new client signal
					sharedDB.mySQLConnection.newClientSignal.emit(str(myClient._idclients))
					
				#remove row from list
				del self._clientsToBeParsed[0]
			else:
				break
		
		#ips
		while True:
			if len(self._ipsToBeParsed)>0:
				row = self._ipsToBeParsed[0]
				existed = False		
				#iterate through ip list
				for ip in sharedDB.myIps:
					#if id exists update entry
					if str(ip._idips) == str(row[0]):
						if not str(sharedDB.mySQLConnection.myIP) == str(row[4]) or sharedDB.testing:
							ip.SetValues(_idips = row[0],_name = row[1],_idclients = row[2])
						existed = True
						break
				if not existed:
					#create ip
					print "New IP found in database CREATING ip: "+str(row[0])
					#sharedDB.myProjects.append(sharedDB.projects.Projects(_idprojects = row[0],_name = row[1],_due_date = row[2],_idstatuses = row[3],_renderWidth = row[4],_renderHeight = row[5],_description = row[6],_folderLocation = row[7],_fps = row[8],_new = 0))
					myIp =sharedDB.ips.Ips(_idips = row[0],_name = row[1],_idclients = row[2],_new = 0)
					#add ip to ip list
					sharedDB.myIps.append(myIp)
					#iterate through projects
					for client in sharedDB.myClients:
						##if idprojects matches
						if client._idclients == myIp._idclients:
							###add to client's ips
							client._ips.append(myIp)
							break
		
		
					#emit new sequence signal
					sharedDB.mySQLConnection.newIpSignal.emit(str(myIp._idips))
					
				#remove row from list
				del self._ipsToBeParsed[0]
			else:
				break
	
		#Projects
		while True:
			#print "Queue Lenght: "+str(x)
			if len(self._projectsToBeParsed)>0:
				row = self._projectsToBeParsed[0]
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
					myProj =sharedDB.projects.Projects(_idprojects = row[0],_name = row[1],_due_date = row[2],_idstatuses = row[3],_renderWidth = row[4],_renderHeight = row[5],_description = row[6],_folderLocation = row[7],_fps = row[8],_idclients = row[11], _idips = row[12],_new = 0)
					#add project to project list
					sharedDB.myProjects.append(myProj)
					#iterate through projects
					for ip in sharedDB.myIps:
						##if idprojects matches
						if ip._idips == myProj._idips:
							###add to project's sequences
							#print "Adding Sequence "+str(mySeq._idsequences)+ " in Project " + str(proj._idprojects)
							ip._projects.append(myProj)
							break
		
		
					#emit new sequence signal
					sharedDB.mySQLConnection.newProjectSignal.emit(str(myProj._idprojects))
					
				#remove row from list
				del self._projectsToBeParsed[0]
			else:
				break
		
		#Phase Assignments           **** idphaseassignments, idprojects, idphases, startdate, enddate, idstatuses, archived, timestamp, lasteditedbyname, lasteditedbyip *****
		while True:
			#print "Queue Lenght: "+str(x)
			if len(self._phaseassignmentsToBeParsed)>0:
				row = self._phaseassignmentsToBeParsed[0]
				
				existed = False
				for phase in sharedDB.myPhaseAssignments:			
					#if id exists update entry
	
					if str(phase._idphaseassignments) == str(row[0]):
						if not str(sharedDB.mySQLConnection.myIP) == str(row[9]) or sharedDB.testing:
							phase.SetValues(_idphaseassignments = row[0],_idprojects = row[1],_idphases = row[2],_startdate = row[3],_enddate = row[4],_idstatuses = row[5],_archived = row[6],_timestamp = row[7])
						existed = True
						break
			
					
				if existed == False:
				#create phase assignment
					print "New PHASE ASSIGNMENT found in database CREATING phase assignment: "+str(row[0])
					#create instance of phase assignment class				
					myPhase =sharedDB.phaseAssignments.PhaseAssignments(_idphaseassignments = row[0],_idprojects = row[1],_idphases = row[2],_startdate = row[3],_enddate = row[4],_idstatuses = row[5],_archived = row[6],_timestamp = row[7], _new = 0)
					#add phase to phase assignment list
					sharedDB.myPhaseAssignments.append(myPhase)
					#iterate through projects
					for proj in sharedDB.myProjects:
						##if idprojects matches
						if proj._idprojects == myPhase._idprojects:
							###add to project's phases
							#print proj._idprojects
							proj._phases.append(myPhase)
							myPhase.project = proj
							###if current project in projectview update
							sharedDB.mySQLConnection.newPhaseAssignmentSignal.emit(str(myPhase._idphaseassignments))					
							break
					
				#remove row from list
				del self._phaseassignmentsToBeParsed[0]
			else:
				break
		
		#Sequences
		while True:
			#print "Queue Lenght: "+str(x)
			if len(self._sequencesToBeParsed)>0:
				row = self._sequencesToBeParsed[0]
				
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
				del self._sequencesToBeParsed[0]
			else:
				break
		
		while True:
			#print "Queue Lenght: "+str(x)
			if len(self._shotsToBeParsed)>0:
				row = self._shotsToBeParsed[0]
	
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
				del self._shotsToBeParsed[0]
			else:
				break
	
		#tasks
		while True:
			#print "Queue Lenght: "+str(x)
			if len(self._tasksToBeParsed)>0:
				row = self._tasksToBeParsed[0]
	
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
				del self._tasksToBeParsed[0]
			else:
				break
				
		#user assignments
		while True:
			#print "Queue Lenght: "+str(x)
			if len(self._userAssignmentsToBeParsed)>0:
				row = self._userAssignmentsToBeParsed[0]
				
				existed = False
				for assignment in sharedDB.myUserAssignments:
					if str(assignment._iduserassignments) == str(row[0]):						
						if not str(sharedDB.mySQLConnection.myIP) == str(row[6]) or sharedDB.testing:
							#iduserassignmentsidusers, idusers, assignmentid, assignmenttype, idstatuses, timestamp, lasteditedbyname, lasteditedbyip
							assignment.SetValues(_iduserassignments = row[0], _idusers = row[1],_assignmentid = row[2],_assignmenttype = row[3], _idstatuses = row[4], _timestamp = row[5])
						existed = True
						break
					
				if existed == False:
				#create project
					print "New USER ASSIGNMENT found in database CREATING user assignment id: "+str(row[0])
					#create instance of user assignment class				
					myUserAssignment =sharedDB.userassignments.UserAssignment(_iduserassignments = row[0], _idusers = row[1],_assignmentid = row[2],_assignmenttype = row[3],_idstatuses = row[4],_timestamp = row[5])
					#add task to task list
					sharedDB.myUserAssignments.append(myUserAssignment)
					'''
					#iterate through shots
					for shot in sharedDB.myShots:
						##if idsequences matches
						#print "Shot id:" +str(shot._idshots)+" Task Id shots: "+str(myTask._idshots)
						if shot._idshots == myUserAssignment._idshots:
							
							###add to shot's task list
							if shot._tasks is not None:
								#print "Appending shot: "+str(shot._idshots)+"'s task list"
								shot._tasks.append(myUserAssignment)
							else:
								#print "Creating shot: "+str(shot._idshots)+"'s task list"
								shot._tasks = [myUserAssignment]
	
							sharedDB.mySQLConnection.newTaskSignal.emit(str(myUserAssignment._idtasks))
							
							break
					'''	
						
					
				#remove row from list
				del self._userAssignmentsToBeParsed[0]
			else:
				if len(sharedDB.myProjects) and sharedDB.initialLoad == 0:
					print "First Load Complete!"
					sharedDB.initialLoad=1
					sharedDB.mySQLConnection.firstLoadComplete.emit()
					sharedDB.mySQLConnection.firstLoadCompleteInt = 1
				break
				
	
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
		
	'''	
	#parseList = sharedDB.mySQLConnection._clientsToBeParsed,existingEntries = sharedDB.myClients,idstring = 
	def CheckForDBUpdates(self,parseList,existingEntries):
		#clients
		while True:
			if len(parseList)>0:
				row = parseList[0]
				existed = False		
				#iterate through ip list
				for entry in existingEntries:
					#if id exists update entry
					if str(entry._idclients) == str(row[0]):
						if not str(sharedDB.mySQLConnection.myIP) == str(row[3]) or sharedDB.testing:
							client.SetValues(_idclients = row[0],_name = row[1])
						existed = True
						break
				if not existed:
					#create client
					print "New Client found in database CREATING client: "+str(row[0])
					#sharedDB.myProjects.append(sharedDB.projects.Projects(_idprojects = row[0],_name = row[1],_due_date = row[2],_idstatuses = row[3],_renderWidth = row[4],_renderHeight = row[5],_description = row[6],_folderLocation = row[7],_fps = row[8],_new = 0))
					myClient =sharedDB.clients.Clients(_idclients = row[0],_name = row[1],_new = 0)
					#add ip to ip list
					sharedDB.myClients.append(myClient)	
		
					#emit new client signal
					sharedDB.mySQLConnection.newClientSignal.emit(str(myClient._idclients))
					
				#remove row from list
				del parseList[0]
			else:
				break
	
	'''