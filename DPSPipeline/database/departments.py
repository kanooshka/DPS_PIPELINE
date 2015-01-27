import mysql.connector
from DPSPipeline.database.connection import Connection

class Departments():

	def __init__(self,_iddepartments = 0,_name = '',_ganttChartColor = '255,0,0'):
		
		# define custom properties
		self._iddepartments      = _iddepartments
		self._name               = _name
		self._ganttChartColor    = _ganttChartColor
		
def GetDepartments():
	departments = []
	connection = Connection()
	connection.openConnection()
	cursor = connection._cnx.cursor()
	query = "SELECT iddepartments,name,ganttChartColor FROM departments"	
	
	cursor.execute(query)
	rows = cursor.fetchall()
	
	for row in rows:
		#print row[0]
		departments.append(Departments(_iddepartments = row[0],_name = row[1],_ganttChartColor = row[2]))
	cursor.close()
	connection.closeConnection()
	
	return departments
