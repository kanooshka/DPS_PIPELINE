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
        self.dateEdit.dateChanged.connect(self.CalculateWeeklies)
        topLayout.addWidget(self.dateEdit)
        
        self.textBox = QtGui.QTextEdit()
        self.textDocument = QtGui.QTextDocument()
        self.textBox.setDocument(self.textDocument)
        
        mainlay.addWidget(self.textBox)       
        
                
        
        #self.setWindowFlags(QtCore.Qt.Tool)
        
    def CalculateWeeklies(self):
        
        day = self.dateEdit.date().toPyDate()

        #dt = datetime.strptime(day, '%d/%b/%Y')
        
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
                if  pname in ["Approval","DUE","Delivery","Internal Review"]:
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