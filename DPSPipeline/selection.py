from PyQt4.QtCore    import QObject
from PyQt4           import QtCore

class Selection(QObject):
    selectionChangedSignal = QtCore.pyqtSignal()
    
    def __init__(self):
        super(Selection, self).__init__()
        
        self.items = []
        
    def select(self, items):
        for item in self.items:
            if hasattr(item, "deselect"):
                item.deselect()       
        
        self.items = []
        #self.items.append(items)
        self.items = items
        
        for item in self.items:
            if hasattr(item, "select"):
                item.select()
        
        self.selectionChangedSignal.emit()
    