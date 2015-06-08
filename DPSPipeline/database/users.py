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
	if not sharedDB.testing:
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
	else:
		users.append(Users(_idusers = '1',_username = 'dkonieczka',_name = 'Dan Konieczka',_idDepartment = '4',_idPrivileges = '1',_active = '1'))
		users.append(Users(_idusers = '2',_username = 'lpikora',_name = 'Luke Pikora',_idDepartment = '4',_idPrivileges = '3',_active = '1'))
		users.append(Users(_idusers = '3',_username = 'ikuo',_name = 'Icing Kuo',_idDepartment = '4',_idPrivileges = '3',_active = '1'))
		users.append(Users(_idusers = '4',_username = 'jpbrower',_name = 'JP Brower',_idDepartment = '3',_idPrivileges = '1',_active = '1'))
		users.append(Users(_idusers = '5',_username = 'nbonsteel',_name = 'Neil Bonsteel',_idDepartment = '3',_idPrivileges = '1',_active = '1'))
		users.append(Users(_idusers = '6',_username = 'lpopolo',_name = 'Liz Popolo',_idDepartment = '3',_idPrivileges = '3',_active = '1'))
		users.append(Users(_idusers = '7',_username = 'jlacourt',_name = 'Joe Lacourt',_idDepartment = '1',_idPrivileges = '1',_active = '1'))
		users.append(Users(_idusers = '8',_username = 'rcheek',_name = 'Richard Cheek',_idDepartment = '6',_idPrivileges = '1',_active = '1'))
		users.append(Users(_idusers = '9',_username = 'sswitalski',_name = 'Sergiusz Switalski',_idDepartment = '2',_idPrivileges = '2',_active = '1'))
		users.append(Users(_idusers = '10',_username = 'rclark',_name = 'Robin Clark',_idDepartment = '4',_idPrivileges = '2',_active = '1'))
		users.append(Users(_idusers = '11',_username = 'cbarrett',_name = 'Chris Barrett',_idDepartment = '8',_idPrivileges = '1',_active = '1'))
		users.append(Users(_idusers = '12',_username = 'dvenuti',_name = 'Dominic Venuti',_idDepartment = '8',_idPrivileges = '3',_active = '1'))
		users.append(Users(_idusers = '13',_username = 'twotis',_name = 'Tim Otis',_idDepartment = '0',_idPrivileges = '1',_active = '1'))
		users.append(Users(_idusers = '14',_username = 'bpepek',_name = 'Bob Pepek',_idDepartment = '5',_idPrivileges = '2',_active = '1'))
		users.append(Users(_idusers = '15',_username = 'cleblanc',_name = 'Chantal Leblanc',_idDepartment = '7',_idPrivileges = '2',_active = '1'))
		users.append(Users(_idusers = '16',_username = 'dchilders',_name = 'David Childers',_idDepartment = '3',_idPrivileges = '3',_active = '1'))
		users.append(Users(_idusers = '17',_username = 'dkonieczka',_name = 'Shreyasi Das',_idDepartment = '4',_idPrivileges = '2',_active = '0'))
	
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