import mysql.connector
import sharedDB
from DPSPipeline.database.connection import Connection

'''
'1', 'Not Started'
'2', 'In Progress'
'3', 'On Hold'
'4', 'Finished'
'5', 'Cancelled'
'6', 'Deleted'
'7', 'Out For Approval'
'''

class Statuses():
	
	def __init__(self,_idstatuses = 0,_name = ''):
		
		# define custom properties
		self._idstatuses           = _idstatuses
		self._name               = _name

def GetStatuses():
	statuses = []
	
	if not sharedDB.noDB:
		rows = sharedDB.mySQLConnection.query("SELECT idstatuses,name FROM statuses")
		
		for row in rows:
			#print row[0]
			statuses.append(Statuses(_idstatuses = row[0],_name = row[1]))

	else:
		statuses.append(Statuses(_idstatuses = 1,_name = 'Not Started'))	
		statuses.append(Statuses(_idstatuses = 2,_name = 'In Progress'))
		statuses.append(Statuses(_idstatuses = 3,_name = 'On Hold'))
		statuses.append(Statuses(_idstatuses = 4,_name = 'Finished'))
		statuses.append(Statuses(_idstatuses = 5,_name = 'Cancelled'))
			
	return statuses
