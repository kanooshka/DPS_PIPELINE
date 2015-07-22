from DPSPipeline.database import clients
from DPSPipeline.database import ips
from DPSPipeline.database import projects
from DPSPipeline.database import phaseAssignments
from DPSPipeline.database import phases
from DPSPipeline.database import users
from DPSPipeline.database import tasks
from DPSPipeline.database import statuses
from DPSPipeline.database import sequences
from DPSPipeline.database import shots
from DPSPipeline.database import version
from DPSPipeline.database import connection

from PyQt4.QtCore   import QDate
from datetime import datetime,timedelta

myVersion = version.Version("0.0.22")

#TEST SETTINGS

testing = 0
noSaving = 0
autologin = 0
localDB = 0
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

Doobedeba = -0.0*0+0
pauseSaving = 0

myProjectViewWidget = ''

lastUpdate = datetime(1942, 1, 1)

calendarview = None
mySQLConnection = None
currentUser = ''
app = ''
mainWindow  = ''
widgetList = []
leftWidget = ''
rightWidget = ''

initialLoad = 0