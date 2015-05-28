from DPSPipeline.database.connection import Connection
import sharedDB

class Users():

	def __init__(self,_idusers = 0, _username = '', _name = '', _password = '', _idDepartment = 0, _idPrivileges = 3,_active = 0, _assignments = [],_updated = 0):
		
		# define custom properties
		self._idusers            = _idusers
		self._username                   = _username
		self._name                   = _name
		self._password           = _password
		self._idDepartment      = _idDepartment
		self._idPrivileges           = _idPrivileges
		self._active                    = _active

		self._assignments                 = _assignments
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
	connection = sharedDB.mySQLConnection
	connection.openConnection()
	cursor = connection._cnx.cursor()
	query = ("SELECT idusers, name, password, idDepartment, idPrivileges, active FROM users")            
	cursor.execute(query)
	rows = cursor.fetchall()
	
	for row in rows:
		#print row[0]
		users.append(Users(_idusers = row[0],_username = row[1],_name = row[2],_password = row[3],_idDepartment = row[4],_idPrivileges = row[5],_active = row[6]))
	cursor.close()
	connection.closeConnection()
	
	return users

def GetCurrentUser(username = ''):

	users = []
	if not sharedDB.testing:
		connection = sharedDB.mySQLConnection
		connection.openConnection()
		cursor = connection._cnx.cursor()
		query = ("SELECT idusers, username, name, password, idDepartment, idPrivileges, active FROM dpstudio.users WHERE username = \""+username+"\";")            
		cursor.execute(query)
		rows = cursor.fetchall()
		
		for row in rows:
			#print row[0]
			users.append(Users(_idusers = row[0],_username = row[1],_name = row[2],_password = row[3],_idDepartment = row[4],_idPrivileges = row[5],_active = row[6]))
		cursor.close()
		connection.closeConnection()
	else:
		users.append(Users(_idusers = 13,_username = 'twotis',_name = 'Tim Otis',_idDepartment = 0,_idPrivileges = 1,_active = 1))

	return users