import sys
import weakref
import projexui
import sharedDB
import math

from datetime import timedelta,datetime,date
from PyQt4 import QtGui,QtCore

#from PyQt4 import QtCore
from PyQt4.QtGui    import QWidget
from PyQt4.QtCore   import QDate,QTime,QVariant,Qt

class MyTasksWidgetItem(QWidget):
    
    def __init__( self, parent = None, _project = None, _userassignment = None, _phaseassignment = None, _rowItem = None ):
    
	super(MyTasksWidgetItem, self).__init__( parent )
	
	# load the user interface# load the user interface
	if getattr(sys, 'frozen', None):
	   projexui.loadUi(sys._MEIPASS, self, uifile = (sys._MEIPASS+"/ui/mytaskswidgetitem.ui"))    
	else:
	    projexui.loadUi(__file__, self)
	    
	self._project = _project
	self._userassignment = _userassignment
	if _userassignment is not None:
	    if str(_userassignment.idUsers()) in sharedDB.myUsers:
		self.user = sharedDB.myUsers[str(_userassignment.idUsers())]
	    self._userassignment.userAssignmentChanged.connect(self.UpdateValues)
	else:
	    self.user = None
	self._phaseassignment = _phaseassignment	
	self.mytaskwidget = parent
	self._rowItem = _rowItem
	
	#connect update values
	self._project.projectChanged.connect(self.UpdateValues)
	
	self._phaseassignment.phaseAssignmentChanged.connect(self.UpdateValues)
	self._phaseassignment.phaseAssignmentChanged.connect(self.SetVisibility)
	self._phaseassignment.userAssigned.connect(self.deleteThisRow)
	
	sharedDB.mySQLConnection.dateChanged.connect(self.UpdateValues)
	
	self.UpdateValues()
	
	
    def UpdateValues(self):	
	self.projectName.setText(self._project._name)
	if self.user is not None:
	    self.phaseName.setText(self._phaseassignment._name+" - "+self.user._name)
	else:
	    self.phaseName.setText(self._phaseassignment._name+" - UNASSIGNED")
	self.due.setText(self._phaseassignment._enddate.strftime('%m/%d/%Y'))
	if self._userassignment is not None:
	    self.hours.setText(str(self._userassignment._hours))
	else:
	    self.hours.setText("0")
	
	if str(self._phaseassignment._idstatuses) in sharedDB.myStatuses:
	    self.status.setText(sharedDB.myStatuses[str(self._phaseassignment._idstatuses)]._name)

	#calculate pace
	if self.user is not None and self._userassignment is not None and self.hours.text() != "0" and self._phaseassignment.hoursAlotted() > 1 and str(self._phaseassignment._taskPerShot) == "1":
	     
	    percentage = float(self._userassignment._hours) / self._phaseassignment.hoursAlotted()
	    
	    '''
		For Pace: Get percentage assigned by comparing assigned hours to total budgeted hours.
		Multiply percentage by number of shots.  
	    '''
	    
	    taskNum = 0
	    #get project
	    for task in self._phaseassignment._tasks.values():
		if task._status != 2 and task._status != 4 and task._status != 1:
		    taskNum += 1

	    print "Tasknum: "+str(taskNum)
	    print "User Hours: "+str(self._userassignment._hours)
	    print "percentage: "+str(percentage)
	    uah = float(self._userassignment._hours)
	    taskpercentage = float(taskNum*percentage)
	    print str(taskNum*percentage)
	    #print str(uah/taskpercentage)
	    
	    if taskNum == 0:
		self.pace = "N/A"
	    else:
		self.pace.setText(str(int(math.ceil(self._userassignment._hours/(taskNum*percentage)))) + " hrs per shot")
	    
	else:
	    self.pace.setText("N/A")
	
	self.UpdateColors()
	    
	self.SetVisibility()
    
    def UpdateColors(self):
	#if due date is already passed turn red
	try:
	    if str(self._phaseassignment.idstatuses()) == "4":
		self.bgFrame.setStyleSheet("background-color: rgb(0,150,0);")
	    elif str(self._phaseassignment.idstatuses()) == "3":
		self.bgFrame.setStyleSheet("background-color: rgb(250,200,0);")
	    elif str(self._phaseassignment.idstatuses()) == "7":
		self.bgFrame.setStyleSheet("background-color: rgb(200,100,255);")
	    elif self._userassignment is None:
		self.bgFrame.setStyleSheet("background-color: rgb(20,150,230);")
	    elif date.today() > self._phaseassignment._enddate:
		self.bgFrame.setStyleSheet("background-color: rgb(255,0,0);")
	    elif date.today() >= self._phaseassignment._startdate:
		self.bgFrame.setStyleSheet("background-color: rgb(159,255,94);")
	    elif date.today()+timedelta(days=5) >= self._phaseassignment._startdate:
		self.bgFrame.setStyleSheet("background-color: rgb(176,220,220);")
	    else:
		self.bgFrame.setStyleSheet("background-color: rgb(186,186,186);")
	except:
	    print "Unable to change color on task item, task was removed from list"
    
    
    def userAssignment(self):
	return self._userassignment
    
    def phaseAssignment(self):
	return self._phaseassignment
    
    def deleteThisRow(self):
	#print "Trying to remove"+self._phaseassignment.name()
	try:
	    if self._userassignment is None:
		self.mytaskwidget.unassignedItems.remove(self)
		'''for i, o in enumerate(self.mytaskwidget.unassignedItems):
		    if o == self:
			del self.mytaskwidget.unassignedItems[i]
			break
		'''
		self.mytaskwidget.removeCellWidget(self._rowItem.row(),0)
		self.mytaskwidget.removeRow(self._rowItem.row())
	except:
	    print "Widget did not exist"
    
    def SetVisibility(self):
	self.mytaskwidget.setSortingEnabled(0)
	
	self.mytaskwidget.setRowHidden(self._rowItem.row(),1)
	
	#if unassigned
	if self._userassignment is None:
	    if self.mytaskwidget.allowedStatuses.count(int(self._phaseassignment.idstatuses())) and self.mytaskwidget.showUnassignedEnabled:
		#if sharedDB.currentUser._idPrivileges == 2 and self._phaseassignment._iddepartments in sharedDB.currentUser.departments():
		if sharedDB.currentUser._idPrivileges == 1 or self.mytaskwidget.showAllUsersEnabled or (self.mytaskwidget.showAllUsersInDepartmentEnabled and str(self._phaseassignment._iddepartments) in str(sharedDB.currentUser.departments())):
		    self.mytaskwidget.setRowHidden(self._rowItem.row(),0)
	else:	
	    if self.mytaskwidget.allowedStatuses.count(int(self._phaseassignment.idstatuses())) and self._userassignment.hours() > 0:
		if self._userassignment.idUsers() == sharedDB.currentUser.idUsers() or self.mytaskwidget.showAllUsersEnabled or (self.mytaskwidget.showAllUsersInDepartmentEnabled and str(self._phaseassignment._iddepartments) in str(sharedDB.currentUser.departments())):
		    #self.mytaskwidget._rowItem.row().setHidden(0)
		    self.mytaskwidget.setRowHidden(self._rowItem.row(),0)
		
	    
	self.mytaskwidget.setSortingEnabled(1)
    
    def select(self):
	if self.bgFrame is not None:
	    self.bgFrame.setStyleSheet("background-color: rgb(250,250,0);")
	
    def deselect(self):
	self.UpdateColors()
    
    