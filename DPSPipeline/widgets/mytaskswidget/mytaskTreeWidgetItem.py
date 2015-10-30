from PyQt4 import QtCore,QtGui
from DPSPipeline.widgets import taskProgressButton
from DPSPipeline.widgets import userLabel
import sharedDB

class MyTaskTreeWidgetItem(QtGui.QTreeWidgetItem):
    
    def __init__(self, parentTreeWidget, task):
        super(QtGui.QTreeWidgetItem, self).__init__()
        
        self.parentTreeWidget = parentTreeWidget
            
        self.parentTreeWidget.addTopLevelItem(self)    
            
        #shot id
        #self.setText(0,(str(self.shot._idshots)))
        
        #shot name
        #self.setText(1,(str(self.shot._number)))        
        
        #if tasklist less than lenshotphasenames - 2
        columnIndex = 0
                
        if task is not None:                
        
            #create button for currentTask
            #btn = self.AddProgressButton(shotWidgetItem,columnIndex,85,currentTask._status)
            
            btn = taskProgressButton.TaskProgressButton(_task=task)
            uLabel = userLabel.UserLabel(task = task)
            
            taskBtnWidget = QtGui.QWidget()
            vLayout = QtGui.QHBoxLayout()
            taskBtnWidget.setLayout(vLayout)
            vLayout.addWidget(btn)
            vLayout.addWidget(uLabel)
            self.parentTreeWidget.setItemWidget(self,columnIndex,taskBtnWidget)

    