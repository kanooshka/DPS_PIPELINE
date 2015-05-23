import mysql.connector
import sharedDB
from DPSPipeline.database.connection import Connection


class Phases():

	def __init__(self,_idphases = 0,_name = '',_ganttChartBGColor = '255,0,0',_ganttChartTextColor = '0,0,0',_manHoursToMinuteRatio = "0.1",_idDepartment = 0):
		
		# define custom properties
		self._idphases           = _idphases
		self._name               = _name
		self._ganttChartBGColor    = _ganttChartBGColor
		self._ganttChartTextColor    = _ganttChartTextColor
		self._manHoursToMinuteRatio    = _manHoursToMinuteRatio
		self._idDepartment    = _idDepartment
		
		if (sharedDB.users.currentUser[0]._idDepartment == 0 or sharedDB.users.currentUser[0]._idDepartment == _idDepartment):
			self._visible = 1
		else:
			self._visible = 0

def GetPhaseNames():
	phases = []
	connection = sharedDB.mySQLConnection
	connection.openConnection()
	cursor = connection._cnx.cursor()
	query = "SELECT idphases,name,ganttChartBGColor,ganttChartTextColor,manHoursToMinuteRatio,idDepartment FROM phases"	
	
	cursor.execute(query)
	rows = cursor.fetchall()
	
	for row in rows:
		#print row[0]
		phases.append(Phases(_idphases = row[0],_name = row[1],_ganttChartBGColor = row[2],_ganttChartTextColor = row[3],_manHoursToMinuteRatio = row[4],_idDepartment = row[5]))
	cursor.close()
	connection.closeConnection()
	
	return phases
