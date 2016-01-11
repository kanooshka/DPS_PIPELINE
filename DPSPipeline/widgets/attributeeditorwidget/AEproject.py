import projexui
import sharedDB
import sys

from PyQt4 import QtGui,QtCore

class AEProject(QtGui.QWidget):

    def __init__( self, parent = None ):
    
	super(AEProject, self).__init__( parent )
	
	self._noImage = projexui.resources.find('img/DP/noImage.png')
	
	# load the user interface# load the user interface
	if getattr(sys, 'frozen', None):
	    projexui.loadUi(sys._MEIPASS, self, uifile = (sys._MEIPASS+"/ui/AEproject.ui"))	    
	else:
	    projexui.loadUi(__file__, self)
	
	self.setHidden(1)

	self.setEnabled(0)
    
    def LoadProject(self, sentProject):

	self._blockUpdates = 1
	
	if isinstance(sentProject, sharedDB.projects.Projects):
	    self._currentProject = sentProject

	if self._currentProject is not None:
	    
	    if len(sharedDB.sel.items):
		if hasattr(sharedDB.sel.items[len(sharedDB.sel.items)-1], "_type") and sharedDB.sel.items[len(sharedDB.sel.items)-1]._type == "project":	    
		    self.setEnabled(1)
		    self.setHidden(0)
		    
		    self._currentProject.projectChanged.connect(self.LoadProject)	    
		    
		    #set title
		    self.ProjectBox.setTitle("Project: "+str(self._currentProject._name))
		    
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