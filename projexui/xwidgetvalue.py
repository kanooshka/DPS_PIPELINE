#!/usr/bin/python

""" Defines methods to abstract the getter/setter process for all widgets. """

# define authorship information
__authors__         = ['Eric Hulser']
__author__          = ','.join(__authors__)
__credits__         = []
__copyright__       = 'Copyright (c) 2011, Projex Software'
__license__         = 'LGPL'

# maintanence information
__maintainer__      = 'Projex Software'
__email__           = 'team@projexsoftware.com'

#------------------------------------------------------------------------------

import logging
import os.path

from projexui import qt #import unwrapVariant
from PyQt4 import QtCore,QtGui
from PyQt4.QtGui    import QAction, QApplication

# used to register saving and loading systems
from projexui.widgets.xcolortreewidget import XColorTreeWidget
from projexui.widgets.xcolorbutton     import XColorButton
from projexui.widgets.xlocationwidget  import XLocationWidget
from projexui.widgets.xurlwidget       import XUrlWidget
from projexui.widgets.xenumbox         import XEnumBox
from projexui.widgets.xiconbutton      import XIconButton
from projexui.widgets.xlineedit        import XLineEdit
from projexui.widgets.xboolcombobox    import XBoolComboBox
from projexui.widgets.xtimedeltaedit   import XTimeDeltaEdit
from projexui.widgets.xfilepathedit    import XFilepathEdit

logger = logging.getLogger(__name__)
_widgetValueTypes   = []

def registerWidgetValue( widgetType, getter, setter ):
    """
    Register a getter/setter for the value for a particular widget class.
    
    :param      widgetType  | <subclass of QWidget>
                getter      | <method>
                setter      | <method>
    """
    _widgetValueTypes.append((widgetType, getter, setter))

def setWidgetValue( widget, value ):
    """
    Sets the value for the inputed widget to the given value.  This will be \
    controlled by the type of widget it is.  You can define new types by \
    calling the registerWidgetValue method.
    
    :param      widget | <QWidget>
                value  | <variant>
    
    :return     <bool> success
    """
    for wtype in reversed(_widgetValueTypes):
        if isinstance(widget, wtype[0]):
            try:
                wtype[2](widget, value)
            except:
                return False
            return True
    return False

def widgetValue( widget ):
    """
    Returns the value for the inputed widget based on its type.
    
    :param      widget | <QWidget>
    
    :return     (<variant> value, <bool> success)
    """
    for wtype in reversed(_widgetValueTypes):
        if isinstance(widget, wtype[0]):
            try:
                return (wtype[1](widget), True)
            except:
                return (None, False)
    return (None, False)

#------------------------------------------------------------------------------

def getComboValue(combo):
    """
    Checks to see if there is a dataType custom property set to determine 
    whether to return an integer or a string.
    
    :param      combo | <QComboBox>
    
    :return     <int> || <str>
    """
    dataType = qt.unwrapVariant(combo.property('dataType'))
    
    if dataType == 'string':
        return combo.currentText()
    elif dataType == 'data':
        return qt.unwrapVariant(combo.itemData(combo.currentIndex()))
    return combo.currentIndex()

def setComboValue(combo, value):
    """
    Checks to see if there is a dataType custom property set to determine 
    whether to return an integer or a string.
    
    :param      combo | <QComboBox>
    
    :return     <int> || <str>
    """
    dataType = qt.unwrapVariant(combo.property('dataType'))
    
    if dataType == 'string':
        return combo.setCurrentIndex(combo.findText(value))
    elif dataType == 'data':
        for i in range(combo.count()):
            if qt.unwrapVariant(combo.itemData(i)) == value:
                return combo.setCurrentIndex(i)
        return combo.setCurrentIndex(-1)
    return combo.setCurrentIndex(value)

#------------------------------------------------------------------------------

# register getter/setter widget types
registerWidgetValue(QtGui.QDateEdit,
                lambda w: w.date().toPyDate(),
                lambda w, v: w.setDate(QtCore.QDate(v)))

registerWidgetValue(QtGui.QTimeEdit,
                lambda w: w.time().toPyTime(),
                lambda w, v: w.setTime(QtCore.QTime(v)))

registerWidgetValue(QtGui.QDateTimeEdit,
                lambda w: w.dateTime().toPyDateTime(),
                lambda w, v: w.setDateTime(QtCore.QDateTime(v)))

registerWidgetValue(QtGui.QGroupBox,
                lambda w: w.isChecked(),
                lambda w, v: w.setChecked(bool(v)))

registerWidgetValue(QtGui.QLineEdit,
                lambda w: str(w.text()),
                lambda w, v: w.setText(v))

registerWidgetValue(QtGui.QTextEdit,
                lambda w: str(w.toPlainText()),
                lambda w, v: w.setText(str(v)))

registerWidgetValue(QtGui.QSpinBox,
                lambda w: w.value(),
                lambda w, v: w.setValue(v))

registerWidgetValue(QtGui.QDoubleSpinBox,
                lambda w: w.value(),
                lambda w, v: w.setValue(v))

registerWidgetValue(QtGui.QComboBox, getComboValue, setComboValue)

registerWidgetValue(QtGui.QCheckBox,
                lambda w: w.isChecked(),
                lambda w, v: w.setChecked(bool(v)))

registerWidgetValue(QtGui.QRadioButton,
                lambda w: w.isChecked(),
                lambda w, v: w.setChecked(bool(v)))

registerWidgetValue(QtGui.QFontComboBox,
                lambda w: w.currentFont(),
                lambda w, v: w.setCurrentFont(v))

registerWidgetValue(XColorTreeWidget,
                lambda w: w.savedColorSet(),
                lambda w, v: w.setColorSet(v))

registerWidgetValue(XColorButton,
                lambda w: w.color(),
                lambda w, v: w.setColor(QtGui.QColor(v)))

registerWidgetValue(XEnumBox,
                lambda w: w.currentValue(),
                lambda w, v: w.setCurrentValue(v))

registerWidgetValue(XLineEdit,
                lambda w: w.currentText() if w.useHintValue() else w.text(),
                lambda w, v: w.setText(v))

registerWidgetValue(XLocationWidget,
                lambda w: w.location(),
                lambda w, v: w.setLocation(str(v)))

registerWidgetValue(XUrlWidget,
                lambda w: w.url(),
                lambda w, v: w.setUrl(str(v)))

registerWidgetValue(XBoolComboBox, 
                    lambda w: w.isChecked(), 
                    lambda w, v: w.setChecked(v))

registerWidgetValue(XIconButton,
                    lambda w: None if w.icon().isNull() else w.icon(),
                    lambda w, v: w.setIcon(w.buildIcon(v)))

registerWidgetValue(XTimeDeltaEdit,
                    lambda w: w.delta(),
                    lambda w, v: w.setDelta(v))

registerWidgetValue(XFilepathEdit,
                    lambda w: w.filepath(),
                    lambda w, v: w.setFilepath(v))