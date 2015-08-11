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
from DPSPipeline.database import projects
from DPSPipeline.widgets.projectviewwidget import sequenceTreeWidgetItem
from DPSPipeline.widgets.projectviewwidget import projectNameLineEdit
from DPSPipeline import clickableImageQLabel


class CheckForImagePath(QtCore.QThread):

    def run(self):
	#search for image
	sentpath = sharedDB.myProjectViewWidget.shotImageDir
	
	try:
		newImage = max(glob.iglob(os.path.join(sentpath, '*.[Jj][Pp]*[Gg]')), key=os.path.getctime)
		if len(newImage)>3:
			print "Loading Shot Image: "+newImage
			sharedDB.myProjectViewWidget.shotImagePath = newImage
			sharedDB.myProjectViewWidget.shotImageFound.emit(newImage)
		
	except:
	    print "No Image file found for selected shot"
	    
class CheckForPlayblastPath(QtCore.QThread):

    def run(self):
	#search for image
	sentpath = sharedDB.myProjectViewWidget.shotPlayblastDir
	
	try:
		newPlayblast = max(glob.iglob(os.path.join(sentpath, '*.[Mm][Oo][Vv]')), key=os.path.getctime)

		if len(newPlayblast)>3:
		    print "Loading Shot Playblast: "+newPlayblast
		    os.startfile(newPlayblast)
		
	except:
	    print "No Playblast file found for selected shot"

class ProjectViewWidget(QWidget):
    shotImageFound = QtCore.pyqtSignal(QtCore.QString)
    refreshProjectValuesSignal = QtCore.pyqtSignal()
    
    def __init__( self, parent = None ):
    
	super(ProjectViewWidget, self).__init__( parent )
	
	self._currentProject = None
	self._currentSequence = None
	self._currentShot = None
	
	self._noImage = projexui.resources.find('img/DP/noImage.png')
	
	# load the user interface# load the user interface
	if getattr(sys, 'frozen', None):
	    projexui.loadUi(sys._MEIPASS, self, uifile = (sys._MEIPASS+"/ui/projectviewwidget.ui"))
	    
	else:
	    projexui.loadUi(__file__, self)
	
	self.shotImage = clickableImageQLabel.ClickableImageQLabel(self)
	self.shotImageLayout.addWidget(self.shotImage)
	
	self.myProjectNameLineEdit = projectNameLineEdit.ProjectNameLineEdit(self)
	self.projectNameLayout.addWidget(self.myProjectNameLineEdit)
	
	self.cfip = CheckForImagePath()
	self.shotImageFound.connect(self.shotImage.assignImage)
	self.shotImageDir = ''	
	
	self.cfpb = CheckForPlayblastPath()
	self.shotPlayblastPath = None
	self.shotPlayblastDir = ''
	self.shotImage.clicked.connect(self.checkForPlayblast)
	
	self._backend               = None
	self._blockUpdates = 0
	
	sharedDB.myProjectViewWidget = self

	self.projectValueGrp.setEnabled(0)
	self.progressListGrp.setEnabled(0)
	self.ShotBox.setEnabled(0)
	
	sharedDB.mySQLConnection.firstLoadComplete.connect(self.propogateUI)
    
    def propogateUI(self, ):
	self.setPrivelages()

	#connects signals
	sharedDB.mySQLConnection.newSequenceSignal.connect(self.AddSequenceToProgressList)
	sharedDB.mySQLConnection.newShotSignal.connect(self.AddShotToProgressList)
	self.refreshProjectValuesSignal.connect(self.LoadProjectValues)
	
	self.propogateStatuses()		
	
	#connect project settings
	self.projectStatus.currentIndexChanged[QtCore.QString].connect(self.SetProjectValues)
	self.fps.valueChanged.connect(self.SetProjectValues)
	self.dueDate.dateChanged.connect(self.SetProjectValues)
	self.renderWidth.valueChanged.connect(self.SetProjectValues)
	self.renderHeight.valueChanged.connect(self.SetProjectValues)
	self.saveProjectDescription.clicked.connect(self.SaveProjectDescription)
	self.projectPath.textChanged.connect(self.SetProjectValues)		
	self.projectPathButton.clicked.connect(self.changeProjectPath)
	
	#self.sequenceStatus.currentIndexChanged[QtCore.QString].connect(self.SetSequenceValues)
	self.addSequence.clicked.connect(self.AddSequence)
	self.updateFolderStructure.clicked.connect(self.CreateFolderStructure)
	
	#connect shot settings
	self.saveShotDescription.clicked.connect(self.SaveShotDescription)
	self.startFrame.valueChanged.connect(self.SetShotValues)
	self.endFrame.valueChanged.connect(self.SetShotValues)
	self.saveShotNotes.clicked.connect(self.SaveShotNotes)

	self.setEnabled(1)    
    
    def cancel(self):
	self.close()

    def CreateFolderStructure(self):
	paths = []
	if os.path.isdir(str(self.projectPath.text())):
	    for seq in self._currentProject._sequences:
		for shot in seq._shots:
		    paths.append(str(self.projectPath.text()+"\\Animation\\seq_"+seq._number+"\\shot_"+seq._number+"_"+shot._number+"\\maya\\anim\\"))
		    paths.append(str(self.projectPath.text()+"\\Animation\\seq_"+seq._number+"\\shot_"+seq._number+"_"+shot._number+"\\img\\"))
		    paths.append(str(self.projectPath.text()+"\\Animation\\seq_"+seq._number+"\\shot_"+seq._number+"_"+shot._number+"\\maya\\lighting\\"))
		    paths.append(str(self.projectPath.text()+"\\Animation\\seq_"+seq._number+"\\shot_"+seq._number+"_"+shot._number+"\\maya\\fx\\"))
		    paths.append(str(self.projectPath.text()+"\\Animation\\seq_"+seq._number+"\\shot_"+seq._number+"_"+shot._number+"\\currentFootage\\"))

	    for path in paths:
		self.ensure_dir(path)
	else:
	    message = QtGui.QMessageBox.question(self, 'Message',
	"Project Directory is not valid. Please select a directory.", QtGui.QMessageBox.Ok)
	
    def setPrivelages(self):
        
        if sharedDB.currentUser._idPrivileges > 1:
            #Project privelages
	    self.projectStatus.setEnabled(0)
	    self.projectPathButton.setVisible(0)
	    self.fps.setEnabled(0)
	    self.dueDate.setEnabled(0)
	    self.renderHeight.setEnabled(0)
	    self.renderWidth.setEnabled(0)
	    self.projectDescription.setReadOnly(1)
	    self.saveProjectDescription.setVisible(0)
        
	
    def projectChanged(self,projectId):
        #set project name
	for project in sharedDB.myProjects:	
		if str(project._idprojects) == projectId:
			for x in range(0,self.projectName.count()):
				if self.projectName.itemData(x, Qt.ToolTipRole).toString() == str(project._idprojects):
					#print (project._name +" project has changed.")
					self.projectName.setItemText(x,project._name)
					if x == self.projectName.currentIndex():
						self.LoadProjectValues()
					break;

    def ensure_dir(self,f):  
	#print f.replace("\\", "\\\\")
	d = os.path.dirname(f)
	#print d
	if not os.path.exists(d):
	    os.makedirs(d)
    
    def propogateProjectNames(self):
	self.projectName.clear()

	for p in range(0,len(sharedDB.myProjects)):
	    project = sharedDB.myProjects[p]
	    if not project._hidden:
		#print project._name
		#item = QtGui.QListWidgetItem(project._name)
		
		self.projectName.addItem(project._name,QVariant(project))
		#print "setting project "+str(project._name)+"'s tooltip to "+str(project._idprojects)
		self.projectName.setItemData(self.projectName.count()-1,project._idprojects, Qt.ToolTipRole)
		project.projectChanged.connect(self.projectChanged)
	
	self.LoadProjectValues()
	
	#self.refreshTasks()
	
    def getCurrentProjectID(self):
		return self.projectName.itemData(self.projectName.currentIndex(), Qt.ToolTipRole).toString()
		
    def propogateStatuses(self):
	for status in sharedDB.myStatuses:
	    self.projectStatus.addItem(status._name, QVariant(status))
	    self.sequenceStatus.addItem(status._name, QVariant(status))
	    self.shotStatus.addItem(status._name, QVariant(status))

    def changeProjectPath(self):
	startingPath = ''
	
	if self._currentProject._folderLocation is not None and len(self._currentProject._folderLocation):
	    startingPath = self._currentProject._folderLocation
	
	fname = QtGui.QFileDialog.getExistingDirectory (self, 'Select Folder', startingPath)
	
	if len(fname):		
	    if self._currentProject._folderLocation is not fname:
		self.projectPath.setText(fname)
		self._currentProject._updated=1
		self._currentProject._folderLocation=fname
	    
    def SetProjectValues(self):
	if not self._blockUpdates:
	    #self._currentProject._name = self.projectName.currentText()
	    self._currentProject._idstatuses = self.projectStatus.currentIndex()+1
	    self._currentProject._fps = self.fps.value()
	    self._currentProject._due_date = self.dueDate.date().toPyDate()
	    self._currentProject._renderWidth = self.renderWidth.value()
	    self._currentProject._renderHeight = self.renderHeight.value()
	    #self._currentProject._description = self.projectDescription.toPlainText()
	    self._currentProject._folderLocation = self.projectPath.text()
	    self._currentProject._updated = 1

    def SaveProjectDescription(self):
	if not (self.projectDescription.toPlainText() == self._currentProject._description):
		self._currentProject._description = self.projectDescription.toPlainText()
		self._currentProject._updated = 1

    def LoadProjectValues(self):
	self._blockUpdates = 1
	#self.blockSignals(True)
	
	if self._currentProject is not None:
	    #set name
	    self.projectValueGrp.setEnabled(1)
	    self.progressListGrp.setEnabled(1)
	    self.ShotBox.setEnabled(0)
	    
	    self.myProjectNameLineEdit.setText(str(self._currentProject._name)+"        (Right Click to Switch Project)")
	    
	    self.newSequenceNumber.setValue(10)
	    #set FPS
	    self.fps.setValue(self._currentProject._fps)
	    #set Path
	    if self._currentProject._folderLocation is not None:
		self.projectPath.setText(self._currentProject._folderLocation)
	    else:
		self.projectPath.setText('')
	    #set Status
	    self.projectStatus.setCurrentIndex(self._currentProject._idstatuses-1)
	    #set res
	    self.renderWidth.setValue(self._currentProject._renderWidth)
	    self.renderHeight.setValue(self._currentProject._renderHeight)
	    #set Due Date
	    self.dueDate.setDate(self._currentProject._due_date)
	    #set Description
	    #print self._currentProject._description
	    if self._currentProject._description is not None:
		    self.projectDescription.setText(self._currentProject._description)
	    else:
		    self.projectDescription.setText('')
		    
	    self.LoadProgressListValues()
    
	self._blockUpdates = 0
	#self.blockSignals(False)
	
    
    def AddSequence(self):
	unique = 1
	
	#get sequence name
	newName = self.getSequenceName()
	
	#iterate through sequences
	for sequence in self._currentProject._sequences:	    
	    #if sequence matches name
	    if newName == sequence._number:
		unique = 0
		break
	    
	#if unique
	if unique:
	    #add sequence
	    seq = self._currentProject.AddSequenceToProject(newName)
	    seq.sequenceAdded.connect(self.AddSequenceToProgressList)
	    
	else:
	    #warning message
	    message = QtGui.QMessageBox.question(self, 'Message',
	"Sequence name already exists, choose a unique name (it is recommended to leave 10 between each sequence in case sequences need to be added in the middle)", QtGui.QMessageBox.Ok)

    def getSequenceName(self):
	sName = str(self.newSequenceNumber.value())
	while( len(sName)<3):
	    sName = "0"+sName
    
	return sName
	    
    def LoadProgressListValues(self):
	self.progressList.clear()
	self.progressList.sortByColumn(0, QtCore.Qt.AscendingOrder);
	self.progressList.setSortingEnabled(True);
	self._currentSequence = None
	
	if (self._currentProject._sequences):
	    for x in range(0,len(self._currentProject._sequences)):
		sequence = self._currentProject._sequences[x]
		    
		#Add Sequences to list
		self.AddSequenceToProgressList(sequence = sequence)
    
    def GetSequenceByID(self,seqid):
	if self._currentProject is not None:
		if self._currentProject._sequences is not None:
			for seq in self._currentProject._sequences:
			    if str(seq._idsequences) == str(seqid):
				return seq    
    
    def AddSequenceToProgressList(self, seqid = None, sequence = None):
	if sequence is None:
	    #print "getting sequence by id"
	    sequence = self.GetSequenceByID(seqid)
	
	if sequence is not None:
		if str(sequence._idprojects) == str(self._currentProject._idprojects):
		
		    #Add Sequences to list
		    sequenceTreeItem = sequenceTreeWidgetItem.SequenceTreeWidgetItem(sequence, self.progressList, self._currentProject,self)	    		
		    self.progressList.addTopLevelItem(sequenceTreeItem)
		    sequenceTreeItem.setExpanded(True)	    
    	
    def GetShotByID(self,shotid):
	if self._currentProject is not None:
		for seq in self._currentProject._sequences:
		    for shot in seq._shots:
			if str(shot._idshots) == str(shotid):
			    return shot	   
    
    def AddShotToProgressList(self, shotid = None, shot = None):
	if shot is None:
	    #print "getting shot by id"
	    shot = self.GetShotByID(shotid)
	
	if shot is not None:
		for x in range(0,self.progressList.topLevelItemCount()):
		    if self.progressList.topLevelItem(x)._sequence._idsequences == shot._idsequences:
			seqTreeItem = self.progressList.topLevelItem(x)
		
			#add shot to that widget
			seqTreeItem._shotTreeWidget.AddShot(shot)		
			break

    def setSequenceSettingsEnabled(self, v):
	self.sequenceNumber.setEnabled(v)
	self.sequenceStatus.setEnabled(v)
	self.sequenceDescription.setEnabled(v)

    def checkForShotImage(self):
	seq = self._currentSequence
	shot= self._currentShot
	
	if len(self.projectPath.text())>3 and seq is not None and shot is not None:
	    d = str(self.projectPath.text()+"\\Animation\\seq_"+seq._number+"\\shot_"+seq._number+"_"+shot._number+"\\img\\")	   
	    
	    #myPixmap = QtGui.QPixmap(self._noImage)
	    self.shotImage.assignImage()
	    #if os.path.isdir(d):
	    if shot is not None:	
		    if len(self.projectPath.text()):
			self.shotImageDir = d
			self.cfip.start()
    
    def checkForPlayblast(self):
	seq = self._currentSequence
	shot= self._currentShot
	
	if len(self.projectPath.text())>3 and seq is not None and shot is not None:
	    d = str(self.projectPath.text()+"\\Animation\\seq_"+seq._number+"\\shot_"+seq._number+"_"+shot._number+"\\currentFootage\\")	   
	    
	    #if os.path.isdir(d):
	    if shot is not None:	
		    if len(self.projectPath.text()):
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
    
    def LoadShotValuesFromSent(self,itemwidget, column):				
		    
	self._blockUpdates = 1
	#self.blockSignals(True)
	
	#make sure _currentSequence is current
	
	
	#self.setCurrentShot()
	self._currentShot = None
	
	for shot in sharedDB.myShots:
		if str(shot._idshots) == str(itemwidget.text(0)):
			self._currentShot = shot
			
			for seq in self._currentProject._sequences:
			    if seq._idsequences == shot._idsequences:
				self._currentSequence = seq
				break
			break

	if self._currentShot is not None and self._currentSequence is not None:
	    
	    self.ShotBox.setEnabled(1)
	    
	    self.checkForShotImage()		    
	    
	    #set title
	    self.ShotBox.setTitle("Shot "+str(self._currentSequence._number)+"_"+str(self._currentShot._number))
	    
	    #set Status
	    self.shotStatus.setCurrentIndex(self._currentShot._idstatuses-1)
	    
	    #set frame range
	    self.startFrame.setValue(self._currentShot._startframe)
	    self.endFrame.setValue(self._currentShot._endframe)
	    
	    #set Description
	    if self._currentShot is not None and self._currentShot._description is not None:
		self.shotDescription.setText(self._currentShot._description)
	    
	    
	    if self._currentShot._shotnotes is None or self._currentShot._shotnotes == '' or self._currentShot._shotnotes == 'None':
		    self.shotNotes.setText('Anim-\n\nShot Prep-\n\nFX-\n\nSound-\n\nLighting-\n\nComp-\n\nRendering-')
	    else:
		    self.shotNotes.setText(self._currentShot._shotnotes)
	
	self._blockUpdates = 0
    
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