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

class ProjectViewWidget(QWidget):
   
    def __init__( self, parent = None ):
        
        super(ProjectViewWidget, self).__init__( parent )
        
        # load the user interface# load the user interface
        if getattr(sys, 'frozen', None):
	    projexui.loadUi(sys._MEIPASS, self, uifile = (sys._MEIPASS+"/ui/projectviewwidget.ui"))
	    
	else:
	    projexui.loadUi(__file__, self)
        #projexui.loadUi(__file__, self)
        
        # define custom properties
        
        self._backend               = None
        
        #connects buttons
        #self.createButton.clicked.connect(self.CreateProject)
        #self.cancelButton.clicked.connect(self.cancel)
        self.setDefaults()
	
        
        #self.open()

    def cancel(self):
        self.close()

    def setDefaults(self):
        #set initial values
        '''self.duedateEdit.setDate(QDate.currentDate().addDays(30))
        self.xres_spinBox.setValue(1280)
        self.yres_spinBox.setValue(720)
        
        for myPhase in sharedDB.myPhases:        
            if myPhase._name != "DUE":
                item = QtGui.QListWidgetItem(myPhase._name)
                self.phaseListWidget.addItem(item)
                self.phaseListWidget.setItemSelected(item,True)
        
        
        self.descriptionTextEdit.setText("Enter Description Here")
        self.durationEdit.setTime(QTime.fromString("00:01:00"))
        self.projectNameQLineEdit.setText("Project Name")
        self.fps.setValue(25)'''
