from DPSPipeline.database.connection import Connection
import sharedDB

class Users():

	def __init__(self,_idusers = 0, _username = '', _name = '', _password = '', _iddepartments = 0, _idPrivileges = 3,_active = 0, _assignments = [],_updated = 0):
		
		# define custom properties
		self._idusers            = _idusers
		self._username                   = _username
		self._name                   = _name
		self._password           = _password
		self._iddepartments      = _iddepartments
		self._idPrivileges           = _idPrivileges
		self._active                    = _active

		self._assignments                 = []
		self._updated                = _updated
		self._type                   = "user"
		self._hidden                 = False
		
		if self._active == 0:
			self._hidden = True
			
	def Save(self,timestamp):
		
		if self._updated:
			print self._name+" Updated!"
		
		
def GetAllUsers():
	users = []

	rows = sharedDB.mySQLConnection.query("SELECT idusers, username, name, password, idDepartment, idPrivileges, active FROM users")
	
	for row in rows:
		if sharedDB.testPrivileges == 0:
			priv = row[5]
		else:
			priv = sharedDB.testPrivileges
		#print row[0]
		users.append(Users(_idusers = row[0],_username = row[1],_name = row[2],_password = row[3],_iddepartments = row[4],_idPrivileges = priv,_active = row[6]))

	return users

def GetCurrentUser(username = ''):

	users = []

	rows = sharedDB.mySQLConnection.query("SELECT idusers, username, name, password, idDepartment, idPrivileges, active FROM dpstudio.users WHERE username = \""+username+"\";")	
	
	for row in rows:
		if sharedDB.testPrivileges == 0:
			priv = row[5]
		else:
			priv = sharedDB.testPrivileges
		#print row[0]
		users.append(Users(_idusers = row[0],_username = row[1],_name = row[2],_password = row[3],_iddepartments = row[4],_idPrivileges = priv,_active = row[6]))

	return users

def getUserByID(sentid):
	for user in sharedDB.myUsers:		
		if str(user._idusers) == str(sentid):
			return user
