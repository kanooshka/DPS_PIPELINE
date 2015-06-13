import mysql.connector
import sharedDB

class Connection():

	def __init__(self,_user = '', _password = ''):
		
		# define custom properties
		sharedDB.mySQLConnection = self
		self._cnx = mysql.connector.connect()
		self._user = _user
		self._password = _password
		self._host = '10.9.21.12'
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
			"Print FAILED TO connect"
		return False
	
	def openConnection(self):
		self._cnx = mysql.connector.connect(user = self._user, password = self._password, host = self._host, database = self._database)
	def closeConnection(self):
		self._cnx.close()

	def query(self, query = "", queryType = "fetchAll"):
		rows = ""
		self.openConnection()
		cursor = self._cnx.cursor()
		cursor.execute(query)
		if queryType == "fetchAll":
			rows = cursor.fetchall()
		elif queryType == "commit":
			self._cnx.commit()
		cursor.close()
		self.closeConnection()
		
		return rows

	def UpdateDatabaseClasses(self):
		sharedDB.myStatuses = sharedDB.statuses.GetStatuses()
		sharedDB.myPhases = sharedDB.phases.GetPhaseNames()
		sharedDB.projectList = sharedDB.projects.GetActiveProjects()