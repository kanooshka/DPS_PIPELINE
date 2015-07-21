from PyQt4 import QtGui, QtCore
import sharedDB
from PyQt4.QtCore import pyqtSlot,SIGNAL,SLOT

class ProjectNameLineEdit(QtGui.QLineEdit):
   
    def __init__(self, parent = None):
        super(ProjectNameLineEdit, self).__init__( parent)
        self._projectviewwidget = parent
        
        self.setText("Right Click To Select Project...")
    
    def contextMenuEvent(self, ev):
        menu	 = QtGui.QMenu()
           
        #iterate through clients
        for i in xrange(0, len(sharedDB.myClients)):
            exec("client_menu%d = QtGui.QMenu(sharedDB.myClients[i]._name)" % (i + 1))
            exec("menu.addMenu(client_menu%d)" % (i + 1))
            #Iterate through Client's IPs
            for j in xrange(0, len(sharedDB.myClients[i]._ips)):
                exec("ip%d_%d = QtGui.QMenu(sharedDB.myClients[i]._ips[j]._name)" % (i + 1,j + 1))
                exec("client_menu%d.addMenu(ip%d_%d)" % (i + 1,i+1,j+1))
                #Iterate through projects in IP
                for k in xrange(0, len(sharedDB.myClients[i]._ips[j]._projects)):
                    #exec("action%d_%d_%d = QtGui.QAction(sharedDB.myClients[i]._ips[j]._projects[k]._name, self)" % (i + 1, j + 1, k + 1))
                    #exec("action%d_%d_%d.triggered[()].connect(lambda item=sharedDB.myClients[i]._ips[j]._projects[k]._idprojects: self.SelectShot(item))" %(i + 1,j + 1,k+1))
                    #exec("ip%d_%d.addAction(action%d_%d_%d)" % (i + 1,j + 1,i + 1,j + 1,k + 1))
                    #exec("self.connect(action%d_%d_%d,SIGNAL(\"triggered(QtGui.QAction)\"),self,SLOT(\"SelectShot(QtGui.QAction)\"))" % (i + 1, j + 1, k + 1))
                    
                    exec("ip%d_%d.addAction(%s)" % (i + 1,j + 1,repr(sharedDB.myClients[i]._ips[j]._projects[k]._name)))
                    exec("ip%d_%d.triggered.connect(self._projectviewwidget.LoadProjectValues)" % (i + 1,j + 1))
                
        menu.exec_(ev.globalPos())
        
    '''def SelectShot(self, action):
        #iterate through projects
        for proj in sharedDB.myProjects:
            if proj._name == str(action.text()):
                print proj._name
                #set projectview

        
        
    def contexohtMenuEvent(self, ev):
        menu	 = QtGui.QMenu()
           
        action1 = QtGui.QAction('&Add Sequence', self)
        action1.triggered[()].connect(
            lambda item="Not working yet": self.AddShot(item))
        menu.addAction(action1)
       
        #action2 = menu.addAction("Set Size 500x500") 
        
        #self.connect(action1,SIGNAL("triggered()"),sharedDB.myProjectViewWidget,SLOT("AddShot()"))
        self.connect(action1,SIGNAL("triggered(QtGui.QAction)"),self,SLOT("AddShot(QtGui.QAction)"))
        
        #self.connect(action2,SIGNAL("triggered()"),self,SLOT("slotShow500x500()"))
        menu.exec_(self.mapToGlobal(point))
        '''
        