import projexui
import projex
from projexui.widgets.xganttwidget.xganttwidget     import XGanttWidget
from projexui.widgets.xganttwidget.xganttviewitem   import XGanttViewItem
from projexui.widgets.xganttwidget.xganttwidgetitem import XGanttWidgetItem 
from PyQt4.QtCore import QDate


class DPGanttWindow():
	""" 
	Defines the main widget item class that contains information for the window
	"""

	def __init__(self):
		#global self._myXGanttWidget
		#global self._myXGanttWidget
		self._myXGanttWidget = XGanttWidget()
		#self._myXGanttWidget.show()
		#self._projects = []

	def show(self):
		_myXGanttWidget.show()
		
	def AddProject(self):
		self._myXGanttWidgetItem = XGanttWidgetItem(self._myXGanttWidget)
		#self._myXGanttViewItem = self._myXGanttWidgetItem.createViewItem()
		self._myXGanttWidgetItem.setName("test")
		self._myXGanttWidgetItem.setDateEnd(QDate.currentDate().addMonths(+1))
		self._myXGanttWidgetItem.setDateStart(QDate.currentDate().addDays(+1))
		
		self._myXGanttWidgetItem.setProperty("Start",QDate(2014,10,1))
		self._myXGanttWidgetItem.setProperty("End",QDate(2014,10,2))
		self._myXGanttWidgetItem.setProperty("Calendar Days",2)
		self._myXGanttWidgetItem.setProperty("Work Days",2)
		
		self._myXGanttWidget.addTopLevelItem(self._myXGanttWidgetItem)
		self._myXGanttWidget.show()
		
	'''def GetProjects(self, connection):
		
		query = ("SELECT first_name, last_name, hire_date FROM employees "
         "WHERE hire_date BETWEEN %s AND %s")

		hire_start = datetime.date(1999, 1, 1)
		hire_end = datetime.date(1999, 12, 31)

		cursor.execute(query, (hire_start, hire_end))

		for (first_name, last_name, hire_date) in cursor:
		  print("{}, {} was hired on {:%d %b %Y}".format(
			last_name, first_name, hire_date))'''
		