
from DPSPipeline.widgets.createprojectwidget.createprojectwidget import CreateProjectWidget

from PyQt4.QtGui import QColor

class CreateProjectTest():

	def __init__(self):
		#global myXGanttWidget
		
		self._myCreateProjectWidget = CreateProjectWidget()
		#self._myCreateProjectWidget.show()
		
	def open(self):
		self._myCreateProjectWidget.show()
		self._myCreateProjectWidget.activateWindow()