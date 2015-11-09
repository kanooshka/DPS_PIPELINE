import sharedDB

from PyQt4 import QtCore,QtGui
from DPSPipeline.widgets import noWheelCombobox
from DPSPipeline.widgets.projectviewwidget import shotTreeWidgetItem
import operator
from PyQt4.QtCore import pyqtSlot,SIGNAL,SLOT

class ShotTreeWidget(QtGui.QTreeWidget):
    
    newVersion = QtCore.pyqtSignal(QtCore.QString)

    def __init__(self,_project,_sequence,_parentWidgetItem):
        super(QtGui.QTreeWidget, self).__init__()
        
        self._project = _project
        self._parentWidgetItem = _parentWidgetItem
        self._shots = _sequence._shots
        self._phases = _project._phases
        self._sequence = _sequence
        
        self.rowHeight = 45
        
        self.shotPhaseNames = ["ShotID","Name"]
        
        
        self.statuses = ["Not Started","In Progress","On Hold","Done"]        
        
        self.SetShotPhaseNames()
        
        self.setHeaderLabels(self.shotPhaseNames)
        
        self.shotTreeItem = QtGui.QTreeWidgetItem() 
        
        #Hides project id column				
        self.setColumnHidden(0,True)
        self.header().setResizeMode(QtGui.QHeaderView.Fixed)
        self.setColumnWidth(1,40)

        #center all headers
        for col in range(0,len(self.shotPhaseNames)):
            self.headerItem().setTextAlignment(col,QtCore.Qt.AlignHCenter)
            self.header().setResizeMode(col,QtGui.QHeaderView.Fixed)
            self.setColumnWidth(col,85)

        self._shots.sort(key=operator.attrgetter('_number'))
        for x in range(0, len(self._shots)):
                shot=self._shots[x]		    

                
                     
                shotWidgetItem = shotTreeWidgetItem.ShotTreeWidgetItem(shotWidget = self,shotPhaseNames = self.shotPhaseNames, shot = shot, phases = self._phases, project = self._project)
                shotWidgetItem.setSizeHint(3,QtCore.QSize(0,self.rowHeight))
                #self.addTopLevelItem(shotWidgetItem)
         
        #self.setSortingEnabled(True)
        #self.sortByColumn(1)
        self.sortItems(1,QtCore.Qt.AscendingOrder)
        
        self.UpdateBackgroundColors()
        
        #self.itemEntered.connect(sharedDB.myProjectViewWidget.LoadShotValuesFromSent)
	#self.itemPressed.connect(sharedDB.myProjectViewWidget.LoadShotValuesFromSent)
        self.itemEntered.connect(self.ChangeSelection)
	self.itemPressed.connect(self.ChangeSelection)
        
        self.itemEntered.connect(self._parentWidgetItem.sequenceDescription.UpdateShotNumberValue)
	self.itemPressed.connect(self._parentWidgetItem.sequenceDescription.UpdateShotNumberValue)
        sharedDB.mySQLConnection.newTaskSignal.connect(self.AttachTaskToButton)
        
        self.UpdateWidgetHeight()
        
        #disables vertical scroll bar
        #self.setHorizontalScrollBarPolicy( QtCore.Qt.ScrollBarAlwaysOff )
        
    def UpdateWidgetHeight(self):
        
        height = self.topLevelItemCount()*self.rowHeight+40
        #self._parentWidgetItem.setSizeHint(0,QtCore.QSize(0,height))
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Maximum)
        self.setSizePolicy(sizePolicy)
        self.setMinimumSize(0,height)
        
    
    def UpdateBackgroundColors(self):
        try:
	    for x in range(0,self.topLevelItemCount()):           
	    
		#sets alternating background colors
		bgc = QtGui.QColor(200,200,200)			
		if x%2:
		     bgc = QtGui.QColor(250,250,250)
		     
		     
		    for col in range(0,self.columnCount()):
			self.topLevelItem(x).setBackground(col,bgc)
	except:
	    print "Unable to change color on shot item, sequence was removed from list"
    
    def AddShot(self,shot):
        shotWidgetItem = shotTreeWidgetItem.ShotTreeWidgetItem(shotWidget = self,shotPhaseNames = self.shotPhaseNames, shot = shot, phases = self._phases, project = self._project)
        self.sortItems(1,QtCore.Qt.AscendingOrder)
        self.UpdateBackgroundColors()
        shotWidgetItem.setSizeHint(3,QtCore.QSize(0,self.rowHeight))
        self.UpdateWidgetHeight()
    def SetShotPhaseNames(self):        
        for phase in self._phases:
            if phase._taskPerShot:
                self.shotPhaseNames.append(phase._name)        
    
    def AttachTaskToButton(self, idtasks):
        #find task with id
        task = None
        for t in sharedDB.myTasks:
            if str(t._idtasks) == str(idtasks):
                task = t
                #print idtasks
                break            
        
        if task is not None:
            #iterate through items to find correct shot index
            for x in range(0,self.topLevelItemCount()):
                if self.topLevelItem(x).shot._idshots == task._idshots:
                    sTreeWidgetItem = self.topLevelItem(x)
                    for btn in sTreeWidgetItem.btns:
                        #if btn phaseid = task phase id
                        if str(btn._forPhase) == str(task._idphases):
                            btn._task = task
                            btn.getTaskState()
                            task.taskChanged.connect(btn.getTaskState)
                    
                    break
        
    
    
    #Disable arrow keys for this qtree
    def keyPressEvent(self, event):
        pass
    
    def wheelEvent(self, event):
	self._parentWidgetItem._progressList.wheelEvent(event)
    
    def ChangeSelection(self,itemwidget, column):
        sharedDB.sel.select([itemwidget,itemwidget.shot])
    
    #def deselect(self):
    #    self.UpdateBackgroundColors()
        
    #def select(self, ):
    #    pass
    
    
    '''
    #self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu);    
    #self.connect(self,SIGNAL("customContextMenuRequested(QPoint)"),self,SLOT("contextMenuRequested(QPoint)"))
    
    @pyqtSlot(QtCore.QPoint)
    def contextMenuRequested(self,point):
        
        menu	 = QtGui.QMenu()
           
        action1 = QtGui.QAction('&Add Sequence', self)
        #action1.setData(10)
        #action1 = self.popMenu.addAction('Selected %s' % item)
        action1.triggered[()].connect(
            lambda item="Not working yet": self.AddShot(item))
        menu.addAction(action1)
       
        #action2 = menu.addAction("Set Size 500x500") 
        
        #self.connect(action1,SIGNAL("triggered()"),sharedDB.myProjectViewWidget,SLOT("AddShot()"))
        self.connect(action1,SIGNAL("triggered(QtGui.QAction)"),self,SLOT("AddShot(QtGui.QAction)"))
        
        #self.connect(action2,SIGNAL("triggered()"),self,SLOT("slotShow500x500()"))
        menu.exec_(self.mapToGlobal(point))
        
    def AddShot(self,yay):
        QtGui.QMessageBox.about(self, "Test", yay)
    '''