import sharedDB
from PyQt4 import QtGui,QtCore
from PyQt4.QtGui    import QWidget,QDockWidget,QTextEdit
import operator
import datetime
from datetime import timedelta, date

class WeekliesWidget(QWidget):
   
    def __init__( self, parent = None ):
        
        super(WeekliesWidget, self).__init__( parent )
        
        self.dockWidget = QDockWidget()
        parent.addDockWidget(QtCore.Qt.RightDockWidgetArea,self.dockWidget)
        self.dockWidget.setFloating(1)
        self.dockWidget.setWindowTitle("Weeklies")
        self.dockWidget.setWidget(self)
        
        mainlay = QtGui.QVBoxLayout()
        self.setLayout(mainlay)
        topLayout = QtGui.QHBoxLayout()
        mainlay.addLayout(topLayout)
        
        self.dateEdit = QtGui.QDateEdit(date.today())
        self.dateEdit.setCalendarPopup(True)
        #self.dateEdit.dateChanged.connect(self.CalculateWeeklies)
        self.dateEdit.dateChanged.connect(self.PopulateTable)
        topLayout.addWidget(self.dateEdit)
        
        self.userDropdown = QtGui.QComboBox()       
        self.userDropdown.currentIndexChanged.connect(self.PopulateTable)
        topLayout.addWidget(self.userDropdown)
        
        '''
        self.textBox = QtGui.QTextEdit()
        self.textDocument = QtGui.QTextDocument()
        self.textBox.setDocument(self.textDocument)        
        '''
        
        self.buttonPrint = QtGui.QPushButton('Print', self)
        self.buttonPrint.clicked.connect(self.handlePrint)
        self.buttonPreview = QtGui.QPushButton('Preview', self)
        self.buttonPreview.clicked.connect(self.handlePreview)
        topLayout.addWidget(self.buttonPrint)
        topLayout.addWidget(self.buttonPreview,1)
        
        self.table = QtGui.QTableWidget()
        self.table.setColumnCount(6)
        self.table.verticalHeader().setVisible(False)
        mainlay.addWidget(self.table)
        '''
        for i,row in enumerate(cur):
            self.table.insertRow(self.table.rowCount())
            for j,val in enumerate(row):
                self.table.setItem(i, j, QtGui.QTableWidgetItem(str(val)))
        '''
        
        self.PopulateUsers()
        #self.PopulateTable()
        
        #mainlay.addWidget(self.textBox)   
        
        #sharedDB.mySQLConnection.newPhaseAssignmentSignal.connect(self.CalculateWeeklies)        
    
    def PopulateUsers(self):
        #for user in user list
        userList = []
        
        for user in sharedDB.myUsers.values():
            if user.isActive() == 1:
                userList.extend(user.name())        
                self.userDropdown.addItem(user.name(),user.idUsers())

        self.userDropdown.model().sort(0)
    
    def handlePrint(self):
        dialog = QtGui.QPrintDialog()
        if dialog.exec_() == QtGui.QDialog.Accepted:
            self.handlePaintRequest(dialog.printer())
        
    def handlePreview(self):
        dialog = QtGui.QPrintPreviewDialog()
        dialog.paintRequested.connect(self.handlePaintRequest)
        dialog.exec_()    
    
    def handlePaintRequest(self, printer):
        document = self.makeTableDocument()
        document.print_(printer)
    
    def makeTableDocument(self):
        document = QtGui.QTextDocument()
        cursor = QtGui.QTextCursor(document)
        rows = self.table.rowCount()
        columns = self.table.columnCount()
        table = cursor.insertTable(rows + 1, columns)
        format = table.format()
        format.setHeaderRowCount(1)
        table.setFormat(format)
        format = cursor.blockCharFormat()
        format.setFontWeight(QtGui.QFont.Bold)
        for column in range(columns):
            cursor.setCharFormat(format)
            cursor.insertText(
                self.table.horizontalHeaderItem(column).text())
            cursor.movePosition(QtGui.QTextCursor.NextCell)
        for row in range(rows):
            for column in range(columns):
                if self.table.item(row, column) is not None:
                    cursor.insertText(self.table.item(row, column).text())
                cursor.movePosition(QtGui.QTextCursor.NextCell)
        return document
    
    def PopulateTable(self):
        day = self.dateEdit.date().toPyDate()
        
        mon = day - timedelta(days=day.weekday())
        
        self.table.setRowCount(0)
        self.table.setWordWrap(1)
        
        
        dates = [mon,mon + timedelta(days=1),mon + timedelta(days=2),mon + timedelta(days=3),mon + timedelta(days=4)]
        self.table.setHorizontalHeaderLabels(("","Mon "+mon.strftime("%m/%d/%y"),"Tues "+(mon + timedelta(days=1)).strftime("%m/%d/%y"),"Wed "+(mon + timedelta(days=2)).strftime("%m/%d/%y"),"Thurs "+(mon + timedelta(days=3)).strftime("%m/%d/%y"),"Fri "+(mon + timedelta(days=4)).strftime("%m/%d/%y")))
    
        self.table.insertRow(0)
    
        #find user then set name column
        currentUser = sharedDB.myUsers[str(self.userDropdown.itemData(self.userDropdown.currentIndex()).toString())]
        self.table.setItem(0,0,QtGui.QTableWidgetItem(str(currentUser.name())))
        
        #d+1 is column, b is row
        for d in range(0,len(dates)):
            #iterate through users bookings
            if str(dates[d]) in currentUser._bookingDict:
                bookings = currentUser._bookingDict[str(dates[d])]
                for b in range(0,len(bookings)):
                    if b >= self.table.rowCount():
                         self.table.insertRow(self.table.rowCount())
                    
                    #assemble Text
                    text = sharedDB.myProjects[str(bookings[b].idprojects())].name() + " - " + sharedDB.myPhaseAssignments[str(bookings[b].idphaseassignments())].name()
                    self.table.setItem(b,d+1,QtGui.QTableWidgetItem(text))
                    #print bookings[b].idprojects() idphaseassignments
                
          
        self.table.resizeRowsToContents()      
    '''    
    def CalculateWeeklies(self):
        
        day = self.dateEdit.date().toPyDate()
        
        mon = day - timedelta(days=day.weekday())
        
        fri = mon + timedelta(days=4)
        
        departmentDict = {}
        phaseDict = {}
        projList = []
        text = "<b> **PROJECTS** </b>"
        
        #iterate through projects and add to project list
        for proj in sharedDB.myProjects.values():
            if proj._startdate <= fri:
                if int(proj._idstatuses) < 4 or int(proj._idstatuses) == 7:
                    projList.append(proj)
                    
        projList.sort(key=operator.attrgetter('_startdate'))
        
        for proj in projList:
            text += "<br><u>"+proj._name+"</u> - "
            stat = proj._statusDescription
            if stat is not None and len(stat):
                text+=stat
            else:
                text+=sharedDB.myStatuses[str(proj._idstatuses)]._name
        
        for phase in sharedDB.myPhaseAssignments.values():
        #    if start before saturday and end after sunday
            proj = sharedDB.myProjects[str(phase._idprojects)]
            if phase._startdate <= fri and int(phase._idstatuses) != 5 and int(phase._idstatuses) != 6 and not 4 <= proj._idstatuses <= 6:
                
                if ((phase._enddate >= mon) and int(phase._idstatuses) != 4) or int(phase._idstatuses) != 4:
                    departmentID = str(sharedDB.myPhases[str(phase._idphases)]._iddepartments)
                    if departmentID in departmentDict:
                        departmentDict[departmentID].append(phase)
                    else:
                       departmentDict[departmentID] = [phase]
                       
                    phaseID = str(phase._idphases)
                    if phaseID in phaseDict:
                        phaseDict[phaseID].append(phase)
                    else:
                        phaseDict[phaseID] = [phase]
                    
                
        #phaselist.sort(key=operator.attrgetter('_startdate'))
        
        text += "<br><br>"
        
        for key in phaseDict.keys():
            text += "<b>"+sharedDB.myPhases[key]._name+"</b>\n"
            phaselist = phaseDict[key]
            phaselist.sort(key=operator.attrgetter('_startdate'))
            for phase in phaselist:
                
                dateInfo = ''
                
                #starting
                if phase._startdate >= mon:
                    #starting and ending this week
                    if phase._enddate <= fri:
                        dateInfo = "<font color=\"green\">"+phase._startdate.strftime("%m/%d")+'</font> - <font color=\"red\">'+phase._enddate.strftime("%m/%d")+'</font> - '
                    else:
                        dateInfo = "<font color=\"green\">"+phase._startdate.strftime("%m/%d")+' - START</font> - '
                #due
                elif phase._enddate <= fri:
                    dateInfo = "<font color=\"red\">"+phase._enddate.strftime("%m/%d")+' - DUE</font> - '
                #continuing
                else:
                    dateInfo = 'Continuing through week... - '
                
                #users
                defaultUserInfo = '<font color=\"blue\"> - UNASSIGNED</font>' 
                userInfo =  defaultUserInfo              
                for ua in phase._userAssignments.values():
                    if ua._hours > 1:
                        if userInfo == defaultUserInfo:
                            userInfo = ' - '+sharedDB.myUsers[str(ua._idusers)]._name
                        else:
                            userInfo += ", "+sharedDB.myUsers[str(ua._idusers)]._name
                
                pname = sharedDB.myPhases[str(phase._idphases)]._name
                if  pname in ["Approval","DUE","Delivery","Internal Review","Rendering"]:
                    userInfo = ""
                
                #if phase or project on hold
                startTag = "<tab>"
                endTag = "</tab>"
                if phase._idstatuses == 3 or proj._idstatuses == 3:
                    startTag += "<s>"
                    endTag += "</s>"
                    startTag += "**ON HOLD** "
                    
                if phase._idstatuses == 4:
                    startTag += "<s>"
                    endTag += "</s>"
                
                if phase._description is not None and phase._description != "None":
                    additionalInfo = " - "+phase._description
                else:
                    additionalInfo = ""
                    
                text += "<br>"+startTag+dateInfo+"<u>"+sharedDB.myProjects[str(phase._idprojects)]._name+"</u>"+userInfo+additionalInfo+endTag+"\n"
            text += "<br><br>"
        self.textDocument.setHtml(text)
    '''