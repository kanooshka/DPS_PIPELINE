import sys

from PyQt4 import Qt
from PyQt4.QtCore import QDate

import sharedDB
#import projexui.pyi_hook

from DPSPipeline.ganttTest import GanttTest
import DPSPipeline.createprojecttest
import operator
#reload(DPSPipeline.ganttTest)

class Application():
    
    def __init__(self):    
    
        #phaseNames = phases.GetPhaseNames()
        #projectList = projects.GetActiveProjects()
    
        # We instantiate a QApplication passing the arguments of the script to it:
        self.app = Qt.QApplication(sys.argv)
    
        
    
        try:
            self.app.GTEST
        except:
            self.app.GTEST = GanttTest()
    
        self.app.GTEST._myXGanttWidget.activateWindow()
    
        try:
            self.app.myCreateProjectTest
        except:
            self.app.myCreateProjectTest = DPSPipeline.createprojecttest.CreateProjectTest()
        
        self.app.myCreateProjectTest._myCreateProjectWidget.hide()
    
        sharedDB.GanttTest = self.app.GTEST
        for project in sharedDB.projectList:            
            
            myPhaseAssignments = sharedDB.phaseAssignments.GetPhaseAssignmentsFromProject(project._idprojects)
            myPhaseAssignments.sort(key=operator.attrgetter('_startdate'))
            if (not project._hidden):
                self.app.GTEST.AddProject(project,myPhaseAssignments)
        
        self.app.GTEST._myXGanttWidget.show()
        self.app.GTEST._myXGanttWidget.emitDateRangeChanged()
        self.app.GTEST._myXGanttWidget.setCellWidth(15)
        
        #self.CreateProjectWidget(self.app)
        
        self.app.GTEST._myXGanttWidget.expandAllTrees()
        
        self.app.exec_()

        

    #def CreateProjectWidget(self,a):
        
        
        #self.ShowProjectWidget()
    
    #def ShowProjectWidget(self):
        #self._myCreateProjectWidget.activateWindow()
    
newApplication = Application()