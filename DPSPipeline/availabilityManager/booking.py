from PyQt4.QtCore import QDate, QObject

bookingIDCounter = 0

class Booking(QObject):
    
    def __init__(self, _idusers = -1 , _hours = 0, _idphaseassignments = -1, _idprojects = -1, _iduserassignments = -1):
	
        global bookingIDCounter
        	
	super(QObject, self).__init__()
	
        self._id = bookingIDCounter
        bookingIDCounter += 1
        
        #user
        self._idusers = _idusers
        #hours
        self._hours = _hours
        #phase assignment
        self._idphaseassignments = _idphaseassignments
        #project
        self._idprojects = _idprojects
        #userassignment
        self._iduserassignments = _iduserassignments
        #date
        #self._date = today
    
    def __radd__(self, other):

    	return other + self._hours
    
    def id(self):
        return self._id
    
    def idusers(self):
        return self._idusers
    
    def hours(self):
        return self._hours
    
    def idphaseassignments(self):
        return self._idphaseassignments
        
    def idprojects(self):
        return self._idprojects
    