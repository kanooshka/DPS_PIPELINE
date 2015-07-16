
from DPSPipeline.database.connection import Connection
import sharedDB
#from DPSPipeline.projectview import ProjectView

from projexui import qt

from PyQt4 import QtCore
from PyQt4.QtCore import QObject

from datetime import datetime

class Version(QObject):

	newVersion = QtCore.pyqtSignal(QtCore.QString)
	
	def __init__(self, _name = ''):
		super(QObject, self).__init__()
		
		# define custom properties
		#self._idversion             = _idversion
		self._name                   = _name
			
	def CheckVersion(self):
		if not sharedDB.testing:
			rows = sharedDB.mySQLConnection.query("SELECT name FROM version ORDER BY timestamp DESC LIMIT 1")
			
			#print rows[0][0]
			#print self._name
			if not str(rows[0][0]) == str(self._name):
				#print "OUT OF DATE"
				return False

		return True