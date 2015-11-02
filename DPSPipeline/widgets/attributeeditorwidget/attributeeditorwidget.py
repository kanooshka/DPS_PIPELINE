import sharedDB

from PyQt4 import QtGui,QtCore

from DPSPipeline.widgets.attributeeditorwidget import AEshot
from DPSPipeline.widgets.attributeeditorwidget import AEproject
from DPSPipeline.widgets.attributeeditorwidget import AEphaseassignment

class AttributeEditorWidget(QtGui.QStackedWidget):
    
    def __init__( self, parent = None ):
    
	super(AttributeEditorWidget, self).__init__( parent )

	sharedDB.myAttributeEditorWidget = self

	sharedDB.sel.selectionChangedSignal.connect(self.LoadSelection)
	
	self.widgets = []
	
	#add shot widget
	self.shotWidget = AEshot.AEShot()
	self.widgets.append(self.shotWidget)
	self.addWidget(self.shotWidget)
	self.shotWidget.setHidden(1)
	
	self.projectWidget = AEproject.AEProject()
	self.widgets.append(self.projectWidget)
	self.addWidget(self.projectWidget)
	self.projectWidget.setHidden(1)
	
	self.phaseAssignmentWidget = AEphaseassignment.AEPhaseAssignment()
	self.widgets.append(self.phaseAssignmentWidget)
	self.addWidget(self.phaseAssignmentWidget)
	self.phaseAssignmentWidget.setHidden(1)
    
    def LoadSelection(self):
	
	item = sharedDB.sel.items[len(sharedDB.sel.items)-1]
	
	self.HideAll()
	if item._type == 'shot':
	    self.setCurrentIndex(0)
	    self.shotWidget.LoadShot(item)
	elif item._type == 'project':
	    self.setCurrentIndex(1)
	    self.projectWidget.LoadProject(item)
	elif item._type == 'phaseassignment':
	    self.setCurrentIndex(2)
	    self.phaseAssignmentWidget.LoadPhaseAssignment(item)
	    item.phaseAssignmentChanged.connect(self.phaseAssignmentWidget.LoadPhaseAssignment)
	else:
	    self.setCurrentIndex(0)
	    
    def HideAll(self):
	for widget in self.widgets:
	    widget.setHidden(1)