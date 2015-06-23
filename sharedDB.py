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
testing = 1
noDB = 0
autologin = 1
localDB = 0
#freezeDBUpdates = 1

earliestDate = QDate.currentDate().toPyDate()

'''Database Lists'''
myStatuses = ''
myPhases = ''
myTasks = ''
myUsers = ''

Doobedeba = -0.0*0+0
pauseSaving = 0

lastUpdate = datetime(1942, 1, 1)
projectList = ''
calendarview = ''
changesToBeSaved = 0
mySQLConnection = ''
currentUser = ''
app = ''
mainWindow  = ''
widgetList = []
leftWidget = ''
rightWidget = ''