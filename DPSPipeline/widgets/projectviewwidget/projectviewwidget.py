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

class ProjectViewWidget(QWidget):
   
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
	#projexui.loadUi(__file__, self)
	
	# define custom properties
	
	self._backend               = None
	self._blockUpdates = 0
	
	sharedDB.myProjectViewWidget = self
	
	self.setPrivelages()
	
	#connects signals
	sharedDB.mySQLConnection.newProjectSignal.connect(self.propogateProjectNames)
	sharedDB.mySQLConnection.newSequenceSignal.connect(self.LoadSequenceNames)
	sharedDB.mySQLConnection.newShotSignal.connect(self.LoadShotNames)
	
	#connects buttons
	#self.createButton.clicked.connect(self.CreateProject)
	#self.cancelButton.clicked.connect(self.cancel)
	self.propogateStatuses()
	self.propogateProjectNames()		
	
	#connect project settings
	self.projectName.currentIndexChanged[QtCore.QString].connect(self.LoadProjectValues)
	#self.projectName.currentIndexChanged[QtCore.QString].connect(self.LoadSequenceNames)
	#self.projectName.currentIndexChanged[QtCore.QString].connect(self.LoadShotNames)
	self.projectName.editTextChanged[QtCore.QString].connect(self.SetProjectValues)
	self.projectStatus.currentIndexChanged[QtCore.QString].connect(self.SetProjectValues)
	self.fps.valueChanged.connect(self.SetProjectValues)
	self.dueDate.dateChanged.connect(self.SetProjectValues)
	self.renderWidth.valueChanged.connect(self.SetProjectValues)
	self.renderHeight.valueChanged.connect(self.SetProjectValues)
	self.saveProjectDescription.clicked.connect(self.SaveProjectDescription)
	self.projectPath.textChanged.connect(self.SetProjectValues)		
	self.projectPathButton.clicked.connect(self.changeProjectPath)
	
	#connect sequence settings		
	self.sequenceNumber.currentRowChanged.connect(self.LoadSequenceValues)
	self.saveSequenceDescription.clicked.connect(self.SaveSequenceDescription)
	self.sequenceStatus.currentIndexChanged[QtCore.QString].connect(self.SetSequenceValues)
	self.addSequence.clicked.connect(self.AddSequence)
	self.updateFolderStructure.clicked.connect(self.CreateFolderStructure)
	
	#connect shot settings
	self.shotNumber.currentRowChanged.connect(self.LoadShotValues)
	self.saveShotDescription.clicked.connect(self.SaveShotDescription)
	self.shotStatus.currentIndexChanged[QtCore.QString].connect(self.SetShotValues)
	self.startFrame.valueChanged.connect(self.SetShotValues)
	self.endFrame.valueChanged.connect(self.SetShotValues)
	self.addShot.clicked.connect(self.AddShot)
	
	
	#connect task settings
	    
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
    
    '''def CheckForDBUpdates(self):
	
	#update projects
	for project in sharedDB.myProjects:
		if project._loadedChanges:			
			for x in range(0,self.projectName.count()):
				if self.projectName.itemData(x, Qt.ToolTipRole).toString() == str(project._idprojects):
					print (project._name +" project has changed.")
					self.projectName.setItemText(x,project._name)
					if x == self.projectName.currentIndex():
						self.LoadProjectValues()
					break;
	'''
	
    def setPrivelages(self):
        
        if sharedDB.currentUser[0]._idPrivileges > 1:
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
	
    def sequenceChanged(self,sequenceId):
        #set project name
	self.LoadSequenceNames()
	'''
	for seq in sharedDB.mySequences:	
		if str(seq._idsequences) == sequenceId:
			if self._currentProject._idprojects == seq._idprojects:
			#self._currentProject._sequences[int(self.sequenceNumber.currentItem().toolTip())]
			    for x in range(0,self.sequenceNumber.count()):
				    print self.sequenceNumber.item(x).data(Qt.ToolTipRole).toString()
				    if self.sequenceNumber.item(x).data(Qt.ToolTipRole).toString() == str(seq._idsequences):
					    print (seq._number +" project has changed.")
					    self.sequenceNumber.item(x).setText(seq._number)
					    if x == self.sequenceNumber.currentIndex():
						    self.LoadSequenceValues()
					    break;
	'''

    def shotChanged(self,shotId):
        #set project name
	self.LoadShotNames()
		    
    def ensure_dir(self,f):  
	#print f.replace("\\", "\\\\")
	d = os.path.dirname(f)
	#print d
	if not os.path.exists(d):
	    os.makedirs(d)
    
    def propogateProjectNames(self):
	#self.projectName.clear()
	for p in range(0,len(sharedDB.myProjects)):
	    project = sharedDB.myProjects[p]
	    #item = QtGui.QListWidgetItem(project._name)
	    project.projectChanged.connect(self.projectChanged)
	    self.projectName.addItem(project._name,QVariant(project))
	    self.projectName.setItemData(p,project._idprojects, Qt.ToolTipRole)
	    #self.projectName[p].setToolTip(p._idprojects)
	
	self.LoadProjectValues()
	#self.LoadSequenceNames()	
	#self.LoadSequenceValues()
	
	#self.LoadShotNames()
	#self.LoadShotValues()
	
	self.refreshTasks()
	
	def getCurrentProjectID():
		return self.projectName.itemData(p, Qt.ToolTipRole).toString()
		
	    
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
	    self._currentProject._name = self.projectName.currentText()
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
	self.blockSignals(True)
	
	self._currentProject = sharedDB.myProjects[self.projectName.currentIndex()]		
	
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
		
	
	self.LoadSequenceNames()
	self._blockUpdates = 1
	#self.LoadShotNames()
	self._blockUpdates = 0
	self.blockSignals(False)
    
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
	    self._currentProject.AddSequenceToProject(newName)
	    self.LoadSequenceNames()
	    self.selectSequenceByName(newName)
	    self.LoadShotNames()
	    #self.newSequenceNumber.setValue(self.newSequenceNumber.value()+10)
	    
	else:
	    #warning message
	    message = QtGui.QMessageBox.question(self, 'Message',
	"Sequence name already exists, choose a unique name (it is recommended to leave 10 between each sequence in case sequences need to be added in the middle)", QtGui.QMessageBox.Ok)
    
	#select sequence by name
    def selectSequenceByName(self, sName):
	for x in range(0,self.sequenceNumber.count()):
	    if self.sequenceNumber.item(x).text()==sName:
		self.sequenceNumber.setCurrentRow(x)
		break
	    
    def getSequenceName(self):
	sName = str(self.newSequenceNumber.value())
	while( len(sName)<3):
	    sName = "0"+sName
    
	return sName
    
    def SetSequenceValues(self):
	if not self._blockUpdates:
	    if self._currentSequence is not None:
		    #self._currentSequence._description = self.sequenceDescription.toPlainText()
		    self._currentSequence._idstatuses = self.sequenceStatus.currentIndex()+1
		    self._currentSequence._updated = 1

    def SaveSequenceDescription(self):
	if not self._blockUpdates:
	    if self._currentSequence is not None:
		if not (self.sequenceDescription.toPlainText() == self._currentSequence._description):
			self._currentSequence._description = self.sequenceDescription.toPlainText()
			self._currentSequence._updated = 1

    def LoadSequenceNames(self):
	self.sequenceNumber.clear()
	self._currentSequence = None
	self.sequenceDescription.setText('')
	self.sequenceStatus.setCurrentIndex(0)
	
	if (self._currentProject._sequences):
	    self.setSequenceSettingsEnabled(1)
	    for x in range(0,len(self._currentProject._sequences)):
		sequence = self._currentProject._sequences[x]
		sequence.sequenceChanged.connect(self.sequenceChanged)
		newWidgetItem = QtGui.QListWidgetItem()
		newWidgetItem.setText(sequence._number)
		newWidgetItem.setToolTip(str(x))
		#newWidgetItem.setFlags(newWidgetItem.flags() | QtCore.Qt.ItemIsEditable)
		#newWidgetItem.setData(sequence._number)
		self.sequenceNumber.addItem(newWidgetItem)
		    
		    
	    if self._currentProject._lastSelectedSequenceNumber == '-1':
		self.sequenceNumber.setCurrentRow(0)
	    else:
		for x in range(0,self.sequenceNumber.count()):
		    if self.sequenceNumber.item(x).text() == self._currentProject._lastSelectedSequenceNumber:
			self.sequenceNumber.setCurrentRow(x)
			break
		
	    self.LoadSequenceValues()
	else:
	    self.setSequenceSettingsEnabled(0)
	    
	    
		
    def setSequenceSettingsEnabled(self, v):
	self.sequenceNumber.setEnabled(v)
	self.sequenceStatus.setEnabled(v)
	self.sequenceDescription.setEnabled(v)
	
    def LoadSequenceValues(self):			
	self._blockUpdates = 1
	self.blockSignals(True)
	
	#make sure _currentSequence is current
	self.setCurrentSequence()
	
	if self._currentSequence is not None:
	    #self.setCurrentShot()
	    
	    #update editName
	    if self.sequenceNumber.currentItem() is not None:
		self.newSequenceNumber.setValue(int(self.sequenceNumber.currentItem().text())+10)
	    
	    #set Status
	    
	    self.sequenceStatus.setCurrentIndex(self._currentSequence._idstatuses-1)
	    
	    #set Description
	    if self._currentSequence is not None and self._currentSequence._description is not None:
		self.sequenceDescription.setText(self._currentSequence._description)
	
	self.LoadShotNames()
	    
	self._blockUpdates = 0
	self.blockSignals(False)
	
    def setCurrentSequence(self):
	self.currentSequence = None
	if len(self._currentProject._sequences) and self.sequenceNumber.currentItem() is not None:
	    self._currentProject._lastSelectedSequenceNumber = self.sequenceNumber.currentItem().text()
	    self._currentSequence = self._currentProject._sequences[int(self.sequenceNumber.currentItem().toolTip())]
    
    def setCurrentShot(self):
	self.currentShot = None
	if len(self._currentSequence._shots) and self.shotNumber.currentItem() is not None:
	    self._currentSequence._lastSelectedShotNumber = self.shotNumber.currentItem().text()
	    self._currentShot = self._currentSequence._shots[int(self.shotNumber.currentItem().toolTip())]
    
    def LoadShotNames(self):
	self.shotNumber.clear()
	self._currentShot = None
	self.shotDescription.setText('')
	self.shotStatus.setCurrentIndex(0)
	
	if self._currentSequence is not None:
	    if (self._currentSequence._shots):		    
		self.setShotSettingsEnabled(1)
		
		for x in range(0,len(self._currentSequence._shots)):
		    shot = self._currentSequence._shots[x]
		    shot.shotChanged.connect(self.shotChanged)
		    newWidgetItem = QtGui.QListWidgetItem()
		    newWidgetItem.setText(shot._number)
		    newWidgetItem.setToolTip(str(x))
		    #newWidgetItem.setFlags(newWidgetItem.flags() | QtCore.Qt.ItemIsEditable)
		    #newWidgetItem.setData(sequence._number)
		    self.shotNumber.addItem(newWidgetItem)
			
		
		#select last selected on switching sequences
		if self._currentSequence._lastSelectedShotNumber == '-1':
		    self.shotNumber.setCurrentRow(0)
		else:
		    for x in range(0,self.shotNumber.count()):
			if self.shotNumber.item(x).text() == self._currentSequence._lastSelectedShotNumber:
			    self.shotNumber.setCurrentRow(x)
			    break
		
		self.LoadShotValues()
		
	    else:
		self.setShotSettingsEnabled(0)
		myPixmap = QtGui.QPixmap(self._noImage)
		#myScaledPixmap = myPixmap.scaled(self.shotImage.width(),self.shotImage.height(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
		self.shotImage.setPixmap(myPixmap)
		
	else:
	    self.setShotSettingsEnabled(0)
	    myPixmap = QtGui.QPixmap(self._noImage)
	    #myScaledPixmap = myPixmap.scaled(self.shotImage.width(),self.shotImage.height(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
	    self.shotImage.setPixmap(myPixmap)
    
    def checkForShotImage(self):
	seq = self._currentSequence
	shot= self._currentShot
	d = str(self.projectPath.text()+"\\Animation\\seq_"+seq._number+"\\shot_"+seq._number+"_"+shot._number+"\\img\\")	   
	
	#if os.path.isdir(d):
	if len(self.projectPath.text()):
	    try:
	
		    #print len(glob.glob(os.path.join(d, '*.[Jj][Pp]*[Gg]')))
		    #if glob.glob(os.path.join(d, '*.[Jj][Pp]*[Gg]')):
		    
		    newImage = max(glob.iglob(os.path.join(d, '*.[Jj][Pp]*[Gg]')), key=os.path.getctime)
		    #print os.path.join(d, '*.[Jj][Pp]*[Gg]')
		    #newImage =''
		
		    #print len(newImage)
		    if len(newImage)>3:
			myPixmap = QtGui.QPixmap(newImage)		    
		    else:
			myPixmap = QtGui.QPixmap(self._noImage)		    
		    #else:
		    #    myPixmap = QtGui.QPixmap(self._noImage)
	    except:
		myPixmap = QtGui.QPixmap(self._noImage)
	else:
	    myPixmap = QtGui.QPixmap(self._noImage)
	    
	self.shotImage.setPixmap(myPixmap)
    
    def setShotSettingsEnabled(self, v):
	self.shotNumber.setEnabled(v)
	self.shotStatus.setEnabled(v)
	self.startFrame.setEnabled(v)
	self.endFrame.setEnabled(v)
	self.shotImage.setEnabled(v)
	self.shotDescription.setEnabled(v)
    
    def LoadShotValues(self):				
		    
	self._blockUpdates = 1
	self.blockSignals(True)
	
	#make sure _currentSequence is current
	self.newShotNumber.setValue(10)
	
	if self._currentSequence is not None:
	    self.setCurrentShot()
	    
	    if self._currentShot is not None:
		
		#update editName
		if self.shotNumber.currentItem() is not None:
		    self.newShotNumber.setValue(int(self.shotNumber.currentItem().text())+10)
		
		#update shotImage
		#myPixmap = QtGui.QPixmap("C:\\Users\\Dan\\Desktop\\5543ce94806f4.jpg")
		#myScaledPixmap = myPixmap.scaled(self.shotImage.width(),self.shotImage.height(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
		#self.shotImage.setPixmap(myPixmap)
		
		#if not remote
		#if not sharedDB.mySQLConnection._remote:
		self.checkForShotImage()		    
		
		#set Status
		self.shotStatus.setCurrentIndex(self._currentShot._idstatuses-1)
		
		#set frame range
		self.startFrame.setValue(self._currentShot._startframe)
		self.endFrame.setValue(self._currentShot._endframe)
		
		#set Description
		if self._currentShot is not None and self._currentShot._description is not None:
		    self.shotDescription.setText(self._currentShot._description)
	    
	self.refreshTasks()
	self._blockUpdates = 0
	self.blockSignals(False)
	    
    def AddShot(self):
	unique = 1
	
	#get sequence name
	newName = self.getShotName()
	
	#iterate through sequences
	for shot in self._currentSequence._shots:	    
	    #if sequence matches name
	    if newName == shot._number:
		unique = 0
		break
	    
	#if unique
	if unique:
	    #add sequence
	    self._currentSequence.AddShotToSequence(newName)
	    self.LoadShotNames()
	    self.selectShotByName(newName)
	    #self.newSequenceNumber.setValue(self.newSequenceNumber.value()+10)
	    
	else:
	    #warning message
	    message = QtGui.QMessageBox.question(self, 'Message',
	"Shot name already exists, choose a unique name (it is recommended to leave 10 between each shot in case shots need to be added in the middle)", QtGui.QMessageBox.Ok)
    
	#select sequence by name
    def selectShotByName(self, sName):
	for x in range(0,self.shotNumber.count()):
	    if self.shotNumber.item(x).text()==sName:
		self.shotNumber.setCurrentRow(x)
		break	
    
    def getShotName(self):
	sName = str(self.newShotNumber.value())
	while( len(sName)<4):
	    sName = "0"+sName
    
	return sName
    
    def SetShotValues(self):
	if not self._blockUpdates:
	    if self._currentShot is not None:
		#self._currentShot._description = self.shotDescription.toPlainText()
		self._currentShot._idstatuses = self.shotStatus.currentIndex()+1
		self._currentShot._startframe = self.startFrame.value()
		self._currentShot._endframe = self.endFrame.value()
		self._currentShot._updated = 1
	    
	    
    def SaveShotDescription(self):
	if not self._blockUpdates:
	    if self._currentShot is not None:
		if not (self.shotDescription.toPlainText() == self._currentShot._description):
			self._currentShot._description = self.shotDescription.toPlainText()
			self._currentShot._updated = 1
			
    def refreshTasks(self):
	self.taskTable.clear()
	'''for x in range(0, len(sharedDB.myTasks)):
	    task = sharedDB.myTasks[x]
	    if task._idshots == self._currentShot._idshots:
		newRow = QtGui.QTreeWidgetItem()
		self.taskTable.insertTopLevelItem(0,newRow)
		
		#add task names
		phaseCombobox = QtGui.QComboBox()
		self.taskTable.setItemWidget(newRow,0,phaseCombobox)
		for y in range(0,len(sharedDB.myPhases)):
		    phase = sharedDB.myPhases[y]
		    phaseCombobox.addItem(phase._name)
		    if phase._idphases == task._idphases:
			phaseCombobox.setCurrentIndex(y)
		
		#add user names
		userComboBox = QtGui.QComboBox()
		self.taskTable.setItemWidget(newRow,1,userComboBox)
		for y in range(0,len(sharedDB.myUsers)):
		    user = sharedDB.myUsers[y]
		    userComboBox.addItem(user._name)
		    if user._idusers == task._idusers:
			userComboBox.setCurrentIndex(y)
		
		#newWidgetItem.setText(str(task._idtasks))
		#newWidgetItem.setToolTip(str(x))
		#newWidgetItem.setFlags(newWidgetItem.flags() | QtCore.Qt.ItemIsEditable)
		#newWidgetItem.setData(sequence._number)
		#
		#self.taskTable.setItem(0,0,newWidgetItem)
		
		#Table
		#self.taskTable.insertRow(0)
		#combobox = QtGui.QComboBox()
		#self.taskTable.setCellWidget(0,0,combobox)
		'''