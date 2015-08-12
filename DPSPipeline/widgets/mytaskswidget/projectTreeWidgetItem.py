import sharedDB
import datetime
from PyQt4 import QtCore,QtGui
#from DPSPipeline.widgets.projectviewwidget import shotTreeWidget
#from DPSPipeline.widgets.projectviewwidget import seqDescription

class ProjectTreeWidgetItem(QtGui.QTreeWidgetItem):

    def __init__(self,phase,parent):
        super(QtGui.QTreeWidgetItem, self).__init__()
        
        self._phaseAssignment = phase
        self._parent = parent
        self._project = phase.project
        #self._projectviewwidget = _projectviewwidget
        
        #self._taskTreeWidget = mytaskTreeWidget.MyTaskTreeWidget(self._project,self._sequence,self)        
        
        self.setValuesFromPhaseAssignment()
        self.setTextAlignment(0,QtCore.Qt.AlignCenter)
        self.setBackground(0,QtGui.QColor('black'))
        self.setForeground(0,QtGui.QColor('white'))
	
	self._phaseAssignment.phaseAssignmentChanged.connect(self.UpdateItem)
	
    def UpdateItem(self):
	self.setValuesFromPhaseAssignment()
	self._parent.sortItems(1,QtCore.Qt.AscendingOrder)
    
    def setValuesFromPhaseAssignment(self):
	self.setText(0,(self._project._name+"             ------>            "+self._phaseAssignment._name)+" DUE: "+self._phaseAssignment._enddate.strftime("%m-%d-%Y"))
        self.setText(1,self._phaseAssignment._enddate.strftime("%Y-%m-%d %H:%M:%S"))
	
	#for all tasks
	for task in self._phaseAssignment._tasks:
	    #if phaseassignment is same and done is 0
	    childItem = QtGui.QTreeWidgetItem(task._idtasks)
	    self.addChild(childItem)
	    #add to task list
	    #locked if previous task isn't ready
	    
	
        #self.addChild(self.descriptionTreeItem)
        #self._parent.setItemWidget(self.descriptionTreeItem,0,self.sequenceDescription)
		    
        #self.addChild(self._shotTreeWidget.shotTreeItem)
        
        #self._progressList.setItemWidget(self._shotTreeWidget.shotTreeItem,0,self._shotTreeWidget)
        