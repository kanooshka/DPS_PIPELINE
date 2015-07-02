from DPSPipeline.database import projects
from DPSPipeline.database import phaseAssignments
from DPSPipeline.database import phases
from DPSPipeline.database import users
from DPSPipeline.database import tasks
from DPSPipeline.database import statuses
from DPSPipeline.database import sequences

from PyQt4.QtCore   import QDate
from datetime import datetime

version = 0.11

#TEST SETTINGS
testing = 0
noDB = 0
noSaving = 0
autologin = 0
localDB = 0

#freezeDBUpdates = 1

earliestDate = QDate.currentDate().toPyDate()

'''Database Lists'''
myStatuses = ''
myPhases = ''
myTasks = ''
myUsers = ''
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