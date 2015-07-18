from PyQt4 import QtGui, QtCore
import projexui
 
class TaskProgressButton(QtGui.QLabel):
    #BUTTON_IMAGE = 'Images\\Popdevelop_Logo.png'
 
    def __init__(self, *args):
        super(QtGui.QLabel, self).__init__()
        
        self._notStarted = projexui.resources.find('img/DP/Statuses/notStarted.png')
        self._inProgress = projexui.resources.find('img/DP/Statuses/inProgress.png')
        self._done = projexui.resources.find('img/DP/Statuses/done.png')
        self._currentIndex = 0
        
        self.buttonOrder = [self._notStarted,self._inProgress,self._done]
        
        self.setAlignment(QtCore.Qt.AlignHCenter)
        
        #self.resize(25, 25)
        self.setPixmap(QtGui.QPixmap(self.buttonOrder[self._currentIndex]))
        #self.connect(self, QtCore.SIGNAL('clicked()'), self.clicked)  
 
    def mouseReleaseEvent(self, ev):
        self.emit(QtCore.SIGNAL('clicked()'))
        
    def clicked(self ):
        if (self._currentIndex == len(self.buttonOrder)-1):
            self._currentIndex = 0
        else:
            self._currentIndex += 1
        
        self.updateImage()
        
    def updateImage(self):
        self.setPixmap(QtGui.QPixmap(self.buttonOrder[self._currentIndex]))
    