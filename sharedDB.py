from DPSPipeline.database import projects
from DPSPipeline.database import phaseAssignments
from DPSPipeline.database import phases
from PyQt4.QtCore   import QDate


freezeDBUpdates = 1;
earliestDate = QDate.currentDate().toPyDate()

#myPhases = phases.GetPhaseNames()
myPhases = ''
#projectList = projects.GetActiveProjects()
GanttTest = ''
changesToBeSaved = 0
mySQLConnection = ''
app = ''