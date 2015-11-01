import sys
import weakref
import projexui
import sharedDB

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
	self._phaseassignment = _phaseassignment	
	self.mytaskwidget = parent
	self._rowItem = _rowItem
	
	#connect update values
	self._project.projectChanged.connect(self.UpdateValues)
	self._userassignment.userAssignmentChanged.connect(self.UpdateValues)
	self._phaseassignment.phaseAssignmentChanged.connect(self.UpdateValues)
	self._phaseassignment.phaseAssignmentChanged.connect(self.SetVisibility)
	
	
	self.UpdateValues()
	self.SetVisibility()
	
    def UpdateValues(self):	
	self.projectName.setText(self._project._name)
	self.phaseName.setText(self._phaseassignment._name)
	self.due.setText(self._phaseassignment._enddate.strftime('%m/%d/%Y'))
	self.hours.setText(str(self._userassignment._hours))
	
	#if due date is already passed turn red
	if date.today() > self._phaseassignment._enddate:
	    #print "OH NO!!!"
	    #p = QtGui.QPalette();
	    #p.setColor(QtGui.QPalette.Background, QtGui.QColor(255,0,0,1));
	    #self.setAutoFillBackground(1)
	    #self.setPalette(p);
	    self.bgFrame.setStyleSheet("background-color: rgb(255,0,0);")
	else:
	    self.bgFrame.setStyleSheet("background-color: rgb(186,186,186);")
    
    def userAssignment(self):
	return self._userassignment
    
    
    def SetVisibility(self):
	self.mytaskwidget.setSortingEnabled(0)
	
	if self._phaseassignment.idstatuses() < 3 or self._phaseassignment.idstatuses() > 6:
	    #self.mytaskwidget._rowItem.row().setHidden(0)
	    self.mytaskwidget.setRowHidden(self._rowItem.row(),0)
	else:
	    #self.mytaskwidget._rowItem.row().setHidden(0)
	    self.mytaskwidget.setRowHidden(self._rowItem.row(),1)
	    
	self.mytaskwidget.setSortingEnabled(1)