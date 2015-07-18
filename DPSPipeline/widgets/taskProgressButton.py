from PyQt4 import QtGui, QtCore
import projexui
 
class TaskProgressButton(QtGui.QLabel):
 
    stateChanged = QtCore.pyqtSignal(int)
 
    def __init__(self, _task = ''):
        super(QtGui.QLabel, self).__init__()
        
        self._notStarted = projexui.resources.find('img/DP/Statuses/notStarted.png')
        self._inProgress = projexui.resources.find('img/DP/Statuses/inProgress.png')
        self._done = projexui.resources.find('img/DP/Statuses/done.png')
        
        self._task = _task
        self._currentState = self._task._status
        
        self.buttonOrder = [self._notStarted,self._inProgress,self._done]
        
        self.setAlignment(QtCore.Qt.AlignHCenter)
        
        #self.resize(25, 25)
        #self.setPixmap(QtGui.QPixmap(self.buttonOrder[self._currentState]))
        self.connect(self, QtCore.SIGNAL('clicked()'), self.clicked)
        self.updateImage()
        
    def mouseReleaseEvent(self, ev):
        self.emit(QtCore.SIGNAL('clicked()'))
        
    def clicked(self):
        if (self._currentState == len(self.buttonOrder)-1):
            self._currentState = 0
        else:
            self._currentState += 1
        
        
        self._task.setStatus(self._currentState)
        self.updateImage()
        
    def updateImage(self):
        self.setPixmap(QtGui.QPixmap(self.buttonOrder[self._currentState])) 