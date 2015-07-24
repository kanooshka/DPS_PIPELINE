from PyQt4 import QtGui, QtCore
import sharedDB
from PyQt4.QtCore import pyqtSlot,SIGNAL,SLOT
import projexui

class ClickableImageQLabel(QtGui.QLabel):
    clicked = QtCore.pyqtSignal()
    
    def __init__(self, parent = None):
        super(ClickableImageQLabel, self).__init__( parent)
        
        self.setMinimumSize(213,120)
        #self.setMaximumSize(213,120)
        
        self._noImage = projexui.resources.find('img/DP/noImage.png')
        self._image = QtGui.QPixmap(self._noImage) 
        self._parent = parent
        
    def mousePressEvent (self, event):
        self.clicked.emit()
    
    def resizeEvent (self, event):
        w = self._parent.shotImageWidget.width()
        h = self._parent.shotImageWidget.height()
        self.setPixmap(self._image.scaled(w,h,QtCore.Qt.KeepAspectRatio))
        
    def assignImage(self, image=None):
        if image is not None:
            self._image = QtGui.QPixmap(image)
        else:
            self._image = QtGui.QPixmap(self._noImage)
            
        self.setPixmap(self._image)
    