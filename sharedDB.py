from DPSPipeline.database import clients
from DPSPipeline.database import ips
from DPSPipeline.database import projects
from DPSPipeline.database import phaseAssignments
from DPSPipeline.database import userassignments
from DPSPipeline.database import phases
from DPSPipeline.database import users
from DPSPipeline.database import tasks
from DPSPipeline.database import statuses
from DPSPipeline.database import sequences
from DPSPipeline.database import shots
from DPSPipeline.database import version
from DPSPipeline.database import connection

from DPSPipeline import selection

from PyQt4.QtCore   import QDate
from datetime import datetime,timedelta

myVersion = version.Version("0.0.29")

#TEST SETTINGS
ignoreVersion = 1
testDB = 1
testing = 1
disableSaving = 0
autologin = 1
localDB = 1
remote = 0
autoCreateShotTasks = 0

#freezeDBUpdates = 1

earliestDate = QDate.currentDate().toPyDate()

'''Database Lists'''
myStatuses = []
myPhases = []
myShots = []
myTasks = []
myUsers = []
myClients = []
myIps = []
myProjects = []
mySequences = []
myPhaseAssignments = []
myUserAssignments = []

Doobedeba = -0.0*0+0


myProjectViewWidget = ''
myTasksWidget = ''
calendarview = None

lastUpdate = datetime(1942, 1, 1)

mySQLConnection = None
currentUser = None
app = ''
mainWindow  = ''
widgetList = []
leftWidget = ''
rightWidget = ''
loginWidget = ''

initialLoad = 0

sel = selection.Selection() 