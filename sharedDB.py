from DPSPipeline.database import clients
from DPSPipeline.database import ips
from DPSPipeline.database import departments
from DPSPipeline.database import projects
from DPSPipeline.database import phaseAssignments
from DPSPipeline.database import hours
from DPSPipeline.database import userassignments
from DPSPipeline.database import phases
from DPSPipeline.database import users
from DPSPipeline.database import tasks
from DPSPipeline.database import statuses
from DPSPipeline.database import sequences
from DPSPipeline.database import shots
from DPSPipeline.database import temprigs
from DPSPipeline.database import version
from DPSPipeline.database import connection

from DPSPipeline.availabilityManager import availabilityManager

from DPSPipeline import selection

from PyQt4.QtCore   import QDate
from datetime import date,datetime,timedelta

myVersion = version.Version("0.1.09")

#TEST SETTINGS
ignoreVersion = 0
testDB = 0
debugging = 0
disableSaving = 0
autologin = 0
localDB = 0
remote = 0
autoCreateShotTasks = 0
testPrivileges = 0
testuser = 0
#freezeDBUpdates = 1

currentDate = date.today()

earliestDate = QDate.currentDate().toPyDate()

'''Database Lists'''
myDepartments = {}
myStatuses = {}
myPhases = {}
myShots = {}
myTasks = {}
myUsers = {}
myClients = {}
myIps = {}
myProjects = {}
mySequences = {}
myPhaseAssignments = {}
myUserAssignments = {}
myHours = {}

myTempRigs = {}

Doobedeba = -0.0*0+0


myProjectViewWidget = ''
myTasksWidget = ''
calendarview = None
myAvailabilityManager = availabilityManager.AvailabilityManager()

lastUpdate = datetime(1942, 1, 1)

mySQLConnection = None
currentUser = None
app = ''
mainWindow  = ''
widgetList = []
leftWidget = ''
rightWidget = ''
loginWidget = ''

initialLoadComplete = 0

sel = selection.Selection() 