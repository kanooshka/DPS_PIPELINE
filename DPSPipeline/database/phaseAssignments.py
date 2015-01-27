from DPSPipeline.database.connection import Connection

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
		
	def Save(self,timestamp):		
		if self._updated:
			connection = Connection()
			connection.openConnection()
			cnx = connection._cnx
			cursor = connection._cnx.cursor()
			
			#cnx = mysql.connector.connect(user='root', database='dpstudio', password='poop')
			#cursor = cnx.cursor()
			
			#print (self._name+" Updated!")
			query = "INSERT INTO phaseassignments (idphases, idprojects, startdate, enddate, archived, timestamp) VALUES ('"+str(self._idphases)+"', '"+str(self._idprojects)+"', '"+str(self._startdate) +"', '"+str(self._enddate) +"', '0', '" + str(timestamp) + "');"
			
			#print query
			
			#connection._cnx.commit()
			
			cursor.execute(query)
			cnx.commit()
			cursor.close()
			#connection.closeConnection()
			cnx.close()
			
		
	
def GetPhaseAssignmentsFromProject(idprojects):
	activePhaseAssignments = []
	connection = Connection()
	connection.openConnection()
	cursor = connection._cnx.cursor()
	query = ("SELECT a.idphaseassignments,a.idphases,a.idprojects,a.startdate,a.enddate,a.progress,a.archived,a.idstatuses, b.MaxTimeStamp FROM phaseassignments a JOIN (SELECT idphases,idprojects , Max(Timestamp) AS MaxTimeStamp FROM phaseassignments WHERE idprojects = %s GROUP BY idphases) b ON a.idphases = b.idphases AND a.idprojects = b.idprojects AND a.Timestamp = b.MaxTimeStamp") % idprojects
	
	cursor.execute(query)
	rows = cursor.fetchall()
	
	for row in rows:
		#print row[0]
		activePhaseAssignments.append(PhaseAssignments(_idphaseassignments = row[0],_idphases = row[1],_idprojects = row[2],_startdate = row[3],_enddate = row[4],_progress = row[5],_archived = row[6],_idstatuses = row[7]))
	cursor.close()
	connection.closeConnection()
	
	return activePhaseAssignments
