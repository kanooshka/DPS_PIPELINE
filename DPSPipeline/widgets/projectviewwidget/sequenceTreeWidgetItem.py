import sharedDB

from PyQt4 import QtCore,QtGui
from DPSPipeline.widgets.projectviewwidget import shotTreeWidget
from DPSPipeline.widgets.projectviewwidget import seqDescription

class SequenceTreeWidgetItem(QtGui.QTreeWidgetItem):

    def __init__(self,sequence,progressList,_project,_projectviewwidget):
        super(QtGui.QTreeWidgetItem, self).__init__()
        
        self._sequence = sequence
        self._progressList = progressList
        self._project = _project
        self._projectviewwidget = _projectviewwidget
        self.sequenceDescription = seqDescription.SeqDescription(_sequence = self._sequence,_sequenceTreeItem = self, _project = self._project)
        self._shotTreeWidget = shotTreeWidget.ShotTreeWidget(self._project,self._sequence,self)
        
        
        self.descriptionTreeItem = QtGui.QTreeWidgetItem()

        self.setText(0,("Seq_"+self._sequence._number))
        self.setTextAlignment(0,QtCore.Qt.AlignCenter)
        self.setBackground(0,QtGui.QColor('grey'))
        self.setForeground(0,QtGui.QColor('white'))
        
        #add description to widget
        #self.sequenceDescription.setFixedHeight(40)
        self.addChild(self.descriptionTreeItem)
        self._progressList.setItemWidget(self.descriptionTreeItem,0,self.sequenceDescription)
		    
        self.addChild(self._shotTreeWidget.shotTreeItem)
        
        self._progressList.setItemWidget(self._shotTreeWidget.shotTreeItem,0,self._shotTreeWidget)
        