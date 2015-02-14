# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'C:\Users\DoodleLights\Documents\GitHub\DPS_PIPELINE\projexui\widgets\xganttwidget\ui\xganttwidget.ui'
#
# Created: Fri Feb 13 18:43:52 2015
#      by: PyQt4 UI code generator 4.11.3
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_XGanttWidget(object):
    def setupUi(self, XGanttWidget):
        XGanttWidget.setObjectName(_fromUtf8("XGanttWidget"))
        XGanttWidget.resize(733, 462)
        self.gridLayout = QtGui.QGridLayout(XGanttWidget)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.verticalLayout_3 = QtGui.QVBoxLayout()
        self.verticalLayout_3.setObjectName(_fromUtf8("verticalLayout_3"))
        self.createProjectButton = QtGui.QPushButton(XGanttWidget)
        self.createProjectButton.setObjectName(_fromUtf8("createProjectButton"))
        self.verticalLayout_3.addWidget(self.createProjectButton)
        self.widget = QtGui.QWidget(XGanttWidget)
        self.widget.setObjectName(_fromUtf8("widget"))
        self.verticalLayout_2 = QtGui.QVBoxLayout(self.widget)
        self.verticalLayout_2.setMargin(0)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.uiGanttSPLT = XSplitter(self.widget)
        self.uiGanttSPLT.setOrientation(QtCore.Qt.Horizontal)
        self.uiGanttSPLT.setObjectName(_fromUtf8("uiGanttSPLT"))
        self.uiGanttTREE = XTreeWidget(self.uiGanttSPLT)
        self.uiGanttTREE.setAlternatingRowColors(True)
        self.uiGanttTREE.setProperty("x_arrowStyle", True)
        self.uiGanttTREE.setObjectName(_fromUtf8("uiGanttTREE"))
        self.uiGanttTREE.headerItem().setText(0, _fromUtf8("Name"))
        self.uiGanttVIEW = QtGui.QGraphicsView(self.uiGanttSPLT)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(1)
        sizePolicy.setHeightForWidth(self.uiGanttVIEW.sizePolicy().hasHeightForWidth())
        self.uiGanttVIEW.setSizePolicy(sizePolicy)
        self.uiGanttVIEW.setViewportUpdateMode(QtGui.QGraphicsView.FullViewportUpdate)
        self.uiGanttVIEW.setObjectName(_fromUtf8("uiGanttVIEW"))
        self.verticalLayout_2.addWidget(self.uiGanttSPLT)
        self.saveButton = QtGui.QPushButton(self.widget)
        self.saveButton.setObjectName(_fromUtf8("saveButton"))
        self.verticalLayout_2.addWidget(self.saveButton)
        self.verticalLayout_3.addWidget(self.widget)
        self.gridLayout.addLayout(self.verticalLayout_3, 0, 0, 1, 1)

        self.retranslateUi(XGanttWidget)
        QtCore.QMetaObject.connectSlotsByName(XGanttWidget)

    def retranslateUi(self, XGanttWidget):
        XGanttWidget.setWindowTitle(_translate("XGanttWidget", "Form", None))
        self.createProjectButton.setText(_translate("XGanttWidget", "CreateProject", None))
        self.uiGanttTREE.headerItem().setText(1, _translate("XGanttWidget", "Date Start", None))
        self.uiGanttTREE.headerItem().setText(2, _translate("XGanttWidget", "Date End", None))
        self.uiGanttTREE.headerItem().setText(3, _translate("XGanttWidget", "Days", None))
        self.uiGanttTREE.headerItem().setText(4, _translate("XGanttWidget", "Weekdays", None))
        self.saveButton.setText(_translate("XGanttWidget", "Save", None))

from projexui.widgets.xsplitter import XSplitter
from projexui.widgets.xtreewidget import XTreeWidget
