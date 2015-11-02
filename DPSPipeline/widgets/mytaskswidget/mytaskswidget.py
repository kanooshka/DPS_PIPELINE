import sys
import weakref
import projexui
import sharedDB

from datetime import timedelta,datetime
#from projexui import qt import Signal
from DPSPipeline.widgets.mytaskswidget import mytaskswidgetitem
from PyQt4 import QtGui,QtCore
#from PyQt4 import QtCore
from PyQt4.QtGui    import QWidget
from PyQt4.QtCore   import QDate,QTime,QVariant,Qt

class MyTasksWidget(QtGui.QTableWidget):
    
    def __init__( self, parent = None ):
    
	super(MyTasksWidget, self).__init__( parent )
	
	# load the user interface# load the user interface
	#if getattr(sys, 'frozen', None):
	#   projexui.loadUi(sys._MEIPASS, self, uifile = (sys._MEIPASS+"/ui/mytaskswidget.ui"))    
	#else:
	#    projexui.loadUi(__file__, self)

	self._blockUpdates = 0
	
	sharedDB.myTasksWidget = self
	
	if sharedDB.initialLoad:
	    self.propogateUI
	else:
	    sharedDB.mySQLConnection.firstLoadComplete.connect(self.propogateUI)
	
	#self.projectTaskItems = []
	self.setEnabled(0)
	
	self.showAllEnabled = 0
	self.showUnassignedEnabled = 0
	
	self.horizontalHeaderLabels = ["Task","Due Date","ID User Assignment"]
	for x in range(0,len(self.horizontalHeaderLabels)):
	    self.insertColumn(x)
	self.setHorizontalHeaderLabels(self.horizontalHeaderLabels)

	self.setShowGrid(0)

	self.verticalHeader().setVisible(False)
	self.verticalHeader().setDefaultSectionSize(95)
	self.horizontalHeader().setVisible(False)
	self.horizontalHeader().setResizeMode( 0, QtGui.QHeaderView.Stretch )
	self.setSortingEnabled(1)
	self.setColumnHidden(1,True)
	self.setColumnHidden(2,True)
	
	self.sortByColumn(1,QtCore.Qt.AscendingOrder)
    
	#create listener for new user assignments
	
	self.myTaskItems = []
	self.unassignedItems = []
	
	sharedDB.mySQLConnection.newUserAssignmentSignal.connect(self.propogateUI)
	
	self.cellClicked.connect(self.sendSelection)
    
    def propogateUI(self):
	#self.clear()
	#for x in range(0,self.rowCount()):
	#    self.removeRow(x)
	
	self.setSortingEnabled(0)
	
	for i in range(0,self.rowCount()):
	    self.setRowHidden(i,1)	
	
	for user in sharedDB.myUsers:
	    if user == sharedDB.currentUser or self.showAllEnabled:	
		for userassignment in user._assignments:	    
		    if str(userassignment.assignmentType()) == "phase_assignment":
			found = 0
			
			#see if it already exists
			if self.myTaskItems is not None:
			    for t in self.myTaskItems:
				if t.userAssignment() == userassignment:
				    t.UpdateValues()
				    found = 1
				    break
			
			if not found:
			    #add phase assignment to widget
			    phase = sharedDB.phaseAssignments.getPhaseAssignmentByID(userassignment._assignmentid)
			    
			    #add userassignment to phase
			    
			    
			    #projectWidgetItem = projectTreeWidgetItem.ProjectTreeWidgetItem(phase = phase, parent = self.myTaskList)
			    #self.myTaskList.insertTopLevelItem(0,projectWidgetItem)		
			    #self.projectTaskItems.append(projectWidgetItem)
			    
			    self.insertRow(self.rowCount())
			    
			    #phase.phaseAssignmentChanged.connect(self.propogateUI)
			    dateitem = QtGui.QTableWidgetItem()	
			    dateitem.setText(phase.endDate().strftime('%Y/%m/%d'))
			    
			    taskItem = mytaskswidgetitem.MyTasksWidgetItem(parent = self, _project = phase.project, _userassignment = userassignment, _phaseassignment = phase, _rowItem = dateitem)	
			    self.myTaskItems.append(taskItem)
			    #taskItem.setText(phase.name())
			    
			    #userassignItem = QtGui.QTableWidgetItem()	
			    #userassignItem.setText(self._userassignment.idUserAssignment)
			    
			    self.setCellWidget(self.rowCount()-1,0,taskItem)
			    self.setItem(self.rowCount()-1,1,dateitem)
			    taskItem.SetVisibility()
			    #self.setItem(self.rowCount()-1,2,userassignItem)
	
	if self.showUnassignedEnabled:
	    for phase in sharedDB.myPhaseAssignments:
		if len(phase.userAssignment()) == 0:
		    
		    found = 0
		    
		    if self.unassignedItems is not None:
			for p in self.unassignedItems:
			    if p.phaseAssignment() == phase:
				p.UpdateValues()
				found = 1
				break
		    
		    if not found:
		    
			self.insertRow(self.rowCount())
	
			dateitem = QtGui.QTableWidgetItem()	
			dateitem.setText(phase.endDate().strftime('%Y/%m/%d'))
			
			if phase.project is not None:
			    taskItem = mytaskswidgetitem.MyTasksWidgetItem(parent = self, _project = phase.project, _phaseassignment = phase, _rowItem = dateitem)	
			    self.unassignedItems.append(taskItem)
		    
			    self.setCellWidget(self.rowCount()-1,0,taskItem)
			    self.setItem(self.rowCount()-1,1,dateitem)
			    taskItem.SetVisibility()

	self.setSortingEnabled(1)

	self.setEnabled(1)
	
    def contextMenuEvent(self, ev):
        
        #if self.isEnabled():
        activeIps = []
        activeClients = []

        for proj in sharedDB.myProjects:
            if not proj._hidden or self.showAllEnabled:
                if str(proj._idclients) not in activeClients or self.showAllEnabled:
                    activeClients.append(str(proj._idclients))
                if str(proj._idips) not in activeIps or self.showAllEnabled:
                    activeIps.append(str(proj._idips))
        
        menu	 = QtGui.QMenu()
        
        showAllAction = menu.addAction('Show All User Assignments')
        showAllAction.setCheckable(True)
        showAllAction.setChecked(self.showAllEnabled)
        showAllAction.triggered.connect(self.toggleShowAllAction)       
           
        menu.addSeparator()
        
	showUnassignedAction = menu.addAction('Show Unassigned')
        showUnassignedAction.setCheckable(True)
        showUnassignedAction.setChecked(self.showUnassignedEnabled)
        showUnassignedAction.triggered.connect(self.toggleShowUnassignedAction)
	
	''' 
        #iterate through clients
        cli = sharedDB.myClients
        cli.sort(key=operator.attrgetter('_name'),reverse=False)
        for i in xrange(0, len(cli)):
            if str(cli[i]._idclients) in activeClients:
                exec("client_menu%d = QtGui.QMenu(cli[i]._name)" % (i + 1))
                exec("menu.addMenu(client_menu%d)" % (i + 1))
                #Iterate through Client's IPs
                if len(cli[i]._ips):
                    ips = cli[i]._ips
                    ips.sort(key=operator.attrgetter('_name'),reverse=False)
                    for j in xrange(0, len(ips)):
                        if str(ips[j]._idips) in activeIps:
                            exec("ip%d_%d = QtGui.QMenu(ips[j]._name)" % (i + 1,j + 1))
                            exec("client_menu%d.addMenu(ip%d_%d)" % (i + 1,i+1,j+1))
                            #Iterate through projects in IP
                            if len(ips[j]._projects):
                                projs = ips[j]._projects
                                projs.sort(key=operator.attrgetter('_name'),reverse=False)
                                for k in xrange(0, len(projs)):
                                    if not projs[k]._hidden or self.showAllEnabled:
                                        exec("ip%d_%d.addAction(%s)" % (i + 1,j + 1,repr(projs[k]._name)))
                                        exec("ip%d_%d.triggered.connect(self.ChangeProject)" % (i + 1,j + 1))
        '''

        menu.exec_(ev.globalPos())
    
    def toggleShowUnassignedAction(self):
	self.showUnassignedEnabled = not self.showUnassignedEnabled
	self.propogateUI()
    
    def toggleShowAllAction(self):
	self.showAllEnabled = not self.showAllEnabled
	self.propogateUI()
	
    def sendSelection(self, row, column):
	sharedDB.sel.select(self.cellWidget(row,column)._phaseassignment)
    