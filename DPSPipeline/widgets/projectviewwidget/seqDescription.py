
from PyQt4 import QtGui,QtCore

class SeqDescription(QtCore.QWidget):

    def __init__( self, parent = None ):
    
	super(SeqDescription, self).__init__( parent )
	
	# load the user interface# load the user interface
	if getattr(sys, 'frozen', None):
	    projexui.loadUi(sys._MEIPASS, self, uifile = (sys._MEIPASS+"/ui/seqDescription.ui")) 
	else:
	    projexui.loadUi(__file__, self)
