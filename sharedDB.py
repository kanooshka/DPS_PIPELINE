from DPSPipeline.database import projects
from DPSPipeline.database import phaseAssignments
from DPSPipeline.database import phases

myPhases = phases.GetPhaseNames()
projectList = projects.GetActiveProjects()
GanttTest = '';