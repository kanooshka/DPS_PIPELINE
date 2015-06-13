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
from PyQt4.QtCore   import QDate,QTime,QVariant
from DPSPipeline.database import projects

class ProjectViewWidget(QWidget):
   
	def __init__( self, parent = None ):
        
		super(ProjectViewWidget, self).__init__( parent )
		
		self._currentProject = ''
		
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
		
		self.projectName.currentIndexChanged[QtCore.QString].connect(self.refreshProjectValues)
		self.projectName.editTextChanged[QtCore.QString].connect(self.updateProjectName)
		self.projectStatus.currentIndexChanged[QtCore.QString].connect(self.updateStatus)
		self.fps.valueChanged.connect(self.updateFPS)
		self.dueDate.dateChanged.connect(self.updateDueDate)
		self.renderWidth.valueChanged.connect(self.updateRenderWidth)
		self.renderHeight.valueChanged.connect(self.updateRenderHeight)
		self.projectDescription.textChanged.connect(self.updateProjectDescription)
		self.projectPath.textChanged.connect(self.updateProjectPath)		
		
		#self.open()

	def cancel(self):
		self.close()

	def propogateProjectNames(self):
		for project in sharedDB.projectList:
			#item = QtGui.QListWidgetItem(project._name)
			self.projectName.addItem(project._name, QVariant(project))
		
		#print sharedDB.projectList[self.projectName.currentIndex()]._name
		self.refreshProjectValues()
		
	def propogateStatuses(self):
		for status in sharedDB.myStatuses:
			#item = QtGui.QListWidgetItem(project._name)
			self.projectStatus.addItem(status._name, QVariant(status))
		
		#print sharedDB.projectList[self.projectName.currentIndex()]._name

	def updateProjectName(self):
		self._currentProject._name = self.projectName.currentText()
		self._currentProject._updated = 1
	
	def updateStatus(self):
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
	
	#def currentIndexChanged(self):
		