import sys

from PyQt4 import Qt
from PyQt4.QtCore import QDate
from PyQt4 import QtGui, QtCore

import sharedDB
#import projexui.pyi_hook

from DPSPipeline.calendarview import CalendarView
from DPSPipeline.widgets.loginwidget import loginwidget
from DPSPipeline.widgets.createprojectwidget import createprojectwidget
from DPSPipeline.widgets.projectviewwidget import projectviewwidget

import DPSPipeline.createprojecttest

class MainWindow(QtGui.QMainWindow):
    
    def __init__( self):
        QtGui.QMainWindow.__init__(self)
        
        self.setWindowTitle("Sludge v"+str(sharedDB.version))
    
        sharedDB.mainWindow = self
        #We instantiate a QApplication passing the arguments of the script to it:
        self.app = sharedDB.app

        if not sharedDB.noDB:
            try:
                self.app.loginWidget
            except:
                self.app.loginWidget = loginwidget.LoginWidget()
                
            self.app.loginWidget.show()
            self.app.loginWidget.activateWindow()
        else:
            sharedDB.users.currentUser = sharedDB.users.GetCurrentUser('twotis')
            self.EnableMainWindow()
    
    def EnableMainWindow(self):
        #self.mw = QtGui.QMainWindow() # mw = MainWindow

        menubar = QtGui.QMenuBar()
	#menubar.sizeHint(QSize.setHeight(10))
	
	fileMenu = menubar.addMenu('&File')
	
	
	fileMenu.addSeparator()
	fileMenu.addAction('Save')
	fileMenu.addSeparator()
	fileMenu.addAction('Exit')
	fileMenu.triggered.connect( self.fileMenuActions )
        
        projectMenu = menubar.addMenu('&Project')
        projectMenu.addAction('Create Project')
        projectMenu.triggered.connect( self.projectMenuActions )
        
        '''userMenu = menubar.addMenu('&Users')
        #userMenu.addAction('Create User')
        userMenu.addAction('Assignment Window')
        userMenu.triggered.connect( self.userMenuActions )
        '''
        self.setMenuBar(menubar)
        self.setCentralWidget(None)
        self.showMaximized()
            
        sharedDB.calendarview = CalendarView()
    
        self.CreateProjectWidget()        
        
    def CreateProjectWidget(self):

        dockWidget1 = QtGui.QDockWidget(sharedDB.mainWindow)
        self._CreateProjectWidget = createprojectwidget.CreateProjectWidget()
        dockWidget1.setWindowTitle("Create Project")
        dockWidget1.setWidget(self._CreateProjectWidget)
        sharedDB.mainWindow.addDockWidget(QtCore.Qt.RightDockWidgetArea, dockWidget1)
        
        dockWidget2 = QtGui.QDockWidget(sharedDB.mainWindow)
        self._ProjectViewWidget = projectviewwidget.ProjectViewWidget()
        dockWidget2.setWindowTitle("ProjectView")
        dockWidget2.setWidget(self._ProjectViewWidget)
        sharedDB.mainWindow.addDockWidget(QtCore.Qt.RightDockWidgetArea, dockWidget2)
        
        sharedDB.mainWindow.setTabPosition(QtCore.Qt.LeftDockWidgetArea,4)
        sharedDB.mainWindow.tabifyDockWidget(sharedDB.leftWidget,dockWidget2)
        
        
    def fileMenuActions( self, action ):
	"""
	Handles file menu actions
	
	:param      action | <QAction>
	"""
	if ( action.text() == 'Save' ):
	    sharedDB.calendarview._myXGanttWidget.SaveToDatabase()
	elif (action.text() == 'Exit'):
            self.app.closeAllWindows()
            
    def projectMenuActions( self, action ):
	"""
	Handles file menu actions
	
	:param      action | <QAction>
	"""
	if ( action.text() == 'Create Project' ):            
	    self.CreateProjectWidget()
    
def main():
    app = QtGui.QApplication(sys.argv)
    sharedDB.app = app
    win = MainWindow()
    #sharedDB.mainWindow.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()