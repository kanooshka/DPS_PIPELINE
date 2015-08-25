import sharedDB

from PyQt4 import QtGui,QtCore

from DPSPipeline.widgets.attributeeditorwidget import AEshot
from DPSPipeline.widgets.attributeeditorwidget import AEproject

class AttributeEditorWidget(QtGui.QStackedWidget):
    
    def __init__( self, parent = None ):
    
	super(AttributeEditorWidget, self).__init__( parent )

	sharedDB.myAttributeEditorWidget = self

	sharedDB.sel.selectionChangedSignal.connect(self.LoadSelection)
	
	#add shot widget
	self.shotWidget = AEshot.AEShot()
	self.addWidget(self.shotWidget)
	self.shotWidget.setHidden(1)
	
	self.projectWidget = AEproject.AEProject()
	self.addWidget(self.projectWidget)
	self.projectWidget.setHidden(1)
    
    def LoadSelection(self):
	
	item = sharedDB.sel.items[len(sharedDB.sel.items)-1]
	if item._type == 'shot':
	    self.setCurrentIndex(0)
	    self.shotWidget.LoadShot(item)
	elif item._type == 'project':
	    self.setCurrentIndex(1)
	    self.projectWidget.LoadProject(item)
	else:
	    self.setCurrentIndex(0)
	    self.shotWidget.setHidden(1)
	    
	    