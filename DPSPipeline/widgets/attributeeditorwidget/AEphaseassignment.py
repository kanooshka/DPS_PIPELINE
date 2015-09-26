import projexui
import sharedDB
import sys

from PyQt4 import QtGui,QtCore

class AEPhaseAssignment(QtGui.QWidget):

    def __init__( self, parent = None ):
    
	super(AEPhaseAssignment, self).__init__( parent )
	
	# load the user interface# load the user interface
	if getattr(sys, 'frozen', None):
	    projexui.loadUi(sys._MEIPASS, self, uifile = (sys._MEIPASS+"/ui/AEPhaseAssignment.ui"))	    
	else:
	    projexui.loadUi(__file__, self)
	
	self.setHidden(1)

	self.setEnabled(0)
    
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
	    
	    #set Status
	    #self.shotStatus.setCurrentIndex(self._currentShot._idstatuses-1)
	    
	    #set Description
	    #if self._currentShot is not None and self._currentShot._description is not None:
		#self.shotDescription.blockSignals = 1
		#self.shotDescription.setText(self._currentShot._description)
		#self.shotDescription.blockSignals = 0
	    
	self._blockUpdates = 0
    
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