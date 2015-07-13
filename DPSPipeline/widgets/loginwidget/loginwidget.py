import sys
import sharedDB
import projexui
from DPSPipeline.database.connection import Connection

from PyQt4 import QtGui,QtCore
from PyQt4.QtGui    import QWidget
from PyQt4.QtCore   import QDate,QTime
from DPSPipeline.database import projects
'''
class InitialLoadThread(QtCore.QThread):

    def run(self):
	#print sharedDB.mySQLConnection._user
	#sharedDB.mySQLConnection.testConnection()
	#sharedDB.mySQLConnection.UpdateDatabaseClasses()
	#sharedDB.calendarview.InitialProjectAdd()
'''	
class LoginWidget(QWidget):
   
    def __init__( self, parent = None ):
        
        super(LoginWidget, self).__init__( parent )
	
        # load the user interface# load the user interface
        if getattr(sys, 'frozen', None):
	    #print (sys._MEIPASS+"/ui/createprojectwidget.ui");
	    projexui.loadUi(sys._MEIPASS, self, uifile = (sys._MEIPASS+"/ui/loginwidget.ui"))
	    
	else:
	    projexui.loadUi(__file__, self)
        
        # define custom properties
        
        self._backend               = None
       # self._InitialLoadThread = InitialLoadThread()
	
        #connects buttons
        self.loginButton.clicked.connect(self.Login)
	self.user.returnPressed.connect(self.Login)
	self.password.returnPressed.connect(self.Login)
	
	if (sharedDB.autologin):
	    self.user.setText("dkonieczka")
	    self.password.setText("doodle")
	    self.Login()
	    self.close()
	
    def Login(self):        
        #print "Logging In"	
	sharedDB.mySQLConnection = Connection(_user = str(self.user.text()), _password = str(self.password.text()))
	
	if (self.remoteAccess.isChecked() or sharedDB.remote):
	    sharedDB.mySQLConnection.setHost("remote")
	else:
	    sharedDB.mySQLConnection.setHost("local")	
	
	if sharedDB.mySQLConnection.testConnection():
	    sharedDB.currentUser = sharedDB.users.GetCurrentUser(str(self.user.text()))
	    sharedDB.mySQLConnection.UpdateDatabaseClasses()
	    sharedDB.mySQLConnection.SaveToDatabase()
	    #self._InitialLoadThread.finished.connect(sharedDB.mySQLConnection.SaveToDatabase)
	    #self._InitialLoadThread.start()	    
	    self.close()
	    sharedDB.mainWindow.EnableMainWindow()
	else:
	    message = QtGui.QMessageBox.question(self, 'Message',
            "Incorrect Username or Password", QtGui.QMessageBox.Ok)