import weakref
import projexui
import sharedDB
import math
import sys

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
		self.propogateProjectNames()
		self.propogateStatuses()
		
		#connect project settings
		self.projectName.currentIndexChanged[QtCore.QString].connect(self.refreshProjectValues)
		self.projectName.currentIndexChanged[QtCore.QString].connect(self.refreshSequenceNames)
		self.projectName.editTextChanged[QtCore.QString].connect(self.updateProjectName)
		self.projectStatus.currentIndexChanged[QtCore.QString].connect(self.updateProjectStatus)
		self.fps.valueChanged.connect(self.updateFPS)
		self.dueDate.dateChanged.connect(self.updateDueDate)
		self.renderWidth.valueChanged.connect(self.updateRenderWidth)
		self.renderHeight.valueChanged.connect(self.updateRenderHeight)
		self.projectDescription.textChanged.connect(self.updateProjectDescription)
		self.projectPath.textChanged.connect(self.updateProjectPath)		
		
		#connect sequence settings		
		self.sequenceNumber.currentRowChanged.connect(self.refreshSequenceValues)
		self.sequenceDescription.textChanged.connect(self.updateSequenceDescription)
		self.sequenceStatus.currentIndexChanged[QtCore.QString].connect(self.updateSequenceStatus)
		
		
	def cancel(self):
		self.close()

	def propogateProjectNames(self):
		for project in sharedDB.projectList:
			#item = QtGui.QListWidgetItem(project._name)
			self.projectName.addItem(project._name, QVariant(project))
		
		self.refreshProjectValues()
		self.refreshSequenceNames()		
		self.refreshSequenceValues()
		
	def propogateStatuses(self):
		for status in sharedDB.myStatuses:
			#item = QtGui.QListWidgetItem(project._name)
			self.projectStatus.addItem(status._name, QVariant(status))
			self.sequenceStatus.addItem(status._name, QVariant(status))
		#print sharedDB.projectList[self.projectName.currentIndex()]._name

	def updateProjectName(self):
		self._currentProject._name = self.projectName.currentText()
		self._currentProject._updated = 1
	
	def updateProjectStatus(self):
		self._currentProject._idstatus = self.projectStatus.currentIndex()+1
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
		
		#set FPS
		self.fps.setValue(self._currentProject._fps)
		#set Path
		self.projectPath.setText(self._currentProject._folderLocation)
		#set Status
		self.projectStatus.setCurrentIndex(self._currentProject._idstatus-1)
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
	
	def updateSequenceDescription(self):
		if self._currentSequence is not None:
			self._currentSequence._description = self.sequenceDescription.toPlainText()
			self._currentSequence._updated = 1
	
	def updateSequenceStatus(self):
		self._currentSequence._idstatus = self.sequenceStatus.currentIndex()+1
		self._currentSequence._updated = 1
		
	def refreshSequenceNames(self):
		self.sequenceNumber.clear()
		self._currentSequence = None
		self.sequenceDescription.setText('')
		
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
				
	def refreshSequenceValues(self):				
			
		#make sure _currentSequence is current
		self.setCurrentSequence()
		
		#set Status
		self.sequenceStatus.setCurrentIndex(self._currentSequence._idstatus)
		
		#set Description
		if self._currentSequence is not None and self._currentSequence._description is not None:
				self.sequenceDescription.setText(self._currentSequence._description)				
		
	def setCurrentSequence(self):
		if len(self._currentProject._sequences) and self.sequenceNumber.currentItem() is not None:
			self._currentProject._lastSelectedSequenceNumber = self.sequenceNumber.currentItem().text()
			self._currentSequence = self._currentProject._sequences[int(self.sequenceNumber.currentItem().toolTip())]
	
	#def currentIndexChanged(self):
		