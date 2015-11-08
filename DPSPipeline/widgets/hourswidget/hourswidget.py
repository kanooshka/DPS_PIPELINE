import projexui
import sharedDB
import sys

import time

from datetime import timedelta,datetime
#from projexui import qt import Signal
from PyQt4 import QtGui,QtCore
#from PyQt4 import QtCore
from PyQt4.QtGui    import QWidget
from PyQt4.QtCore   import QDate,QTime,QVariant,Qt


class HoursWidget(QWidget):
    refreshHourValuesSignal = QtCore.pyqtSignal()
    
    def __init__( self, parent = None ):
    
	super(HoursWidget, self).__init__( parent )
	
	self._currentProject = None
	
	# load the user interface# load the user interface
	if getattr(sys, 'frozen', None):
	    projexui.loadUi(sys._MEIPASS, self, uifile = (sys._MEIPASS+"/ui/hourswidget.ui"))
	    
	else:
	    projexui.loadUi(__file__, self)
	