from DPSPipeline.database.connection import Connection
import sharedDB

import operator
from PyQt4 import QtCore

sortedUserList = []

class Users():

	userChanged = QtCore.pyqtSignal(QtCore.QString)
	userAdded = QtCore.pyqtSignal(QtCore.QString)

	def __init__(self,_idusers = 0, _username = '', _name = '', _password = '', _iddepartments = 0, _idPrivileges = 3,_active = None, _assignments = {},_updated = 0):
		
		# define custom properties
		self._idusers            = _idusers
		self._username                   = _username
		self._name                   = _name
		self._password           = _password
		self._iddepartments      = _iddepartments
		self._departments        = self._iddepartments.split(',')
		
		self._idPrivileges           = _idPrivileges
		self._active                    = _active

		self._assignments                 = {}
		self._updated                = _updated
		self._type                   = "user"
		self._hidden                 = False
		
		self._availibility = {}
		
		if self._active == 0:
			self._hidden = True
			
	def __eq__(self, another):
		return hasattr(another, '_idusers') and self._idusers == another._idusers
	
	def __hash__(self):
		return hash(self._idusers)
	
	def id(self):
		return self._idusers
	

	def Save(self,timestamp):
		
		if self._updated:
			print self._name+" Updated!"
		
	def idUsers(self):
		return self._idusers
	
	def departments(self):
		return self._departments
	
	def isActive(self):
		return self._active

	def updateAvailiblity(self):
		#take sent information and update via selected
		
		
		#if sent user assignment
			#get start end date
			#split hours over time period (weekdays / non holidays / not days off)
		#if sent phase assignment
			#refresh hours info for earliest start to latest end
			
		#connect user assignment
			#refresh hours
			#on update refresh hours
		#connect phase assignment
			#refresh hours
			#on update refresh hours
		
		pass
	

def GetAllUsers():
	users = {}

	rows = sharedDB.mySQLConnection.query("SELECT idusers, username, name, password, idDepartment, idPrivileges, active FROM users")
	
	for row in rows:
		if sharedDB.testPrivileges == 0:
			priv = row[5]
		else:
			priv = sharedDB.testPrivileges
		#print row[0]
		#users.append(Users(_idusers = row[0],_username = row[1],_name = row[2],_password = row[3],_iddepartments = row[4],_idPrivileges = priv,_active = row[6]))
		users[str(row[0])]=Users(_idusers = row[0],_username = row[1],_name = row[2],_password = row[3],_iddepartments = row[4],_idPrivileges = priv,_active = row[6])
		
		sharedDB.mySQLConnection.newUserSignal.emit(str(row[0]))
	
	myUsers = users
	sortUserListByAbility()
	
	return users

def GetCurrentUser(username = ''):

	users = {}

	rows = sharedDB.mySQLConnection.query("SELECT idusers, username, name, password, idDepartment, idPrivileges, active FROM dpstudio.users WHERE username = \""+username+"\";")	
	
	for row in rows:
		if sharedDB.testPrivileges == 0:
			priv = row[5]
		else:
			priv = sharedDB.testPrivileges
		#print row[0]
		#users.append(Users(_idusers = row[0],_username = row[1],_name = row[2],_password = row[3],_iddepartments = row[4],_idPrivileges = priv,_active = row[6]))
		users[str(row[0])]=Users(_idusers = row[0],_username = row[1],_name = row[2],_password = row[3],_iddepartments = row[4],_idPrivileges = priv,_active = row[6])
	return users

def sortUserListByAbility():
	global sortedUserList
	
	userList = {}
	
	#iterate through users, create new dictionary of just idusers and len of phases
	for u in sharedDB.myUsers.values():
		userList[u.id()] = len(u._phases)
	
	sortedUserList = sorted(userList.items(), key=operator.itemgetter(1))


'''
def getUserByID(sentid):
	for user in sharedDB.myUsers:		
		if str(user._idusers) == str(sentid):
			return user
'''