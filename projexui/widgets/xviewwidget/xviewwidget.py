#!/usr/bin python

""" Defines the main container widget for a view system. """

# define authorship information
__authors__     = ['Eric Hulser']
__author__      = ','.join(__authors__)
__credits__     = []
__copyright__   = 'Copyright (c) 2011, Projex Software'

# maintanence information
__maintainer__  = 'Projex Software'
__email__       = 'team@projexsoftware.com'

from projexui.qt import Slot, wrapVariant, unwrapVariant, PyObject
from projexui.qt.QtCore import QDir, Qt

from projexui.qt.QtGui import QCursor, \
                              QIcon,\
                              QMenu, \
                              QMessageBox,\
                              QScrollArea,\
                              QFileDialog,\
                              QPalette

import projexui.resources

from projexui.widgets.xviewwidget.xview          import XView
from projexui.widgets.xviewwidget.xviewpanel     import XViewPanel
from projexui.widgets.xviewwidget.xviewpanelmenu import XViewPanelMenu
from projexui.widgets.xviewwidget.xviewprofile   import XViewProfile

class XViewWidget(QScrollArea):
    __designer_icon__ = projexui.resources.find('img/ui/scrollarea.png')
    
    def __init__( self, parent ):
        super(XViewWidget, self).__init__(parent)
        
        # intiailize the scroll area
        self.setBackgroundRole(QPalette.Window)
        self.setFrameShape( QScrollArea.NoFrame )
        self.setWidgetResizable(True)
        self.setWidget(XViewPanel(self))
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        
        # define custom properties
        self._customData        = {}
        self._viewTypes         = []
        self._locked            = False
        self._panelMenu         = None
        self._interfaceMenu     = None
        self._defaultProfile    = None
        
        self.customContextMenuRequested.connect(self.showMenu)
    
    def canClose( self ):
        """
        Checks to see if the view widget can close by checking all of its \
        sub-views to make sure they're ok to close.
        
        :return     <bool>
        """
        for view in self.findChildren(XView):
            if ( not view.canClose() ):
                return False
        return True
    
    def createMenu( self, parent ):
        """
        Creates a new menu for the inputed parent item.
        
        :param      parent | <QMenu>
        """
        menu = QMenu(parent)
        menu.setTitle('&View')
        
        act = menu.addAction('Lock/Unlock Layout')
        act.setIcon(QIcon(projexui.resources.find('img/view/lock.png')))
        act.triggered.connect(self.toggleLocked)
        
        menu.addSeparator()
        act = menu.addAction('Export Layout as...')
        act.setIcon(QIcon(projexui.resources.find('img/view/export.png')))
        act.triggered.connect(self.exportProfile)
        
        act = menu.addAction('Import Layout from...')
        act.setIcon(QIcon(projexui.resources.find('img/view/import.png')))
        act.triggered.connect(self.importProfile)
        
        menu.addSeparator()
        act = menu.addAction('Reset Layout')
        act.setIcon(QIcon(projexui.resources.find('img/view/remove.png')))
        act.triggered.connect(self.reset)
        
        return menu
    
    def currentPanel( self ):
        """
        Returns the currently active panel based on whether or not it has \
        focus.
        
        :return     <XViewPanel>  || None
        """
        panels = self.panels()
        for panel in panels:
            if ( panel.hasFocus() ):
                return panel
        
        if ( panels ):
            return panels[0]
        
        return None
    
    def currentView( self ):
        """
        Returns the current view for this widget.
        
        :return     <projexui.widgets.xviewwidget.XView> || NOne
        """
        panel = self.currentPanel()
        if ( panel ):
            return panel.currentWidget()
        return None
    
    def customData( self, key, default = None ):
        """
        Returns the custom data for the given key.
        
        :param      key     | <str>
                    default | <variant>
        
        :return     <variant>
        """
        return self._customData.get(str(key), default)
    
    def defaultProfile( self ):
        """
        Returns the default profile for this view widget.
        
        :return     <XViewProfile>
        """
        return self._defaultProfile
    
    def exportProfile( self, filename  = '' ):
        """
        Exports the current profile to a file.
        
        :param      filename | <str>
        """
        if not (filename and isinstance(filename, basestring)):
            filename = QFileDialog.getSaveFileName( self,
                                                    'Export Layout as...',
                                                    QDir.currentPath(),
                                                    'XView (*.xview)')
            
            if type(filename) == tuple:
                filename = filename[0]
        
        filename = str(filename)
        if not filename:
            return
        
        if not filename.endswith('.xview'):
            filename += '.xview'
        
        profile = self.saveProfile()
        profile.save(filename)
        
    def findViewType( self, viewTypeName ):
        """
        Looks up the view type based on the inputed view type name.
        
        :param      viewTypeName | <str>
        """
        for viewType in self._viewTypes:
            if ( viewType.viewTypeName() == viewTypeName ):
                return viewType
        return None
    
    def importProfile( self, filename  = '' ):
        """
        Exports the current profile to a file.
        
        :param      filename | <str>
        """
        if ( not (filename and isinstance(filename, basestring)) ):
            filename = QFileDialog.getOpenFileName( self,
                                                    'Import Layout from...',
                                                    QDir.currentPath(),
                                                    'XView (*.xview)')
            
            if type(filename) == tuple:
                filename = str(filename[0])
        
        filename = str(filename)
        if not filename:
            return
        
        if not filename.endswith('.xview'):
            filename += '.xview'
        
        profile = XViewProfile.load(filename)
        if ( not profile ):
            return
            
        profile.restore(self)
        
    def isLocked( self ):
        """
        Returns whether or not this widget is in locked mode.
        
        :return     <bool>
        """
        return self._locked
    
    def panels( self ):
        """
        Returns a lis of the panels that are assigned to this view widget.
        
        :return     [<XViewPanel>, ..]
        """
        return self.findChildren(XViewPanel)
    
    def registerViewType( self, cls, window = None ):
        """
        Registers the inputed widget class as a potential view class.  If the \
        optional window argument is supplied, then the registerToWindow method \
        will be called for the class.
        
        :param          cls     | <subclass of XView>
                        window  | <QMainWindow> || <QDialog> || None
        """
        if ( not cls in self._viewTypes ):
            self._viewTypes.append(cls)
            
            if ( window ):
                cls.registerToWindow(window)
    
    @Slot(PyObject)
    def restoreProfile( self, profile ):
        """
        Restores the profile settings based on the inputed profile.
        
        :param      profile | <XViewProfile>
        """
        return profile.restore(self)
    
    def restoreSettings( self, settings ):
        """
        Restores the current structure of the view widget from the inputed \
        settings instance.
        
        :param      settings | <QSettings>
        """
        key     = self.objectName()
        value   = unwrapVariant(settings.value('%s/profile' % key))
        
        if ( not value ):
            self.reset(force = True)
            return False
            
        profile = value
        
        # restore the view type settings
        for viewType in self.viewTypes():
            viewType.restoreGlobalSettings(settings)
        
        # restore the profile
        self.restoreProfile(XViewProfile.fromString(profile))
        
        if ( not self.views() ):
            self.reset(force = True)
        
        return True
    
    def reset( self, force = False ):
        """
        Clears out all the views and panels and resets the widget to a blank \
        parent.
        
        :return     <bool>
        """
        answer = QMessageBox.Yes
        opts = QMessageBox.Yes | QMessageBox.No
        
        if not force:
            answer = QMessageBox.question( self,
                                           'Reset Layout',
                                           'Are you sure you want to reset?',
                                           opts )
        
        if answer == QMessageBox.No:
            return
            
        prof = self.defaultProfile()
        if prof:
            return prof.restore(self)
        
        widget = self.widget()
        
        # we should always have a widget, but double check
        if not widget:
            return False
        
        # make sure we can close the current view
        if not widget.close():
            return False
        
        # reset the system
        self.takeWidget()
        widget.deleteLater()
        
        # set a new widget
        self.setWidget(XViewPanel(self))
        
        return True
    
    def saveProfile( self ):
        """
        Saves the profile for the current state and returns it.
        
        :return     <XViewProfile>
        """
        return XViewProfile.record(self)
    
    def saveSettings( self, settings ):
        """
        Records the current structure of the view widget to the inputed \
        settings instance.
        
        :param      settings | <QSettings>
        """
        # record the profile
        profile = self.saveProfile()
        key     = self.objectName()
        
        settings.setValue('%s/profile' % key, wrapVariant(profile.toString()))
        
        # record the view type settings
        for viewType in self.viewTypes():
            viewType.saveGlobalSettings(settings)
    
    def setCurrent( self ):
        """
        Sets this view widget as the current widget in case there are multiple
        ones.
        """
        for view in self.findChildren(XView):
            view.setCurrent()
    
    def setCustomData( self, key, value ):
        """
        Sets the custom data for this instance to the inputed value.
        
        :param      key     | <str>
                    value   | <variant>
        """
        self._customData[str(key)] = value
    
    def setDefaultProfile( self, profile ):
        """
        Sets the default profile for this view to the inputed profile.
        
        :param      profile | <XViewProfile>
        """
        self._defaultProfile = profile
    
    def setLocked( self, state ):
        """
        Sets the locked state for this view widget.  When locked, a user no \
        longer has control over editing views and layouts.  A view panel with \
        a single entry will hide its tab bar, and if it has multiple views, it \
        will simply hide the editing buttons.
        
        :param      state | <bool>
        """
        self._locked = state
        
        for panel in self.panels():
            panel.setLocked(state)
    
    def setViewTypes( self, viewTypes, window = None ):
        """
        Sets the view types that can be used for this widget.  If the optional \
        window member is supplied, then the registerToWindow method will be \
        called for each view.
        
        :param      viewTypes | [<sublcass of XView>, ..]
                    window    | <QMainWindow> || <QDialog> || None
        """
        if ( window ):
            for viewType in self._viewTypes:
                viewType.unregisterFromWindow(window)
            
        self._viewTypes = viewTypes[:]
        
        if ( window ):
            for viewType in viewTypes:
                viewType.registerToWindow(window)
    
    def showMenu(self, point=None):
        """
        Displays the menu for this view widget.
        
        :param      point | <QPoint>
        """
        if point is None:
            point = QCursor.pos()
        else:
            point = self.mapToGlobal(point)
        
        menu = self.createMenu(self)
        menu.exec_(point)
        menu.deleteLater()
    
    def showInterfaceMenu( self, panel, point = None ):
        """
        Creates the interface menu for this view widget.  If no point is \
        supplied, then the current cursor position will be used.
        
        :param      panel | <XViewPanel>
                    point | <QPoint> || None
        """
        if not self._interfaceMenu:
            self._interfaceMenu = XViewPanelMenu(self, True)
        
        if ( not point ):
            point = QCursor.pos()
        
        self._interfaceMenu.setCurrentPanel(panel)
        self._interfaceMenu.exec_(point)
    
    def showPanelMenu( self, panel, point = None ):
        """
        Creates the panel menu for this view widget.  If no point is supplied,\
        then the current cursor position will be used.
        
        :param      panel   | <XViewPanel>
                    point   | <QPoint> || None
        """
        if not self._panelMenu:
            self._panelMenu = XViewPanelMenu(self)
            
        if ( not point ):
            point = QCursor.pos()
        
        self._panelMenu.setCurrentPanel(panel)
        self._panelMenu.exec_(point)
    
    def toggleLocked( self ):
        """
        Toggles whether or not this view is locked 
        """
        self.setLocked(not self.isLocked())
    
    def unregisterViewType( self, cls, window = None ):
        """
        Unregisters the view at the given name.  If the window option is \
        supplied then the unregisterFromWindow method will be called for the \
        inputed class.
        
        :param          cls    | <subclass of XView>    
                        window | <QMainWindow> || <QDialog> || None
        
        :return     <bool> changed
        """
        if ( cls in self._viewTypes ):
            self._viewTypes.remove(cls)
            
            if ( window ):
                cls.unregisterFromWindow(window)
                
            return True
        return False
    
    def views( self ):
        """
        Returns a list of the current views associated with this view widget.
        
        :return     [<XView>, ..]
        """
        return self.findChildren(XView)
    
    def viewType( self, name ):
        """
        Looks up the view class based on the inputd name.
        
        :param      name | <str>
        
        :return     <subclass of XView> || None
        """
        for view in self._viewTypes:
            if ( view.viewName() == name ):
                return view
        return None
    
    def viewTypes( self ):
        """
        Returns a list of all the view types registered for this widget.
        
        :return     <str>
        """
        return sorted(self._viewTypes, key = lambda x: x.viewName())