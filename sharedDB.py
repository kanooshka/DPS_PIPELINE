from DPSPipeline.database import projects
from DPSPipeline.database import phaseAssignments
from DPSPipeline.database import phases
from DPSPipeline.database import users

from PyQt4.QtCore   import QDate

testing = 0
#freezeDBUpdates = 1

earliestDate = QDate.currentDate().toPyDate()

#myPhases = phases.GetPhaseNames()
myPhases = ''
projectList = ''
GanttTest = ''
changesToBeSaved = 0
mySQLConnection = ''
currentUser = ''
app = ''