#!/usr/bin/python

""" Defines a system for controlling multiple states for a view widget. """

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

# version 1
"""
<profile>
 <split orient="vertical">
  <split orient="horizontal">
   <view name="Test01" type="Test"/>
   <view name="Test02" type="Test"/>
  </split>
  <view name="Test03" type="Test"/>
 </split>
</profile>
"""

# version 2
"""
<profile name="Testing" icon="path/to/icon" version="2">
 <desc>
  Testing a description
 </desc>
 <data/>
 <layout>
  <split orient="vertical">
   <split orient="horizontal">
    <view name="Test01" type="Test"/>
    <view name="Test02" type="Test"/>
   </split>
   <view name="Test03" type="Test"/>
  </split>
 </layout>
</profile>
"""

import copy
import logging
from xml.etree          import ElementTree
from xml.parsers.expat  import ExpatError

from PyQt4.QtCore   import Qt, QByteArray

import projex.text
from projex.dataset import DataSet

from projexui.widgets.xviewwidget.xview      import XView
from projexui.widgets.xviewwidget.xviewpanel import XViewPanel
from projexui.widgets.xsplitter              import XSplitter

logger = logging.getLogger(__name__)

class XViewProfile(object):
    def __init__( self ):
        self._icon          = ''
        self._name          = ''
        self._description   = ''
        self._customData    = DataSet()
        self._xmlElement    = None
    
    def customData( self, key, default = None ):
        """
        Returns the custom information linked with this profile for the given
        tag.
        
        :param      key     | <str>
                    default | <variant> || None
        
        :return     <variant>
        """
        return self._customData.value(key, default)
    
    def description( self ):
        """
        Returns the description of this profile.
        
        :return     <str>
        """
        return self._description
    
    def duplicate( self ):
        """
        Create a duplicate of this profile and returns it.
        
        :return     <XViewProfile>
        """
        out = XViewProfile()
        
        out._icon = self._icon
        out._name = self._name
        out._description = self._description
        out._customData  = copy.deepcopy(self._customData)
        out._xmlElement  = copy.deepcopy(self._xmlElement)
        
        return out
    
    def icon( self ):
        """
        Returns the icon path for this profile.
        
        :return     <str>
        """
        return self._icon
    
    def isEmpty( self ):
        """
        Returns whether or not this profile is empty or not.  This is determined
        if it actually defines any view data or not.
        
        :return     <bool>
        """
        return self._xmlElement is None
    
    def name( self ):
        """
        Returns the name of this profile.
        
        :return     <str>
        """
        return self._name
    
    def restore(self, viewWidget):
        """
        Applies the profile to the inputed view widget.
        
        :param      viewWidget | <XViewWidget>
        """
        if self._xmlElement is None:
            viewWidget.reset(force = True)
            return False
        
        # disable all the information
        viewWidget.blockSignals(True)
        viewWidget.setUpdatesEnabled(False)
        viewWidget.setCursor(Qt.WaitCursor)
        
        # reset the view widget
        if not viewWidget.canClose():
            viewWidget.blockSignals(False)
            viewWidget.setUpdatesEnabled(True)
            
            return False
        
        # close all the views (handles additional closing logic for threads and
        # cleanup)
        for view in viewWidget.findChildren(XView):
            view.close()
            view.deleteLater()
        
        # clear the reset data
        oldwidget = viewWidget.takeWidget()
        if oldwidget:
            oldwidget.close()
            oldwidget.deleteLater()
        
        # restore the widget data
        widget = self.restoreWidget(viewWidget,
                                    viewWidget,
                                    self._xmlElement[0])
                                    
        viewWidget.setWidget(widget)
        viewWidget.setLocked(self._xmlElement.get('locked') == 'True')
        
        # enable the infromation
        viewWidget.unsetCursor()
        viewWidget.blockSignals(False)
        viewWidget.setUpdatesEnabled(True)
        return True
    
    def restoreWidget( self, viewWidget, parent, xwidget ):
        """
        Creates the widget with the inputed parent based on the given xml type.
        
        :param      viewWidget  | <XViewWidget>
                    parent      | <QWidget>
                    xwidget     | <xml.etree.Element>
        
        :return     <QWidget>
        """
        # create a new splitter
        if ( xwidget.tag == 'split' ):
            widget = XSplitter(parent)
            
            if ( xwidget.get('orient') == 'horizontal' ):
                widget.setOrientation( Qt.Horizontal )
            else:
                widget.setOrientation( Qt.Vertical )
            
            # restore the children
            for xchild in xwidget:
                widget.addWidget( self.restoreWidget( viewWidget,
                                                      widget,
                                                      xchild ) )
                                                     
            widget.restoreState(QByteArray.fromBase64(xwidget.get('state')))
            
            return widget
        
        # create a new panel
        elif ( xwidget.tag == 'panel' ):
            widget = XViewPanel(parent)
            widget.blockSignals(True)
            
            # restore the children
            for xchild in xwidget:
                child = self.restoreWidget( viewWidget,
                                            widget,
                                            xchild )
                
                if ( not child ):
                    err = 'Missing View Type: %s' % xchild.get('type')
                    logger.warning(err)
                    continue
                
                widget.addTab(child, child.windowTitle())
            
            widget.setCurrentIndex(int(xwidget.get('current', 0)))
            widget.blockSignals(False)
            widget.markCurrentChanged()
            
            view = widget.currentWidget()
            if isinstance(view, XView):
                view.initialize(force=True)
            
            return widget
        
        # create a new view
        else:
            viewType = viewWidget.findViewType( xwidget.get('type') )
            if ( not viewType ):
                return None
            
            widget = viewType.createInstance(parent)
            widget.setObjectName(xwidget.get('name'))
            widget.restoreXml(xwidget)
            widget.setViewingGroup(int(xwidget.get('group', 0)))
            
            title = xwidget.get('title')
            if ( title ):
                widget.setWindowTitle(title)
            
            return widget
    
    def save( self, filename ):
        """
        Saves the xml data to the inputed filename.
        
        :param      filename | <str>
        """
        projex.text.xmlindent(self.xmlElement())
        
        try:
            f = open(filename, 'w')
        except IOError:
            logger.exception('Could not save file: %s' % filename)
            return False
            
        f.write(self.toString())
        f.close()
        return True
    
    def setCustomData( self, key, value ):
        """
        Sets the value for the profile to the inputed value at the given key.
        
        :param      key | <str>
                    value | <variant>
        """
        self._customData.setValue(key, value)
    
    def setDescription( self, description ):
        """
        Sets the description of this profile to the inputed description.
        
        :param      description | <str>
        """
        if description is not None:
            self._description = description
    
    def setIcon( self, icon ):
        """
        Sets the path to the icon for this profile to the given icon.
        
        :param      icon | <str>
        """
        self._icon = icon
    
    def setName( self, name ):
        """
        Sets the name for this profile.
        
        :param      name | <str>
        """
        self._name = name
    
    def setXmlElement( self, element ):
        """
        Sets the xml data that defines this profile to the inputed value.
        
        :param      element | <xml.etree.Element>
        """
        self._xmlElement = copy.deepcopy(element)
    
    def toXml( self, xparent = None ):
        """
        Converts the data for this profile into an XML blob.
        
        :return     <xml.etree.ElementTree.Element>
        """
        if ( xparent is not None ):
            xprofile = ElementTree.SubElement(xparent, 'profile')
        else:
            xprofile = ElementTree.Element('profile')
        
        xprofile.set('version', '2')
        xprofile.set('name', self.name())
        xprofile.set('icon', self.icon())
        
        xdata = ElementTree.SubElement(xprofile, 'data')
        self._customData.toXml(xdata)
        
        xdesc = ElementTree.SubElement(xprofile, 'desc')
        xdesc.text = self.description()
        
        if ( self._xmlElement is not None ):
            xlayout = copy.deepcopy(self._xmlElement)
            xlayout.tag = 'layout'
            xprofile.append(xlayout)
        
        return xprofile
    
    def toString( self ):
        """
        Converts the data about this view widget into a string value.
        
        :return     <str>
        """
        xprofile = self.toXml()
        projex.text.xmlindent(xprofile)
        return ElementTree.tostring(xprofile)
    
    def xmlElement( self ):
        """
        Returns the xml element that defines this profile.
        
        :return     <xml.etree.Element> || None
        """
        return self._xmlElement
    
    @staticmethod
    def recordWidget(xparent, widget):
        """
        Records the inputed widget to the parent profile.
        
        :param      xparent | <xml.etree.Element>
                    widget  | <QWidget>
        """
        # record a splitter
        if isinstance(widget, XSplitter):
            xwidget = ElementTree.SubElement(xparent, 'split')
            if ( widget.orientation() == Qt.Horizontal ):
                xwidget.set('orient', 'horizontal')
            else:
                xwidget.set('orient', 'vertical')
            
            xwidget.set('state', str(widget.saveState().toBase64()))
            
            # record sub-widgets
            for i in range(widget.count()):
                XViewProfile.recordWidget(xwidget, widget.widget(i))
        
        # record a view panel
        elif isinstance(widget, XViewPanel):
            xwidget = ElementTree.SubElement(xparent, 'panel')
            xwidget.set('current', str(widget.currentIndex()))
            for i in range(widget.count()):
                XViewProfile.recordWidget(xwidget, widget.widget(i))
        
        # record a view
        elif widget is not None:
            xwidget = ElementTree.SubElement(xparent, 'view')
            xwidget.set('name',  str(widget.objectName()))
            xwidget.set('title', str(widget.windowTitle()))
            xwidget.set('type',  str(widget.viewTypeName()))
            xwidget.set('group', str(widget.viewingGroup()))
            
            widget.saveXml(xwidget)
    
    @staticmethod
    def record( viewWidget ):
        """
        Records the state for the inputed view widget into data.
        
        :param      viewWidget | <XViewWidget>
        """
        profile = XViewProfile()
        
        xprofile = ElementTree.Element('profile')
        xprofile.set('locked', str(viewWidget.isLocked()))
        XViewProfile.recordWidget(xprofile, viewWidget.widget())
        profile.setXmlElement(xprofile)
        
        return profile
    
    @staticmethod
    def fromXml( xprofile ):
        """
        Restores the profile information from XML.
        
        :param      xprofile | <xml.etree.ElementTree.Element>
        
        :return     <XViewProfile>
        """
        # determine the proper version
        if ( xprofile.tag != 'profile' ):
            return XViewProfile()
        
        version = int(xprofile.get('version', '1'))
        
        # load the legacy information - just layout data
        if ( version == 1 ):
            prof = XViewProfile()
            prof.setXmlElement(xprofile)
            return prof
        
        # load latest information
        prof = XViewProfile()
        prof.setName(xprofile.get('name', ''))
        prof.setIcon(xprofile.get('icon', ''))
        
        # restore data
        xdata = xprofile.find('data')
        if ( xdata is not None ):
            prof._customData = DataSet.fromXml(xdata)
        
        # load description
        xdesc = xprofile.find('desc')
        if ( xdesc is not None ):
            prof.setDescription(xdesc.text)
        
        # load layout
        xlayout = xprofile.find('layout')
        if ( xlayout is not None ):
            prof.setXmlElement(xlayout)
        
        return prof
    
    @staticmethod
    def fromString( strdata ):
        """
        Generates profile data from the inputed string data.
        
        :param      strdata | <str>
        
        :return     <XViewProfile>
        """
        if ( strdata ):
            try:
                xprofile = ElementTree.fromstring(str(strdata))
            except ExpatError:
                return XViewProfile()
            
            return XViewProfile.fromXml(xprofile)
        return XViewProfile()
    
    @staticmethod
    def load( filename ):
        """
        Loads the profile from the inputed filename.
        
        :param      filename | <str>
        """
        try:
            f = open(filename, 'r')
            
        except IOError:
            logger.exception('Could not load the file: %s' % filename)
            return False
        
        strdata = f.read()
        f.close()
        
        return XViewProfile.fromString(strdata)