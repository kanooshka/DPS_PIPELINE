import weakref
import projexui
import sharedDB
import math
import sys
import os
import glob

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
		
		# load the user interface# load the user interface
		if getattr(sys, 'frozen', None):
		    projexui.loadUi(sys._MEIPASS, self, uifile = (sys._MEIPASS+"/ui/projectviewwidget.ui"))		    
		else:
		    projexui.loadUi(__file__, self)
		#projexui.loadUi(__file__, self)
		
		self._noImage = projexui.resources.find('img/DP/noImage.png')
		myPixmap = QtGui.QPixmap(projexui.resources.find('img/DP/folder.png'))
		self.projectPathButton.setIcon(QtGui.QIcon(QtGui.QPixmap(myPixmap)))
		
		# define custom properties
		
		self._backend               = None
		
		#connects buttons
		#self.createButton.clicked.connect(self.CreateProject)
		#self.cancelButton.clicked.connect(self.cancel)
		self.propogateStatuses()
		self.propogateProjectNames()		
		
		#connect project settings
		self.projectName.currentIndexChanged[QtCore.QString].connect(self.refreshProjectValues)
		self.projectName.currentIndexChanged[QtCore.QString].connect(self.refreshSequenceNames)
		self.projectName.currentIndexChanged[QtCore.QString].connect(self.refreshShotNames)
		self.projectName.editTextChanged[QtCore.QString].connect(self.updateProjectName)
		self.projectStatus.currentIndexChanged[QtCore.QString].connect(self.updateProjectStatus)
		self.fps.valueChanged.connect(self.updateFPS)
		self.dueDate.dateChanged.connect(self.updateDueDate)
		self.renderWidth.valueChanged.connect(self.updateRenderWidth)
		self.renderHeight.valueChanged.connect(self.updateRenderHeight)
		self.projectDescription.textChanged.connect(self.updateProjectDescription)
		self.projectPath.textChanged.connect(self.updateProjectPath)		
		self.projectPathButton.clicked.connect(self.changeProjectPath)
		
		#connect sequence settings		
		self.sequenceNumber.currentRowChanged.connect(self.refreshSequenceValues)
		self.sequenceDescription.textChanged.connect(self.updateSequenceDescription)
		self.sequenceStatus.currentIndexChanged[QtCore.QString].connect(self.updateSequenceStatus)
		self.addSequence.clicked.connect(self.AddSequence)
		self.updateFolderStructure.clicked.connect(self.CreateFolderStructure)
		
		#connect shot settings
		self.shotNumber.currentRowChanged.connect(self.refreshShotValues)
		self.shotDescription.textChanged.connect(self.updateShotDescription)
		self.shotStatus.currentIndexChanged[QtCore.QString].connect(self.updateShotStatus)
		self.addShot.clicked.connect(self.AddShot)
		self.startFrame.valueChanged.connect(self.updateStartFrame)
		self.endFrame.valueChanged.connect(self.updateEndFrame)
		
	def cancel(self):
		self.close()

	def CreateFolderStructure(self):
	    paths = []
	    if os.path.isdir(str(self.projectPath.text())):
		for seq in self._currentProject._sequences:
		    for shot in seq._shots:
			paths.append(str(self.projectPath.text()+"\\Sequences\\seq_"+seq._number+"\\shot_"+seq._number+"_"+shot._number+"\\maya\\anim\\FaceRenders\\"))
			paths.append(str(self.projectPath.text()+"\\Sequences\\seq_"+seq._number+"\\shot_"+seq._number+"_"+shot._number+"\\maya\\lighting\\"))
			paths.append(str(self.projectPath.text()+"\\Sequences\\seq_"+seq._number+"\\shot_"+seq._number+"_"+shot._number+"\\maya\\caches\\capeCache\\"))
			paths.append(str(self.projectPath.text()+"\\Sequences\\seq_"+seq._number+"\\shot_"+seq._number+"_"+shot._number+"\\maya\\shotExtras\\"))
			paths.append(str(self.projectPath.text()+"\\Sequences\\seq_"+seq._number+"\\shot_"+seq._number+"_"+shot._number+"\\maya\\fx\\"))
			paths.append(str(self.projectPath.text()+"\\Sequences\\seq_"+seq._number+"\\shot_"+seq._number+"_"+shot._number+"\\currentFootage\\"))
			paths.append(str(self.projectPath.text()+"\\Sequences\\seq_"+seq._number+"\\shot_"+seq._number+"_"+shot._number+"\\img\\"))
    
		for path in paths:
		    self.ensure_dir(path)
	    else:
		message = QtGui.QMessageBox.question(self, 'Message',
            "Project Directory is not valid. Please select a directory.", QtGui.QMessageBox.Ok)
	
	    
	def ensure_dir(self,f):  
	    #print f.replace("\\", "\\\\")
	    d = os.path.dirname(f)
	    #print d
	    if not os.path.exists(d):
		os.makedirs(d)
	

	def propogateProjectNames(self):
		for project in sharedDB.projectList:
			#item = QtGui.QListWidgetItem(project._name)
			self.projectName.addItem(project._name, QVariant(project))
		
		self.refreshProjectValues()
		self.refreshSequenceNames()	
		self.refreshSequenceValues()
		
		self.refreshShotNames()
		self.refreshShotValues()
		
	def propogateStatuses(self):
		for status in sharedDB.myStatuses:
			#item = QtGui.QListWidgetItem(project._name)
			self.projectStatus.addItem(status._name, QVariant(status))
			self.sequenceStatus.addItem(status._name, QVariant(status))
			self.shotStatus.addItem(status._name, QVariant(status))
		#print sharedDB.projectList[self.projectName.currentIndex()]._name
	
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
		
		

	def updateProjectName(self):
		self._currentProject._name = self.projectName.currentText()
		self._currentProject._updated = 1
	
	def updateProjectStatus(self):
		self._currentProject._idstatuses = self.projectStatus.currentIndex()+1
		self._currentProject._updated = 1
		
	def updateFPS(self):
		self._currentProject._fps = self.fps.value()
		self._currentProject._updated = 1
		
	def updateDueDate(self):
		self._currentProject._due_date = self.dueDate.date().toPyDate()
		self._currentProject._updated = 1
		
	def updateRenderWidth(self):
		self._currentProject._renderWidth = self.renderWidth.value()
		self._currentProject._updated = 1
		
	def updateRenderHeight(self):
		self._currentProject._renderHeight = self.renderHeight.value()
		self._currentProject._updated = 1
		
	def updateProjectDescription(self):
		self._currentProject._description = self.projectDescription.toPlainText()
		self._currentProject._updated = 1
		
	def updateProjectPath(self):
		self._currentProject._folderLocation = self.projectPath.text()
		self._currentProject._updated = 1

	def refreshProjectValues(self):
		self._currentProject = sharedDB.projectList[self.projectName.currentIndex()]		
		
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
		self.refreshSequenceNames()
		self.selectSequenceByName(newName)
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
	
	def updateSequenceDescription(self):
		if self._currentSequence is not None:
			self._currentSequence._description = self.sequenceDescription.toPlainText()
			self._currentSequence._updated = 1
	
	def updateSequenceStatus(self):
		if self._currentSequence is not None:
		    self._currentSequence._idstatuses = self.sequenceStatus.currentIndex()+1
		    self._currentSequence._updated = 1
		
	def refreshSequenceNames(self):
		self.sequenceNumber.clear()
		self._currentSequence = None
		self.sequenceDescription.setText('')
		self.sequenceStatus.setCurrentIndex(0)
		
		if (self._currentProject._sequences):
		    self.setSequenceSettingsEnabled(1)
		    for x in range(0,len(self._currentProject._sequences)):
			    sequence = self._currentProject._sequences[x]
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
		else:
		    self.setSequenceSettingsEnabled(0)
		    
	def setSequenceSettingsEnabled(self, v):
	    self.sequenceNumber.setEnabled(v)
	    self.sequenceStatus.setEnabled(v)
	    self.sequenceDescription.setEnabled(v)
	    
	def refreshSequenceValues(self):			
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
	    
	    self.refreshShotNames()
		
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
	
	def refreshShotNames(self):
		self.shotNumber.clear()
		self._currentShot = None
		self.shotDescription.setText('')
		self.shotStatus.setCurrentIndex(0)
		
		if self._currentSequence is not None:
		    if (self._currentSequence._shots):		    
			self.setShotSettingsEnabled(1)
			
			for x in range(0,len(self._currentSequence._shots)):
				shot = self._currentSequence._shots[x]
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
	    d = str(self.projectPath.text()+"\\Sequences\\seq_"+seq._number+"\\shot_"+seq._number+"_"+shot._number+"\\img\\")	   
	    
	    if os.path.exists(d):
		newImage = max(glob.iglob(os.path.join(d, '*.[Jj][Pp]*[Gg]')), key=os.path.getctime)

		if len(newImage):
		    myPixmap = QtGui.QPixmap(newImage)		    
		else:
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
	
	def refreshShotValues(self):				
			
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
		    self.checkForShotImage()
		    
		    
		    #set Status
		    self.shotStatus.setCurrentIndex(self._currentShot._idstatuses-1)
		    
		    #set frame range
		    self.startFrame.setValue(self._currentShot._startframe)
		    self.endFrame.setValue(self._currentShot._endframe)
		    
		    #set Description
		    if self._currentShot is not None and self._currentShot._description is not None:
		    	self.shotDescription.setText(self._currentShot._description)
		
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
		self.refreshShotNames()
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
	
	def updateShotDescription(self):
		if self._currentShot is not None:
			self._currentShot._description = self.shotDescription.toPlainText()
			self._currentShot._updated = 1
	
	def updateShotStatus(self):
		if self._currentShot is not None:
		    self._currentShot._idstatuses = self.shotStatus.currentIndex()+1
		    self._currentShot._updated = 1
	
	def updateStartFrame(self):
		self._currentShot._startframe = self.startFrame.value()
		self._currentShot._updated = 1
	
	def updateEndFrame(self):
		self._currentShot._endframe = self.endFrame.value()
		self._currentShot._updated = 1	
	