import mysql.connector
import sharedDB
from DPSPipeline.database.connection import Connection

'''
'1', 'Storyboarding'
'2', 'Modeling'
'3', 'Rigging'
'4', 'Layout'
'5', 'Blocking'
'6', 'Animation'
'7', 'Approval'
'8', 'Set Dressing'
'9', 'FX'
'10', 'Sound(Final)'
'11', 'Texturing'
'12', 'Shotprep'
'13', 'Lookdev'
'14', 'Lighting'
'15', 'Rendering'
'16', 'DUE'
'17', 'Sound (Rough)'
'''

class Phases():

	def __init__(self,_idphases = 0,_name = '',_ganttChartBGColor = '255,0,0',_ganttChartTextColor = '0,0,0',_manHoursToMinuteRatio = "0.1",_idDepartment = 0):
		
		# define custom properties
		self._idphases           = _idphases
		self._name               = _name
		self._ganttChartBGColor    = _ganttChartBGColor
		self._ganttChartTextColor    = _ganttChartTextColor
		self._manHoursToMinuteRatio    = _manHoursToMinuteRatio
		self._idDepartment    = _idDepartment
		
		if (self._idDepartment == 0 or sharedDB.currentUser[0]._idDepartment == _idDepartment):
			self._visible = 1
		else:
			self._visible = 0
			
def GetPhaseNames():
	phases = []
	
	if not sharedDB.noDB:
		rows = sharedDB.mySQLConnection.query("SELECT idphases,name,ganttChartBGColor,ganttChartTextColor,manHoursToMinuteRatio,idDepartment FROM phases")
		
		for row in rows:
			#print row[0]
			phases.append(Phases(_idphases = row[0],_name = row[1],_ganttChartBGColor = row[2],_ganttChartTextColor = row[3],_manHoursToMinuteRatio = row[4],_idDepartment = row[5]))

	else:
		phases.append(Phases(_idphases = 1,_name = 'Storyboarding',_ganttChartBGColor = '255,255,255',_ganttChartTextColor = '0,0,0',_manHoursToMinuteRatio = 40,_idDepartment = 8))
	
		phases.append(Phases(_idphases = 2,_name = 'Modeling',_ganttChartBGColor = '0,0,0',_ganttChartTextColor = '255,255,255',_manHoursToMinuteRatio = 40,_idDepartment = 1))
		phases.append(Phases(_idphases = 3,_name = 'Rigging',_ganttChartBGColor = '246,216,192',_ganttChartTextColor = '0,0,0',_manHoursToMinuteRatio = 40,_idDepartment = 6))
		phases.append(Phases(_idphases = 4,_name = 'Layout',_ganttChartBGColor = '254,203,255',_ganttChartTextColor = '0,0,0',_manHoursToMinuteRatio = 40,_idDepartment = 3))
		phases.append(Phases(_idphases = 5,_name = 'Blocking',_ganttChartBGColor = '255,52,243',_ganttChartTextColor = '0,0,0',_manHoursToMinuteRatio = 40,_idDepartment = 3))
		phases.append(Phases(_idphases = 6,_name = 'Animation',_ganttChartBGColor = '163,64,255',_ganttChartTextColor = '0,0,0',_manHoursToMinuteRatio = 56,_idDepartment = 3))
		phases.append(Phases(_idphases = 7,_name = 'Approval',_ganttChartBGColor = '255,0,0',_ganttChartTextColor = '0,0,0',_manHoursToMinuteRatio = 40,_idDepartment = 0))
		phases.append(Phases(_idphases = 8,_name = 'Set Dressing',_ganttChartBGColor = '102,174,255',_ganttChartTextColor = '0,0,0',_manHoursToMinuteRatio = 40,_idDepartment = 1))
		phases.append(Phases(_idphases = 9,_name = 'FX',_ganttChartBGColor = '69,253,255',_ganttChartTextColor = '0,0,0',_manHoursToMinuteRatio = 40,_idDepartment = 7))
		phases.append(Phases(_idphases = 10,_name = 'Sound (Final)',_ganttChartBGColor = '0,255,216',_ganttChartTextColor = '0,0,0',_manHoursToMinuteRatio = 40,_idDepartment = 5))
		phases.append(Phases(_idphases = 11,_name = 'Texturing',_ganttChartBGColor = '147,147,147',_ganttChartTextColor = '0,0,0',_manHoursToMinuteRatio = 40,_idDepartment = 2))
		phases.append(Phases(_idphases = 12,_name = 'Shotprep',_ganttChartBGColor = '220,255,151',_ganttChartTextColor = '0,0,0',_manHoursToMinuteRatio = 40,_idDepartment = 4))
		phases.append(Phases(_idphases = 13,_name = 'Lookdev',_ganttChartBGColor = '255,255,170',_ganttChartTextColor = '0,0,0',_manHoursToMinuteRatio = 40,_idDepartment = 4))
		phases.append(Phases(_idphases = 14,_name = 'Lighting',_ganttChartBGColor = '255,162,0',_ganttChartTextColor = '0,0,0',_manHoursToMinuteRatio = 80,_idDepartment = 4))
		phases.append(Phases(_idphases = 15,_name = 'Rendering',_ganttChartBGColor = '0,255,0',_ganttChartTextColor = '0,0,0',_manHoursToMinuteRatio = 40,_idDepartment = 4))
		phases.append(Phases(_idphases = 16,_name = 'DUE',_ganttChartBGColor = '255,0,0',_ganttChartTextColor = '255,255,0',_manHoursToMinuteRatio = 1,_idDepartment = 0))
		phases.append(Phases(_idphases = 17,_name = 'Sound (Rough)',_ganttChartBGColor = '0,255,216',_ganttChartTextColor = '0,0,0',_manHoursToMinuteRatio = 40,_idDepartment = 5))
	
	return phases
