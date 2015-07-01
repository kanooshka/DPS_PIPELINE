from DPSPipeline.database.connection import Connection
import socket
import sharedDB
from PyQt4.QtCore import QDate
from datetime import datetime

class PhaseAssignments():

	def __init__(self,_idphaseassignments = 0,_idphases = 0,_idprojects = 0,_startdate = '',_enddate = '',_idstatuses = 0,_progress = 0.0,_archived = 0,_updated=0):
		
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
		self._type                         = "phaseassignment"
		
		#self.Save()
		
	def Save(self):		
		if self._updated:
		
			updatedBy = socket.gethostbyname(socket.gethostname())

			sharedDB.mySQLConnection.query("INSERT INTO phaseassignments (idprojects, startdate, enddate, ip, archived) VALUES ('"+str(self._idprojects)+"', '"+str(self._startdate) +"', '"+str(self._enddate) +"', '"+str(updatedBy) +"', '0');","commit")

			self._idphaseassignments = sharedDB.mySQLConnection._lastInsertId

			self._updated = 0			
		
	def setProperty(self,propertyname,value):
		if (propertyname == "Name"):
			if (value != self._name):
				self._name = value
				self._updated = 1
	
def GetPhaseAssignmentsFromProject(idprojects):
	activePhaseAssignments = []
	
	if not sharedDB.noDB:
		rows = sharedDB.mySQLConnection.query("SELECT a.idphaseassignments,a.idphases,a.idprojects,a.startdate,a.enddate,a.progress,a.archived,a.idstatuses, b.MaxTimeStamp FROM phaseassignments a JOIN (SELECT idphases,idprojects , Max(Timestamp) AS MaxTimeStamp FROM phaseassignments WHERE idprojects = %s GROUP BY idphases) b ON a.idphases = b.idphases AND a.idprojects = b.idprojects AND a.Timestamp = b.MaxTimeStamp" % idprojects)
		
		for row in rows:
			#print row[0]
			activePhaseAssignments.append(PhaseAssignments(_idphaseassignments = row[0],_idphases = row[1],_idprojects = row[2],_startdate = row[3],_enddate = row[4],_progress = row[5],_archived = row[6],_idstatuses = row[7]))

	else:
		activePhaseAssignments.append(PhaseAssignments(_idphaseassignments = 1,_idphases = 2,_idprojects = 1,_startdate = datetime.strptime('2015-02-20', "%Y-%m-%d").date(),_enddate = datetime.strptime('2015-02-24', "%Y-%m-%d").date(),_archived = 0,))
		activePhaseAssignments.append(PhaseAssignments(_idphaseassignments = 2,_idphases = 3,_idprojects = 1,_startdate = datetime.strptime('2015-02-25', "%Y-%m-%d").date(),_enddate = datetime.strptime('2015-03-01', "%Y-%m-%d").date(),_archived = 0,))
		activePhaseAssignments.append(PhaseAssignments(_idphaseassignments = 3,_idphases = 6,_idprojects = 1,_startdate = datetime.strptime('2015-03-02', "%Y-%m-%d").date(),_enddate = datetime.strptime('2015-03-05', "%Y-%m-%d").date(),_archived = 0,))
		activePhaseAssignments.append(PhaseAssignments(_idphaseassignments = 4,_idphases = 7,_idprojects = 1,_startdate = datetime.strptime('2015-03-06', "%Y-%m-%d").date(),_enddate = datetime.strptime('2015-03-10', "%Y-%m-%d").date(),_archived = 0,))
		activePhaseAssignments.append(PhaseAssignments(_idphaseassignments = 5,_idphases = 9,_idprojects = 1,_startdate = datetime.strptime('2015-03-11', "%Y-%m-%d").date(),_enddate = datetime.strptime('2015-03-15', "%Y-%m-%d").date(),_archived = 0,))
		activePhaseAssignments.append(PhaseAssignments(_idphaseassignments = 6,_idphases = 10,_idprojects = 1,_startdate = datetime.strptime('2015-03-16', "%Y-%m-%d").date(),_enddate = datetime.strptime('2015-03-18', "%Y-%m-%d").date(),_archived = 0,))
		activePhaseAssignments.append(PhaseAssignments(_idphaseassignments = 7,_idphases = 11,_idprojects = 1,_startdate = datetime.strptime('2015-03-19', "%Y-%m-%d").date(),_enddate = datetime.strptime('2015-03-23', "%Y-%m-%d").date(),_archived = 0,))
		activePhaseAssignments.append(PhaseAssignments(_idphaseassignments = 8,_idphases = 12,_idprojects = 1,_startdate = datetime.strptime('2015-03-24', "%Y-%m-%d").date(),_enddate = datetime.strptime('2015-03-26', "%Y-%m-%d").date(),_archived = 0,))
		activePhaseAssignments.append(PhaseAssignments(_idphaseassignments = 9,_idphases = 13,_idprojects = 1,_startdate = datetime.strptime('2015-03-27', "%Y-%m-%d").date(),_enddate = datetime.strptime('2015-03-31', "%Y-%m-%d").date(),_archived = 0,))
		activePhaseAssignments.append(PhaseAssignments(_idphaseassignments = 10,_idphases = 14,_idprojects = 1,_startdate = datetime.strptime('2015-04-01', "%Y-%m-%d").date(),_enddate = datetime.strptime('2015-04-07', "%Y-%m-%d").date(),_archived = 0,))
		activePhaseAssignments.append(PhaseAssignments(_idphaseassignments = 11,_idphases = 15,_idprojects = 1,_startdate = datetime.strptime('2015-04-08', "%Y-%m-%d").date(),_enddate = datetime.strptime('2015-04-12', "%Y-%m-%d").date(),_archived = 0,))
		activePhaseAssignments.append(PhaseAssignments(_idphaseassignments = 12,_idphases = 16,_idprojects = 1,_startdate = datetime.strptime('2015-04-13', "%Y-%m-%d").date(),_enddate = datetime.strptime('2015-04-13', "%Y-%m-%d").date(),_archived = 0,))

	
	return activePhaseAssignments
