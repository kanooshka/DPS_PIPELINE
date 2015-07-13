import sys
from PyQt4 import Qt
from PyQt4.QtCore import QDate
from PyQt4 import QtGui, QtCore
import traceback

import sharedDB
from datetime import datetime
#import projexui.pyi_hook

from DPSPipeline.calendarview import CalendarView
from DPSPipeline.widgets.loginwidget import loginwidget
from DPSPipeline.widgets.createprojectwidget import createprojectwidget
from DPSPipeline.widgets.projectviewwidget import projectviewwidget

#import DPSPipeline.createprojecttest

class MainWindow(QtGui.QMainWindow):
    
    def __init__( self):
        QtGui.QMainWindow.__init__(self)
        
        self.setWindowTitle("Sludge v"+sharedDB.myVersion._name)
        self._fileMenu = ''
        
        sharedDB.mainWindow = self
        #We instantiate a QApplication passing the arguments of the script to it:
        self.app = sharedDB.app

        #sharedDB.lastUpdate = datetime.now()

        if not sharedDB.noDB:
            try:
                self.app.loginWidget
            except:
                self.app.loginWidget = loginwidget.LoginWidget()
                
            self.app.loginWidget.show()
            self.app.loginWidget.activateWindow()
        else:
            sharedDB.users.currentUser = sharedDB.users.GetCurrentUser('twotis')
            sharedDB.myStatuses = sharedDB.statuses.GetStatuses()
            sharedDB.myPhases = sharedDB.phases.GetPhaseNames()
            sharedDB.myProjects = sharedDB.projects.GetActiveProjects()
            self.EnableMainWindow()
	    sharedDB.mySQLConnection.closeConnection()
    
    def EnableMainWindow(self):
        #self.mw = QtGui.QMainWindow() # mw = MainWindow

        menubar = QtGui.QMenuBar()
	#menubar.sizeHint(QSize.setHeight(10))
	
	self._fileMenu = menubar.addMenu('&File')
	
	
	self._fileMenu.addSeparator()
	autosaveAction = self._fileMenu.addAction('Autosave Enabled')
        autosaveAction.setEnabled(0)
        self._fileMenu.addAction('Save')
        
	self._fileMenu.addSeparator()
	self._fileMenu.addAction('Exit')
	self._fileMenu.triggered.connect( self.fileMenuActions )
        
        
        projectMenu = menubar.addMenu('&Project')
        createProjectMenuItem = projectMenu.addAction('Create Project')
        projectMenu.triggered.connect( self.projectMenuActions )
        
        if sharedDB.currentUser[0]._idPrivileges > 1:
            createProjectMenuItem.setEnabled(0)
            
        '''userMenu = menubar.addMenu('&Users')
        #userMenu.addAction('Create User')
        userMenu.addAction('Assignment Window')
        userMenu.triggered.connect( self.userMenuActions )
        '''
        self.setMenuBar(menubar)
        self.setCentralWidget(None)   
        self.resize(1280,720)
        self.show()
        #self.showMaximized()
            
        sharedDB.calendarview = CalendarView()
        sharedDB.mainWindow.setTabPosition(QtCore.Qt.LeftDockWidgetArea,4)
        sharedDB.mainWindow.setTabPosition(QtCore.Qt.RightDockWidgetArea,2)
        #self.CreateProjectWidget()
	self.CreateProjectViewWidget()
        #sharedDB.mySQLConnection.SaveToDatabase()
        
    def CreateProjectWidget(self):
	
        dockWidget1 = QtGui.QDockWidget(sharedDB.mainWindow)
        self._CreateProjectWidget = createprojectwidget.CreateProjectWidget()
        dockWidget1.setWindowTitle("Create Project")
        dockWidget1.setWidget(self._CreateProjectWidget)
        sharedDB.mainWindow.addDockWidget(QtCore.Qt.RightDockWidgetArea, dockWidget1)
        dockWidget1.setFloating(1)
        #sharedDB.mainWindow.setTabPosition(QtCore.Qt.LeftDockWidgetArea,4)
        #sharedDB.mainWindow.tabifyDockWidget(sharedDB.leftWidget,dockWidget2)
    
    def CreateProjectViewWidget(self):
	
        dockWidget = QtGui.QDockWidget(sharedDB.mainWindow)
        self._ProjectViewWidget = projectviewwidget.ProjectViewWidget()
        dockWidget.setWindowTitle("ProjectView")
        dockWidget.setWidget(self._ProjectViewWidget)
        sharedDB.mainWindow.addDockWidget(QtCore.Qt.LeftDockWidgetArea, dockWidget)
        sharedDB.mainWindow.tabifyDockWidget(sharedDB.leftWidget,dockWidget)
        dockWidget.show()
        dockWidget.raise_()
    def fileMenuActions( self, action ):
	"""
	Handles file menu actions
	
	:param      action | <QAction>
	"""
	#if ( action.text() == 'Save' ):
	    #sharedDB.calendarview._myXGanttWidget.SaveToDatabase()
	if (action.text() == 'Exit'):
            self.app.closeAllWindows()
            
    def projectMenuActions( self, action ):
	"""
	Handles file menu actions
	
	:param      action | <QAction>
	"""
	if ( action.text() == 'Create Project' ):            
	    self.CreateProjectWidget()

def my_excepthook(type , value, tback):
    # Custom exception handling here
    errorMessage = QtGui.QMessageBox()
    errorMessage.setWindowTitle("ERROR!")
    traceString = ''
    trac = traceback.extract_tb(tback)
    trac = traceback.format_list(trac)
    for t in trac:
        traceString = t+"\n"
    #traceback.print_tb(tback)
    errorMessage.setText("An Error has Occurred, please contact support: \nTraceback: "+traceString+"\nValue: "+str(value))
    errorMessage.exec_()
    
    # then call the default handler
    sys.__excepthook__(type, value, tback)
    
def main():
        #sys.excepthook = my_excepthook    
        app = QtGui.QApplication(sys.argv)
        sharedDB.app = app
        
        win = MainWindow()
        
        #sharedDB.mainWindow.show()
        sys.exit(app.exec_())
    

if __name__ == "__main__":
    main()
    