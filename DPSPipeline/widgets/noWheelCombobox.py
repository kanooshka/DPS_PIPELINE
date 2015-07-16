from PyQt4 import QtCore,QtGui

class NoWheelComboBox(QtGui.QComboBox):

    def __init__(self):
        super(QtGui.QComboBox, self).__init__()

    def wheelEvent(self, event):
        pass
    