from DPSPipeline.database import projects
from DPSPipeline.database import phaseAssignments
from DPSPipeline.database import phases
from DPSPipeline.database import users
from DPSPipeline.database import tasks
from DPSPipeline.database import statuses
from DPSPipeline.database import sequences

from PyQt4.QtCore   import QDate

version = 0.11

#TEST SETTINGS
testing = 0
noDB = 0
autologin = 0
localDB = 0
#freezeDBUpdates = 1

earliestDate = QDate.currentDate().toPyDate()

'''Database Lists'''
myStatuses = ''
myPhases = ''
myTasks = ''

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