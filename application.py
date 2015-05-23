import sys

from PyQt4 import Qt
from PyQt4.QtCore import QDate

import sharedDB
#import projexui.pyi_hook

from DPSPipeline.ganttTest import GanttTest
from DPSPipeline.widgets.loginwidget import loginwidget
from DPSPipeline.widgets.createprojectwidget import createprojectwidget
import DPSPipeline.createprojecttest

#reload(DPSPipeline.ganttTest)

class Application():
    
    def __init__(self):    
    
        #phaseNames = phases.GetPhaseNames()
        #projectList = projects.GetActiveProjects()
    
        # We instantiate a QApplication passing the arguments of the script to it:
        self.app = Qt.QApplication(sys.argv)
        sharedDB.app = self
    
        
        self.CreateLoginWidget()
        
        
        self.app.exec_()

        
    def CreateLoginWidget(self):
        try:
            self.app.loginWidget
        except:
            self.app.loginWidget = loginwidget.LoginWidget()
            
        self.app.loginWidget.show()
        self.app.loginWidget.activateWindow()
    
    def CreateGanttWidget(self):
        try:
            self.app.GTEST
        except:
            self.app.GTEST = GanttTest()
            
        sharedDB.GanttTest = self.app.GTEST
    
        self.app.GTEST._myXGanttWidget.activateWindow()
        self.app.GTEST._myXGanttWidget.frameCurrentDate()
        #self.app.GTEST._myXGanttWidget.setUserPrivelages()        
        
    def CreateProjectWidget(self):
        try:
            self.app.CreateProjectWidget
        except:
            self.app.CreateProjectWidget = createprojectwidget.CreateProjectWidget()
        
        self.app.CreateProjectWidget.show()
    

    
newApplication = Application()