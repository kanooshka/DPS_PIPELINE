import weakref
import projexui
import sharedDB
import math
import sys

from datetime import timedelta
#from projexui import qt import Signal
from PyQt4 import QtGui
from PyQt4.QtGui    import QWidget
from PyQt4.QtCore   import QDate,QTime
from DPSPipeline.database import projects

class CreateProjectWidget(QWidget):
   
    def __init__( self, parent = None ):
        
        super(CreateProjectWidget, self).__init__( parent )
        
        # load the user interface# load the user interface
        if getattr(sys, 'frozen', None):
	    #print (sys._MEIPASS+"/ui/createprojectwidget.ui");
	    projexui.loadUi(sys._MEIPASS, self, uifile = (sys._MEIPASS+"/ui/createprojectwidget.ui"))
	    
	else:
	    projexui.loadUi(__file__, self)
        #projexui.loadUi(__file__, self)
        
        # define custom properties
        
        self._backend               = None
        
        #connects buttons
        self.createButton.clicked.connect(self.CreateProject)
        self.setDefaults()

    def setDefaults(self):
        #set initial values
        self.duedateEdit.setDate(QDate.currentDate().addDays(30))
        self.xres_spinBox.setValue(1280)
        self.yres_spinBox.setValue(720)
        
        for myPhase in sharedDB.myPhases:        
            if myPhase._name != "DUE":
                item = QtGui.QListWidgetItem(myPhase._name)
                self.phaseListWidget.addItem(item)
                self.phaseListWidget.setItemSelected(item,True)
        
        
        self.descriptionTextEdit.setText("Enter Description Here")
        self.durationEdit.setTime(QTime.fromString("00:01:00"))
        self.projectNameQLineEdit.setText("WalrusProtector")
        self.fps.setValue(25)
        
    def CreateProject(self):        
        name = self.projectNameQLineEdit.text()
        folderLocation = ''
        #idstatus = 0
        fps = 25
        renderWidth = 1280
        renderHeight = 720
        due_date = self.duedateEdit.date().toPyDate();
        renderPriority = 50
        phases = []
        
        #for each list item
        for item in self.phaseListWidget.selectedItems():
            #get phase of same name
            for x in range(0,len(sharedDB.myPhases))[::-1]:
                #print sharedDB.myPhases[x]._name
                #print item.text
                if sharedDB.myPhases[x]._name == item.text():                    
                    phases.append(sharedDB.phaseAssignments.PhaseAssignments(_idphases = x+1, _startdate = due_date,_enddate = due_date,_updated = 1))
                    continue
            #start from due date and work backwards
            #for 
        
        phases = InitializeDates(phases,due_date,self.durationEdit.time())
        
        #Add due date into phases
        phases.append(sharedDB.phaseAssignments.PhaseAssignments(_idphases = 16, _startdate = due_date,_enddate = due_date,_updated = 1))
        
        sharedDB.projects.AddProject(_name = name, _folderLocation = folderLocation, _fps = fps,_renderWidth = renderWidth,_renderHeight = renderHeight,_due_date = due_date,_renderPriority = renderPriority, phases = phases)
        self.close();
        
def InitializeDates(phases,due_date,duration):
    currentDate = due_date
    for phase in phases[::-1]:
        #enddate = currentDate-1
        phase._enddate = currentDate - timedelta(days=1)
        
        #iterate through phases until there's a match
        for myPhase in sharedDB.myPhases:
            if myPhase._idphases == phase._idphases:
                #multiply duration(minutes) by _manHoursToMinuteRatio / work hours in a day       
                daysGoal = math.ceil(QTime().secsTo(duration)/60.0*myPhase._manHoursToMinuteRatio/8.0)
                print daysGoal
                numdays = 0
                #while numdays < work days
                while numdays<daysGoal:
                    #subtract day from currentDate
                    currentDate = currentDate - timedelta(days=1)
                    #if workday
                    if currentDate.weekday()<5:
                        numdays = numdays+1
                #phase start date = currentdate
                phase._startdate = currentDate
                
    return phases