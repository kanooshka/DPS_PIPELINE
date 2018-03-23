from DPSPipeline.database.connection import Connection
#import socket
import sharedDB
from PyQt4 import QtCore
from PyQt4.QtCore import QDate, QObject
from datetime import datetime,timedelta,date
import operator

class PhaseAssignments(QObject):
	phaseAssignmentChanged = QtCore.pyqtSignal(QtCore.QString)
	phaseAssignmentAdded = QtCore.pyqtSignal(QtCore.QString)
	userAssigned = QtCore.pyqtSignal()
	unassignedSignal = QtCore.pyqtSignal(QtCore.QString)
	
	def __init__(self,_idphaseassignments = 0,_idphases = 0,_idprojects = -1,_name = '', _startdate = '',_enddate = '',_idstatuses = 1,_progress = 0.0,_archived = 0, _updated = 0, _new = 0, _hoursalotted = 0, _assigned = 0, _description = '', _timestamp = datetime.now()):
		
		super(QObject, self).__init__()
		
		# define custom properties
		self._idphaseassignments           = _idphaseassignments
		self._idphases                     = _idphases
		self._idprojects                   = _idprojects
		self._startdate                    = _startdate
		self._enddate                      = _enddate
		self._progress                     = _progress
		self._idstatuses                   = _idstatuses
		self._hoursalotted		   = _hoursalotted
		self._assigned		   	   = _assigned
		self._archived                     = _archived
		self._description                  = _description
		self._timestamp		     	   = _timestamp
		
		self._hidden                 = False
		
		self._updated                      = _updated
		self._new                    	   = _new
		self._name                         = _name
		self._taskPerShot		   = 1
		self._type                         = "phaseassignment"
		self.project                       = None
		self._calendarWidgetItem	   = None
		self._tasks			   = {}
		self._iddepartments	           = 1
		
		self._estimatedHoursLeft           = -1
		
		self._weekdays = 0
		self.CalculateWeekdays()
		
		self.phaseAssignmentAdded.emit(str(self._idphaseassignments))
		
		#sharedDB.mySQLConnection.newTaskSignal.connect(self.AddTaskToList)
		
		self.SetPhaseValues()
		
		self._scarcityIndex = self._phase._scarcityIndex
		#self.updateAvailability()
		
		#connect to phase
		self._phase._phaseAssignments[str(self.id())] = self
		
		#print self._startdate.strftime("%Y-%m-%d")
		#print QDate(self._startdate).toString("yyyy-MM-dd")
		
		#******SWITCH TO USERASSIGNMENT, NOT WIDGET*********
		self._userAssignments = {}
		#self._unassigned = []
		
		#self.phaseAssignmentChanged.connect(sharedDB.myAvailabilityManager.CalculateBooking)
		
		self.UpdateVisibility()
	
	def __eq__(self, another):
		return hasattr(another, '_idphaseassignments') and self._idphaseassignments == another._idphaseassignments
	
	def __hash__(self):
		return hash(self._idphaseassignments)	
	
	def id(self):
		return self._idphaseassignments

	def Save(self):		

		if self._new:	
			self.AddPhaseAssignmentToDB()
			print "Phase '"+str(self._idphaseassignments)+"' Added to Database!"
			sharedDB.mySQLConnection.newPhaseAssignmentSignal.emit(str(self._idphaseassignments))
			self._new = 0
		elif self._updated:
			#print self._number+" Updated!"
			self.UpdatePhaseAssignmentInDB()
			self.UpdateVisibility()
			self.phaseAssignmentChanged.emit(str(self._idphaseassignments))
			if str(self._idphases) == '16':
				self.project._updated = 1
			print "Phase '"+str(self._idphaseassignments)+"' Updated in Database!"
			
			
			
			self._updated = 0
		
	def SetPhaseValues(self):
		if str(self._idphases) in sharedDB.myPhases:
			phase = sharedDB.myPhases[str(self._idphases)]

			self._phase = phase
			if self._name == '' or self._name == 'None' or self._name is None:
				self._name = phase._name
			self._taskPerShot = phase._taskPerShot
			self._iddepartments = phase._iddepartments
		
	def AddPhaseAssignmentToDB(self):
		if self._description is None:
			self._description = "None"

		if isinstance(self._description, QtCore.QString):
			self._description = unicode(self._description.toUtf8(), encoding="UTF-8")
		
		self._description = self._description.replace("\\","/")
		
		descr = self._description.replace("\'","\'\'")	
		
		rows,self._idphaseassignments = sharedDB.mySQLConnection.query("INSERT INTO phaseassignments (idprojects, idphases, name, startdate, enddate, idstatuses, archived, description, lasteditedbyname, lasteditedbyip, appsessionid, hoursalotted, assigned) VALUES ('"+str(self._idprojects)+"', '"+str(self._idphases)+"', '"+str(self._name)+"', '"+str(self._startdate)+"', '"+str(self._enddate)+"', '"+str(self._idstatuses)+"', '"+str(self._archived)+"', '"+descr+"', '"+str(sharedDB.currentUser._name)+"', '"+str(sharedDB.mySQLConnection.myIP)+"', '"+str(sharedDB.app.sessionId())+"', '"+str(self._hoursalotted)+"', '"+str(self._assigned)+"');","commit")	
	
		#self._idphaseassignments = sharedDB.mySQLConnection._lastInsertId
	
		sharedDB.myPhaseAssignments[str(self.id())] = self	
		
		self.phaseAssignmentAdded.emit(str(self._idphaseassignments))
		
	def UpdatePhaseAssignmentInDB (self):
		if self._description is None:
			self._description = "None"

		if isinstance(self._description, QtCore.QString):
			self._description = unicode(self._description.toUtf8(), encoding="UTF-8")
		
		self._description = self._description.replace("\\","/")
		
		descr = self._description.replace("\'","\'\'")
		
		sharedDB.mySQLConnection.query("UPDATE phaseassignments SET idprojects = '"+str(self._idprojects)+"', idphases = '"+str(self._idphases)+"', name = '"+str(self._name)+"', startdate = '"+str(self._startdate)+"', enddate = '"+str(self._enddate)+"', idstatuses = '"+str(self._idstatuses)+"', archived = '"+str(self._archived)+"', description = '"+descr+"', lasteditedbyname = '"+str(sharedDB.currentUser._name)+"', lasteditedbyip = '"+str(sharedDB.mySQLConnection.myIP)+"', appsessionid = '"+str(sharedDB.app.sessionId())+"', hoursalotted = '"+str(self._hoursalotted)+"', assigned = '"+str(self._assigned)+"' WHERE idphaseassignments = "+str(self._idphaseassignments)+";","commit")
		#print ("Updating phase in DB: "+str(self._idphaseassignments))
		
		
	def SetValues(self,_idphaseassignments = 0, _idprojects = '', _idphases = 1, _name = '', _startdate = '', _enddate = '',_idstatuses = 1 ,_archived = 0, _timestamp = '', _hoursalotted = 0, _assigned = 0, _description = ''):
		print ("Downloaded updated for PhaseAssignment '"+str(self._idphaseassignments)+"'")
		
		self._idphaseassignments             = _idphaseassignments
		self._idprojects                   = _idprojects
		self._idphases         = _idphases
		self._name		= _name
		self._startdate               = _startdate
		self._enddate               = _enddate
		self._idstatuses               = _idstatuses
		self._hoursalotted               = _hoursalotted
		self._assigned               = _assigned
		self._archived               = _archived
		self._description               = _description
		self._timestamp                    = _timestamp
		
		
		self.CalculateWeekdays()
		
		self.UpdateVisibility()
		
		self.phaseAssignmentChanged.connect(sharedDB.myAvailabilityManager.CalculateBooking)
		
		self.phaseAssignmentChanged.emit(str(self._idphaseassignments))
		
		#self.updateAvailability()
	
	def UpdateVisibility(self):
		if self._idstatuses == 5 or self._idstatuses == 6:
			self._hidden = True
		else:
			self._hidden = False
	
	def visibility(self):
		return not self._hidden
	
	'''	
	def AddTaskToList(self, task):
		if task._idphaseassignments == self._idphaseassignments:
			self._tasks.append(task)
			return
	'''
	def setHoursAlotted(self, sent):
		self._hoursalotted = sent
		self._updated = 1
	
	def hoursAlotted(self):
		return self._hoursalotted

	def idphaseassignments(self):
		return self._idphaseassignments

	def name(self):
		return self._name
	
	def idprojects(self):
		return self._idprojects
	
	
	def idstatuses(self):
		return self._idstatuses
	
	def setIdstatuses(self, value):
		self._idstatuses = value
		self._updated = 1

	def startDate(self):
		return self._startdate
	
	
	def endDate(self):
		return self._enddate
	
	def addUserAssignment(self, userAssignment ):	
		self._userAssignments[str(userAssignment.id())] = userAssignment
		#self.updateAssigned()
	
	def userAssignments(self):
		return self._userAssignments
	
	'''
	def addUserAssignmentTaskItem(self, taskitem):
		self._userAssignments.append(taskitem)
		#print "added user assignment"
		self.userAssigned.emit()
		
	def userAssignmentTaskItems(self):
		return self._userAssignments
	'''	
	def iddepartments(self):
		return self._iddepartments

	def assigned(self):
		return self._assigned
	
	def setAssigned(self, value):
		if str(self.assigned())!= str(value):
			self._assigned = value
			self._updated = 1
	
	def idusers(self):
		idusers = []
		for ua in self._userAssignments.values():
			#print ua.idUsers()
			idusers.append(str(ua.idUsers()))
			
		return idusers
	
	def setName(self, newname):
		self._name = newname
		self._updated = 1
	
	'''
	def updateAvailability(self):
		self._availability = {}
		for n in range(int ((self._enddate - self._startdate).days)+1):
			#print self._startdate + timedelta(n)
			self._availability[str(self._startdate + timedelta(n))] = 10
			#booking = sharedDB.myAvailabilityManager.AddBookingAtDate(str(self._startdate + timedelta(n)))
			
		view = sharedDB.calendarview._departmentXGanttWidget.uiGanttVIEW.scene()
		view.setDirty()
		view.update()
		#view.syncView()
	'''
	
	def type(self):
		return self._type
	

	def updateAssigned(self):
		for userids in self._userAssignments:
			user = self._userAssignments[str(userids)]
			if user.hours()>0:
				self.setAssigned(1)
				self.userAssigned.emit()
				return
			
		self.setAssigned(0)
		self.unassignedSignal.emit(str(self.idphaseassignments()))
		return
	
	def CalculateWeekdays(self):
		daygenerator = (self._startdate + timedelta(x) for x in xrange((self._enddate - self._startdate).days + 1))

		self._weekdays = sum(day.weekday() < 5 for day in daygenerator)
		
		#print "Num Weekdays: "+ str(self._weekdays)
	
	def WeekdaysFromStartDate(self, startdate = None):
		if startdate == None:
			startdate = self._startdate
			
		daygenerator = (startdate + timedelta(x) for x in xrange((self._enddate - startdate).days + 1))

		return sum(day.weekday() < 5 for day in daygenerator)