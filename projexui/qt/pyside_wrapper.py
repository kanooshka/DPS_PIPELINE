""" Sets up the Qt environment to work with various Python Qt wrappers """

# define authorship information
__authors__         = ['Eric Hulser']
__author__          = ','.join(__authors__)
__credits__         = []
__copyright__       = 'Copyright (c) 2012, Projex Software'
__license__         = 'LGPL'

# maintenance information
__maintainer__      = 'Projex Software'
__email__           = 'team@projexsoftware.com'

import logging
import re
import sys
from xml.etree import ElementTree
import xml.parsers.expat

from PySide import QtCore,\
                   QtGui,\
                   QtUiTools,\
                   QtXml,\
                   QtNetwork,\
                   QtWebKit

logger = logging.getLogger(__name__)
try:
    from PySide import Qsci
except ImportError:
    logger.debug('PySide.Qsci is not installed.')
    Qsci = None

try:
    from PySide import QtDesigner
except ImportError:
    logger.debug('PySide.QtDesigner is not installed.')
    QtDesigner = None

def SIGNAL(signal):
    match = re.match(r'^(?P<method>\w+)\(?(?P<args>[^\)]*)\)?$', str(signal))
    if not match:
        return QtCore.SIGNAL(signal)
    
    method = match.group('method')
    args   = match.group('args')
    args   = re.sub(r'\bPyQt_PyObject\b', 'QVariant', args)
    args   = re.sub(r'\bobject\b', 'QVariant', args)
    
    new_signal = '%s(%s)' % (method, args)
    return QtCore.SIGNAL(new_signal)

class NonePlaceholder(object):
    pass

NONE_PLACEHOLDER = NonePlaceholder()

def wrapNone(value):
    """
    Handles any custom wrapping that needs to happen for Qt to process
    None values properly (PySide issue)
    
    :param      value | <variant>
    
    :return     <variant>
    """
    if value is None:
        return NONE_PLACEHOLDER
    return value

def unwrapNone(value):
    """
    Handles any custom wrapping that needs to happen for Qt to process
    None values properly (PySide issue)
    
    :param      value | <variant>
    
    :return     <variant>
    """
    if value is NONE_PLACEHOLDER:
        return None
    return value

#----------------------------------------------------------

class PySideDialog(QtGui.QDialog):
    def exec_(self, *args):
        """
        Ensure the dialogs are properly centered - doesn't seem to happen
        automatically with PySide.
        
        :return     <int> result
        """
        parent = self.parent()
        if parent and parent.window():
            point = parent.window().geometry().center()
            point.setX(point.x() - self.width() / 2.0)
            point.setY(point.y() - self.height() / 2.0)
            self.move(point)
        
        return super(PySideDialog, self).exec_(*args)
    
    def show(self, *args):
        """
        Ensure the dialogs are properly centered - doesn't seem to happen
        automatically with PySide.
        
        :return     <int> result
        """
        parent = self.parent()
        if parent and parent.window():
            point = parent.window().geometry().center()
            point.setX(point.x() - self.width() / 2.0)
            point.setY(point.y() - self.height() / 2.0)
            self.move(point)
        
        return super(PySideDialog, self).show(*args)
    
QtGui.QDialog = PySideDialog

#----------------------------------------------------------

class UiLoader(QtUiTools.QUiLoader):
    def __init__(self, baseinstance):
        super(UiLoader, self).__init__()
        
        self.dynamicWidgets = {}
        self._baseinstance = baseinstance
    
    def createAction(self, parent=None, name=''):
        """
        Overloads teh create action method to handle the proper base
        instance information, similar to the PyQt4 loading system.
        
        :param      parent | <QWidget> || None
                    name   | <str>
        """
        action = super(UiLoader, self).createAction(parent, name)
        if not action.parent():
            action.setParent(self._baseinstance)
        setattr(self._baseinstance, name, action)
        return action
    
    def createActionGroup(self, parent=None, name=''):
        """
        Overloads teh create action method to handle the proper base
        instance information, similar to the PyQt4 loading system.
        
        :param      parent | <QWidget> || None
                    name   | <str>
        """
        actionGroup = super(UiLoader, self).createActionGroup(parent, name)
        if not actionGroup.parent():
            actionGroup.setParent(self._baseinstance)
        setattr(self._baseinstance, name, actionGroup)
        return actionGroup
    
    def createLayout(self, className, parent=None, name=''):
        """
        Overloads teh create action method to handle the proper base
        instance information, similar to the PyQt4 loading system.
        
        :param      className | <str>
                    parent | <QWidget> || None
                    name   | <str>
        """
        layout = super(UiLoader, self).createLayout(className, parent, name)
        setattr(self._baseinstance, name, layout)
        return layout
    
    def createWidget(self, className, parent=None, name=''):
        """
        Overloads the createWidget method to handle the proper base instance
        information similar to the PyQt4 loading system.
        
        :param      className | <str>
                    parent    | <QWidget> || None
                    name      | <str>
        
        :return     <QWidget>
        """
        className = str(className)
        
        # create a widget off one of our dynamic classes
        if className in self.dynamicWidgets:
            widget = self.dynamicWidgets[className](parent)
            widget.setObjectName(name)
            
            # hack fix on a QWebView (will crash app otherwise)
            # forces a URL to the QWebView before it finishes
            if className == 'QWebView':
                widget.setUrl(QtCore.QUrl('http://www.google.com'))
        
        # create a widget from the default system
        else:
            widget = super(UiLoader, self).createWidget(className, parent, name)
        
        if parent is None:
            return self._baseinstance
        else:
            setattr(self._baseinstance, name, widget)
            return widget

#----------------------------------------------------------

class Uic(object):
    def compileUi(self, filename, file):
        import pysideuic
        pysideuic.compileUi(filename, file)
        
    def loadUi(self, filename, baseinstance=None):
        """
        Generate a loader to load the filename.
        
        :param      filename | <str>
                    baseinstance | <QWidget>
        
        :return     <QWidget> || None
        """
        try:
            xui = ElementTree.parse(filename)
        except xml.parsers.expat.ExpatError:
            logger.exception('Could not load file: %s' % filename)
            return None
        
        loader = UiLoader(baseinstance)
        
        # pre-load custom widgets
        xcustomwidgets = xui.find('customwidgets')
        if xcustomwidgets is not None:
            for xcustom in xcustomwidgets:
                header = xcustom.find('header').text
                clsname = xcustom.find('class').text
                
                if not header:
                    continue
                
                if clsname in loader.dynamicWidgets:
                    continue
                
                # modify the C++ headers to use the Python wrapping
                if '/' in header:
                    header = 'projexui.qt.' + '.'.join(header.split('/')[:-1])
                
                # try to use the custom widgets
                try:
                    __import__(header)
                    module = sys.modules[header]
                    cls = getattr(module, clsname)
                except (ImportError, KeyError, AttributeError):
                    logger.error('Could not load %s.%s' % (header, clsname))
                    continue
                
                loader.dynamicWidgets[clsname] = cls
                loader.registerCustomWidget(cls)
        
        # load the options
        ui = loader.load(filename)
        QtCore.QMetaObject.connectSlotsByName(ui)
        return ui

#----------------------------------------------------------------------

def createMap(qt):
    # helpers
    qt['uic']       = Uic()
    qt['PyObject']  = object
    
    # modules
    qt['QtCore']        = QtCore
    qt['QtDesigner']    = QtDesigner
    qt['QtGui']         = QtGui
    qt['Qsci']          = Qsci
    qt['QtWebKit']      = QtWebKit
    qt['QtNetwork']     = QtNetwork
    qt['QtXml']         = QtXml
    
    # variables
    qt['SIGNAL']   = SIGNAL
    qt['Signal']   = QtCore.Signal
    qt['Slot']     = QtCore.Slot
    qt['Property'] = QtCore.Property
    qt['wrapNone'] = wrapNone
    qt['unwrapNone'] = unwrapNone
    qt['QStringList'] = list
    
    # map additional options
    QtCore.QDate.toPyDate = lambda x: x.toPython()
    QtCore.QDateTime.toPyDateTime = lambda x: x.toPython()
    QtCore.QTime.toPyTime = lambda x: x.toPython()