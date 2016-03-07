import sys
from PyQt4 import Qt
from PyQt4.QtCore import QDate
from PyQt4 import QtGui, QtCore
import traceback
import sharedDB
from datetime import datetime

import projexui

from DPSPipeline.widgets.calendarviewwidget import calendarviewwidget
from DPSPipeline.widgets.loginwidget import loginwidget
from DPSPipeline.widgets.createprojectwidget import createprojectwidget
from DPSPipeline.widgets.projectviewwidget import projectviewwidget
from DPSPipeline.widgets.mytaskswidget import mytaskswidget
from DPSPipeline.widgets.attributeeditorwidget import attributeeditorwidget
from DPSPipeline.widgets.hourswidget import hourswidget
from DPSPipeline.widgets.weeklieswidget import weeklieswidget

#import DPSPipeline.createprojecttest

class MainWindow(QtGui.QMainWindow):
    
    def __init__( self):
        #QtGui.QMainWindow.__init__(self)

	super(MainWindow, self).__init__( )

        self.setWindowTitle("Sludge v"+sharedDB.myVersion._name)
        self._fileMenu = ''
        
	self.centralTabbedWidget = QtGui.QTabWidget()
	self.setCentralWidget(self.centralTabbedWidget)
	
        sharedDB.mainWindow = self
        #We instantiate a QApplication passing the arguments of the script to it:
        self.app = sharedDB.app

        try:
            self.app.loginWidget
        except:
            self.app.loginWidget = loginwidget.LoginWidget()
        
	if not sharedDB.autologin:    
	    self.app.loginWidget.show()
	    self.app.loginWidget.activateWindow()
	
	
	
    def EnableMainWindow(self):

        menubar = QtGui.QMenuBar()
	
	self._fileMenu = menubar.addMenu('&File')
	
	
	
	self._fileMenu.addSeparator()
	'''
	autosaveAction = self._fileMenu.addAction('Autosave Enabled')
        autosaveAction.setEnabled(0)
        self._fileMenu.addAction('Save')
        
	self._fileMenu.addSeparator()
	'''
	self._fileMenu.addAction('Exit')
	self._fileMenu.triggered.connect( self.fileMenuActions )
        
        
        projectMenu = menubar.addMenu('&Project')
        self.createProjectMenuItem = projectMenu.addAction('Create Project')
        projectMenu.triggered.connect( self.projectMenuActions )
        
        if sharedDB.currentUser._idPrivileges > 1:
            self.createProjectMenuItem.setEnabled(0)
	
	#self._userMenu = menubar.addMenu('&Users')
	
	windowMenu = menubar.addMenu('&Windows')
	#self._windowMenuMenuItem = windowMenu.addAction('Weeklies')
	windowMenu.addAction('Assignments')
	windowMenu.addAction('Attribute Editor')
	windowMenu.addAction('Weeklies')	
        windowMenu.triggered.connect( self.windowMenuActions )
	
        self.setMenuBar(menubar)
          
        self.resize(1280,720)
        self.show()
            
        #sharedDB.calendarview = CalendarView()
        #sharedDB.mainWindow.setTabPosition(QtCore.Qt.LeftDockWidgetArea,4)
        sharedDB.mainWindow.setTabPosition(QtCore.Qt.RightDockWidgetArea,2)
	self.CreateProjectViewWidget()
	self.CreateCalendarWidget()	
        self.CreateMyTasksWidget()
	self.CreateAttributeEditorWidget()
	self.CreateHoursWidget()

    def CreateProjectWidget(self):
	
	if not hasattr(sharedDB, 'myCreateProjectWidget'):
	    sharedDB.myCreateProjectWidget = createprojectwidget.CreateProjectWidget(sharedDB.mainWindow)
		
	sharedDB.myCreateProjectWidget.setDefaults()
	sharedDB.myCreateProjectWidget.dockWidget.show()

    def CreateProjectViewWidget(self):
	
        self._ProjectViewWidget = projectviewwidget.ProjectViewWidget()
	self.centralTabbedWidget.addTab(self._ProjectViewWidget, "Project View")
	
    def CreateCalendarWidget(self):	
        self._CalendarWidget = calendarviewwidget.CalendarViewWidget()	
	self.centralTabbedWidget.addTab(self._CalendarWidget, "Calendar View")
    
    def CreateHoursWidget(self):
	
        self._HoursWidget = hourswidget.HoursWidget()
	self.centralTabbedWidget.addTab(self._HoursWidget, "Hours View")
    
    def CreateAttributeEditorWidget(self):
        if not hasattr(sharedDB, 'myAttributeEditorWidget'):
	    sharedDB.myAttributeEditorWidget = attributeeditorwidget.AttributeEditorWidget(sharedDB.mainWindow)
		
	#sharedDB.myAttributeEditorWidget.setDefaults()
	sharedDB.myAttributeEditorWidget.dockWidget.show()

    def CreateMyTasksWidget(self):	
        if not hasattr(sharedDB, 'myAssignmentsWidget'):
	    sharedDB.myAssignmentsWidget = mytaskswidget.MyTasksWidget(sharedDB.mainWindow)
		
	#sharedDB.myAttributeEditorWidget.setDefaults()
	sharedDB.myAssignmentsWidget.dockWidget.setMinimumWidth(195);
	sharedDB.myAssignmentsWidget.dockWidget.setMaximumWidth(195);
	sharedDB.myAssignmentsWidget.dockWidget.show()
	sharedDB.myAssignmentsWidget.dockWidget.setMaximumWidth(9999999);

    def fileMenuActions( self, action ):
	"""
	Handles file menu actions
	
	:param      action | <QAction>
	"""
	if (action.text() == 'Exit'):
            self.app.closeAllWindows()
	    
    def windowMenuActions( self, action ):
	"""
	Handles window menu actions
	
	:param      action | <QAction>
	"""
	if (action.text() == 'Weeklies'):
            if not hasattr(sharedDB, 'myWeekliesWidget'):
		sharedDB.myWeekliesWidget = weeklieswidget.WeekliesWidget(sharedDB.mainWindow)
		
	    sharedDB.myWeekliesWidget.CalculateWeeklies()
	    sharedDB.myWeekliesWidget.dockWidget.show()
	if (action.text() == 'Assignments'):		
	    sharedDB.myAssignmentsWidget.dockWidget.show()
	if (action.text() == 'Attribute Editor'):		
	    sharedDB.myAttributeEditorWidget.dockWidget.show()
            
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
    
    if errorMessage.Ok:
	sharedDB.app.quit()
	
    
    # then call the default handler
    #sys.__excepthook__(type, value, tback)
    
def main():
        if not sharedDB.debugging:
            sys.excepthook = my_excepthook    
        app = QtGui.QApplication(sys.argv)
        path = projexui.resources.find('img/DP/pipe.gif')
        app.setWindowIcon(QtGui.QIcon(path))
        sharedDB.app = app
        '''
	stylesheet = projexui.resources.find('styles/DarkOrange.stylesheet')
	qfile = QtCore.QFile(stylesheet)
	qfile.open(QtCore.QFile.ReadOnly);
	StyleSheet = QtCore.QLatin1String(qfile.readAll());
	
	app.setStyleSheet(StyleSheet)'''
	
        win = MainWindow()
        
        #sharedDB.mainWindow.show()
        sys.exit(app.exec_())
    

if __name__ == "__main__":
    main()
    