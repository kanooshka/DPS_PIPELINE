from PyQt4 import QtGui, QtCore
import sharedDB
from PyQt4.QtCore import pyqtSlot,SIGNAL,SLOT
import operator

class ClientIPLineEdit(QtGui.QLineEdit):
   
    def __init__(self, parent = None):
        super(ClientIPLineEdit, self).__init__( parent)
        self._projectviewwidget = parent
        
        self.setText("Right Click To Select...")
        self.setReadOnly(True)
        self.showAllEnabled = 0
        self._project = None
    
    def contextMenuEvent(self, ev):
        
        activeIps = []
        activeClients = []

        for proj in sharedDB.myProjects:
            if not proj._hidden or self.showAllEnabled:
                if proj._idclients not in activeClients or self.showAllEnabled:
                    activeClients.append(proj._idclients)
                if proj._idips not in activeIps or self.showAllEnabled:
                    activeIps.append(proj._idips)
        
        menu	 = QtGui.QMenu()
        
        
           
           
        showAllAction = menu.addAction('Show Inactive Projects')
        showAllAction.setCheckable(True)
        showAllAction.setChecked(self.showAllEnabled)
        showAllAction.triggered.connect(self.toggleShowAllAction)       
           
        menu.addSeparator()
           
        #iterate through clients
        cli = sharedDB.myClients
        cli.sort(key=operator.attrgetter('_name'),reverse=False)
        for i in xrange(0, len(cli)):
            if cli[i]._idclients in activeClients:
                exec("client_menu%d = QtGui.QMenu(cli[i]._name)" % (i + 1))
                exec("menu.addMenu(client_menu%d)" % (i + 1))
                #Iterate through Client's IPs
                if len(cli[i]._ips):
                    ips = cli[i]._ips
                    ips.sort(key=operator.attrgetter('_name'),reverse=False)
                    for j in xrange(0, len(ips)):
                        if ips[j]._idips in activeIps:
                            exec("ip%d_%d = QtGui.QMenu(ips[j]._name)" % (i + 1,j + 1))
                            exec("client_menu%d.addMenu(ip%d_%d)" % (i + 1,i+1,j+1))
                            #Iterate through projects in IP
                            if len(ips[j]._projects):
                                projs = ips[j]._projects
                                projs.sort(key=operator.attrgetter('_name'),reverse=False)
                                for k in xrange(0, len(projs)):
                                    #exec("action%d_%d_%d = QtGui.QAction(sharedDB.myClients[i]._ips[j]._projects[k]._name, self)" % (i + 1, j + 1, k + 1))
                                    #exec("action%d_%d_%d.triggered[()].connect(lambda item=sharedDB.myClients[i]._ips[j]._projects[k]._idprojects: self.SelectShot(item))" %(i + 1,j + 1,k+1))
                                    #exec("ip%d_%d.addAction(action%d_%d_%d)" % (i + 1,j + 1,i + 1,j + 1,k + 1))
                                    #exec("self.connect(action%d_%d_%d,SIGNAL(\"triggered(QtGui.QAction)\"),self,SLOT(\"SelectShot(QtGui.QAction)\"))" % (i + 1, j + 1, k + 1))
                                    if not projs[k]._hidden or self.showAllEnabled:
                                        exec("ip%d_%d.addAction(%s)" % (i + 1,j + 1,repr(projs[k]._name)))
                                        exec("ip%d_%d.triggered.connect(self.ChangeProject)" % (i + 1,j + 1))
                
        menu.exec_(ev.globalPos())
    
    def ChangeProject(self, projname):
        for proj in sharedDB.myProjects:
            if str(proj._name) == str(projname.text()):
                self._projectviewwidget._currentProject = proj
                break
            
        self._projectviewwidget.LoadProjectValues()
        
    
      
    def toggleShowAllAction(self):
        self.showAllEnabled = not self.showAllEnabled

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
        