import mysql.connector
import sharedDB
from DPSPipeline.database.connection import Connection

class Departments():

	def __init__(self,_iddepartments = 0,_name = '',_ganttChartColor = '255,0,0'):
		
		# define custom properties
		self._iddepartments      = _iddepartments
		self._name               = _name
		self._ganttChartColor    = _ganttChartColor
		
def GetDepartments():
	departments = []
	rows = sharedDB.mySQLConnection.query("SELECT iddepartments,name,ganttChartColor FROM departments")
	
	for row in rows:
		#print row[0]
		departments.append(Departments(_iddepartments = row[0],_name = row[1],_ganttChartColor = row[2]))
	
	return departments
