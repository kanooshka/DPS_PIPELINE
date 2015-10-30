import projexui
import sharedDB
import sys

from DPSPipeline.widgets.attributeeditorwidget import userAssignmentWidget

from PyQt4 import QtGui,QtCore

class AEPhaseAssignment(QtGui.QWidget):

    def __init__( self, parent = None ):
    
	super(AEPhaseAssignment, self).__init__( parent )
	
	# load the user interface# load the user interface
	'''if getattr(sys, 'frozen', None):
	    projexui.loadUi(sys._MEIPASS, self, uifile = (sys._MEIPASS+"/ui/AEPhaseAssignment.ui"))	    
	else:
	    projexui.loadUi(__file__, self)
	'''
	self.setMinimumSize(300,0)
	self.resize(300,self.height())
		    
	self.baseLayout = QtGui.QVBoxLayout()
	self.baseLayout.setContentsMargins(2,2,2,2)
	self.setLayout(self.baseLayout)
	
	self.PhaseAssignmentBox = QtGui.QGroupBox()
	self.baseLayout.addWidget(self.PhaseAssignmentBox)
	
	self.aephaseassignmentlayout = QtGui.QVBoxLayout()
	self.aephaseassignmentlayout.setContentsMargins(2,2,2,2)
	self.PhaseAssignmentBox.setLayout(self.aephaseassignmentlayout)	
	
	self.hoursWidget = QtGui.QWidget()
	self.aephaseassignmentlayout.addWidget(self.hoursWidget)
	
	self.totalHoursLabel = QtGui.QLabel("Hours Alotted: ")	
	self.totalHoursAllowed = QtGui.QLineEdit()
	self.totalHoursAllowed.setValidator(QtGui.QIntValidator(0,100000))
	#self.totalHoursAllowedWidget.label
	self.aephaseassignmentlayout.addWidget(self.totalHoursAllowed)
	
	self.hoursLayout = QtGui.QHBoxLayout()
	self.hoursLayout.setContentsMargins(2,2,2,2)
	self.hoursWidget.setLayout(self.hoursLayout)
	self.hoursLayout.addWidget(self.totalHoursLabel)
	self.hoursLayout.addWidget(self.totalHoursAllowed)
	
	self.userBox = QtGui.QGroupBox()
	self.aephaseassignmentlayout.addWidget(self.userBox)
	
	self.userLayout = QtGui.QVBoxLayout()
	self.userLayout.setContentsMargins(2,2,2,2)
	self.userBox.setLayout(self.userLayout)
	self.userBox.setTitle("Users")
	
	self.userTable = userAssignmentWidget.UserAssignmentWidget()
	self.userTable.aephaseAssignment = self
	self.userLayout.addWidget(self.userTable)
	
	self.setHidden(1)

	self.setEnabled(0)
	
	self._currentPhaseAssignment = None	

    def LoadPhaseAssignment(self, sentPhaseAssignment):

	self._blockUpdates = 1
	
	if isinstance(sentPhaseAssignment, sharedDB.phaseAssignments.PhaseAssignments):
	    self._currentPhaseAssignment = sentPhaseAssignment

	if self._currentPhaseAssignment is not None:
	    
	    self.setEnabled(1)
	    self.setHidden(0)
	    
	    self._currentPhaseAssignment.phaseAssignmentChanged.connect(self.LoadPhaseAssignment)	    
	    
	    #set title
	    self.PhaseAssignmentBox.setTitle("PhaseAssignment: "+str(self._currentPhaseAssignment.project._name)+" - "+str(self._currentPhaseAssignment._name))
	    
	    self.userTable.UpdateWidget()
	    #set Status
	    #self.shotStatus.setCurrentIndex(self._currentShot._idstatuses-1)
	    
	    #set Description
	    #if self._currentShot is not None and self._currentShot._description is not None:
		#self.shotDescription.blockSignals = 1
		#self.shotDescription.setText(self._currentShot._description)
		#self.shotDescription.blockSignals = 0
	    
	self._blockUpdates = 0
    '''
    def setShotSettingsEnabled(self, v):
	self.shotNumber.setEnabled(v)
	self.shotStatus.setEnabled(v)
	self.startFrame.setEnabled(v)
	self.endFrame.setEnabled(v)
	self.shotImage.setEnabled(v)
	self.shotDescription.setEnabled(v)
	self.shotNotes.setEnabled(v)
    
    def SetShotValues(self):
	if not self._blockUpdates:
		if self._currentShot is not None:
		    #self._currentShot._description = self.shotDescription.toPlainText()
		    self._currentShot._idstatuses = self.shotStatus.currentIndex()+1
		    self._currentShot._startframe = self.startFrame.value()
		    self._currentShot._endframe = self.endFrame.value()
		    self._currentShot._updated = 1
    '''