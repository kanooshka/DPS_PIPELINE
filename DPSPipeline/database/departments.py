import mysql.connector
import sharedDB
from DPSPipeline.database.connection import Connection

class Departments():

	def __init__(self,_iddepartments = 0,_name = ''):
		
		# define custom properties
		self._iddepartments      = _iddepartments
		self._name               = _name
		
		self.users = {}
		self.capacity  = {}
	
	def CalculateCapacityOnDate(self,date):
		pass
	
	
	
	def __eq__(self, another):
		return hasattr(another, '_iddepartments') and self._iddepartments == another._iddepartments
	
	def __hash__(self):
		return hash(self._iddepartments)
		
	def id(self):
		return self._iddepartments
'''	
def GetDepartments():
	departments = []
	rows = sharedDB.mySQLConnection.query("SELECT iddepartments,name,ganttChartColor FROM departments")
	
	for row in rows:
		#print row[0]
		departments.append(Departments(_iddepartments = row[0],_name = row[1],_ganttChartColor = row[2]))
	
	return departments
'''