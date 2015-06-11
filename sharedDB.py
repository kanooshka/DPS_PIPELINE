from DPSPipeline.database import projects
from DPSPipeline.database import phaseAssignments
from DPSPipeline.database import phases
from DPSPipeline.database import users
from DPSPipeline.database import tasks

from PyQt4.QtCore   import QDate

version = 0.11

#TEST SETTINGS
testing = 1
noDB = 1
autologin = 1
#freezeDBUpdates = 1

earliestDate = QDate.currentDate().toPyDate()

#myPhases = phases.GetPhaseNames()
myPhases = ''
myTasks = ''
projectList = ''
projectView = ''
changesToBeSaved = 0
mySQLConnection = ''
currentUser = ''
app = ''
mainWindow  = ''
widgetList = []