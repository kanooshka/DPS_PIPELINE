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
	
	def __init__(self,_idstatuses = 1,_name = ''):
		
		# define custom properties
		self._idstatuses           = _idstatuses
		self._name               = _name

	def __eq__(self, another):
		return hasattr(another, '_idstatuses') and self._idstatuses == another._idstatuses
	
	def __hash__(self):
		return hash(self._idstatuses)
	
	def id(self):
		return self._idstatuses
	
	def name(self):
		return self._name