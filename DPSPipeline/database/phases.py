import mysql.connector
import sharedDB
from DPSPipeline.database.connection import Connection
from DPSPipeline.database import users
from PyQt4 import QtCore
import operator

'''
'1', 'Storyboarding'
'2', 'Modeling'
'3', 'Rigging'
'4', 'Layout'
'5', 'Blocking'
'6', 'Animation'
'7', 'Approval'
'8', 'Set Dressing'
'9', 'FX'
'10', 'Sound(Final)'
'11', 'Texturing'
'12', 'Shotprep'
'13', 'Lookdev'
'14', 'Lighting'
'15', 'Rendering'
'16', 'DUE'
'17', 'Sound (Rough)'
'''

sortedPhaseList = []
phaseDictToSort = {}

class Phases():
	
	def __init__(self,_idphases = 0,_name = '',_ganttChartBGColor = '255,0,0',_ganttChartTextColor = '0,0,0',_manHoursToMinuteRatio = "0.1",_iddepartments = 0,_taskPerShot = 1,_defaultTaskStatus = 0):
		
		# define custom properties
		self._idphases           = _idphases
		self._name               = _name
		self._ganttChartBGColor    = _ganttChartBGColor
		self._ganttChartTextColor    = _ganttChartTextColor
		self._manHoursToMinuteRatio    = _manHoursToMinuteRatio
		self._iddepartments    = _iddepartments
		self._taskPerShot     = _taskPerShot
		self._defaultTaskStatus = _defaultTaskStatus
		self._type                   = "phase"
		
		self._phaseAssignments = {}
		#self._capacity = {}
		
		self._availability = {}
		
		self._users = {}
		self.ConnectUsers()
		
		self.CalculateCapacityPerDay()
		
		if "0" in sharedDB.currentUser.departments() or str(_iddepartments) in sharedDB.currentUser.departments() or sharedDB.currentUser._idPrivileges == 1:
			self._visible = 1
		else:
			self._visible = 0
		
		
		self._scarcityIndex = 0
		self.addToSortedPhaseList()
		
		#sharedDB.mySQLConnection.newPhaseSignal.emit(str(self._idphases))
	
	def __eq__(self, another):
		return hasattr(another, '_idphases') and self._idphases == another._idphases
	
	def __hash__(self):
		return hash(self._idphases)
	
	def id(self):
		return self._idphases
	
	def name(self):
		return self._name

	def isVisible(self):
		return self._visible

	def addToSortedPhaseList(self):
		global phaseDictToSort
		
		count = 0
		
		#iterate through users, add 1 for each phase assignment they can do
		for uid in users.sortedUserList:
			for pid in sharedDB.myUsers[str(uid[0])]._phases:
				if str(pid) == str(self.id()):
					count = count+1
					
		if count > 0:
			phaseDictToSort[str(self.id())] = count		
			self.sortPhaseListByScarcity()
	
	def sortPhaseListByScarcity(self):
		global sortedPhaseList
		
		sortedPhaseList = sorted(phaseDictToSort.items(), key=operator.itemgetter(1))
		
		for x in range(0,len(sortedPhaseList)):
			if str(sortedPhaseList[x][0]) == str(self.id()):
				self._scarcityIndex = x
				break
		#print sortedPhaseList
		
	def ConnectUsers(self):
		for user in sharedDB.myUsers.values():
			if str(self.id()) in user._phases and str(user._active) == "1":
				self._users[str(user.id())] = user

	def CalculateCapacityPerDay(self):
		self._capacity = 0
		
		for u in self._users.values():
			self._capacity = self._capacity+8
		
		#print "Phase "+self._name+" capacity: "+str(self._capacity)	
			
	def SetValues(self,_idphases , _name , _ganttChartBGColor, _ganttChartTextColor, _manHoursToMinuteRatio, _iddepartments, _taskPerShot, _defaultTaskStatus):
		print ("Downloaded updated for Phase '"+str(self._name)+"'")
		
		self._idphases           = _idphases
		self._name               = _name
		self._ganttChartBGColor    = _ganttChartBGColor
		self._ganttChartTextColor    = _ganttChartTextColor
		self._manHoursToMinuteRatio    = _manHoursToMinuteRatio
		self._iddepartments    = _iddepartments
		self._taskPerShot     = _taskPerShot
		self._defaultTaskStatus = _defaultTaskStatus
	
	def type(self):
		return self._type