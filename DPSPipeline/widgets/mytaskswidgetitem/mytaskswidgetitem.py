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
	self.tasklist = []
	
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
	self.pace.setText("N/A")
	if self.user is not None and self._userassignment is not None and self.hours.text() != "0" and self._phaseassignment.hoursAlotted() > 1 and str(self._phaseassignment._taskPerShot) == "1":
	     
	    percentage = float(self._userassignment._hours) / self._phaseassignment.hoursAlotted()
	    
	    taskNum = 0
	    #get project
	    for task in self._phaseassignment._tasks.values():
		if (int(task._approved) == 0 and task._status != 2 and task._status != 4 and task._status != 1) or (task._status == 1 and task._idusers == self.user.id() ):
		    #if shot deleted skip task
		    if int(task._idshots) > 0 and str(task._idshots) in sharedDB.myShots and sharedDB.myShots[str(task._idshots)]._idstatuses > 2:
			#print "Shot "+sharedDB.myShots[str(task._idshots)]._number+" Deleted, skipping tasks."
			continue		    
		    taskNum += 1
	    
	    if taskNum > 0 and self._userassignment._hours>1:

		for task in self._phaseassignment._tasks.values():
		    if task not in self.tasklist:
			task.taskChanged.connect(self.UpdateValues)
			self.tasklist.append(task)

		if self._phaseassignment._startdate <= date.today() <= self._phaseassignment._enddate:
		    user = sharedDB.myUsers[str(self._userassignment._idusers)]
		    numhours = 0
		    currdate = date.today()
		    while currdate <= self._phaseassignment._enddate:
			if str(currdate) in user._bookingDict:
			   for b in user._bookingDict[str(currdate)]:
				if str(b._idphaseassignments) == str(self._phaseassignment.id()):
				    hourspassed = 0
				    if currdate == date.today():
					h = datetime.now().hour
					if h > 9:
					    if h < 17:
						hourspassed = h-9						
					    else:
						hourspassed = 8
						
					    if hourspassed > b._hours:
						hourspassed = int(b._hours)
					#print hourspassed
				    numhours += int(b._hours)-hourspassed
			
			currdate = currdate + timedelta(days=1)

		elif date.today()>self._phaseassignment._enddate:
		    numhours = 1
		else:
		    numhours = self._userassignment._hours
		
		#print "\nTasknum: "+str(taskNum)
		#print "User Hours: "+str(numhours)
		#print "percentage: "+str(percentage)
		#print "numtasksToAssign: "+str(math.ceil(taskNum*percentage))
		#print "pace: "+str(numhours/(math.ceil(taskNum*percentage)))

		pace = round(numhours/(math.ceil(taskNum*percentage)),1)
		if pace != 0:
		    self.pace.setText(str(pace) + " hrs per shot")

	
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
	
	if self._project._archived == 0:
	    
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
    
    