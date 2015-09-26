import weakref
import projexui
import sharedDB
import math
import sys
import os
import glob

import multiprocessing
import time

from datetime import timedelta,datetime
#from projexui import qt import Signal
from PyQt4 import QtGui,QtCore
#from PyQt4 import QtCore
from PyQt4.QtGui    import QWidget
from PyQt4.QtCore   import QDate,QTime,QVariant,Qt
from DPSPipeline import clickableImageQLabel
from DPSPipeline.widgets import textEditAutosave


class CheckForImagePath(QtCore.QThread):

    def run(self):
	#search for image
	sentpath = sharedDB.myAttributeEditorWidget.shotWidget.shotImageDir
	
	try:
		newImage = max(glob.iglob(os.path.join(sentpath, '*.[Jj][Pp]*[Gg]')), key=os.path.getctime)
		if len(newImage)>3:
			print "Loading Shot Image: "+newImage
			sharedDB.myAttributeEditorWidget.shotWidget.shotImagePath = newImage
			sharedDB.myAttributeEditorWidget.shotWidget.shotImageFound.emit(newImage)
		
	except:
	    print "No Image file found for selected shot"
	    
class CheckForPlayblastPath(QtCore.QThread):

    def run(self):
	#search for image
	sentpath = sharedDB.myAttributeEditorWidget.shotWidget.shotPlayblastDir
	
	try:
		newPlayblast = max(glob.iglob(os.path.join(sentpath, '*.[Mm][Oo][Vv]')), key=os.path.getctime)

		if len(newPlayblast)>3:
		    print "Loading Shot Playblast: "+newPlayblast
		    os.startfile(newPlayblast)
		
	except:
	    print "No Playblast file found for selected shot"

class AEShot(QWidget):
    shotImageFound = QtCore.pyqtSignal(QtCore.QString)
    
    def __init__( self, parent = None ):
    
	super(AEShot, self).__init__( parent )
	
	self._noImage = projexui.resources.find('img/DP/noImage.png')
	
	# load the user interface# load the user interface
	if getattr(sys, 'frozen', None):
	    projexui.loadUi(sys._MEIPASS, self, uifile = (sys._MEIPASS+"/ui/AEshot.ui"))	    
	else:
	    projexui.loadUi(__file__, self)
	
	self.setHidden(1)
	
	self.shotImage = clickableImageQLabel.ClickableImageQLabel(self)
	self.shotImageLayout.addWidget(self.shotImage)
	
	self.shotDescription = textEditAutosave.TextEditAutoSave()
	self.shotDescriptionLayout.addWidget(self.shotDescription)
	self.shotDescription.save.connect(self.SaveShotDescription)
	
	self.shotNotes = textEditAutosave.TextEditAutoSave()
	self.shotNotesLayout.addWidget(self.shotNotes)
	self.shotNotes.save.connect(self.SaveShotNotes)
	
	self.cfip = CheckForImagePath()
	self.shotImageFound.connect(self.shotImage.assignImage)
	self.shotImageDir = ''	
	
	self.cfpb = CheckForPlayblastPath()
	self.shotPlayblastPath = None
	self.shotPlayblastDir = ''
	self.shotImage.clicked.connect(self.checkForPlayblast)
	
	self.startFrame.valueChanged.connect(self.SetShotValues)
	self.endFrame.valueChanged.connect(self.SetShotValues)
	
	self._backend               = None
	self._blockUpdates = 0

	self.setEnabled(0)
    
    def LoadShot(self, sentShot):

	self._blockUpdates = 1
	

	self._currentShot = sentShot

	if self._currentShot is not None:
	    
	    self.setEnabled(1)
	    self.setHidden(0)
	    
	    self._currentShot.shotChanged.connect(self.LoadShot)
	    
	    self.checkForShotImage()		    
	    
	    #set title
	    self.ShotBox.setTitle("Shot "+str(self._currentShot._sequence._number)+"_"+str(self._currentShot._number))
	    
	    #set Status
	    self.shotStatus.setCurrentIndex(self._currentShot._idstatuses-1)
	    
	    #set frame range
	    self.startFrame.setValue(self._currentShot._startframe)
	    self.endFrame.setValue(self._currentShot._endframe)
	    
	    #set Description
	    if self._currentShot is not None and self._currentShot._description is not None:
		self.shotDescription.blockSignals = 1
		self.shotDescription.setText(self._currentShot._description)
		self.shotDescription.blockSignals = 0
	    
	    self.shotNotes.blockSignals = 1
	    if self._currentShot._shotnotes is None or self._currentShot._shotnotes == '' or self._currentShot._shotnotes == 'None':
		    self.shotNotes.setText('Anim-\n\nShot Prep-\n\nFX-\n\nSound-\n\nLighting-\n\nComp-\n\nRendering-')
	    else:
		    self.shotNotes.setText(self._currentShot._shotnotes)
	    self.shotNotes.blockSignals = 0
	    
	self._blockUpdates = 0    
    
	#connect shot settings
	#self.saveShotDescription.clicked.connect(self.SaveShotDescription)
	
	#self.saveShotNotes.clicked.connect(self.SaveShotNotes)

    def ensure_dir(self,f):  
	#print f.replace("\\", "\\\\")
	d = os.path.dirname(f)
	#print d
	if not os.path.exists(d):
	    os.makedirs(d)

    def checkForShotImage(self):
	shot= self._currentShot
	seq = self._currentShot._sequence
	
	if len(seq._project._folderLocation)>3:
	    d = str(seq._project._folderLocation+"\\Animation\\seq_"+seq._number+"\\shot_"+seq._number+"_"+shot._number+"\\img\\")	   
	    
	    #myPixmap = QtGui.QPixmap(self._noImage)
	    self.shotImage.assignImage()
	    #if os.path.isdir(d):
	    if shot is not None:	
		    if len(seq._project._folderLocation):
			self.shotImageDir = d
			self.cfip.start()
    
    def checkForPlayblast(self):
	shot= self._currentShot
	seq = self._currentShot._sequence
	
	if len(seq._project._folderLocation)>3:
	    d = str(seq._project._folderLocation+"\\Animation\\seq_"+seq._number+"\\shot_"+seq._number+"_"+shot._number+"\\currentFootage\\")	   
	    
	    #if os.path.isdir(d):
	    if shot is not None:	
		    if len(seq._project._folderLocation):
			self.shotPlayblastDir = d
			self.cfpb.start()
    
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
	    
	    
    def SaveShotDescription(self):
	#if not self._blockUpdates:
	if self._currentShot is not None:
	    if not (self.shotDescription.toPlainText() == self._currentShot._description):
		    self._currentShot._description = self.shotDescription.toPlainText()
		    self._currentShot._updated = 1

    def SaveShotNotes(self):
	#if not self._blockUpdates:
	if self._currentShot is not None:
	    if not (self.shotNotes.toPlainText() == self._currentShot._shotnotes):
		    self._currentShot._shotnotes = self.shotNotes.toPlainText()
		    self._currentShot._updated = 1