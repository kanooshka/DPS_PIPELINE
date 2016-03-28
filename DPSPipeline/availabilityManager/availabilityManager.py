from PyQt4 import QtCore
from PyQt4.QtCore import QDate, QObject
from DPSPipeline.availabilityManager import booking
from DPSPipeline.database import phases
from DPSPipeline.database import users
from datetime import timedelta, date
import sharedDB
import operator
import atexit

class updateAvailability(QtCore.QThread):
    
    def run(self):
	sortedPhaseAssignmentList = []
	tempUserAssignmentDict = {}
	start_date = date(1700,1,1)
	end_date = date(1700,1,1)
	
	#clear booking for all users
	for u in sharedDB.myUsers.values():
	    u._bookingDict.clear()
	    
	for p in sharedDB.myPhases.values():
	    p._availability.clear()
	    
	for ua in sharedDB.myUserAssignments.values():
	    ua._estimatedHoursLeft = ua._hours
	
	#needs to just add phases that end beforce current date
	for pa in sharedDB.myPhaseAssignments.values():
	    if int(sharedDB.myProjects[str(pa._idprojects)]._idstatuses) < 3 and pa._enddate >= date.today() and not 5 <= int(pa._idstatuses) <= 6:
	    #if QDate(pa._enddate) <= sharedDB.calendarview._myXGanttWidget.dateStart() and int(sharedDB.myProjects[str(pa._idprojects)]._idstatuses) < 3:
		pa._estimatedHoursLeft = int(pa._hoursalotted)
		sortedPhaseAssignmentList.append(pa)
		if end_date < pa._enddate:
		    end_date = pa._enddate

		pa.CalculateWeekdays()    
	
	sortedPhaseAssignmentList.sort(key=operator.attrgetter('_startdate'))
	
	if len(sortedPhaseAssignmentList):
	    start_date = sortedPhaseAssignmentList[0]._startdate
    
	    self.CreatePhaseAssignmentList(start_date, end_date, list(sortedPhaseAssignmentList),"UA")
	    self.CreatePhaseAssignmentList(start_date, end_date, list(sortedPhaseAssignmentList), "")
	
    def CreatePhaseAssignmentList(self, start_date, end_date, sortedPhaseAssignmentList, typ):
	#iterate through days
	for d in self.daterange(start_date, end_date):
	    #if weekend or holiday continue
	    if not d.isoweekday() in range(1, 6):
		continue	    

	    phaseAssignmentsByPhaseId = {}
	    phaseAssignmentsByPhaseId.clear()
	    
	    #reset temp user assignment list
	    tempUserAssignmentDict = {}
	    
	    #iterate through phase assignments
	    x = 0
	    while len(sortedPhaseAssignmentList):		
		if x == len(sortedPhaseAssignmentList):
		    break
		pa = sortedPhaseAssignmentList[x]
		
		#if date in phase range
		if pa._startdate <= d <= pa._enddate:
		    
		    #is it even possible with capacity?
		    
		    if pa._phase._capacity * pa._weekdays < int(pa._hoursalotted):
			pa._phase._availability[str(d)] = 3
		    elif str(d) not in pa._phase._availability:
			pa._phase._availability[str(d)] = 2	
		    #print sharedDB.myPhases[str(pa._idphases)]._name + "  " +str(d)
		    
		    if typ == "UA":
			#iterate through userassignments on phase assignment
			for ua in pa._userAssignments.values():	    
			    if str(ua._hours) > "1":
				if str(ua._idusers) in tempUserAssignmentDict:
				    tempUserAssignmentDict[str(ua._idusers)].append(ua)
				else:
				    tempUserAssignmentDict[str(ua._idusers)] = [ua]
		    else:
			#add to phase dict 
			if str(pa._idphases) not in phaseAssignmentsByPhaseId:
			    phaseAssignmentsByPhaseId[str(pa._idphases)] = [pa]
			    #print pa.id()
			else:			
			    phaseAssignmentsByPhaseId[str(pa._idphases)].append(pa)
			    #print pa.id()
		    #increment to next phase assignment
		    x = x+1
		elif pa._enddate < d:
		    sortedPhaseAssignmentList.pop(x)
		    continue
		else:
		    break

	    tempSortedPhaseAssignmentList = []
	    for y in range(0,x):
		tempSortedPhaseAssignmentList.append(sortedPhaseAssignmentList[y])
	    
	    #sort by scarcity
	    tempSortedPhaseAssignmentList.sort(key=operator.attrgetter('_scarcityIndex'))
	    
	    if typ == "UA":
		self.CalculateUserAssignmentAvailablity(d, tempUserAssignmentDict)
	    else:
		self.CalculateUserAvailability(d, tempSortedPhaseAssignmentList)
    
    def CalculateUserAvailability(self,d, tempSortedPhaseAssignmentList):
	if len(tempSortedPhaseAssignmentList):
	    #create temp user list
	    tempUserListIds = list(users.sortedUserList)
	else:
	    tempUserListIds = []

	#print "Date: "+str(d)

	while len(tempUserListIds):
	    user = sharedDB.myUsers[str(tempUserListIds[0][0])]
	    #print "User: "+str(user._name)
	    
	    if str(d) not in user._bookingDict :
		origHours = 0
	    elif sum(user._bookingDict[str(d)]) < 8:
		origHours = sum(user._bookingDict[str(d)])
	    else:
		del tempUserListIds[0]
		continue
	    
	    #iterate through sorted phase list
	    assignedHours = 0
	    for pai in range(0,len(tempSortedPhaseAssignmentList)):				    
		pa = tempSortedPhaseAssignmentList[pai]
		if pa._estimatedHoursLeft < 1:
		    if pa._phase._availability[str(d)] != 3:
			pa._phase._availability[str(d)] = 2
		    continue
		if str(pa._idphases) in user._phases:				
		    
		    #move pa to end of list to spread the wealth
		    tempSortedPhaseAssignmentList.pop(pai)
		    tempSortedPhaseAssignmentList.append(pa)
		    
		    #find max number hours for user 8-origHours
		    maxHours = 8-origHours
		    #print "Max Hours: "+str(maxHours)
		    
		    if maxHours <= int(pa._estimatedHoursLeft):
			#print "Assigned Hours = max hours "+str(maxHours)
			assignedHours = maxHours
		    else:
			#print "Assigned Hours = Estimated Hours left "+str(pa._estimatedHoursLeft)
			assignedHours = int(pa._estimatedHoursLeft)
		    
		    #print "Assigned Hours: "+str(assignedHours)+" to phase "+pa._phase._name
		    
		    #subtract assigned hours from pa
		    pa._estimatedHoursLeft = pa._estimatedHoursLeft - assignedHours
		    
		    #print "PA Availability: "+str(pa._availability[str(d)])		    
		    #print str(pa.id()) + " "+user._name+" "+str(assignedHours)
		    
		    book = booking.Booking(_idusers = user.id() , _hours = assignedHours, _idphaseassignments = pa.id())
		    if str(d) in user._bookingDict:
			user._bookingDict[str(d)].append(book)
		    else:
			user._bookingDict[str(d)] = [book]
		    
		    #print "Total Hours For User on day: "+str(origHours+assignedHours)
		    
		    if pa._estimatedHoursLeft < 1:
			#print pa._name +" is filled"
			if pa._phase._availability[str(d)] != 3:
			    pa._phase._availability[str(d)] = 2
			
		    if sum(user._bookingDict[str(d)])==8:
			break
			
	    if assignedHours == 0:
		for phaseid in user._phases:			
		    if str(d) not in sharedDB.myPhases[str(phaseid)]._availability or sharedDB.myPhases[str(phaseid)]._availability[str(d)] != 3:
			sharedDB.myPhases[str(phaseid)]._availability[str(d)] = 1
		del tempUserListIds[0]
		
	for pa in tempSortedPhaseAssignmentList:
	    if pa._estimatedHoursLeft > 0:
		#if enddate and still not finished
		if str(d) == str(pa._enddate):
		    #print pa._name +" still has hours left"
		    pa._phase._availability[str(d)] = 3
		    #break
		#if not possible even at capacity
		elif pa._phase._capacity * (pa.WeekdaysFromStartDate(d)) < pa._estimatedHoursLeft:
		    #print pa._name +" Impossible to complete at this point because of " + str(pa._estimatedHoursLeft) + " hours needed over " + str(pa.WeekdaysFromStartDate(d)) + " days"
		    pa._phase._availability[str(d)] = 3
		    #break

    def CalculateUserAssignmentAvailablity(self, d, tempUserAssignmentDict):
	    
	    #book for user assignments
	    # NEED TO MAKE IT DO FREELANCERS FIRST
	    for userid in tempUserAssignmentDict.keys():
		uas = tempUserAssignmentDict[str(userid)]
		uas.sort(key=operator.attrgetter('_hours'))
		factor = len(uas)
		hoursLeft = 8.0
		user = sharedDB.myUsers[str(userid)]
		for q in range(0,len(uas)):
		    maxHours = hoursLeft / (len(uas) - q)
		    ua = uas[q]		    
		    
		    if ua._estimatedHoursLeft < maxHours:
			maxHours = ua._estimatedHoursLeft
		    
		    pa = sharedDB.myPhaseAssignments[str(ua._assignmentid)]
		    if maxHours <= int(pa._estimatedHoursLeft):
			#print "Assigned Hours = max hours "+str(maxHours)
			assignedHours = maxHours
		    else:
			#print "Assigned Hours = Estimated Hours left "+str(pa._estimatedHoursLeft)
			assignedHours = int(pa._estimatedHoursLeft)
		    
		    hoursLeft = hoursLeft-assignedHours
		    
		    #print "Assigned Hours: "+str(assignedHours)+" to phase "+pa._phase._name
		    
		    #subtract assigned hours from pa
		    pa._estimatedHoursLeft = pa._estimatedHoursLeft - assignedHours
		    ua._estimatedHoursLeft = ua._estimatedHoursLeft - assignedHours
		    
		    #print "PA Availability: "+str(pa._availability[str(d)])
		    #print str(pa.id()) + " "+user._name+" "+str(assignedHours)
		    
		    book = booking.Booking(_idusers = user.id() , _hours = assignedHours, _idphaseassignments = pa.id(), _iduserassignments = ua.id())
		    if str(d) in user._bookingDict:
			user._bookingDict[str(d)].append(book)
		    else:
			user._bookingDict[str(d)] = [book]
    
    def daterange(self,start_date, end_date):
	for n in range(int ((end_date - start_date).days)+1):
	    yield start_date + timedelta(n)

class AvailabilityManager(QObject):
    
    availabilityCalcUpdated = QtCore.pyqtSignal()
    
    def __init__(self):
		
	super(QObject, self).__init__()
	
	self._updateAvailability = updateAvailability()
	self._updateAvailability.finished.connect(self.emitUpdate)
	self._updateAvailability.daemon = True
	
	atexit.register(self._updateAvailability.quit)
	
    def CalculateBooking(self):
	self._updateAvailability.quit()
	
	self._updateAvailability.start()
			
    def emitUpdate(self):	
	if sharedDB.calendarview is not None:
	    view = sharedDB.calendarview._departmentXGanttWidget.uiGanttVIEW.scene()
	    view.setDirty()
	    view.update()
	    #view.syncView()

	self.availabilityCalcUpdated.emit()