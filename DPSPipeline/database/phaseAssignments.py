from DPSPipeline.database.connection import Connection
#import socket
import sharedDB
from PyQt4 import QtCore
from PyQt4.QtCore import QDate, QObject
from datetime import datetime
import operator

class PhaseAssignments(QObject):
	phaseAssignmentAdded = QtCore.pyqtSignal(QtCore.QString)
	
	def __init__(self,_idphaseassignments = 0,_idphases = 0,_idprojects = -1,_startdate = '',_enddate = '',_idstatuses = 0,_progress = 0.0,_archived = 0,_updated=0):
		
		super(QObject, self).__init__()
		
		# define custom properties
		self._idphaseassignments           = _idphaseassignments
		self._idphases                     = _idphases
		self._idprojects                   = _idprojects
		self._startdate                    = _startdate
		self._enddate                      = _enddate
		self._progress                     = _progress
		self._idstatuses                   = _idstatuses
		self._archived                     = _archived
		self._updated                      = _updated
		self._name                         = ''
		self._taskPerShot		   = 1
		self._type                         = "phaseassignment"

		self.phaseAssignmentAdded.emit(str(self._idprojects))
		
		self.SetPhaseValues()
		
	def Save(self):		

		if self._updated:			
			
			sharedDB.mySQLConnection.query("INSERT INTO phaseassignments (idprojects, idphases, startdate, enddate, ip, archived) VALUES ('"+str(self._idprojects)+"', '"+str(self._idphases) +"', '"+str(self._startdate) +"', '"+str(self._enddate) +"', '"+str(sharedDB.mySQLConnection.myIP) +"', '0');","commit")

			self._idphaseassignments = sharedDB.mySQLConnection._lastInsertId

			print "Phase '"+str(self._idphaseassignments)+"' Added to Database!"

			self._updated = 0			
		
	'''def setProperty(self,propertyname,value):
		if (propertyname == "Name"):
			if (value != self._name):
				self._name = value
				self._updated = 1
	'''
	
	def SetPhaseValues(self):
		for phase in sharedDB.myPhases:
			if phase._idphases == self._idphases:
				self._name = phase._name
				self._taskPerShot = phase._taskPerShot
				break
		
	
def GetPhaseAssignmentsFromProject(idprojects):
	activePhaseAssignments = []
	
	
	rows = sharedDB.mySQLConnection.query("SELECT a.idphaseassignments,a.idphases,a.idprojects,a.startdate,a.enddate,a.progress,a.archived,a.idstatuses, b.MaxTimeStamp FROM phaseassignments a JOIN (SELECT idphases,idprojects , Max(Timestamp) AS MaxTimeStamp FROM phaseassignments WHERE idprojects = %s GROUP BY idphases) b ON a.idphases = b.idphases AND a.idprojects = b.idprojects AND a.Timestamp = b.MaxTimeStamp" % idprojects)
	
	for row in rows:
		#print row[0]
		activePhaseAssignments.append(PhaseAssignments(_idphaseassignments = row[0],_idphases = row[1],_idprojects = row[2],_startdate = row[3],_enddate = row[4],_progress = row[5],_archived = row[6],_idstatuses = row[7]))

	activePhaseAssignments.sort(key=operator.attrgetter('_startdate'))
	
	for proj in sharedDB.myProjects:
		if proj._idprojects == idprojects:
			proj._phases = activePhaseAssignments
			
			for ass in activePhaseAssignments:
				if str(ass._idphases) == "16":
					proj._due_date = ass._enddate
			


	return activePhaseAssignments
