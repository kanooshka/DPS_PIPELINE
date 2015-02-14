#!/usr/bin python

""" Defines the base View plugin class for the ViewWidget system. """

# define authorship information
__authors__     = ['Eric Hulser']
__author__      = ','.join(__authors__)
__credits__     = []
__copyright__   = 'Copyright (c) 2011, Projex Software'

# maintanence information
__maintainer__  = 'Projex Software'
__email__       = 'team@projexsoftware.com'

from xml.etree import ElementTree

import weakref

from projexui import qt #import Signal, SIGNAL
from PyQt4.QtCore   import Qt,\
                                 QObject,\
                                 QSettings,\
                                 QThread,\
                                 QTimer
                           
from PyQt4.QtGui    import QApplication,\
                                 QWidget,\
                                 QDialog,\
                                 QVBoxLayout

from projexui.widgets.xloaderwidget import XLoaderWidget

from projex.enum        import enum
from projex.decorators  import deprecatedmethod, wraps
from projexui           import resources

def xviewSlot(*typs, **opts):
    """
    Defines a method as being a slot for the XView system.  This will validate
    the method against the signal properties if it is triggered from the
    dispatcher, taking into account currency and grouping for the widget.  
    You can specify the optional policy keyword to define the specific signal
    policy for this slot, otherwise it will use its parent view's policy.
    
    :param      default | <variant> | default return value
                policy  | <XView.SignalPolicy> || None
                
    :usage      |from projexui.widgets.xviewwidget import xviewSlot
                |
                |class A(XView):
                |   @xviewSlot()
                |   def format( self ):
                |       print 'test'
    """
    default = opts.get('default')
    policy  = opts.get('policy')
    
    if typs:
        typ_count = len(typs)
    else:
        typ_count = 0
    
    def decorated(func):
        @wraps(func)
        def wrapped(*args, **kwds):
            if ( args and isinstance(args[0], XView) ):
                validated = args[0].validateSignal(policy)
            else:
                validated = True
            
            if ( validated ):
                new_args = args[:typ_count+1]
                return func(*new_args, **kwds)
            return default
        return wrapped
    return decorated

#------------------------------------------------------------------------------

class XViewDispatcher(QObject):
    """ Class to control signals and slots at a view level """
    
    def __init__( self, viewType ):
        super(XViewDispatcher, self).__init__()
        
        self._viewType = viewType
    
    def viewType( self ):
        """
        Returns the view class type that this dispatcher is linked to.
        
        :return     <subclass of XView>
        """
        return self._viewType

#------------------------------------------------------------------------------

class XViewDispatch(QObject):
    def __init__( self, parent ):
        super(XViewDispatch, self).__init__(parent)
        
        self._signals = set()
        self._blockedSignals = {}
    
    def blockSignal( self, signal, state ):
        """
        Blocks the particular signal.
        
        :param      signal | <str>
                    state  | <bool>
        """
        signal = str(signal)
        if ( state ):
            self._blockedSignals.setdefault(signal, 0)
            self._blockedSignals[signal] += 1
        else:
            val = self._blockedSignals.get(signal, 0)
            val -= 1
            if ( val > 0 ):
                self._blockedSignals[signal] = val
            elif ( val == 0 ):
                self._blockedSignals.pop(signal)
    
    def connect( self, signal, slot ):
        """
        Creates a connection for this instance for the given signal.
        
        :param      signal | <str>
                    slot   | <callable>
        """
        super(XViewDispatch, self).connect(self, SIGNAL(signal), slot)
    
    def emit( self, signal, *args ):
        """
        Emits a signal through the dispatcher.
        
        :param      signal | <str>
                    *args  | additional arguments
        """
        if ( not (self.signalsBlocked() or self.signalBlocked(signal)) ):
            super(XViewDispatch, self).emit(SIGNAL(signal), *args)
    
    def registerSignal( self, signal ):
        """
        Registers a single signal to the system.
        
        :param      signal | <str>
        """
        self._signals.add(signal)
    
    def registerSignals( self, signals ):
        """
        Registers signals to the system.
        
        :param      signals | [<str>, ..]
        """
        self._signals = self._signals.union(signals)
    
    def signalBlocked( self, signal ):
        """
        Returns whether or not the signal is blocked.
        
        :param      signal | <str>
        """
        return str(signal) in self._blockedSignals
    
    def signals( self ):
        return sorted(list(self._signals))

#------------------------------------------------------------------------------

class XView(QWidget):
    activated               = qt.Signal()
    currentStateChanged     = qt.Signal()
    windowTitleChanged      = qt.Signal(str)
    sizeConstraintChanged   = qt.Signal()
    initialized             = qt.Signal()
    visibleStateChanged     = qt.Signal(bool)
    
    _registry       = {}
    _globals        = {}
    
    _viewName           = ''
    _viewGroup          = 'Default'
    _viewIcon           = resources.find('img/view/view.png')
    _viewSingleton      = False
    _popupSingleton     = True
    _popupInstance      = None
    
    _currentViewRef     = None
    _instances          = None
    _instanceSingleton  = None
    _dispatcher         = None
    _dispatch           = {}
    
    __designer_icon__ = resources.find('img/ui/view.png')
    
    SignalPolicy        = enum('BlockIfNotCurrent',
                               'BlockIfNotInGroup',
                               'BlockIfNotVisible',
                               'BlockIfNotInitialized',
                               'NeverBlock')
    
    def __init__(self, parent, autoKillThreads=True):
        super(XView, self).__init__( parent )
        
        if not self._viewSingleton:
            self.setAttribute(Qt.WA_DeleteOnClose)
        
        # define custom properties
        self._initialized = False
        self._destroyThreadsOnClose = True
        self._viewingGroup = 0
        self._signalPolicy = XView.SignalPolicy.BlockIfNotInitialized | \
                             XView.SignalPolicy.BlockIfNotVisible | \
                             XView.SignalPolicy.BlockIfNotInGroup
        
        self._visibleState = False  # storing this state for knowing if a
                                    # widget WILL be visible once Qt finishes
                                    # processing for purpose of signal
                                    # validation.
        
        # setup default properties
        self.setFocusPolicy( Qt.StrongFocus )
        self.setWindowTitle( self.viewName() )
        self.registerInstance(self)
        
        if autoKillThreads:
            QApplication.instance().aboutToQuit.connect(self.killChildThreads)
    
    def canClose( self ):
        return True
    
    def closeEvent( self, event ):
        if self.isViewSingleton():
            self.setParent(None)
        
        # make sure to destroy any threads running on close
        if self.testAttribute(Qt.WA_DeleteOnClose) and \
           self.destroyThreadsOnClose():
            self.killChildThreads()
        
        # clear out any progress loaders
        XLoaderWidget.stopAll(self)
        
        # remove any registered instances
        if self.testAttribute(Qt.WA_DeleteOnClose):
            self.unregisterInstance(self)
        
        super(XView, self).closeEvent(event)
    
    def dispatchConnect( self, signal, slot ):
        """
        Connect the slot for this view to the given signal that gets
        emitted by the XView.dispatch() instance.
        
        :param      signal | <str>
                    slot   | <callable>
        """
        XView.dispatch().connect(signal, slot)
    
    def dispatchEmit( self, signal, *args ):
        """
        Emits the given signal via the XView dispatch instance with the
        given arguments.
        
        :param      signal | <str>
                    args   | <tuple>
        """
        XView.setGlobal('emitGroup', self.viewingGroup())
        XView.dispatch().emit(signal, *args)
    
    def destroyThreadsOnClose( self ):
        """
        Marks whether or not any child threads should be destroyed when \
        this view is closed.
        
        :return     <bool>
        """
        return self._destroyThreadsOnClose
    
    def duplicate( self, parent ):
        """
        Duplicates this current view for another.  Subclass this method to 
        provide any additional duplication options.
        
        :param      parent | <QWidget>
        
        :return     <XView> | instance of this class
        """
        # only return a single singleton instance
        if ( self.isViewSingleton() ):
            return self
            
        output = type(self).createInstance(parent)
        
        # save/restore the current settings
        xdata = ElementTree.Element('data')
        self.saveXml(xdata)
        new_name = output.objectName()
        output.setObjectName(self.objectName())
        output.restoreXml(xdata)
        output.setObjectName(new_name)
        
        return output
    
    def killChildThreads(self):
        """
        Kills all child threads for this view.
        """
        threads = self.findChildren(QThread)
        for thread in threads:
            thread.finished.connect(thread.deleteLater)
            thread.quit()
            thread.wait(100)
    
    def hideEvent(self, event):
        """
        Sets the visible state for this widget.  If it is the first time this
        widget will be visible, the initialized signal will be emitted.
        
        :param      state | <bool>
        """
        super(XView, self).hideEvent(event)
        
        # record the visible state for this widget to be separate of Qt's
        # system to know if this view WILL be visible or not once the 
        # system is done processing.  This will affect how signals are
        # validated as part of the visible slot delegation
        self._visibleState = False
        
        if not self.signalsBlocked():
            self.visibleStateChanged.emit(False)
    
    def initialize(self, force=False):
        """
        Initializes the view if it is visible or being loaded.
        """
        if force or (self.isVisible() and \
                     not self.isInitialized() and \
                     not self.signalsBlocked()):
            
            self._initialized = True
            self.initialized.emit()
    
    def isCurrent( self ):
        return self == self.currentView()
    
    def isInitialized(self):
        """
        Returns whether or not this view has been initialized.  A view will
        be initialized the first time it becomes visible to the user.  You
        can use this to delay loading of information until it is needed by
        listening for the initialized signal.
        
        :return     <bool>
        """
        return self._initialized
    
    @deprecatedmethod('XView', 'Use restoreXml instead.')
    def restoreSettings( self, settings ):
        """
        Restores the settings for this view from the inputed QSettings.
        
        :param      settings | <QSettings>
        """
        pass
    
    def restoreXml( self, xml ):
        """
        Restores the settings for this view from the inputed XML node.
        
        :param      xml | <xml.etree.ElementTree.Element>
        """
        pass
    
    @deprecatedmethod('XView', 'Use saveXml instead.')
    def saveSettings( self, settings ):
        """
        Saves the current settings for this view to the inputed QSettings.
        
        :param      settings | <QSettings>
        """
        pass
    
    def saveXml( self, xml ):
        """
        Saves the settings for this view to the inputed XML node.
        
        :param      xml | <xml.etree.ElementTree.Element>
        """
        pass
    
    def settingsName( self ):
        """
        Returns the default settings name for this view.
        
        :return     <str>
        """
        return 'Views/%s' % self.objectName()
    
    def setCurrent( self, state = True ):
        """
        Marks this view as the current source based on the inputed flag.  \
        This method will return True if the currency changes.
        
        :return     <bool>
        """
        if ( state ):
            changed = self.setCurrentView(self)
            
        elif ( self.currentView() == self ):
            changed = self.setCurrentView(None)
        
        if ( changed and not self.signalsBlocked() ):
            self.currentStateChanged.emit()
            if state:
                self.activated.emit()
        
        return changed
    
    def setDestroyThreadsOnClose( self, state ):
        """
        Marks whether or not any child threads should be destroyed when \
        this view is closed.
        
        :param     state | <bool>
        """
        self._destroyThreadsOnClose = state
    
    def setFixedHeight( self, height ):
        """
        Sets the maximum height value to the inputed height and emits the \
        sizeConstraintChanged signal.
        
        :param      height | <int>
        """
        super(XView, self).setFixedHeight(height)
        
        if ( not self.signalsBlocked() ):
            self.sizeConstraintChanged.emit()
    
    def setFixedWidth( self, width ):
        """
        Sets the maximum width value to the inputed width and emits the \
        sizeConstraintChanged signal.
        
        :param      width | <int>
        """
        super(XView, self).setFixedWidth(width)
        
        if ( not self.signalsBlocked() ):
            self.sizeConstraintChanged.emit()
    
    def setMaximumHeight( self, height ):
        """
        Sets the maximum height value to the inputed height and emits the \
        sizeConstraintChanged signal.
        
        :param      height | <int>
        """
        super(XView, self).setMaximumHeight(height)
        
        if ( not self.signalsBlocked() ):
            self.sizeConstraintChanged.emit()
    
    def setMaximumSize( self, *args ):
        """
        Sets the maximum size value to the inputed size and emits the \
        sizeConstraintChanged signal.
        
        :param      *args | <tuple>
        """
        super(XView, self).setMaximumSize(*args)
        
        if ( not self.signalsBlocked() ):
            self.sizeConstraintChanged.emit()
    
    def setMaximumWidth( self, width ):
        """
        Sets the maximum width value to the inputed width and emits the \
        sizeConstraintChanged signal.
        
        :param      width | <int>
        """
        super(XView, self).setMaximumWidth(width)
        
        if ( not self.signalsBlocked() ):
            self.sizeConstraintChanged.emit()
    
    def setMinimumHeight( self, height ):
        """
        Sets the minimum height value to the inputed height and emits the \
        sizeConstraintChanged signal.
        
        :param      height | <int>
        """
        super(XView, self).setMinimumHeight(height)
        
        if ( not self.signalsBlocked() ):
            self.sizeConstraintChanged.emit()
    
    def setMinimumSize( self, *args ):
        """
        Sets the minimum size value to the inputed size and emits the \
        sizeConstraintChanged signal.
        
        :param      *args | <tuple>
        """
        super(XView, self).setMinimumSize(*args)
        
        if ( not self.signalsBlocked() ):
            self.sizeConstraintChanged.emit()
    
    def setMinimumWidth( self, width ):
        """
        Sets the minimum width value to the inputed width and emits the \
        sizeConstraintChanged signal.
        
        :param      width | <int>
        """
        super(XView, self).setMinimumWidth(width)
        
        if ( not self.signalsBlocked() ):
            self.sizeConstraintChanged.emit()
    
    def setSignalPolicy( self, policy ):
        """
        Sets the signal delegation policy for this instance to the given 
        policy.  By default, signals will be delegates for groups or
        by currency if they are not in a group.  This will not directly
        affect signal propogation, only the result of the validateSignal
        method, so if you want to test against this, then you will need
        to check in your slot.
        
        :param      policy | <XView.SignalPolicy>
        """
        self._signalPolicy = policy
    
    def setViewingGroup( self, grp ):
        """
        Sets the viewing group that this view is associated with.
        
        :param      grp | <int>
        """
        self._viewingGroup = grp
    
    def setWindowTitle( self, title ):
        """
        Sets the window title for this view, and emits the windowTitleChanged \
        signal if the signals are not blocked.  Setting this title will update \
        the tab title for the view within the widget.
        
        :param      title | <str>
        """
        super(XView, self).setWindowTitle(title)
        if ( not self.signalsBlocked() ):
            self.windowTitleChanged.emit(title)
    
    def showActiveState( self, state ):
        """
        Shows this view in the active state based on the inputed state settings.
        
        :param      state | <bool>
        """
        self.setAutoFillBackground(True)
        
        palette = self.window().palette()
        clr = palette.color(palette.Window)
        avg = (clr.red() + clr.green() + clr.blue()) / 3
        
        if ( avg < 180 and state ):
            clr = clr.lighter(105)
        elif ( not state ):
            clr = clr.darker(105)
        
        palette.setColor(palette.Window, clr)
        self.setPalette(palette)
    
    def showEvent(self, event):
        """
        Sets the visible state for this widget.  If it is the first time this
        widget will be visible, the initialized signal will be emitted.
        
        :param      state | <bool>
        """
        super(XView, self).showEvent(event)
        
        # record the visible state for this widget to be separate of Qt's
        # system to know if this view WILL be visible or not once the 
        # system is done processing.  This will affect how signals are
        # validated as part of the visible slot delegation
        self._visibleState = True
        
        if not self.isInitialized():
            self.initialize()
        
        # after the initial time the view is loaded, the visibleStateChanged
        # signal will be emitted
        elif not self.signalsBlocked():
            self.visibleStateChanged.emit(True)
            
    def signalPolicy( self ):
        """
        Returns the signal policy for this instance.
        
        :return     <XView.SignalPolicy>
        """
        return self._signalPolicy
    
    def rootWidget( self ):
        widget = self
        while ( widget.parent() ):
            widget = widget.parent()
        return widget
    
    def validateSignal( self, policy = None ):
        """
        Validates that this view is part of the group that was emitting
        the signal.  Views that are not in any viewing group will accept
        all signals.
        
        :param      policy | <XView.SignalPolicy> || None
        
        :return     <bool>
        """
        # validate whether or not to process a signal
        if policy is None:
            policy = self.signalPolicy()
        
        group_check   = XView.getGlobal('emitGroup') == self.viewingGroup()
        current_check = self.isCurrent()
        
        # always delegate signals if they are not set to block,
        # or if the method is called directly (not from a signal)
        if not self.sender() or policy & XView.SignalPolicy.NeverBlock:
            return True
        
        # block delegation of the signal if the view is not initialized
        elif policy & XView.SignalPolicy.BlockIfNotInitialized and \
             not self.isInitialized():
            return False
        
        # block delegation if the view is not visible
        elif policy & XView.SignalPolicy.BlockIfNotVisible and \
            not self._visibleState:
            return False
        
        # block delegation if the view is not part of a group
        elif self.viewingGroup() and \
             policy & XView.SignalPolicy.BlockIfNotInGroup:
            return group_check
        
        # look for only currency releated connections
        elif policy & XView.SignalPolicy.BlockIfNotCurrent:
            return current_check
        
        else:
            return True
        
    def viewingGroup( self ):
        """
        Returns the viewing group that this view is assigned to.
        
        :return     <int>
        """
        return self._viewingGroup
    
    @classmethod
    def currentView( cls ):
        # look for last focused view
        if ( cls._currentViewRef ):
            inst = cls._currentViewRef()
            if ( inst ):
                return inst
        
        cls._currentViewRef = None
        return None
    
    @classmethod
    def createInstance( cls, parent ):
        # assign the singleton instance
        if ( cls._instanceSingleton ):
            instance = cls._instanceSingleton()
            
            # make sure the instance is still in use
            if ( not instance ):
                cls._instanceSingleton = None
            else:
                instance.setParent(parent)
                return instance
        
        # determine if we need to store a singleton
        inst = cls(parent)
        inst.setObjectName( cls.uniqueName() )
        if ( cls.isViewSingleton() ):
            cls._instanceSingleton = weakref.ref(inst)
        
        return inst
    
    @classmethod
    def destroyInstance( cls, inst ):
        if ( cls.isViewSingleton() ):
            inst.close()
            return
        
        inst.close()
        inst.setParent(None)
        inst.deleteLater()
    
    @classmethod
    @deprecatedmethod('XView', 'Use the XView.dispatch() syntax now.')
    def dispatcher( cls ):
        if ( not cls._dispatcher ):
            cls._dispatcher = cls.MetaDispatcher(cls)
            
        return cls._dispatcher
    
    @classmethod
    def instances( cls ):
        """
        Returns all generated instances of a particular view type.
        
        :return     [<XView>, ..]
        """
        if ( not cls._instances ):
            return []
        
        # purge the instance list
        insts = []
        refs  = []
        for ref in cls._instances:
            inst = ref()
            if ( not inst ):
                continue
            
            insts.append(inst)
            refs.append(ref)
        
        cls._instances = refs
        return insts
    
    @classmethod
    def isViewSingleton( cls ):
        return cls._viewSingleton
    
    @classmethod
    def isPopupSingleton( cls ):
        return cls._popupSingleton
    
    @classmethod
    def popup( cls, parent = None ):
        """
        Pops up this view as a new dialog.  If the forceDialog flag is set to \
        False, then it will try to activate the first instance of the view \
        within an existing viewwidget context before creating a new dialog.
        
        :param      parent      | <QWidget> || None
        """
        # popup the singleton view for this class
        if ( cls.isViewSingleton() ):
            inst = cls.currentView()
            if ( not inst ):
                inst = cls.createInstance(parent)
                
            inst.setWindowFlags(Qt.Dialog)
            inst.show()
        
        # popup the popupSingleton for this class
        inst = cls.popupInstance(parent)
        inst.show()
    
    @classmethod
    def popupInstance( cls, parent ):
        if ( cls._popupInstance ):
            return cls._popupInstance
        
        inst = cls.createInstance(parent)
        inst.setWindowFlags(Qt.Dialog)
        if cls.isPopupSingleton():
            inst.setAttribute(Qt.WA_DeleteOnClose, False)
            cls._popupInstance = inst
        
        return inst
    
    @classmethod
    def registerInstance( cls, instance ):
        if ( not cls._instances ):
            cls._instances = []
        
        cls._instances.append(weakref.ref(instance))
    
    @classmethod
    def registerToWindow( cls, window ):
        """
        Registers this view to the window to update additional menu items, \
        actions, and toolbars.
        
        :param      window | <QWidget>
        """
        pass
    
    @classmethod
    def restoreGlobalSettings( cls, settings ):
        """
        Restores the global settings for the inputed view class type.
        
        :param      cls      | <subclass of XView>
                    settings | <QSettings>
        """
        pass
    
    @classmethod
    def saveGlobalSettings( cls, settings ):
        """
        Saves the global settings for the inputed view class type.
        
        :param      cls      | <subclass of XView>
                    settings | <QSettings>
        """
        pass
    
    @classmethod
    def setViewGroup( cls, grp ):
        cls._viewGroup = grp
    
    @classmethod
    def setCurrentView( cls, view ):
        current = cls.currentView()
        if ( current == view ):
            return False
            
        elif ( current ):
            current.showActiveState(False)
        
        if ( view ):
            view.showActiveState(True)
        
        cls._currentViewRef = weakref.ref(view)
        return True
    
    @classmethod
    def setViewIcon( cls, icon ):
        cls._viewIcon = icon
    
    @classmethod
    def setViewName( cls, name ):
        cls._viewName = name
    
    @classmethod
    def setViewSingleton( cls, state ):
        cls._viewSingleton = state
    
    @classmethod
    def setPopupSingleton( cls, state ):
        cls._popupSingleton = state
    
    @classmethod
    def uniqueName( cls ):
        names = map(lambda x: str(x.objectName()), cls.instances())
        index = 1
        base  = cls.viewName()
        name  = '%s%02i' % (base, index)
        
        while ( name in names ):
            index += 1
            name = '%s%02i' % (base, index)
        
        return name
    
    @classmethod
    def unregisterInstance( cls, instance ):
        if ( not cls._instances ):
            return
        
        if ( cls._currentViewRef and instance == cls._currentViewRef() ):
            cls._currentViewRef = None
        
        refs = []
        for ref in cls._instances:
            inst = ref()
            if ( not inst or inst == instance ):
                continue
            
            refs.append(ref)
        
        cls._instances = refs
    
    @classmethod
    def unregisterToWindow( cls, window ):
        """
        Registers this view to the window to update additional menu items, \
        actions, and toolbars.
        
        :param      window | <QWidget>
        """
        pass
    
    @classmethod
    def viewGroup( cls ):
        return cls._viewGroup
    
    @classmethod
    def viewIcon( cls ):
        return cls._viewIcon
    
    @classmethod
    def viewName( cls ):
        return cls._viewName
    
    @classmethod
    def viewTypeName( cls ):
        """
        Returns the unique name for this view type by joining its group with \
        its name.
        
        :return     <str>
        """
        return '%s.%s' % (cls.viewGroup(), cls.viewName())
    
    #--------------------------------------------------------------------------
    
    @staticmethod
    def dispatch( location = 'Central' ):
        """
        Returns the instance of the global view dispatching system.  All views \
        will route their signals through the central hub so no single view \
        necessarily depends on another.
        
        :return     <XViewDispatch>
        """
        dispatch = XView._dispatch.get(str(location))
        if ( not dispatch ):
            dispatch = XViewDispatch(QApplication.instance())
            XView._dispatch[str(location)] = dispatch
        
        return dispatch
        
    @staticmethod
    def getGlobal( key, default = None ):
        """
        Returns the global value for the inputed key.
        
        :param      key     | <str>
                    default | <variant>
        
        :return     <variant>
        """
        return XView._globals.get(key, default)
    
    @staticmethod
    def registeredView( viewName, location = 'Central' ):
        """
        Returns the view that is registered to the inputed location for the \
        given name.
        
        :param      viewName | <str>
                    location | <str>
        
        :return     <subclass of XView> || None
        """
        for viewType in XView._registry.get(str(location), []):
            if ( viewType.viewName() == viewName ):
                return viewType
        return None
    
    @staticmethod
    def registeredViews( location = 'Central' ):
        """
        Returns all the views types that have bene registered to a particular \
        location.
        
        :param      location | <str>
        
        :return     [<subclass of XView>, ..]
        """
        return XView._registry.get(str(location), [])
        
    @staticmethod
    def registerView( viewType, location = 'Central' ):
        """
        Registers the inputed view type to the given location.  The location \
        is just a way to group and organize potential view plugins for a \
        particular widget, and is determined per application.  This eases \
        use when building a plugin based system.  It has no relevance to the \
        XView class itself where you register a view.
        
        :param      viewType | <subclass of XView>
        """
        # update the dispatch signals
        if ( '__xview_signals__' in viewType.__dict__ ):
            XView.dispatch(location).registerSignals(viewType.__xview_signals__)
            
        location = str(location)
        XView._registry.setdefault(location, [])
        XView._registry[str(location)].append(viewType)
    
    @staticmethod
    def setGlobal( key, value ):
        """
        Shares a global value across all views by setting the key in the \
        globals dictionary to the inputed value.
        
        :param      key     | <str> 
                    value   | <variant>
        """
        XView._globals[key] = value
    
    @staticmethod
    def updateCurrentView( oldWidget, newWidget ):
        """
        Updates the current view for each view class type based on the new \
        focused widget.
        
        :param      oldWidget | <QWidget>
                    newWidget | <QWidget>
        """
        widget = newWidget
        
        while widget:
            if isinstance(widget, XView):
                widget.setCurrent()
                break
                
            widget = widget.parent()