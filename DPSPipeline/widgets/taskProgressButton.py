from PyQt4 import QtGui, QtCore
import projexui
import sharedDB
 
class TaskProgressButton(QtGui.QLabel):
 
    stateChanged = QtCore.pyqtSignal(int)
 
    def __init__(self, _task = None,_shot = '',_forPhase = ''):
        super(QtGui.QLabel, self).__init__()
        
        self._notStarted = projexui.resources.find('img/DP/Statuses/notStarted.png')
        self._inProgress = projexui.resources.find('img/DP/Statuses/inProgress.png')
        self._done = projexui.resources.find('img/DP/Statuses/done.png')
        
        self._forPhase = _forPhase
        self._task = _task
        self._shot = _shot
        self._currentState = 0
        
        self.buttonOrder = [self._notStarted,self._inProgress,self._done]
        
        self.setAlignment(QtCore.Qt.AlignHCenter)
        
        #self.resize(25, 25)
        #self.setPixmap(QtGui.QPixmap(self.buttonOrder[self._currentState]))
        self.connect(self, QtCore.SIGNAL('clicked()'), self.clicked)
        
        #connect task update from DB to update status
        
        if self._task is not None:
            self._task.taskChanged.connect(self.getTaskState)        
            self.getTaskState()
        else:
            if self._shot._tasks is not None:
                for t in self._shot._tasks:
                    if t._idphases == self._forPhase:
                        self._task = t
                        self.getTaskState()
                        self._task.taskChanged.connect(self.getTaskState)
                
        if self._task is None:  
            self.setText("loading")
        
    def mouseReleaseEvent(self, ev):
        if ev.button() == QtCore.Qt.RightButton and self._task is not None:
            self.emit(QtCore.SIGNAL('clicked()'))
            
        
    def clicked(self):
        if (self._currentState == len(self.buttonOrder)-1):
            self._currentState = 0
        else:
            self._currentState += 1
        
        self.updateState()        
        
    def updateState(self):
        self._task.setStatus(self._currentState)
        self.updateImage()
        
    def updateImage(self):
        self.setPixmap(QtGui.QPixmap(self.buttonOrder[self._currentState]))
    
    
    def getTaskState(self):
        self._currentState = self._task._status
        self.updateImage()
    