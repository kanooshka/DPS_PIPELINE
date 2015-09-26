from PyQt4.QtCore    import QObject
from PyQt4           import QtCore

class Selection(QObject):
    selectionChangedSignal = QtCore.pyqtSignal()
    
    def __init__(self):
        super(Selection, self).__init__()
        
        self.items = []
        
    def select(self, item):
        self.items.append(item)
        self.selectionChangedSignal.emit()
    