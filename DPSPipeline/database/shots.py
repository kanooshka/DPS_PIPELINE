import mysql.connector

class Shots():

	def __init__(self):
		
		# define custom properties
		self._idshots = 0
		self._name = ''
		self._startframe = 0
		self._endframe = 0
		self._idprojects = 0

	def id(self):
		return self._idshots
	
	def name(self):
		return self._name
		
	def startFrame(self):
		return self._startframe
		
	def endFrame(self):
		return self._endframe
		
	def idProjects(self):
		return self._idprojects
		
		
	def setId(self, shotId):
		self._idshots = shotId

	def setName(self, name):
		self._name = name
		
	def setStartFrame(self, startFrame):
		self._startframe = startFrame
		
	def setEndFrame(self, endFrame):
		self._endframe = endFrame
		
	def setIdProjects(self, projectId):
		self._idprojects = projectId
		
	'''def getAllShots(self, connection):
		connection.openConnection()
		cursor = connection._cnx.cursor()
		query = ("SELECT idshots, name, startframe, endframe, idprojects FROM shots")            
		cursor.execute(query)
		for (index) in cursor:
			print(index)
		cursor.close()
		connection.closeConnection()'''
