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

class CheckForImagePath(QtCore.QThread):

    def run(self):
	#search for image
	sentpath = sharedDB.myProjectViewWidget.shotImageDir
	
	try:
		newImage = max(glob.iglob(os.path.join(sentpath, '*.[Jj][Pp]*[Gg]')), key=os.path.getctime)
		#print os.path.join(d, '*.[Jj][Pp]*[Gg]')
		#print sentpath
		#print newImage
		if len(newImage)>3:
			print "Loading Shot Image: "+newImage
			sharedDB.myProjectViewWidget.shotImagePath = newImage
			sharedDB.myProjectViewWidget.shotImageFound.emit()
		
	except:
	    print "No Image file found for selected shot"
	    

class ProjectViewWidget(QWidget):
    shotImageFound = QtCore.pyqtSignal()
    refreshProjectValuesSignal = QtCore.pyqtSignal()
    
    def __init__( self, parent = None ):
    
	super(ProjectViewWidget, self).__init__( parent )
	
	self._currentProject = None
	self._currentSequence = None
	self._currentShot = None
	
	self._noImage = projexui.resources.find('img/DP/noImage.png')
	
	self.cfip = CheckForImagePath()
	self.shotImageFound.connect(self.setImagePath)
	self.shotImagePath = projexui.resources.find('img/DP/noImage.png')
	self.shotImageDir = ''
	
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
	
	sharedDB.mySQLConnection.firstLoadComplete.connect(self.propogateUI)
	
	self.setEnabled(0)
    
    def propogateUI(self, ):
	self.setPrivelages()

	#connects signals
	sharedDB.mySQLConnection.newProjectSignal.connect(self.AddProjectNameToList)
	sharedDB.mySQLConnection.newSequenceSignal.connect(self.AddSequenceToProgressList)
	sharedDB.mySQLConnection.newShotSignal.connect(self.AddShotToProgressList)
	self.refreshProjectValuesSignal.connect(self.LoadProjectValues)
	
	self.propogateStatuses()		
	
	#connect project settings
	self.projectName.currentIndexChanged[QtCore.QString].connect(self.LoadProjectValues)
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
	#self.sequenceNumber.currentRowChanged.connect(self.LoadSequenceValues)
	self.saveSequenceDescription.clicked.connect(self.SaveSequenceDescription)
	#self.sequenceStatus.currentIndexChanged[QtCore.QString].connect(self.SetSequenceValues)
	self.addSequence.clicked.connect(self.AddSequence)
	self.updateFolderStructure.clicked.connect(self.CreateFolderStructure)
	
	#connect shot settings
	#self.shotNumber.currentRowChanged.connect(self.LoadShotValues)
	self.saveShotDescription.clicked.connect(self.SaveShotDescription)
	#self.shotStatus.currentIndexChanged[QtCore.QString].connect(self.SetShotValues)
	self.startFrame.valueChanged.connect(self.SetShotValues)
	self.endFrame.valueChanged.connect(self.SetShotValues)
	self.addShot.clicked.connect(self.AddShot)
	self.saveShotNotes.clicked.connect(self.SaveShotNotes)
	
	self.propogateProjectNames()
	
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
		
    def AddProjectNameToList(self,projectid):
	
	projectMatch = None
	#find project with id
	for proj in sharedDB.myProjects:
		if str(proj._idprojects) == (projectid):
			projectMatch = proj
			break
		
	if projectMatch is not None and not projectMatch._hidden:
		unique = 1
		#iterate through projectname bar
		for x in range(0,self.projectName.count()):
		    
		    if self.projectName.itemData(x, Qt.ToolTipRole).toString() == str(projectid):
			unique = 0
			break
		    
				    
		if unique:		
			
			self.projectName.addItem(projectMatch._name,QVariant(projectMatch))
			#print "setting project "+str(projectMatch._name)+"'s tooltip to "+str(projectMatch._idprojects)
			self.projectName.setItemData(self.projectName.count()-1,projectMatch._idprojects, Qt.ToolTipRole)
			projectMatch.projectChanged.connect(self.projectChanged)
		
		if self.projectName.count() == 1:
			self.refreshProjectValuesSignal.emit()

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
	
	if sharedDB.myProjects:
	    
	    for project in sharedDB.myProjects:	
		#print self.projectName.itemData(self.projectName.currentIndex(), Qt.ToolTipRole).toString()
		if str(project._idprojects) == self.projectName.itemData(self.projectName.currentIndex(), Qt.ToolTipRole).toString():
			self._currentProject = project
	    
	    if self._currentProject is not None:
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
		self.LoadSequenceNames()
		
    
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
	    seq = self._currentProject.AddSequenceToProject(newName)
	    seq.sequenceAdded.connect(self.AddSequenceToProgressList)
	    #self.LoadProgressListValues()
	    #self.LoadSequenceNames()
	    #self.selectSequenceByName(newName)
	    #self.LoadShotNames()
	    
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
	    #print str(len(self._currentProject._sequences)) + " Sequences found in project"
	    self.setSequenceSettingsEnabled(1)
	    for x in range(0,len(self._currentProject._sequences)):
		sequence = self._currentProject._sequences[x]
	
		sequence.sequenceChanged.connect(self.sequenceChanged)
		newWidgetItem = QtGui.QListWidgetItem()
		newWidgetItem.setText(sequence._number)
		newWidgetItem.setToolTip(str(x))
		newWidgetItem.setFlags(newWidgetItem.flags() ^ Qt.ItemIsSelectable)
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
	    self.LoadShotNames()
	    
	    
    def LoadProgressListValues(self):
	self.progressList.clear()
	#self.progressList.header().sortIndicatorOrder()
	self.progressList.sortByColumn(0, QtCore.Qt.AscendingOrder);
	self.progressList.setSortingEnabled(True);
	self._currentSequence = None
	
	if (self._currentProject._sequences):
	    #self.setProjectListEnabled(1)
	    for x in range(0,len(self._currentProject._sequences)):
		sequence = self._currentProject._sequences[x]
		    
		#Add Sequences to list
		self.AddSequenceToProgressList(sequence = sequence)
    
    def GetSequenceByID(self,seqid):
	for seq in self._currentProject._sequences:
	    if str(seq._idsequences) == str(seqid):
		return seq    
    
    def AddSequenceToProgressList(self, seqid = None, sequence = None):
	if sequence is None:
	    print "getting sequence by id"
	    sequence = self.GetSequenceByID(seqid)
	
	if str(sequence._idprojects) == str(self._currentProject._idprojects):
	
	    #Add Sequences to list
	    sequenceTreeItem = sequenceTreeWidgetItem.SequenceTreeWidgetItem(sequence, self.progressList, self._currentProject,self)	    		
	    self.progressList.addTopLevelItem(sequenceTreeItem)
	    sequenceTreeItem.setExpanded(True)	    
    	
    def GetShotByID(self,shotid):
	for seq in self._currentProject._sequences:
	    for shot in seq._shots:
		if str(shot._idshots) == str(shotid):
		    return shot	
	
    def AddShotToProgressList(self, shotid = None, shot = None):
	if shot is None:
	    print "getting shot by id"
	    shot = self.GetShotByID(shotid)

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
	self.shotNotes.setText('')
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
	
	myPixmap = QtGui.QPixmap(self._noImage)
	self.shotImage.setPixmap(myPixmap)
	#if os.path.isdir(d):
	if shot is not None:	
		if len(self.projectPath.text()):
		    self.shotImageDir = d
		    self.cfip.start()
		    '''try:
			newImage = max(glob.iglob(os.path.join(d, '*.[Jj][Pp]*[Gg]')), key=os.path.getctime)
			if len(newImage)>3:
			    myPixmap = QtGui.QPixmap(newImage)    
		    except:
			myPixmap = QtGui.QPixmap(self._noImage)'''
	
	
    
    def setImagePath(self):
	#print len(newImage)
	#if len(newImage)>3:
	myPixmap = QtGui.QPixmap(self.shotImagePath)    
	#else:
	    #myPixmap = QtGui.QPixmap(self._noImage)
	    
	self.shotImage.setPixmap(myPixmap)    
    
    def setShotSettingsEnabled(self, v):
	self.shotNumber.setEnabled(v)
	self.shotStatus.setEnabled(v)
	self.startFrame.setEnabled(v)
	self.endFrame.setEnabled(v)
	self.shotImage.setEnabled(v)
	self.shotDescription.setEnabled(v)
	self.shotNotes.setEnabled(v)
    
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
		
		
		if self._currentShot._shotnotes is None or self._currentShot._shotnotes == '' or self._currentShot._shotnotes == 'None':
			#print "Setting shot Note text to default"
			self.shotNotes.setText('Anim-\n\nFX-\n\nSound-\n\nLighting-\n\nComp-')
		else:
			#print self._currentShot._shotnotes
			#print "Loading shot note text"
			self.shotNotes.setText(self._currentShot._shotnotes)    
	    
	self._blockUpdates = 0
	self.blockSignals(False)
	
    def LoadShotValuesFromSent(self,itemwidget, column):				
		    
	self._blockUpdates = 1
	self.blockSignals(True)
	
	#make sure _currentSequence is current
	
	
	#self.setCurrentShot()
	
	for shot in sharedDB.myShots:
		if str(shot._idshots) == str(itemwidget.text(0)):
			self._currentShot = shot
	
	if self._currentShot is not None:
	    
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
	    
	    
	    if self._currentShot._shotnotes is None or self._currentShot._shotnotes == '' or self._currentShot._shotnotes == 'None':
		    #print "Setting shot Note text to default"
		    self.shotNotes.setText('Anim-\n\nFX-\n\nSound-\n\nLighting-\n\nComp-')
	    else:
		    #print self._currentShot._shotnotes
		    #print "Loading shot note text"
		    self.shotNotes.setText(self._currentShot._shotnotes)
	
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
	    shot = self._currentSequence.AddShotToSequence(newName)
	    shot.shotAdded.connect(self.AddShotToProgressList)
	    #self.LoadShotNames()	    
	    #self.LoadProgressListValues()
	    #self.selectShotByName(newName)
	    
	    
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

    def SaveShotNotes(self):
	#if not self._blockUpdates:
	if self._currentShot is not None:
	    if not (self.shotNotes.toPlainText() == self._currentShot._shotnotes):
		    self._currentShot._shotnotes = self.shotNotes.toPlainText()
		    self._currentShot._updated = 1