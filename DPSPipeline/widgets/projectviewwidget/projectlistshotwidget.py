import sharedDB

from PyQt4 import QtCore,QtGui
from DPSPipeline.widgets import noWheelCombobox
from DPSPipeline.widgets import taskProgressButton
import operator

class ProjectlistShotWidget(QtGui.QTreeWidget):
    
    newVersion = QtCore.pyqtSignal(QtCore.QString)

    def __init__(self,_currentProject,_shots, _projectphases):
        super(QtGui.QTreeWidget, self).__init__()
        
        self._project = _currentProject
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
            self.header().setResizeMode(col,QtGui.QHeaderView.Fixed)

        self._shots.sort(key=operator.attrgetter('_number'))
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

                #get tasklist from shot
                tasks = shot._tasks
                #if tasklist less than lenshotphasenames - 2
                for phase in self._phases:
                    if phase._taskPerShot:
                        currentTask = None
                        
                        for task in tasks:
                            if task._idphases == phase._idphases:
                                print "MATCH FOUND"
                                currentTask = task
                        
                        #if task didn't exist, create task  
                        if currentTask is None:
                            print "TASKS ADDED"
                            currentTask = sharedDB.tasks.Tasks(_idphaseassignments = phase._idphases, _idprojects = self._project._idprojects, _idshots = shot._idshots, _idphases = phase._idphases, _percentcomplete = 0, _done = 0, _new = 1)
                            tasks.append(currentTask)
                            sharedDB.myTasks.append(currentTask)
                
                for p in range(2,len(self.shotPhaseNames)):                
                    #layout button
                    #self.AddStatusCombobox(shotWidgetItem,p,85)       
                    self.AddProgressButton(shotWidgetItem,p,85)
                    
    def SetShotPhaseNames(self):        
        for phase in self._phases:
            if phase._taskPerShot:
                self.shotPhaseNames.append(phase._name)
    
    def AddStatusCombobox(self,widgetItem,index,width):
        cmbox = noWheelCombobox.NoWheelComboBox()
        cmbox.addItems(self.statuses)
        self.setItemWidget(widgetItem,index,cmbox)
        self.setColumnWidth(index,width)
    
    def AddProgressButton(self,widgetItem,index,width):
        btn = taskProgressButton.TaskProgressButton()
        self.connect(btn, QtCore.SIGNAL('clicked()'), btn.clicked)
        self.setItemWidget(widgetItem,index,btn)
        self.setColumnWidth(index,width)
    
    #Disable arrow keys for this qtree
    def keyPressEvent(self, event):
        pass