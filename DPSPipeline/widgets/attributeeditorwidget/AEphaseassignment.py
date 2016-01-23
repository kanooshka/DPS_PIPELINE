import projexui,projex
import sharedDB
import sys

from DPSPipeline.widgets.attributeeditorwidget import userAssignmentWidget

from PyQt4 import QtGui,QtCore

class AEPhaseAssignment(QtGui.QWidget):

    def __init__( self, parent = None ):
    
	super(AEPhaseAssignment, self).__init__( parent )
	
	# load the user interface# load the user interface
	'''if getattr(sys, 'frozen', None):
	    projexui.loadUi(sys._MEIPASS, self, uifile = (sys._MEIPASS+"/ui/AEPhaseAssignment.ui"))	    
	else:
	    projexui.loadUi(__file__, self)
	'''
	self.setMinimumSize(300,0)
	self.resize(300,self.height())
		    
	self.baseLayout = QtGui.QVBoxLayout()
	self.baseLayout.setContentsMargins(2,2,2,2)
	self.setLayout(self.baseLayout)
	
	self.PhaseAssignmentBox = QtGui.QGroupBox()
	self.baseLayout.addWidget(self.PhaseAssignmentBox)
	
	self.aephaseassignmentlayout = QtGui.QVBoxLayout()
	self.aephaseassignmentlayout.setContentsMargins(2,2,2,2)
	self.PhaseAssignmentBox.setLayout(self.aephaseassignmentlayout)	
	
	#Status Box
	self.statusBox = QtGui.QGroupBox()
	self.statusBox.setTitle("Status")
	self.aephaseassignmentlayout.addWidget(self.statusBox)

	self.phaseStatus = QtGui.QComboBox()
	self.phaseStatus.currentIndexChanged[QtCore.QString].connect(self.saveStatus)
	#self.phaseStatus.currentIndexChanged[QtCore.QString].connect(sharedDB.myTasksWidget.propogateUI)
	
	self.statusLayout = QtGui.QGridLayout()
	self.statusLayout.setContentsMargins(2,2,2,2)
	self.statusBox.setLayout(self.statusLayout)
	self.statusLayout.addWidget(self.phaseStatus,0,0)
	
	#Date box
	self.datesBox = QtGui.QGroupBox()
	self.datesBox.setTitle("Dates")
	self.aephaseassignmentlayout.addWidget(self.datesBox)
	
	self.startDateLabel = QtGui.QLabel("Start Date: ")	
	self.startDate = QtGui.QDateEdit()
	self.startDate.setCalendarPopup(1)
	self.endDateLabel = QtGui.QLabel("End Date: ")	
	self.endDate = QtGui.QDateEdit()
	self.endDate.setCalendarPopup(1)
	self.calendarDaysLabel = QtGui.QLabel("Calendar Days: ")	
	self.calendarDays = QtGui.QSpinBox()
	self.calendarDays.setKeyboardTracking(0)
	self.workDaysLabel = QtGui.QLabel("Work Days: ")	
	self.workDays = QtGui.QSpinBox()
	self.workDays.setKeyboardTracking(0)
	
	#connect date box to calendarwidgetitem
	self.calendarDays.valueChanged.connect(self.changeCalendarDays)
	self.workDays.valueChanged.connect(self.changeWorkDays)
	self.startDate.dateChanged.connect(self.changeStartDate)
	self.endDate.dateChanged.connect(self.changeEndDate)

	self.dateLayout = QtGui.QGridLayout()
	self.dateLayout.setContentsMargins(2,2,2,2)
	self.datesBox.setLayout(self.dateLayout)
	self.dateLayout.addWidget(self.startDateLabel,0,0)
	self.dateLayout.addWidget(self.startDate,0,1)
	self.dateLayout.addWidget(self.endDateLabel,0,2)
	self.dateLayout.addWidget(self.endDate,0,3)
	self.dateLayout.addWidget(self.calendarDaysLabel,1,0)
	self.dateLayout.addWidget(self.calendarDays,1,1)
	self.dateLayout.addWidget(self.workDaysLabel,1,2)
	self.dateLayout.addWidget(self.workDays,1,3)
	
	#user box
	self.userBox = QtGui.QGroupBox()
	self.aephaseassignmentlayout.addWidget(self.userBox)
	
	self.userLayout = QtGui.QVBoxLayout()
	self.userLayout.setContentsMargins(2,2,2,2)
	self.userBox.setLayout(self.userLayout)
	self.userBox.setTitle("Users")
	
	#Hours Box	
	self.hoursWidget = QtGui.QWidget()
	self.userLayout.addWidget(self.hoursWidget)
	
	self.totalHoursLabel = QtGui.QLabel("Budgeted Hours: ")	
	self.hoursalotted = QtGui.QSpinBox()
	self.hoursalotted.setMaximum(999999)
	self.hoursalotted.setKeyboardTracking(0)
	self.hoursalotted.valueChanged.connect(self.changeAlottedHours)

	self.unassignedHoursLabel = QtGui.QLabel("Unassigned: ")	
	self.unassignedHours = QtGui.QLabel("0")
	
	self.hoursLayout = QtGui.QHBoxLayout()
	self.hoursLayout.setContentsMargins(2,2,2,2)
	self.hoursWidget.setLayout(self.hoursLayout)
	self.hoursLayout.addWidget(self.totalHoursLabel)
	self.hoursLayout.addWidget(self.hoursalotted)
	self.hoursLayout.addWidget(self.unassignedHoursLabel)
	self.hoursLayout.addWidget(self.unassignedHours)
	
	#users table
	self.userTable = userAssignmentWidget.UserAssignmentWidget(self)
	self.userTable.aephaseAssignment = self
	self.userLayout.addWidget(self.userTable)
	
	#Bottom spacer
	self.spacer = QtGui.QSpacerItem(20,40,QtGui.QSizePolicy.Minimum,QtGui.QSizePolicy.Expanding)
	self.aephaseassignmentlayout.addItem(self.spacer)
	
	self.setHidden(1)

	self.setEnabled(0)
	
	self._currentPhaseAssignment = None	

    def LoadPhaseAssignment(self, sentPhaseAssignment):

	self._signalsBlocked = 1
	
	if isinstance(sentPhaseAssignment, sharedDB.phaseAssignments.PhaseAssignments):
	    self._currentPhaseAssignment = sentPhaseAssignment

	if self._currentPhaseAssignment is not None:
	    
	    if len(sharedDB.sel.items):
		if hasattr(sharedDB.sel.items[len(sharedDB.sel.items)-1], "_type") and sharedDB.sel.items[len(sharedDB.sel.items)-1]._type == "phaseassignment":
		    self.setPrivileges()
		    self.setEnabled(1)
		    self.setHidden(0)   
		    
		    self.refresh()
		    self.userTable.UpdateWidget()
		    #set Status
		    #self.shotStatus.setCurrentIndex(self._currentShot._idstatuses-1)
		    
		    #set Description
		    #if self._currentShot is not None and self._currentShot._description is not None:
			#self.shotDescription.blockSignals = 1
			#self.shotDescription.setText(self._currentShot._description)
			#self.shotDescription.blockSignals = 0
	    
	self._signalsBlocked = 0
    
    def refresh(self):
	pa = self._currentPhaseAssignment	
	self.propogateStatuses()
	self.setStatus()
	#
	
	#set title
	self.PhaseAssignmentBox.setTitle(str(self._currentPhaseAssignment.project._name)+" : "+str(self._currentPhaseAssignment._name))
	
	if self.startDate.date().toPyDate() != pa._startdate:
	    #print "Start Date updating"
	    self.startDate.setDate(pa._startdate)
	if self.endDate.date().toPyDate() != pa._enddate:
	    #print "End Date updating"
	    self.endDate.setDate(pa._enddate)
	
	self.calendarDays.setValue(self.duration())
	self.workDays.setValue(self.weekdays())
	'''
	if self.calendarDays.value() != pa._calendarWidgetItem.duration():
	    self.calendarDays.setValue(pa._calendarWidgetItem.duration())
	if self.workDays.value() != pa._calendarWidgetItem.weekdays():
	    self.workDays.setValue(pa._calendarWidgetItem.weekdays())
	'''
	
	
	if self.hoursalotted.value() != pa.hoursAlotted():
	    #print "Work Days updating"
	    self.hoursalotted.setValue(pa.hoursAlotted())
	    
	self.UpdateHourValues()
    
    def UpdateHourValues(self):
	unassignedHoursNum = self.hoursalotted.value()-self.userTable.totalAssignedHours
	self.unassignedHours.setText(str(unassignedHoursNum))
	if unassignedHoursNum>=0:
	    self.unassignedHours.setStyleSheet('color: green')
	else:
	    self.unassignedHours.setStyleSheet('color: red')
    
    def changeAlottedHours(self):
	if not self._signalsBlocked:
	    self._currentPhaseAssignment.setHoursAlotted(self.hoursalotted.value())
	    
	    #update colors
	    self.userTable.setTotalAssignedHours()
    
    def changeCalendarDays(self):
	if not self._signalsBlocked:
	    self._currentPhaseAssignment._calendarWidgetItem.setProperty("Calendar Days",self.calendarDays.value())
    
    def changeWorkDays(self):
	if not self._signalsBlocked:
	    self._currentPhaseAssignment._calendarWidgetItem.setProperty("Work Days",self.workDays.value())
	
    def changeStartDate(self):
	if not self._signalsBlocked:
	    self._currentPhaseAssignment._calendarWidgetItem.setProperty("Start",self.startDate.date())
	
    def changeEndDate(self):
	if not self._signalsBlocked:
	    self._currentPhaseAssignment._calendarWidgetItem.setProperty("End",self.endDate.date())
    
    def setPrivileges (self):
        if sharedDB.currentUser._idPrivileges == 2:
            self.startDate.setReadOnly(1)
	    self.endDate.setReadOnly(1)
	    self.workDays.setReadOnly(1)
	    self.calendarDays.setReadOnly(1)
	    self.hoursalotted.setReadOnly(1)
	    if str(self._currentPhaseAssignment.iddepartments()) not in sharedDB.currentUser.departments():
		self.phaseStatus.setEnabled(0)
	    else:
		self.phaseStatus.setEnabled(1)
	    
	if sharedDB.currentUser._idPrivileges == 3:
	    self.startDate.setReadOnly(1)
	    self.endDate.setReadOnly(1)
	    self.workDays.setReadOnly(1)
	    self.calendarDays.setReadOnly(1)
	    self.phaseStatus.setEnabled(0)
	    self.userBox.setVisible(0)
	
    def setStatus(self):
	self.phaseStatus.blockSignals(1)
	status = self._currentPhaseAssignment._idstatuses-1
	if status<0:
	    status = 0
	self.phaseStatus.setCurrentIndex(status)
	self.phaseStatus.blockSignals(0)
    def saveStatus(self):
	self._currentPhaseAssignment.setIdstatuses(self.phaseStatus.currentIndex()+1)
    
        
    def propogateStatuses(self):
	self.phaseStatus.blockSignals(1)
	self.phaseStatus.clear()
	for status in sharedDB.myStatuses:
	    self.phaseStatus.addItem(status._name, QtCore.QVariant(status))
	self.phaseStatus.blockSignals(0)
    
    def duration( self ):
        """
        Returns the number of days this gantt item represents.
        
        :return     <int>
        """
        return 1 + self.startDate.date().daysTo(self.endDate.date())
  
    def weekdays(self):
        """
        Returns the number of weekdays this item has.
        
        :return     <int>
        """            
	dstart = self.startDate.date().toPyDate()
	dend   = self.endDate.date().toPyDate()
	self._workdays = projex.dates.weekdays(dstart, dend)
	return self._workdays  
    
    '''
    def setShotSettingsEnabled(self, v):
	self.shotNumber.setEnabled(v)
	self.shotStatus.setEnabled(v)
	self.startFrame.setEnabled(v)
	self.endFrame.setEnabled(v)
	self.shotImage.setEnabled(v)
	self.shotDescription.setEnabled(v)
	self.shotNotes.setEnabled(v)
    
    def SetShotValues(self):
	if not self._blockUpdates:
		if self._currentShot is not None:
		    #self._currentShot._description = self.shotDescription.toPlainText()
		    self._currentShot._idstatuses = self.shotStatus.currentIndex()+1
		    self._currentShot._startframe = self.startFrame.value()
		    self._currentShot._endframe = self.endFrame.value()
		    self._currentShot._updated = 1
    '''