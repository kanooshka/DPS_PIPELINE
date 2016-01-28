import sys
from PyQt4 import QtGui,QtCore
import projexui
import sharedDB
from DPSPipeline.widgets import textEditAutosave

class SeqDescription(QtGui.QWidget):

    def __init__( self, parent = None, _sequence = '',_sequenceTreeItem = '', _project = '' ):
    
	super(SeqDescription, self).__init__( parent )
	
	# load the user interface# load the user interface
	if getattr(sys, 'frozen', None):
	    projexui.loadUi(sys._MEIPASS, self, uifile = (sys._MEIPASS+"/ui/seqDescription.ui")) 
	else:
	    projexui.loadUi(__file__, self)

	self._sequence = _sequence
	self._sequenceTreeItem = _sequenceTreeItem
	self._project = _project
	
	self.sequenceDescription = textEditAutosave.TextEditAutoSave(source = self._sequence, sourceAttr = "_description")
	self.seqDescriptionLayout.addWidget(self.sequenceDescription)
	self.sequenceDescription.save.connect(self.SaveSequenceDescription)
	
	self.setDescription()
	
	self.descriptionBox.setTitle("Sequence "+str(self._sequence._number)+" Description")
	
	self.addShot.clicked.connect(self.AddShot)
	self._sequence.sequenceChanged.connect(self.setDescription)
	#self.saveSequenceDescription.clicked.connect(self.SaveSequenceDescription)
	
    def SaveSequenceDescription(self):
	    if not (self.sequenceDescription.toPlainText() == self._sequence._description):
		    self._sequence._description = self.sequenceDescription.toPlainText()
		    self._sequence._updated = 1
		    
    def setDescription(self):
	self.sequenceDescription.blockSignals = 1
	
	if self._sequence._description is not None:	    
	    self.sequenceDescription.setText(self._sequence._description)
	
	self.sequenceDescription.blockSignals = 0
    
    def getShotName(self):
	sName = str(self.newShotNumber.value())
	while( len(sName)<4):
	    sName = "0"+sName
    
	return sName
    
    def UpdateShotNumberValue(self):
	#get selected shottreewidgetitem
	if self._sequenceTreeItem._shotTreeWidget.currentItem() is not None:
	    self.newShotNumber.setValue(int(self._sequenceTreeItem._shotTreeWidget.currentItem().shot._number)+10)
    
    def AddShot(self):
	unique = 1
	
	#get sequence name
	newName = self.getShotName()
	
	#iterate through sequences
	for shot in self._sequence._shots.values():	    
	    #if sequence matches name
	    if newName == shot._number:
		unique = 0
		break
	    
	#if unique
	if unique:
	    #add sequence
	    shot = self._sequence.AddShotToSequence(newName)
	    self.CreateTasks(str(shot.id()))
	    #shot.shotAdded.connect(self.CreateTasks)
	    
	    self.newShotNumber.setValue(self.newShotNumber.value()+10)
	    #self.LoadShotNames()	    
	    #self.LoadProgressListValues()	    
	else:
	    #warning message
	    message = QtGui.QMessageBox.question(self, 'Message',
	"Shot name already exists, choose a unique name (it is recommended to leave 10 between each shot in case shots need to be added in the middle)", QtGui.QMessageBox.Ok)

    def selectShotByName(self, sName):
	
	stree = self._sequenceTreeItem._shotTreeWidget
	#item = stree.findItems(sName,1)
	for x in range(0,stree.topLevelItemCount()):
	    print stree.topLevelItem(x).text(1)
	    print sName
	    if int(stree.topLevelItem(x).text(1))==int(sName):
		item = stree.topLevelItem(x)
		stree.setCurrentItem(item)
		break

    '''
    def GetShotByID(self,shotid):
	for shot in self._sequence._shots:
	    if str(shot._idshots) == str(shotid):
		return shot	    
    '''    
    def CreateTasks(self, shotid = None, shot = None):
	if shot is None:
	    #print "getting shot by id"
	    if str(shotid) in sharedDB.myShots:
		shot = sharedDB.myShots[str(shotid)]

	if shot is not None:
    
	    		
	    
	    if not sharedDB.autoCreateShotTasks:
		self.selectShotByName(shot._number)
		for phase in self._project._phases.values():	    
		    if phase._taskPerShot:
			task = sharedDB.tasks.Tasks(_idphaseassignments = phase._idphaseassignments, _idprojects = self._project._idprojects, _idshots = shot._idshots, _idphases = phase._idphases, _new = 1)
			task.taskAdded.connect(self._sequenceTreeItem._shotTreeWidget.AttachTaskToButton)
			task.Save()
			
			shot._tasks[str(task.id())] = task
	    
	    #add shot to that widget
	    self._sequenceTreeItem._shotTreeWidget.AddShot(shot)