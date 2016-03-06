import mysql.connector
import sharedDB
#import threading
from datetime import date,datetime,timedelta
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

		if sharedDB.currentDate != date.today():
			sharedDB.currentDate = date.today()
			print "Changing date to "+str(date.today())
			sharedDB.mySQLConnection.dateChanged.emit()

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
				
				#sharedDB.myStatuses = sharedDB.statuses.GetStatuses()				
				#sharedDB.myPhases = sharedDB.phases.GetPhaseNames()
				#sharedDB.myUsers = sharedDB.users.GetAllUsers()
			
			self._queries.append(["SELECT","departments","SELECT iddepartments,name,appsessionid FROM departments WHERE timestamp > \""+str(sharedDB.lastUpdate)+"\""])			
			self._queries.append(["SELECT","statuses","SELECT idstatuses,name,appsessionid FROM statuses WHERE timestamp > \""+str(sharedDB.lastUpdate)+"\""])			
			self._queries.append(["SELECT","phases","SELECT idphases,name,ganttChartBGColor,ganttChartTextColor,manHoursToMinuteRatio,idDepartment,taskPerShot,defaultTaskStatus,appsessionid FROM phases WHERE timestamp > \""+str(sharedDB.lastUpdate)+"\""])			
			self._queries.append(["SELECT","clients","SELECT idclients, name, lasteditedbyname, lasteditedbyip, appsessionid FROM clients WHERE timestamp > \""+str(sharedDB.lastUpdate)+"\""])			
			self._queries.append(["SELECT","ips","SELECT idips, name, idclients, lasteditedbyname, lasteditedbyip, appsessionid FROM ips WHERE timestamp > \""+str(sharedDB.lastUpdate)+"\""])			
			self._queries.append(["SELECT","projects","SELECT idprojects, name, due_date, idstatuses, renderWidth, renderHeight, description, statusDescription, folderLocation, fps, lasteditedbyname, lasteditedbyip, idclients, idips, appsessionid FROM projects WHERE timestamp > \""+str(sharedDB.lastUpdate)+"\""])			
			self._queries.append(["SELECT","temprigs","SELECT idtemprigs, name, idprojects, setNumber, type, status, description, folderLocation, appsessionid FROM temprigs WHERE timestamp > \""+str(sharedDB.lastUpdate)+"\""])			
			self._queries.append(["SELECT","phaseassignments","SELECT idphaseassignments,idprojects, idphases, startdate, enddate, idstatuses, archived, description, timestamp, lasteditedbyname, lasteditedbyip, appsessionid, hoursalotted, assigned FROM phaseassignments WHERE timestamp > \""+str(sharedDB.lastUpdate)+"\""])			
			self._queries.append(["SELECT","sequences","SELECT idsequences, number, idstatuses, description, timestamp, idprojects, lasteditedbyname, lasteditedbyip, appsessionid FROM sequences WHERE timestamp > \""+str(sharedDB.lastUpdate)+"\""])			
			self._queries.append(["SELECT","shots","SELECT idshots, number, startframe, endframe, description, idstatuses, timestamp, idprojects, idsequences, lasteditedbyname, lasteditedbyip, shotnotes, appsessionid FROM shots WHERE timestamp > \""+str(sharedDB.lastUpdate)+"\""])			
			self._queries.append(["SELECT","tasks","SELECT idtasks, idphaseassignments, idprojects, idshots, idusers, idphases, timealotted, idsequences, duedate, percentcomplete, approved, timestamp, lasteditedbyname, lasteditedbyip, status, appsessionid FROM tasks WHERE timestamp > \""+str(sharedDB.lastUpdate)+"\""])
			self._queries.append(["SELECT","userassignments","SELECT iduserassignments, idusers, assignmentid, assignmenttype, idstatuses, timestamp, lasteditedbyname, lasteditedbyip, appsessionid, hours FROM userassignments WHERE timestamp > \""+str(sharedDB.lastUpdate)+"\""])
			self._queries.append(["SELECT","hours","SELECT idhours,idusers, idphaseassignments, idprojects, description, hours, date, timestamp, lasteditedbyname, lasteditedbyip, appsessionid FROM hours WHERE timestamp > \""+str(sharedDB.lastUpdate)+"\""])
			
			while True:
				if len(self._queries)>0:
					try:
						self._currentQueryType =  self._queries[0][0]
						self._currentDB = self._queries[0][1]		
						self._currentQuery = self._queries[0][2]
						
						rows,lastrowid = sharedDB.mySQLConnection.query(self._currentQuery)
					
						if self._currentDB == "departments":						
							rows.sort(key=lambda x: x[2])
							sharedDB.mySQLConnection._departmentsToBeParsed.extend(rows)
						elif self._currentDB == "statuses":						
							rows.sort(key=lambda x: x[2])
							sharedDB.mySQLConnection._statusesToBeParsed.extend(rows)
						elif self._currentDB == "phases":						
							rows.sort(key=lambda x: x[2])
							sharedDB.mySQLConnection._phasesToBeParsed.extend(rows)
						elif self._currentDB == "clients":						
							rows.sort(key=lambda x: x[2])
							sharedDB.mySQLConnection._clientsToBeParsed.extend(rows)
						elif self._currentDB == "ips":
							rows.sort(key=lambda x: x[2])
							sharedDB.mySQLConnection._ipsToBeParsed.extend(rows)
						elif self._currentDB == "projects":
							rows = sorted(rows, key=lambda x: x[2])
							sharedDB.mySQLConnection._projectsToBeParsed.extend(rows)
						elif self._currentDB == "temprigs":
							rows = sorted(rows, key=lambda x: x[2])
							sharedDB.mySQLConnection._tempRigsToBeParsed.extend(rows)							
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
						elif self._currentDB == "hours":
							sharedDB.mySQLConnection._hoursToBeParsed.extend(rows)
							
						del self._queries[0]
					except:
						print "MySQL Connection Failed....trying again"	
				else:
					break
			
			#parse updates
			sharedDB.mySQLConnection.ParseUpdatesFromDB()
			
			#save changes				
			for proj in sharedDB.myProjects :		
			    sharedDB.myProjects[str(proj)].Save()
			
			for ua in sharedDB.myUserAssignments:
				sharedDB.myUserAssignments[str(ua)].Save()
			
		else:
			sharedDB.mySQLConnection.wrongVersionSignal.emit()
			time.sleep(99999)
	
		time.sleep(sharedDB.mySQLConnection._autoUpdateFrequency)
		
	

    
class Connection(QObject):
	newUserSignal = QtCore.pyqtSignal(QtCore.QString)
	newDepartmentSignal = QtCore.pyqtSignal(QtCore.QString)
	newStatusSignal = QtCore.pyqtSignal(QtCore.QString)
	newPhaseSignal = QtCore.pyqtSignal(QtCore.QString)
	newClientSignal = QtCore.pyqtSignal(QtCore.QString)
	newIpSignal = QtCore.pyqtSignal(QtCore.QString)
	newProjectSignal = QtCore.pyqtSignal(QtCore.QString)
	newTempRigSignal = QtCore.pyqtSignal(QtCore.QString)
	newPhaseAssignmentSignal = QtCore.pyqtSignal(QtCore.QString)
	newSequenceSignal = QtCore.pyqtSignal(QtCore.QString)
	newShotSignal = QtCore.pyqtSignal(QtCore.QString)
	newTaskSignal = QtCore.pyqtSignal(QtCore.QString)
	newUserAssignmentSignal = QtCore.pyqtSignal(QtCore.QString)
	newHoursSignal = QtCore.pyqtSignal(QtCore.QString)
	wrongVersionSignal = QtCore.pyqtSignal()
	firstLoadComplete = QtCore.pyqtSignal()
	
	dateChanged = QtCore.pyqtSignal()

	def __init__(self,_user = '', _password = ''):
		
		super(QObject, self).__init__()
		
		self.firstLoadComplete.connect(sharedDB.myAvailabilityManager.CalculateBooking)
		
		# define custom properties
		self._user = _user
		self._password = _password
		self._localhost = '10.9.21.12'
		self._remotehost = '174.79.161.184'
		
		sharedDB.mySQLConnection = self
		
		if sharedDB.localDB:
			self._localhost = 'localhost'
		elif sharedDB.remote:
			self.localhost = self._remotehost
		
		self._host = self._localhost
		self._remote = 0
		self._autoUpdateFrequency = 2
	
		self.myIP = socket.gethostbyname(socket.gethostname())
		
		#self._lastInsertId = ''		
		
		if sharedDB.localDB:
			self._host = 'localhost'
		if sharedDB.testDB:
			self._database = 'testDB'
		else:
			self._database = 'dpstudio'
		
		self.wrongVersionSignal.connect(self.wrongVersion)
		
		self._departmentsToBeParsed = []
		self._statusesToBeParsed = []
		self._phasesToBeParsed = []
		self._clientsToBeParsed = []
		self._ipsToBeParsed = []
		self._projectsToBeParsed = []
		self._phaseassignmentsToBeParsed = []
		self._sequencesToBeParsed = []
		self._shotsToBeParsed = []
		self._phaseAssignmentsToBeParsed = []
		self._tasksToBeParsed = []
		self._userAssignmentsToBeParsed = []
		self._hoursToBeParsed = []
		self._tempRigsToBeParsed = []
		
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
		return mysql.connector.connect(user = self._user, password = self._password, host = self._host, database = self._database)

	def query(self, query = "", queryType = "fetchAll"):
		rows = []
		cnx = self.openConnection()
		cursor = cnx.cursor()
		
		limitAmount = 20

		#self._lastInsertId = cursor.lastrowid
		if queryType == "fetchAll":
			loop = 1
			while loop:
				#print query+" LIMIT "+str(limitAmount)
				cursor.execute(query+" LIMIT "+str(limitAmount)+" OFFSET "+str((loop-1)*limitAmount))
				newRows = cursor.fetchall()
				if not len(newRows):
					loop = 0
				else:
					loop += 1
				rows.extend(newRows)
		elif queryType == "commit":
			cursor.execute(query)
			if not sharedDB.disableSaving:
				cnx.commit()
		
		
		cursor.close()
		
		cnx.close()

		return rows,cursor.lastrowid

	def GetTimestamp(self):
		rows = ""
		cnx = self.openConnection()
		cursor = cnx.cursor()
		cursor.execute("SELECT NOW()")
		rows = cursor.fetchall()		
		
		cursor.close()
		
		cnx.close()

		return rows[0]		
	
	def ParseUpdatesFromDB(self):
		#sharedDB.blockSignals = 1
		
		#departments
		while True:
			if len(self._departmentsToBeParsed)>0:
				row = self._departmentsToBeParsed[0]			
			
				if str(row[0]) in sharedDB.myDepartments:
					department = sharedDB.myDepartments[str(row[0])]
					#if not str(sharedDB.app.sessionId()) == str(row[2]) or sharedDB.testing:
					#	department.SetValues(_iddepartments = row[0],_name = row[1])
				else:
					#create department
					print "New Department found in database CREATING department: "+str(row[0])
					myDepartment =sharedDB.departments.Departments(_iddepartments = row[0],_name = row[1])
					#add department to department list
					sharedDB.myDepartments[str(row[0])] = myDepartment
					
					#emit new department signal
					sharedDB.mySQLConnection.newDepartmentSignal.emit(str(myDepartment._iddepartments))
				
				#remove row from list
				del self._departmentsToBeParsed[0]
			else:
				break		
		#statuses
		while True:
			if len(self._statusesToBeParsed)>0:
				row = self._statusesToBeParsed[0]			
			
				if str(row[0]) in sharedDB.myStatuses:
					status = sharedDB.myStatuses[str(row[0])]
					#if not str(sharedDB.app.sessionId()) == str(row[3]) or sharedDB.testing:
						#phase.SetValues(_idstatuses = row[0],_name = row[1])
				else:
					#create status
					print "New Status found in database CREATING status: "+str(row[0])
					myStatus =sharedDB.statuses.Statuses(_idstatuses = row[0],_name = row[1])
					#add status to status list
					sharedDB.myStatuses[str(row[0])] = myStatus
					
					#emit new status signal
					sharedDB.mySQLConnection.newStatusSignal.emit(str(myStatus._idstatuses))
					
				#remove row from list
				del self._statusesToBeParsed[0]
			else:
				break
		#phases  _idphases , _name = '', _ganttChartBGColor, _ganttChartTextColor, _manHoursToMinuteRatio, _iddepartments, _taskPerShot, _defaultTaskStatus
		while True:
			if len(self._phasesToBeParsed)>0:
				row = self._phasesToBeParsed[0]			
			
				if str(row[0]) in sharedDB.myPhases:
					phase = sharedDB.myPhases[str(row[0])]
					if not str(sharedDB.app.sessionId()) == str(row[8]) or sharedDB.testing:
						phase.SetValues(_idphases = row[0],_name = row[1],_ganttChartBGColor = row[2],_ganttChartTextColor = row[3],_manHoursToMinuteRatio = row[4],_iddepartments = row[5],_taskPerShot = row[6],_defaultTaskStatus = row[7])
				else:
					#create phase
					print "New Phase found in database CREATING phase: "+str(row[0])
					myPhase =sharedDB.phases.Phases(_idphases = row[0],_name = row[1],_ganttChartBGColor = row[2],_ganttChartTextColor = row[3],_manHoursToMinuteRatio = row[4],_iddepartments = row[5],_taskPerShot = row[6],_defaultTaskStatus = row[7])
					#add phase to phase list
					sharedDB.myPhases[str(row[0])] = myPhase
					
					#emit new phase signal
					sharedDB.mySQLConnection.newPhaseSignal.emit(str(myPhase._idphases))
					
				#remove row from list
				del self._phasesToBeParsed[0]
			else:
				break
		#clients
		while True:
			if len(self._clientsToBeParsed)>0:
				row = self._clientsToBeParsed[0]			
			
				if str(row[0]) in sharedDB.myClients:
					client = sharedDB.myClients[str(row[0])]
					if not str(sharedDB.app.sessionId()) == str(row[4]) or sharedDB.testing:
						client.SetValues(_idclients = row[0],_name = row[1])
				else:
					#create client
					print "New Client found in database CREATING client: "+str(row[0])
					myClient =sharedDB.clients.Clients(_idclients = row[0],_name = row[1],_new = 0)
					#add ip to ip list
					sharedDB.myClients[str(row[0])] = myClient
					
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

				if str(row[0]) in sharedDB.myIps:
					ip = sharedDB.myIps[str(row[0])]
					if not str(sharedDB.app.sessionId()) == str(row[5]) or sharedDB.testing:
						ip.SetValues(_idips = row[0],_name = row[1],_idclients = row[2])
				else:
					#create ip
					print "New IP found in database CREATING ip: "+str(row[0])
					#sharedDB.myProjects.append(sharedDB.projects.Projects(_idprojects = row[0],_name = row[1],_due_date = row[2],_idstatuses = row[3],_renderWidth = row[4],_renderHeight = row[5],_description = row[6],_folderLocation = row[7],_fps = row[8],_new = 0))
					myIp =sharedDB.ips.Ips(_idips = row[0],_name = row[1],_idclients = row[2],_new = 0)
					#add ip to ip list
					sharedDB.myIps[str(row[0])] = myIp
					
					#connect ip to client
					if str(myIp._idclients) in sharedDB.myClients:
						client = sharedDB.myClients[str(myIp._idclients)]
						if str(myIp.id()) not in client._ips:
							client._ips[str(myIp.id())] = myIp

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

				if str(row[0]) in sharedDB.myProjects:
					proj = sharedDB.myProjects[str(row[0])]
					if not str(sharedDB.app.sessionId()) == str(row[14]) or sharedDB.testing:
						proj.SetValues(_idprojects = row[0],_name = row[1],_due_date = row[2],_idstatuses = row[3],_renderWidth = row[4],_renderHeight = row[5],_description = row[6],_statusDescription = row[7],_folderLocation = row[8],_fps = row[9],_idclients = row[12], _idips = row[13])

				else:
					#create project
					print "New PROJECT found in database CREATING project: "+str(row[0])
					#sharedDB.myProjects.append(sharedDB.projects.Projects(_idprojects = row[0],_name = row[1],_due_date = row[2],_idstatuses = row[3],_renderWidth = row[4],_renderHeight = row[5],_description = row[6],_folderLocation = row[7],_fps = row[8],_new = 0))
					myProj =sharedDB.projects.Projects(_idprojects = row[0],_name = row[1],_due_date = row[2],_idstatuses = row[3],_renderWidth = row[4],_renderHeight = row[5],_description = row[6],_statusDescription = row[7],_folderLocation = row[8],_fps = row[9],_idclients = row[12], _idips = row[13],_new = 0)
					#add project to project list
					sharedDB.myProjects[str(row[0])] = myProj
					#iterate through projects
					
					#connect project to ip
					if str(myProj._idips) in sharedDB.myIps:
						ip = sharedDB.myIps[str(myProj._idips)]
						if str(myProj.id()) not in ip._projects:
							ip._projects[str(myProj.id())] = myProj

					#emit new sequence signal
					sharedDB.mySQLConnection.newProjectSignal.emit(str(myProj._idprojects))
					
				#remove row from list
				del self._projectsToBeParsed[0]
			else:
				break
		
		#TempRigs  ************   idtemprigs, name, idprojects, setNumber, type, status, description, folderLocation, appsessionid
		while True:
			#print "Queue Lenght: "+str(x)
			if len(self._tempRigsToBeParsed)>0:
				row = self._tempRigsToBeParsed[0]
				#print "Adding temp rig "+str(row[1])

				if str(row[0]) in sharedDB.myTempRigs:
					rig = sharedDB.myTempRigs[str(row[0])]
					if not str(sharedDB.app.sessionId()) == str(row[8]) or sharedDB.testing:
						rig.SetValues(_idtemprigs = row[0],_name = row[1],_idprojects = row[2],_setnumber = row[3],_typ = row[4],_status = row[5],_description = row[6],_folderLocation = row[7])

				else:
					#create rig
					print "New RIG found in database CREATING rig: "+str(row[1])					
					myRig =sharedDB.temprigs.TempRigs(_idtemprigs = row[0],_name = row[1],_idprojects = row[2],_setnumber = row[3],_typ = row[4],_status = row[5],_description = row[6],_folderLocation = row[7],_new = 0)
					#add rig to rig list
					sharedDB.myTempRigs[str(row[0])] = myRig
					
					#connect rig to project
					if str(myRig._idprojects) in sharedDB.myProjects:
						proj = sharedDB.myProjects[str(myRig._idprojects)]
						if str(myRig.id()) not in proj._rigs:
							proj._rigs[str(myRig.id())] = myRig

					#emit new sequence signal
					sharedDB.mySQLConnection.newTempRigSignal.emit(str(myRig._idtemprigs))
					
				#remove row from list
				del self._tempRigsToBeParsed[0]
			else:
				break
		
		
		#Phase Assignments           **** idphaseassignments, idprojects, idphases, startdate, enddate, idstatuses, archived, description, timestamp, lasteditedbyname, lasteditedbyip *****
		while True:
			#print "Queue Lenght: "+str(x)
			if len(self._phaseassignmentsToBeParsed)>0:
				row = self._phaseassignmentsToBeParsed[0]
				
				if str(row[0]) in sharedDB.myPhaseAssignments:
					phase = sharedDB.myPhaseAssignments[str(row[0])]
					if not str(sharedDB.app.sessionId()) == str(row[11]) or sharedDB.testing:
						phase.SetValues(_idphaseassignments = row[0],_idprojects = row[1],_idphases = row[2],_startdate = row[3],_enddate = row[4],_idstatuses = row[5],_archived = row[6],_description = row[7],_timestamp = row[8],_hoursalotted = row[12],_assigned = row[13])

				else:
					#create phase assignment
					print "New PHASE ASSIGNMENT found in database CREATING phase assignment: "+str(row[0])
					#create instance of phase assignment class				
					myPhase =sharedDB.phaseAssignments.PhaseAssignments(_idphaseassignments = row[0],_idprojects = row[1],_idphases = row[2],_startdate = row[3],_enddate = row[4],_idstatuses = row[5],_archived = row[6],_description = row[7],_timestamp = row[8], _new = 0, _hoursalotted = row[12], _assigned = row[13])
					#add phase to phase assignment list
					sharedDB.myPhaseAssignments[str(row[0])] = myPhase
					
					#connect phaseassignment to project
					if str(myPhase._idprojects) in sharedDB.myProjects:
						proj = sharedDB.myProjects[str(myPhase._idprojects)]
						if str(myPhase.id()) not in proj._phases:
							proj._phases[str(myPhase.id())] = myPhase
							myPhase.project = proj
							myPhase.phaseAssignmentChanged.connect(proj.UpdateStartDate)

					sharedDB.mySQLConnection.newPhaseAssignmentSignal.emit(str(myPhase._idphaseassignments))
					
				#remove row from list
				del self._phaseassignmentsToBeParsed[0]
			else:
				break
		
		#Sequences
		while True:
			#print "Queue Lenght: "+str(x)
			if len(self._sequencesToBeParsed)>0:
				row = self._sequencesToBeParsed[0]
	
				if str(row[0]) in sharedDB.mySequences:
					seq = sharedDB.mySequences[str(row[0])]
					if not str(sharedDB.app.sessionId()) == str(row[8]) or sharedDB.testing:
						seq.SetValues(_idsequences = row[0],_number = row[1],_idstatuses = row[2],_description = row[3],_timestamp = row[4])

				else:
				#create project
					print "New SEQUENCE found in database CREATING sequence: "+str(row[0])
					#create instance of sequence class				
					mySeq =sharedDB.sequences.Sequences(_idsequences = row[0],_number = row[1],_idstatuses = row[2],_description = row[3],_timestamp = row[4], _idprojects = row[5], _new = 0)
					#add sequence to sequence list
					sharedDB.mySequences[str(row[0])] = mySeq
					
					#connect sequence to project
					if str(mySeq._idprojects) in sharedDB.myProjects:
						proj = sharedDB.myProjects[str(mySeq._idprojects)]
						if str(mySeq.id()) not in proj._sequences:
							proj._sequences[str(mySeq.id())] = mySeq
					
					sharedDB.mySQLConnection.newSequenceSignal.emit(str(mySeq._idsequences))
					
				#remove row from list
				del self._sequencesToBeParsed[0]
			else:
				break
		
		#shots
		while True:
			#print "Queue Lenght: "+str(x)
			if len(self._shotsToBeParsed)>0:
				row = self._shotsToBeParsed[0]
	
				if str(row[0]) in sharedDB.myShots:
					shot = sharedDB.myShots[str(row[0])]						
					if not str(sharedDB.app.sessionId()) == str(row[12]) or sharedDB.testing:
						shot.SetValues(_idshots = row[0],_number = row[1],_startframe = row[2],_endframe = row[3],_description = row[4],_idstatuses = row[5],_timestamp = row[6],_idprojects = row[7],_idsequences = row[8], _shotnotes = row[11])

				else:
				#create project
					print "New SHOT found in database CREATING shot: "+str(row[0])
					#create instance of shot class				
					myShot =sharedDB.shots.Shots(_idshots = row[0],_number = row[1],_startframe = row[2],_endframe = row[3],_description = row[4],_idstatuses = row[5],_timestamp = row[6],_idprojects = row[7],_idsequences = row[8], _new = 0, _shotnotes = row[11])
					#add shot to shot list
					sharedDB.myShots[str(row[0])] = myShot
					
					
					#iterate through sequences
					if myShot._idsequences == 0:
						#connect shot to project
						if str(myShot._idprojects) in sharedDB.myProjects:
							proj = sharedDB.myProjects[str(myShot._idprojects)]
							if str(myShot.id()) not in proj._sequences:
								proj._images[str(myShot.id())] = myShot
					else:
						#connect shot to sequence
						if str(myShot._idsequences) in sharedDB.mySequences:
							seq = sharedDB.mySequences[str(myShot._idsequences)]
							if str(myShot.id()) not in seq._shots:
								seq._shots[str(myShot.id())] = myShot
					
					sharedDB.mySQLConnection.newShotSignal.emit(str(myShot._idshots))
							
					
				#remove row from list
				del self._shotsToBeParsed[0]
			else:
				break
	
		#tasks
		while True:
			#print "Queue Lenght: "+str(x)
			if len(self._tasksToBeParsed)>0:
				row = self._tasksToBeParsed[0]

				if str(row[0]) in sharedDB.myTasks:
					task = sharedDB.myTasks[str(row[0])]						
					if not str(sharedDB.app.sessionId()) == str(row[15]) or sharedDB.testing:
						#idtasks, idphaseassignments, idprojects, idshots, idusers, idphases, timealotted, idsequences, duedate, percentcomplete, approved, timestamp
						task.SetValues(_idtasks = row[0],_idphaseassignments = row[1],_idprojects = row[2],_idshots = row[3],_idusers = row[4],_idphases = row[5],_timealotted = row[6], _idsequences = row[7], _duedate = row[8], _percentcomplete = row[9], _approved = row[10], _timestamp = row[11], _status = row[14])
					
				else:
				#create project
					print "New TASK found in database CREATING task: "+str(row[0])
					#create instance of shot class				
					myTask =sharedDB.tasks.Tasks(_idtasks = row[0],_idphaseassignments = row[1],_idprojects = row[2],_idshots = row[3],_idusers = row[4],_idphases = row[5],_timealotted = row[6], _idsequences = row[7], _duedate = row[8], _percentcomplete = row[9], _approved = row[10], _timestamp = row[11], _status = row[14])
					#add task to task list
					sharedDB.myTasks[str(row[0])] = myTask
					#iterate through shots
					
					#connect task to phase
					if str(myTask._idphaseassignments) in sharedDB.myPhaseAssignments:
						phase = sharedDB.myPhaseAssignments[str(myTask._idphaseassignments)]
						if str(myTask.id()) not in phase._tasks:
							phase._tasks[str(myTask.id())] = myTask
	
					#connect task to shot
					if str(myTask._idshots) in sharedDB.myShots:
						shot = sharedDB.myShots[str(myTask._idshots)]
						if str(myTask.id()) not in shot._tasks:
							shot._tasks[str(myTask.id())] = myTask
					
					#connect task to task
					if str(myTask._parenttaskid) in sharedDB.myTasks:
						t = sharedDB.myTasks[str(myTask._parenttaskid)]
						if str(myTask.id()) not in t.childTasks:
							t.childTasks[str(myTask.id())] = myTask

					sharedDB.mySQLConnection.newTaskSignal.emit(str(myTask._idtasks))
				
					
				#remove row from list
				del self._tasksToBeParsed[0]
			else:
				break
				
		#user assignments
		while True:
			#print "Queue Lenght: "+str(x)
			if len(self._userAssignmentsToBeParsed)>0:
				row = self._userAssignmentsToBeParsed[0]

				if str(row[0]) in sharedDB.myUserAssignments:
					assignment = sharedDB.myUserAssignments[str(row[0])]						
					if not str(sharedDB.app.sessionId()) == str(row[8]) or sharedDB.testing:
						#iduserassignmentsidusers, idusers, assignmentid, assignmenttype, idstatuses, timestamp, lasteditedbyname, lasteditedbyip
						assignment.SetValues(_iduserassignments = row[0], _idusers = row[1],_assignmentid = row[2],_assignmenttype = row[3], _idstatuses = row[4], _timestamp = row[5], _hours = row[9])
					
				else:
				#create User Assignment
					print "New USER ASSIGNMENT found in database CREATING user assignment id: "+str(row[0])
					#create instance of user assignment class				
					myUserAssignment =sharedDB.userassignments.UserAssignment(_iduserassignments = row[0], _idusers = row[1],_assignmentid = row[2],_assignmenttype = row[3],_idstatuses = row[4],_timestamp = row[5], _hours = row[9])
					#add task to task list
					sharedDB.myUserAssignments[str(row[0])] = myUserAssignment
					sharedDB.mySQLConnection.newUserAssignmentSignal.emit(str(myUserAssignment._iduserassignments))
					
		
				#remove row from list
				del self._userAssignmentsToBeParsed[0]
			else:
				break
		
		#hours
		while True:
			#print "Queue Lenght: "+str(x)
			if len(self._hoursToBeParsed)>0:
				row = self._hoursToBeParsed[0]
				
				existed = False
				for hours in sharedDB.myHours:
					if str(hours._idhours) == str(row[0]):						
						if not str(sharedDB.app.sessionId()) == str(row[9]) or sharedDB.testing:
							#idhours,idusers, idphaseassignments, idprojects, description, hours, date, timestamp, lasteditedbyname, lasteditedbyip, appsessionid
							assignment.SetValues(_idhours = row[0], _idusers = row[1],_idphaseassignments = row[2],_idprojects = row[3], _description = row[4], _hours = row[5], _date = row[6], _timestamp = row[7])
						existed = True
						break
					
				if existed == False:
				#create Hours
					print "New HOURS found in database CREATING hour id: "+str(row[0])
					#create instance of user assignment class				
					myHours =sharedDB.hours.Hours(_idhours = row[0], _idusers = row[1],_idphaseassignments = row[2],_idprojects = row[3],_description = row[4],_hours = row[5],_date = row[6], _timestamp = row[7])

					sharedDB.myHours[str(row[0])] = myHours
					sharedDB.mySQLConnection.newHoursSignal.emit(str(myHours._idhours))
					
				#remove row from list
				del self._hoursToBeParsed[0]
					
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