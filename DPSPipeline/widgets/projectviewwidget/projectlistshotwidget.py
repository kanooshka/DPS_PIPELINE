from PyQt4 import QtCore,QtGui
from DPSPipeline.widgets import noWheelCombobox

class ProjectlistShotWidget(QtGui.QTreeWidget):
    
    newVersion = QtCore.pyqtSignal(QtCore.QString)

    def __init__(self,_shots, _projectphases):
        super(QtGui.QTreeWidget, self).__init__()
        
        self._shots = _shots
        self._phases = _projectphases
        
        self.shotPhaseNames = ["ShotID","Name"]
        
        
        self.statuses = ["Not Started","In Progress","On Hold","Done"]
        
        
        self.SetShotPhaseNames()
        
        self.setHeaderLabels(self.shotPhaseNames)
        
        self.shotTreeItem = QtGui.QTreeWidgetItem()        
        
        #Hides project id column				
        self.setColumnHidden(0,True)
        self.header().setResizeMode(QtGui.QHeaderView.Fixed)

        #center all headers
        for col in range(0,len(self.shotPhaseNames)):
            self.headerItem().setTextAlignment(col,QtCore.Qt.AlignHCenter)

        for x in range(0, len(self._shots)):
                shot=self._shots[x]		    

                shotWidgetItem = QtGui.QTreeWidgetItem()

                #sets alternating background colors
                bgc = QtGui.QColor(200,200,200)			
                if x%2:
                     bgc = QtGui.QColor(250,250,250)

                for col in range(0,len(self.shotPhaseNames)):
                    shotWidgetItem.setBackground(col,bgc) 

                self.addTopLevelItem(shotWidgetItem)
                
                #shot id
                shotWidgetItem.setText(0,(str(shot._idshots)))
                
                #shot name
                shotWidgetItem.setText(1,(str(shot._number)))
                self.setColumnWidth(1,40)
                
                for p in range(2,len(self.shotPhaseNames)+2):                
                    #layout button
                    self.AddStatusCombobox(shotWidgetItem,p,85)                

    def SetShotPhaseNames(self):
        
        for phase in self._phases:
            if phase._taskPerShot:
                self.shotPhaseNames.append(phase._name)
    
    def AddStatusCombobox(self,widgetItem,index,width):
        cmbox = noWheelCombobox.NoWheelComboBox()
        cmbox.addItems(self.statuses)
        self.setItemWidget(widgetItem,index,cmbox)
        self.setColumnWidth(index,width)