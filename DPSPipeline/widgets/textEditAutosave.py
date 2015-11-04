import time
from PyQt4.QtCore import pyqtSlot,SIGNAL,SLOT
from PyQt4 import QtGui,QtCore

class AutoSaveTimer(QtCore.QThread):
    save = QtCore.pyqtSignal()
    
    def run(self):
        #wait two seconds
        time.sleep(1)
        #if not reset emit save signal
        self.save.emit()

class TextEditAutoSave(QtGui.QTextEdit):

    def __init__(self):
	super(TextEditAutoSave, self).__init__()
        
        self.AutoSaveTimer = AutoSaveTimer()
        self.save = self.AutoSaveTimer.save
        self.blockSignals = 0
	
	self.normalPalette = QtGui.QPalette(self.palette())
	
	self.changedPalette = QtGui.QPalette(self.palette())
	self.changedPalette.setColor(QtGui.QPalette.Base,QtGui.QColor(255,255,200))

        self.connect(self,SIGNAL("textChanged()"),
					self,SLOT("slotTextChanged()"))
    
    def keyPressEvent(self, event):
	modifiers = QtGui.QApplication.keyboardModifiers()
	
	if (event.key() == QtCore.Qt.Key_Return and not modifiers == QtCore.Qt.ShiftModifier):
            #self.blockSignals(1)
	    self.resetColorPalette()
	    #print "Enter Pressed!"
	    self.save.emit()
	else:
	    #print ("Text Inputted!"+str(event.key()))
	    #self.blockSignals(0)
	    self.changeColorPalette()
	    super(TextEditAutoSave, self).keyPressEvent(event)
    
    def resetColorPalette(self):
	self.setPalette(self.normalPalette)
    
    def changeColorPalette(self):
	self.setPalette(self.changedPalette)
    
    
    @pyqtSlot()
    def slotTextChanged(self):        
        if not self.blockSignals:
            #print "Text edited!"
            self.needToSave = 1
            #self.AutoSaveTimer.terminate()
            #self.AutoSaveTimer.start()