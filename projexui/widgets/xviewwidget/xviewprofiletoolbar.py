""" Defines the XViewProfileToolBar class """

# define authorship information
__authors__         = ['Eric Hulser']
__author__          = ','.join(__authors__)
__credits__         = []
__copyright__       = 'Copyright (c) 2011, Projex Software, LLC'
__license__         = 'LGPL'

__maintainer__      = 'Projex Software, LLC'
__email__           = 'team@projexsoftware.com'

import os.path

from projexui.qt import Signal,\
                        Slot,\
                        Property,\
                        PyObject,\
                        wrapVariant,\
                        unwrapVariant
from projexui.qt.QtCore import Qt,\
                               QSize

from projexui.qt.QtGui import QAction,\
                              QActionGroup,\
                              QApplication,\
                              QCursor,\
                              QIcon,\
                              QMenu,\
                              QMessageBox,\
                              QFileDialog

from xml.etree          import ElementTree
from xml.parsers.expat  import ExpatError

import projex.text

from projexui import resources
from projexui.widgets.xtoolbar import XToolBar
from projexui.widgets.xviewwidget.xviewprofile import XViewProfile
from projexui.widgets.xviewwidget.xviewprofiledialog import XViewProfileDialog

class XViewProfileAction(QAction):
    def __init__( self, profile, parent = None ):
        super(XViewProfileAction, self).__init__(parent)
        
        # create custom properties
        self._profile = None
        
        # set default options
        self.setCheckable(True)
        self.setProfile(profile)
    
    def profile( self ):
        """
        Returns the profile linked with this action.
        
        :return     <projexui.widgets.xviewwidget.XViewProfile>
        """
        return self._profile
    
    def setProfile( self, profile ):
        """
        Sets the profile linked with this action.
        
        :param      profile | <projexui.widgets.xviewwidget.XViewProfile>
        """
        self._profile = profile
        
        # update the interface
        self.setIcon(QIcon(os.path.expandvars(profile.icon())))
        self.setText(profile.name())
        self.setToolTip(profile.description())

#------------------------------------------------------------------------------

class XViewProfileToolBar(XToolBar):
    profileCreated        = Signal(PyObject)
    profileChanged        = Signal(PyObject)
    profileRemoved        = Signal(PyObject)
    currentProfileChanged = Signal(PyObject)
    
    def __init__( self, parent ):
        super(XViewProfileToolBar, self).__init__(parent)
        
        # create custom properties
        self._editingEnabled    = True
        self._viewWidget        = None
        self._profileGroup      = QActionGroup(self)
        
        # set the default options
        self.setIconSize(QSize(48, 48))
        self.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        
        # create connections
        self.actionTriggered.connect(self.handleActionTrigger)
        self.customContextMenuRequested.connect(self.showProfileMenu)
        
    def addProfile(self, profile):
        """
        Adds the inputed profile as an action to the toolbar.
        
        :param      profile | <projexui.widgets.xviewwidget.XViewProfile>
        """
        act = XViewProfileAction(profile, self)
        self._profileGroup.addAction(act)
        self.addAction(act)
        return act
    
    def currentProfile( self ):
        """
        Returns the current profile for this toolbar.
        
        :return     <projexui.widgets.xviewwidget.XViewProfile> || None
        """
        act = self._profileGroup.checkedAction()
        if ( act ):
            return act.profile()
        return None
    
    def createProfile( self, profile = None, clearLayout = True ):
        """
        Prompts the user to create a new profile.
        """
        if ( profile ):
            prof = profile
        elif ( not self.viewWidget() or clearLayout ):
            prof = XViewProfile()
        else:
            prof = self.viewWidget().saveProfile()
        
        blocked = self.signalsBlocked()
        self.blockSignals(False)
        changed = self.editProfile(prof)
        self.blockSignals(blocked)
        
        if ( not changed ):
            return
        
        act = self.addProfile(prof)
        act.setChecked(True)
        
        # update the interface
        if ( self.viewWidget() and (profile or clearLayout) ):
            self.viewWidget().restoreProfile(prof)
        
        if ( not self.signalsBlocked() ):
            self.profileCreated.emit(prof)
    
    @Slot(PyObject)
    def editProfile( self, profile ):
        """
        Prompts the user to edit the given profile.
        
        :param      profile | <projexui.widgets.xviewwidget.XViewProfile>
        """
        mod = XViewProfileDialog.edit(self, profile)
        if ( not mod ):
            return False
        
        # update the action interface
        for act in self._profileGroup.actions():
            if ( act.profile() == profile ):
                act.setProfile(profile)
                break
        
        # signal the change
        if ( not self.signalsBlocked() ):
            self.profileChanged.emit(profile)
        
        return True
    
    def exportProfiles( self, filename = None ):
        """
        Exports this toolbar to the given filename.
        
        :param      filename | <str> || None
        """
        if ( not filename ):
            filename = QFileDialog.getSaveFileName(self,
                                                   'Export Toolbar',
                                                   '',
                                                   'Toolbar Files (*.xtool)')
        
        if ( not filename ):
            return False
        
        profile_xml = self.toXml()
        
        projex.text.xmlindent(profile_xml)
        profile_string = ElementTree.tostring(profile_xml)
        
        f = open(str(filename), 'w')
        f.write(profile_string)
        f.close()
        
        return True
    
    def handleActionTrigger(self, action):
        """
        Handles when an action has been triggered.  If the inputed action is a 
        XViewProfileAction, then the currentProfileChanged signal will emit.
        
        :param      action | <QAction>
        """
        # trigger a particular profile
        if ( isinstance(action, XViewProfileAction) ):
            if ( not self.signalsBlocked() ):
                self.currentProfileChanged.emit(action.profile())
            
            if ( self._viewWidget ):
                self._viewWidget.restoreProfile(action.profile())
    
    def importProfiles( self, filename = None ):
        """
        Imports the profiles from the given filename.
        
        :param      filename | <str> || None
        """
        if ( not filename ):
            filename = QFileDialog.getOpenFileName( self,
                                                    'Import Toolbar',
                                                    '',
                                                    'Toolbar Files (*.xtool)')
            
            if type(filename) == tuple:
                filename = str(filename[0])
            
        if ( not (filename and os.path.exists(filename)) ):
            return False
        
        f = open(str(filename), 'r')
        profile_string = f.read()
        f.close()
        
        self.loadString(profile_string)
        
        # load the default toolbar
        action = self._profileGroup.checkedAction()
        if ( action ):
            self.handleActionTrigger(action)
    
    def isEditingEnabled( self ):
        """
        Sets whether or not the create is enabled for this toolbar.
        
        :return     <bool>
        """
        return self._editingEnabled
    
    def isEmpty( self ):
        """
        Returns whether or not this toolbar is empty.
        
        :return     <bool>
        """
        return len(self._profileGroup.actions()) == 0
    
    def loadString( self, profilestr ):
        """
        Loads the information for this toolbar from the inputed string.
        
        :param      profilestr | <str>
        """
        try:
            xtoolbar = ElementTree.fromstring(str(profilestr))
        except ExpatError, e:
            return
        
        self.clear()
        curr = xtoolbar.get('current')
        
        for xprofile in xtoolbar:
            prof = XViewProfile.fromXml(xprofile)
            act  = self.addProfile(prof)
            if ( prof.name() == curr ):
                act.setChecked(True)
    
    def profiles( self ):
        """
        Returns a list of profiles for this toolbar.
        
        :return     <projexui.widgets.xviewwidget.XViewProfile>
        """
        output = []
        for act in self.actions():
            if ( isinstance(act, XViewProfileAction) ):
                output.append(act.profile())
        return output
    
    def restoreSettings( self, settings ):
        """
        Restores this profile from settings.
        
        :param      settings | <QSettings>
        """
        value = unwrapVariant(settings.value('profile_toolbar'))
        if ( not value ):
            return
        
        self.loadString(value)
    
    @Slot(PyObject)
    def removeProfile( self, profile ):
        """
        Removes the given profile from the toolbar.
        
        :param      profile | <projexui.widgets.xviewwidget.XViewProfile>
        """
        if ( not profile ):
            return
        
        title = 'Remove Layout'
        opts  = QMessageBox.Yes | QMessageBox.No
        quest = 'Are you sure you want to remove "%s" from the toolbar?'
        quest %= profile.name()
        answer = QMessageBox.question(self, title, quest, opts)
        
        if ( answer == QMessageBox.Yes ):
            # remove the actions from this toolbar
            for act in self.actions():
                if ( isinstance(act, XViewProfileAction) ):
                    if ( act.profile() == profile ):
                        self.removeAction(act)
                        self._profileGroup.removeAction(act)
                        break
            
            if ( not self.signalsBlocked() ):
                self.profileRemoved.emit(profile)
    
    def setEditingEnabled( self, state ):
        """
        Sets whether or not the creation is enabled for this toolbar.
        
        :param      state | <bool>
        """
        self._editingEnabled = state
    
    def setViewWidget( self, viewWidget ):
        """
        Sets the view widget linked with this toolbar.
        
        :param      viewWidget | <XViewWidget>
        """
        self._viewWidget = viewWidget
    
    def saveSettings( self, settings ):
        """
        Saves these profiles as settings.
        
        :param      settings | <QSettings>
        """
        settings.setValue('profile_toolbar', wrapVariant(self.toString()))
    
    def saveProfileLayout( self, profile ):
        """
        Saves the profile layout to the inputed profile.
        
        :param      profile | <projexui.widgets.xviewwidget.XViewProfile>
        """
        if ( not self.viewWidget() ):
            QMessageBox.information(self, 
                                    'Could Not Save Layout',
                                    'Error saving layout, '\
                                    'No View Widget Assigned')
            return
        
        # save the profile from the view widget
        prof = self.viewWidget().saveProfile()
        profile.setXmlElement(prof.xmlElement())
        
        if ( not self.signalsBlocked() ):
            self.profileChanged.emit(profile)
    
    @Slot(PyObject)
    def setCurrentProfile( self, profile ):
        """
        Sets the current profile for this toolbar to the inputed profile.
        
        :param      profile | <projexui.widgets.xviewwidget.XViewProfile>
        """
        blocked = self.signalsBlocked()
        self.blockSignals(True)
        for act in self._profileGroup.actions():
            profileact.setChecked(act.profile())
        self.blockSignals(blocked)
        
        if ( not blocked ):
            self.currentProfileChanged.emit(profile)
    
    def showProfileMenu( self, point ):
        """
        Prompts the user for profile menu options.  Editing needs to be enabled
        for this to work.
        """
        if ( not self.isEditingEnabled() ):
            return
        
        trigger = self.actionAt(point)
        if (isinstance(trigger, XViewProfileAction)):
            prof = trigger.profile()
        else:
            prof = None
        
        # define the menu
        menu = QMenu(self)
        
        new_act  = menu.addAction('New Blank Layout...')
        new_act.setIcon( QIcon(resources.find('img/add.png')))
        
        if ( prof ):
            edit_act = menu.addAction('Edit Information...')
            menu.addSeparator()
            
            save_act    = menu.addAction('Save from Current Layout')
            copy_act    = menu.addAction('Copy Layout')
            copy_as_act = menu.addAction('Copy Layout as...')
            paste_act   = menu.addAction('Paste Layout')
            
            menu.addSeparator()
            
            export_act  = menu.addAction('Export Toolbar...')
            import_act  = menu.addAction('Import Toolbar...')
            
            menu.addSeparator()
            
            rem_act  = menu.addAction('Remove Layout')
            
            # set the icons
            save_act.setIcon(QIcon(resources.find('img/save.png')))
            edit_act.setIcon(QIcon(resources.find('img/edit.png')))
            copy_act.setIcon(QIcon(resources.find('img/copy.png')))
            paste_act.setIcon(QIcon(resources.find('img/paste.png')))
            rem_act.setIcon( QIcon(resources.find('img/remove.png')))
            
            create_current_act = -1
        else:
            create_current_act    = menu.addAction('New from Current Layout...')
            
            menu.addSeparator()
            
            paste_act   = menu.addAction('Paste Layout')
            
            menu.addSeparator()
            
            export_act  = menu.addAction('Export Toolbar...')
            import_act  = menu.addAction('Import Toolbar...')
            
            save_act    = -1
            edit_act    = -1
            copy_act    = -1
            copy_as_act = -1
            rem_act     = -1
            
            paste_act.setIcon(QIcon(resources.find('img/paste.png')))
            
        # run the menu
        act = menu.exec_(QCursor.pos())
        
        # create a new profile
        if ( act == new_act ):
            self.createProfile()
        
        # create a new clear profile
        elif ( act == create_current_act ):
            self.createProfile(clearLayout = False)
        
        # edit an existing profile
        elif ( act == edit_act ):
            self.editProfile(prof)
        
        # save or create a new profile
        elif ( act == save_act ):
            self.saveProfileLayout(prof)
            
        # copy profile
        elif ( act == copy_act ):
            QApplication.clipboard().setText(prof.toString())
        
        # copy profile as
        elif ( act == copy_as_act ):
            self.createProfile(profile = prof.duplicate())
        
        # export
        elif ( act == export_act ):
            self.exportProfiles()
        
        # export
        elif ( act == import_act ):
            self.importProfiles()
        
        # paste profile
        elif ( act == paste_act ):
            text = QApplication.clipboard().text()
            prof = XViewProfile.fromString(text)
            if ( not prof.isEmpty() ):
                self.createProfile(profile = prof)
        
        # remove the profile
        elif ( act == rem_act ):
            self.removeProfile(prof)
    
    def toString( self ):
        """
        Saves this profile toolbar as string information.
        
        :return     <str>
        """
        return ElementTree.tostring(self.toXml())
    
    def toXml( self ):
        """
        Saves this profile toolbar as XML information.
        
        :return     <xml.etree.ElementTree.Element>
        """
        xtoolbar = ElementTree.Element('toolbar')
        
        act = self._profileGroup.checkedAction()
        if ( act ):
            xtoolbar.set('current', act.profile().name())
        
        for profile in self.profiles():
            profile.toXml(xtoolbar)
        
        return xtoolbar
    
    def viewWidget( self ):
        """
        Returns the view widget linked with this toolbar.
        
        :return     <projexui.widgets.xviewwidget.XViewWidget>
        """
        return self._viewWidget
    
    x_editingEnabled = Property(bool, isEditingEnabled, setEditingEnabled)