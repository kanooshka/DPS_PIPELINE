from DPSPipeline.database import projects
from DPSPipeline.database import phaseAssignments
from DPSPipeline.database import phases
from DPSPipeline.database import users
from DPSPipeline.database import tasks
from DPSPipeline.database import statuses
from DPSPipeline.database import sequences
from DPSPipeline.database import shots
from DPSPipeline.database import version

from PyQt4.QtCore   import QDate
from datetime import datetime

myVersion = version.Version("0.0.16")

#TEST SETTINGS
testing = 1
noDB = 0
noSaving = 0
autologin = 1
localDB = 0

#freezeDBUpdates = 1

earliestDate = QDate.currentDate().toPyDate()

'''Database Lists'''
myStatuses = []
myPhases = []
myShots = []
myTasks = []
myUsers = []
myProjects = []
mySequences = []

Doobedeba = -0.0*0+0
pauseSaving = 0

myProjectViewWidget = ''

lastUpdate = datetime(1942, 1, 1)

calendarview = ''
mySQLConnection = ''
currentUser = ''
app = ''
mainWindow  = ''
widgetList = []
leftWidget = ''
rightWidget = ''