#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
from PyQt4 import QtGui, QtCore


class Button(QtGui.QPushButton):
    
    def mouseMoveEvent(self, e):
        if e.buttons() != QtCore.Qt.LeftButton:
            return

        # write the relative cursor position to mime data
        mimeData = QtCore.QMimeData()
        # simple string with 'x,y'
        userName = 'Dan Konieczka'
        mimeData.setText('%s,%d,%d' % (userName,e.x(), e.y()))

        # let's make it fancy. we'll show a "ghost" of the button as we drag
        # grab the button to a pixmap
        pixmap = QtGui.QPixmap.grabWidget(self)

        # below makes the pixmap half transparent
        painter = QtGui.QPainter(pixmap)
        painter.setCompositionMode(painter.CompositionMode_DestinationIn)
        painter.fillRect(pixmap.rect(), QtGui.QColor(0, 0, 0, 127))
        painter.end()

        # make a QDrag
        drag = QtGui.QDrag(self)
        # put our MimeData
        drag.setMimeData(mimeData)
        # set its Pixmap
        drag.setPixmap(pixmap)
        # shift the Pixmap so that it coincides with the cursor position
        drag.setHotSpot(e.pos())

        # start the drag operation
        # exec_ will return the accepted action from dropEvent
        if drag.exec_(QtCore.Qt.CopyAction | QtCore.Qt.MoveAction) == QtCore.Qt.MoveAction:
            print 'moved'
        else:
            print 'copied'


    def mousePressEvent(self, e):
        QtGui.QPushButton.mousePressEvent(self, e)
        if e.button() == QtCore.Qt.LeftButton:
            print 'press'
        #super(Button, self).mousePressEvent(e)

class MainWindow(QtGui.QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.initUI()


    def initUI(self):
        #self.setAcceptDrops(True)

        self.setWindowTitle('MainWindow')
        self.setGeometry(300, 300, 280, 150)


class DragFrom(QtGui.QWidget):
    def __init__(self):
        super(DragFrom, self).__init__()
        self.initUI()


    def initUI(self):
        #self.setAcceptDrops(True)

        button = Button('Button', self)
        button.move(100, 65)

        self.buttons = [button]

        self.setWindowTitle('Copy or Move')
        self.setGeometry(300, 300, 280, 150)


    def dragEnterEvent(self, e):
        e.accept()

class DragTo(QtGui.QWidget):
    def __init__(self):
        super(DragTo, self).__init__()
        self.initUI()


    def initUI(self):
        self.setAcceptDrops(True)

        self.setWindowTitle('Drop Here')
        self.setGeometry(600, 300, 280, 150)


    def dragEnterEvent(self, e):
        e.accept()


    def dropEvent(self, e):
        # get the relative position from the mime data
        source = e.source()
        print e.source()
        print self
        if e.source() != e.target():
            mime = e.mimeData().text()
            splitMime = mime.split(',')
            name = splitMime[0]
            x = int(splitMime[1])
            y = int(splitMime[2])
            
            #if e.keyboardModifiers() & QtCore.Qt.ShiftModifier:
            # copy
            # so create a new button
            button = Button(name, self)
            # move it to the position adjusted with the cursor position at drag
            button.move(e.pos()-QtCore.QPoint(x, y))
            # show it
            button.show()
            # store it
            #self.buttons.append(button)
            # set the drop action as Copy
            #e.setDropAction(QtCore.Qt.CopyAction)
    
            # tell the QDrag we accepted it
    
            e.accept()

if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    
    mw = QtGui.QMainWindow() # mw = MainWindow
    mw.setCentralWidget(None)
    mw.showMaximized()
    
    #mw.dockWidgets.add(QtGui.QDockWidget(mw))
    
    mw.dockWdg1 = QtGui.QDockWidget(mw)
    mw.dockWidgets = [mw.dockWdg1]
    mw.dockWidgets[0].setWidget(DragFrom())
    mw.addDockWidget(QtCore.Qt.DockWidgetArea(1), mw.dockWidgets[0])
    
    mw.dockWidgets.append(QtGui.QDockWidget(mw))
    mw.dockWidgets[1].setWidget(DragTo())
    mw.addDockWidget(QtCore.Qt.DockWidgetArea(2), mw.dockWidgets[1])
    app.exec_()  