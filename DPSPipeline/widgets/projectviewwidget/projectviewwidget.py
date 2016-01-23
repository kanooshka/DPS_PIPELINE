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
from DPSPipeline.widgets.projectviewwidget import shotTreeWidget
from DPSPipeline.widgets import textEditAutosave
from DPSPipeline import clickableImageQLabel

class ProjectViewWidget(QWidget):
    #shotImageFound = QtCore.pyqtSignal(QtCore.QString)
    refreshProjectValuesSignal = QtCore.pyqtSignal()
    
    def __init__( self, parent = None ):
    
	super(ProjectViewWidget, self).__init__( parent )
	
	self._currentProject = None
	
	# load the user interface# load the user interface
	if getattr(sys, 'frozen', None):
	    projexui.loadUi(sys._MEIPASS, self, uifile = (sys._MEIPASS+"/ui/projectviewwidget.ui"))
	    
	else:
	    projexui.loadUi(__file__, self)
	
	self.projectDescription = textEditAutosave.TextEditAutoSave()
	self.projDescrLayout.addWidget(self.projectDescription)
	self.projectDescription.save.connect(self.SaveProjectDescription)
	
	self.myProjectNameLineEdit = projectNameLineEdit.ProjectNameLineEdit(self)
	self.projectNameLayout.addWidget(self.myProjectNameLineEdit)
	
	self._backend               = None
	self._blockUpdates = 0
	
	sharedDB.myProjectViewWidget = self

	self.projectValueGrp.setEnabled(0)
	self.progressListGrpInner.setEnabled(0)
	self.AddImageBox.setHidden(1)
	
	
	self.stillImagesCheckbox.stateChanged.connect(self.ToggleStillImages)
	
	sharedDB.mySQLConnection.firstLoadComplete.connect(self.propogateUI)
	sharedDB.mySQLConnection.firstLoadComplete.connect(self.myProjectNameLineEdit.firstLoadComplete)
	
	self._shotTreeWidget = None
	#self.progressListLayout.addWidget(self._shotTreeWidget)
	#self.setProgressListVisibility()
	
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
	#self.saveProjectDescription.clicked.connect(self.SaveProjectDescription)
	self.projectPath.textChanged.connect(self.SetProjectValues)		
	self.projectPathButton.clicked.connect(self.changeProjectPath)
	
	self.addImageNameButton.clicked.connect(self.AddImagePath)
	self.imageNameLineEdit.returnPressed.connect(self.AddImagePath)
	
	#self.sequenceStatus.currentIndexChanged[QtCore.QString].connect(self.SetSequenceValues)
	self.addSequence.clicked.connect(self.AddSequence)
	self.updateFolderStructure.clicked.connect(self.CreateFolderStructure)
	
	self.setEnabled(1)
	self.setProgressListVisibility()
    
    def cancel(self):
	self.close()

    def CreateFolderStructure(self):
	paths = []
	if os.path.isdir(str(self.projectPath.text())):
	    for seq in self._currentProject._sequences.values():
		for shot in seq._shots.values():
		    paths.append(str(self.projectPath.text()+"\\Animation\\seq_"+seq._number+"\\shot_"+seq._number+"_"+shot._number+"\\maya\\anim\\"))
		    paths.append(str(self.projectPath.text()+"\\Animation\\seq_"+seq._number+"\\shot_"+seq._number+"_"+shot._number+"\\img\\"))
		    paths.append(str(self.projectPath.text()+"\\Animation\\seq_"+seq._number+"\\shot_"+seq._number+"_"+shot._number+"\\maya\\lighting\\"))
		    paths.append(str(self.projectPath.text()+"\\Animation\\seq_"+seq._number+"\\shot_"+seq._number+"_"+shot._number+"\\maya\\fx\\"))
		    paths.append(str(self.projectPath.text()+"\\Animation\\seq_"+seq._number+"\\shot_"+seq._number+"_"+shot._number+"\\currentFootage\\"))
	    
	    for image in self._currentProject._images.values():
		paths.append(str(self.projectPath.text()+"\\"+image._number+"\\_SCENES\\"))
		paths.append(str(self.projectPath.text()+"\\"+image._number+"\\_PREVIEWS\\"))
		paths.append(str(self.projectPath.text()+"\\"+image._number+"\\_ASSETS\\"))
		paths.append(str(self.projectPath.text()+"\\"+image._number+"\\_RENDERS\\"))
		paths.append(str(self.projectPath.text()+"\\"+image._number+"\\_COMP\\"))
	    
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
	    #self.saveProjectDescription.setVisible(0)
	if sharedDB.currentUser._idPrivileges == 2:
	    self.projectPathButton.setVisible(1)
	    self.projectDescription.setReadOnly(0)
	    
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
	    #self.shotStatus.addItem(status._name, QVariant(status))

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
	    self._currentProject._description = self.projectDescription.toPlainText()
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
	    self.progressListGrpInner.setEnabled(1)
	    #self.ShotBox.setEnabled(0)
	    
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
	    
	    self.projectDescription.blockSignals = 1
	    
	    self.projectDescription.setSource(self._currentProject,"_description")
	    self.projectDescription.getSourceText()	    
	    
	    self.projectDescription.blockSignals = 0
	    
	    self.LoadProgressListValues()
	    
	    self.setProgressListVisibility()
	    
	self._blockUpdates = 0
	#self.blockSignals(False)
	
    def AddImagePath(self):
	self.stillImagesCheckbox.setHidden(1)
	
	unique = 1
	
	#get sequence name
	newName = self.getImageName()
	
	if len(newName):
	
	    #iterate through sequences
	    for image in self._currentProject._images.values():	    
		#if image matches name
		if newName == image._number:
		    unique = 0
		    break
		
	    #if unique
	    if unique:
		#add image
		im = self._currentProject.AddShotToProject(newName)
		self.CreateTasks(shot = im)
		#im.shotAdded.connect(self.CreateTasks)
		#im.shotAdded.connect(self.AddShotToProgressList)
		
	    else:
		#warning message
		message = QtGui.QMessageBox.question(self, 'Message',
	    "Image name already exists, choose a unique name.", QtGui.QMessageBox.Ok)
	else:
	    message = QtGui.QMessageBox.question(self, 'Message',
	    "Please enter a name.", QtGui.QMessageBox.Ok)
	
    def AddSequence(self):
	unique = 1
	
	#get sequence name
	newName = self.getSequenceName()
	
	#iterate through sequences
	for sequence in self._currentProject._sequences.values():	    
	    #if sequence matches name
	    if newName == sequence._number:
		unique = 0
		break
	    
	#if unique
	if unique:
	    #add sequence
	    seq = self._currentProject.AddSequenceToProject(newName)
	    self.AddSequenceToProgressList(sequence = seq)
	    #seq.sequenceAdded.connect(self.AddSequenceToProgressList)
	    
	else:
	    #warning message
	    message = QtGui.QMessageBox.question(self, 'Message',
	"Sequence name already exists, choose a unique name (it is recommended to leave 10 between each sequence in case sequences need to be added in the middle)", QtGui.QMessageBox.Ok)

    def getSequenceName(self):
	sName = str(self.newSequenceNumber.value())
	while( len(sName)<3):
	    sName = "0"+sName
    
	return sName
    
    def getImageName(self):
	return self.imageNameLineEdit.text()
	    
    def LoadProgressListValues(self):
	self.progressList.clear()
	
	#self._shotTreeWidget.addTopLevelItem(self._shotTreeWidget.shotTreeItem)
	
	self.progressList.sortByColumn(0, QtCore.Qt.AscendingOrder);
	self.progressList.setSortingEnabled(True);
	self._currentSequence = None
	
	if (self._currentProject._sequences):
	    for seqid in self._currentProject._sequences:
		sequence = self._currentProject._sequences[str(seqid)]
	    #for x in range(0,len(self._currentProject._sequences)):
		#sequence = self._currentProject._sequences[x]
		    
		#Add Sequences to list
		self.AddSequenceToProgressList(sequence = sequence)
	elif (self._currentProject._images):
	    
	    self.stillImagesCheckbox.setChecked(1)
	    self.CreateShotTreeWidget()
	    
	    for imageid in self._currentProject._images:
		image = self._currentProject._images[str(imageid)]
		self.AddShotToProgressList(shot = image)
	    '''
	    for x in range(0,len(self._currentProject._images)):
		image = self._currentProject._images[x]
		#Add Shot to list
		self.AddShotToProgressList(shot = image)
	    '''
    
    def CreateShotTreeWidget(self):
	self.progressList.clear()
	self._shotTreeWidget = shotTreeWidget.ShotTreeWidget(self._currentProject,None,self)
	self._shotTreeWidget.setProject(self._currentProject)
	self._shotTreeWidget.SetupTable()
	#add shotwidget to progresslist
	self.progressList.addTopLevelItem(self._shotTreeWidget.shotTreeItem)        
	self.progressList.setItemWidget(self._shotTreeWidget.shotTreeItem,0,self._shotTreeWidget)

    def AddSequenceToProgressList(self, seqid = None, sequence = None):
	if sequence is None:
	    #print "getting sequence by id"
	    if str(seqid) in sharedDB.mySequences:
		sequence = sharedDB.mySequences[str(seqid)]
	
	if sequence is not None and self._currentProject is not None:
	    if str(sequence._idprojects) == str(self._currentProject._idprojects):
	    
		#Add Sequences to list
		sequenceTreeItem = sequenceTreeWidgetItem.SequenceTreeWidgetItem(sequence, self.progressList, self._currentProject,self)	    		
		self.progressList.addTopLevelItem(sequenceTreeItem)
		sequenceTreeItem.setExpanded(True)
		#self.CreateFolderStructure()
    	
    def AddShotToProgressList(self, shotid = None, shot = None):
	if shot is None:
	    #print "getting shot by id"
	    if str(shotid) in sharedDB.myShots:
		shot = sharedDB.myShots[str(shotid)]
	
	if shot is not None and self._currentProject is not None:
	    if str(shot._idprojects) == str(self._currentProject._idprojects):
		if self.stillImagesCheckbox.isChecked():
		    self._shotTreeWidget.AddShot(shot)
		    #print "BLAH"
		    #self.UpdateShots()
		
		else:
		    for x in range(0,self.progressList.topLevelItemCount()):
			if self.progressList.topLevelItem(x)._sequence._idsequences == shot._idsequences:
			    seqTreeItem = self.progressList.topLevelItem(x)
		    
			    #add shot to that widget
			    seqTreeItem._shotTreeWidget.AddShot(shot)		
			    #self.CreateFolderStructure()
			    break
	
    def setProgressListVisibility(self):
	if self._currentProject is not None:
	
	    if len(self._currentProject._sequences):
		self.stillImagesCheckbox.setHidden(1)
		self.stillImagesCheckbox.setChecked(0)
		self.AddImageBox.setHidden(1)
		#self._shotTreeWidget.setHidden(1)
		#self.progressList.setHidden(0)
		self.AddSequenceBox.setHidden(0)
	    elif len(self._currentProject._images):
		self.stillImagesCheckbox.setHidden(1)
		self.stillImagesCheckbox.setChecked(1)
		self.AddImageBox.setHidden(0)
		#self._shotTreeWidget.setHidden(0)
		#self.progressList.setHidden(1)
		self.AddSequenceBox.setHidden(1)
	    else:
		self.stillImagesCheckbox.setHidden(0)
		self.stillImagesCheckbox.setChecked(0)
		#self.progressList.setHidden(0)
		#self._shotTreeWidget.setHidden(1)
		self.AddSequenceBox.setHidden(0)
		self.AddImageBox.setHidden(1)		
	else:
	    self.stillImagesCheckbox.setHidden(0)
	    self.stillImagesCheckbox.setChecked(0)
	    #self.progressList.setHidden(0)
	    #if self._shotTreeWidget is not None:
		#self._shotTreeWidget.setHidden(1)
	    self.AddSequenceBox.setHidden(0)
	    self.AddImageBox.setHidden(1)
	
	pass

    def ToggleStillImages(self):
	#if self._currentProject._sequences is None:	
	if self.stillImagesCheckbox.isChecked():
	    self.AddSequenceBox.setHidden(1)
	    self.AddImageBox.setHidden(0)
	    #self._shotTreeWidget.setHidden(0)
	    #self.progressList.setHidden(1)
	    
	else:
	    self.AddSequenceBox.setHidden(0)
	    self.AddImageBox.setHidden(1)
	    #self._shotTreeWidget.setHidden(1)
	    #self.progressList.setHidden(0)
	    
    def setSequenceSettingsEnabled(self, v):
	self.sequenceNumber.setEnabled(v)
	self.sequenceStatus.setEnabled(v)
	self.sequenceDescription.setEnabled(v)


    def CreateTasks(self, shotid = None, shot = None):
	if shot is None:
	    print "getting shot by id "+str(shotid)
	    shot = self.GetShotByID(shotid)

	if shot is not None:
	    
	    #add shot to that widget
	    if self._shotTreeWidget is None:
		self.CreateShotTreeWidget()
	    		
	    
	    if not sharedDB.autoCreateShotTasks:
		self.selectShotByName(shot._number)
		for phase in self._currentProject._phases.values():	    
		    if phase._taskPerShot:
			task = sharedDB.tasks.Tasks(_idphaseassignments = phase._idphaseassignments, _idprojects = self._currentProject._idprojects, _idshots = shot._idshots, _idphases = phase._idphases, _new = 1)
			task.taskAdded.connect(self._shotTreeWidget.AttachTaskToButton)			
			task.Save()
			
			shot._tasks[str(task.id())] = task
			
	    self._shotTreeWidget.AddShot(shot)
	    
	else:
	    print "SHOT NOT FOUND!"
    def selectShotByName(self, sName):
	
	stree = self._shotTreeWidget
	#item = stree.findItems(sName,1)
	for x in range(0,stree.topLevelItemCount()):
	    print stree.topLevelItem(x).text(1)
	    print sName
	    if str(stree.topLevelItem(x).text(1))==str(sName):
		item = stree.topLevelItem(x)
		stree.setCurrentItem(item)
		break