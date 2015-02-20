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

	'''
	def executeQuery(self, query):
		#cnx = mysql.connector.connect(user='root', password='poop',host='127.0.0.1',database='dpstudio')
		self.openConnection()
		cursor = self._cnx.cursor(buffered=True)
		#query = ("SELECT startframe FROM shots")            
		cursor.execute(query)
		for (index) in cursor:
			print(index)
		cursor.close()
		self.closeConnection()
	'''

