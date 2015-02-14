#!/usr/bin/python

"""
Extends the base QLineEdit class to support some additional features like \
setting hints on line edits.
"""

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

from projexui import qt #import Property, Slot, Signal
from PyQt4.QtCore import  QSize,\
                                Qt,\
                                QSize

from PyQt4.QtGui import QFontMetrics,\
                              QLineEdit,\
                              QPalette,\
                              QPainter,\
                              QIcon

import projex.text
from projex.enum import enum

import projexui.resources

LINEEDIT_STYLE = """
QLineEdit#%(objectName)s {
    border: 1px solid palette(mid);
    border-radius: %(corner_radius)spx;
    padding: 1px %(padding)spx;
    background-color: palette(base);
}
QLineEdit#%(objectName)s:disabled {
    background-color: palette(window);
}
"""

class XLineEdit( QLineEdit ):
    """
    Creates a new QLineEdit that allows the user to define a grayed out text
    hint that will be drawn when there is no text assigned to the widget.
    """
    
    __designer_icon__ = projexui.resources.find('img/ui/lineedit.png')
    
    textEntered = qt.Signal(str)
    
    InputFormat = enum('Normal', 
                       'CamelHump', 
                       'Underscore', 
                       'Dash', 
                       'ClassName',
                       'NoSpaces',
                       'Capitalize',
                       'Uppercase',
                       'Lowercase',
                       'Pretty')
    
    def __init__( self, *args ):
        super(XLineEdit, self).__init__(*args)
        
        palette     = self.palette()
        hint_clr    = palette.color(palette.Disabled, palette.Text)
        
        # set the hint property
        self._hint             = ''
        self._spacer           = '_'
        self._hintColor        = hint_clr
        self._cornerRadius     = 0
        self._inputFormat      = XLineEdit.InputFormat.Normal
        self._selectAllOnFocus = False
        self._focusedIn        = False
        self._useHintValue     = False
        
        self._icon          = QIcon()
        self._iconSize      = QSize(14, 14)
        self._buttons       = {}
        
        self.textChanged.connect(self.adjustText)
        self.returnPressed.connect(self.emitTextEntered)
    
    def adjustText(self):
        """
        Updates the text based on the current format options.
        """
        pos = self.cursorPosition()
        self.blockSignals(True)
        super(XLineEdit, self).setText(self.formatText(self.text()))
        self.setCursorPosition(pos)
        self.blockSignals(False)
    
    def addButton(self, button, alignment=None):
        """
        Adds a button the edit.  All the buttons will be layed out at the \
        end of the widget.
        
        :param      button      | <QToolButton>
                    alignment   | <Qt.Alignment>
        
        :return     <bool> | success
        """
        if alignment == None:
            if button.pos().x() < self.pos().x():
                alignment = Qt.AlignLeft
            else:
                alignment = Qt.AlignRight
        
        all_buttons = self.buttons()
        if button in all_buttons:
            return False
        
        # move the button to this edit
        button.setAutoRaise(True)
        button.setParent(self)
        button.setIconSize(self.iconSize())
        button.setCursor(Qt.ArrowCursor)
        button.setFixedSize(QSize(self.height() - 2, self.height() - 2))
        
        self._buttons.setdefault(alignment, [])
        self._buttons[alignment].append(button)
        self.adjustButtons()
        return True
    
    def adjustButtons( self ):
        """
        Adjusts the placement of the buttons for this line edit.
        """
        y = 1
        
        for btn in self.buttons():
            btn.setIconSize(self.iconSize())
            btn.setFixedSize(QSize(self.height() - 2, self.height() - 2))
        
        # adjust the location for the left buttons
        left_buttons = self._buttons.get(Qt.AlignLeft, [])
        x = (self.cornerRadius() / 2.0) + 2
        
        for btn in left_buttons:
            btn.move(x, y)
            x += btn.width()
        
        # adjust the location for the right buttons
        right_buttons = self._buttons.get(Qt.AlignRight, [])
        
        w       = self.width()
        bwidth  = sum([btn.width() for btn in right_buttons])
        bwidth  += (self.cornerRadius() / 2.0) + 1
        
        for btn in right_buttons:
            btn.move(w - bwidth, y)
            bwidth -= btn.width()
        
        self.adjustTextMargins()
    
    def adjustTextMargins( self ):
        """
        Adjusts the margins for the text based on the contents to be displayed.
        """
        left_buttons    = self._buttons.get(Qt.AlignLeft, [])
        
        if left_buttons:
            bwidth = left_buttons[-1].pos().x() + left_buttons[-1].width() - 4
        else:
            bwidth = 0 + (max(8, self.cornerRadius()) - 8)
            
        self.setTextMargins(bwidth, 0, 0, 0)
    
    def adjustStyleSheet( self ):
        """
        Adjusts the stylesheet for this widget based on whether it has a \
        corner radius and/or icon.
        """
        radius  = self.cornerRadius()
        icon    = self.icon()
        
        if not self.objectName():
            self.setStyleSheet('')
        elif not (radius or icon):
            self.setStyleSheet('')
        else:
            palette = self.palette()
            
            options = {}
            options['corner_radius']    = radius
            options['padding']          = 5
            options['objectName']       = self.objectName()
            
            if icon and not icon.isNull():
                options['padding'] += self.iconSize().width() + 2
            
            self.setStyleSheet(LINEEDIT_STYLE % options)
    
    def buttons(self):
        """
        Returns all the buttons linked to this edit.
        
        :return     [<QToolButton>, ..]
        """
        all_buttons = []
        for buttons in self._buttons.values():
            all_buttons += buttons
        return all_buttons
    
    def cornerRadius( self ):
        """
        Returns the rounding radius for this widget's corner, allowing a \
        developer to round the edges for a line edit on the fly.
        
        :return     <int>
        """
        return self._cornerRadius
    
    def currentText( self ):
        """
        Returns the text that is available currently, \
        if the user has set standard text, then that \
        is returned, otherwise the hint is returned.
        
        :return     <str>
        """
        text = str(self.text())
        if ( text ):
            return text
        return self._hint
    
    def emitTextEntered(self):
        """
        Emits the text entered signal for this line edit, provided the
        signals are not being blocked.
        """
        if not self.signalsBlocked():
            self.textEntered.emit(self.text())
    
    def focusInEvent(self, event):
        """
        Updates the focus in state for this edit.
        
        :param      event | <QFocusEvent>
        """
        super(XLineEdit, self).focusInEvent(event)
        
        self._focusedIn = True
    
    def focusOutEvent(self, event):
        """
        Updates the focus in state for this edit.
        
        :param      event | <QFocusEvent>
        """
        super(XLineEdit, self).focusOutEvent(event)
        
        self._focusedIn = False
    
    def formatText(self, text):
        """
        Formats the inputed text based on the input format assigned to this
        line edit.
        
        :param      text | <str>
        
        :return     <str> | frormatted text
        """
        format = self.inputFormat()
        if format == XLineEdit.InputFormat.Normal:
            return text
        
        text = projex.text.toUtf8(text)
        if format == XLineEdit.InputFormat.CamelHump:
            return projex.text.camelHump(text)
        
        elif format == XLineEdit.InputFormat.Pretty:
            return projex.text.pretty(text)
        
        elif format == XLineEdit.InputFormat.Underscore:
            return projex.text.underscore(text)
        
        elif format == XLineEdit.InputFormat.Dash:
            return projex.text.dashed(text)
        
        elif format == XLineEdit.InputFormat.ClassName:
            return projex.text.classname(text)
        
        elif format == XLineEdit.InputFormat.NoSpaces:
            return projex.text.joinWords(text, self.spacer())
        
        elif format == XLineEdit.InputFormat.Capitalize:
            return text.capitalize()
        
        elif format == XLineEdit.InputFormat.Uppercase:
            return text.upper()
        
        elif format == XLineEdit.InputFormat.Lowercase:
            return text.lower()
        
        return text
    
    def hint( self ):
        """
        Returns the hint value for this line edit.
        
        :return     <str>
        """
        return self._hint
    
    def hintColor( self ):
        """
        Returns the hint color for this text item.
        
        :return     <QColor>
        """
        return self._hintColor
    
    def icon( self ):
        """
        Returns the icon instance that is being used for this widget.
        
        :return     <QIcon> || None
        """
        return self._icon
    
    def iconSize( self ):
        """
        Returns the icon size that will be used for this widget.
        
        :return     <QSize>
        """
        return self._iconSize
    
    def inputFormat( self ):
        """
        Returns the input format for this widget.
        
        :return     <int>
        """
        return self._inputFormat
    
    def inputFormatText( self ):
        """
        Returns the input format as a text value for this widget.
        
        :return     <str>
        """
        return XLineEdit.InputFormat[self.inputFormat()]
    
    def mousePressEvent(self, event):
        """
        Selects all the text if the property is set after this widget
        first gains focus.
        
        :param      event | <QMouseEvent>
        """
        super(XLineEdit, self).mousePressEvent(event)
        
        if self._focusedIn and self.selectAllOnFocus():
            self.selectAll()
            self._focusedIn = False
    
    def paintEvent( self, event ):
        """
        Overloads the paint event to paint additional \
        hint information if no text is set on the \
        editor.
        
        :param      event      | <QPaintEvent>
        """
        super(XLineEdit, self).paintEvent(event)
        
        # paint the hint text if not text is set
        if self.text() and not (self.icon() and not self.icon().isNull()):
            return
        
        # paint the hint text
        painter = QPainter(self)
        painter.setPen(self.hintColor())
        
        icon = self.icon()
        left, top, right, bottom = self.getTextMargins()
        
        w = self.width()
        h = self.height() - 2
        
        w -= (right + left)
        h -= (bottom + top)
        
        if icon and not icon.isNull():
            size = icon.actualSize(self.iconSize())
            x    = 5 + left
            y    = (self.height() - size.height()) / 2.0
            
            painter.drawPixmap(x, y, icon.pixmap(size.width(), size.height()))
            
            w -= size.width() - 2
        else:
            x = 6 + left
        
        w -= sum([btn.width() for btn in self.buttons()])
        y = 2 + top
        
        # create the elided hint
        if not self.text() and self.hint():
            rect    = self.cursorRect()
            metrics = QFontMetrics(self.font())
            hint    = metrics.elidedText(self.hint(), Qt.ElideRight, w)
            align   = self.alignment()
            
            if align & Qt.AlignHCenter:
                x = 0
            else:
                x = rect.center().x()
            
            painter.drawText(x, y, w, h, align, hint)
        
    def resizeEvent( self, event ):
        """
        Overloads the resize event to handle updating of buttons.
        
        :param      event | <QResizeEvent>
        """
        super(XLineEdit, self).resizeEvent(event)
        self.adjustButtons()
    
    def selectAllOnFocus(self):
        """
        Returns whether or not this edit will select all its contents on
        focus in.
        
        :return     <bool>
        """
        return self._selectAllOnFocus
    
    def setCornerRadius( self, radius ):
        """
        Sets the corner radius for this widget tot he inputed radius.
        
        :param      radius | <int>
        """
        self._cornerRadius = radius
        
        self.adjustStyleSheet()
    
    @qt.Slot(str)
    def setHint( self, hint ):
        """
        Sets the hint text to the inputed value.
        
        :param      hint       | <str>
        """
        self._hint = self.formatText(hint)
        self.repaint()
    
    def setHintColor( self, clr ):
        """
        Sets the color for the hint for this edit.
        
        :param      clr     | <QColor>
        """
        self._hintColor = clr
    
    def setIcon(self, icon):
        """
        Sets the icon that will be used for this widget to the inputed icon.
        
        :param      icon | <QIcon> || None
        """
        self._icon = QIcon(icon)
        
        self.adjustStyleSheet()
    
    def setIconSize( self, size ):
        """
        Sets the icon size that will be used for this edit.
        
        :param      size | <QSize>
        """
        self._iconSize = size
        self.adjustTextMargins()
    
    def setInputFormat( self, inputFormat ):
        """
        Sets the input format for this text.
        
        :param      inputFormat | <int>
        """
        self._inputFormat = inputFormat
    
    def setInputFormatText( self, text ):
        """
        Sets the input format text for this widget to the given value.
        
        :param      text | <str>
        """
        try:
            self._inputFormat = XLineEdit.InputFormat[str(text)]
        except KeyError:
            pass
    
    def setObjectName( self, objectName ):
        """
        Updates the style sheet for this line edit when the name changes.
        
        :param      objectName | <str>
        """
        super(XLineEdit, self).setObjectName(objectName)
        self.adjustStyleSheet()
    
    def setSelectAllOnFocus(self, state):
        """
        Returns whether or not this edit will select all its contents on
        focus in.
        
        :param      state | <bool>
        """
        self._selectAllOnFocus = state
    
    def setSpacer( self, spacer ):
        """
        Sets the spacer that will be used for this line edit when replacing
        NoSpaces input formats.
        
        :param      spacer | <str>
        """
        self._spacer = spacer
    
    def setUseHintValue(self, state):
        """
        This method sets whether or not the value for this line edit should
        use the hint value if no text is found (within the projexui.xwidgetvalue
        plugin system).  When set to True, the value returned will first look
        at the text of the widget, and if it is blank, will then return the
        hint value.  If it is False, only the text value will be returned.
        
        :param      state | <bool>
        """
        self._useHintValue = state
    
    def setText( self, text ):
        """
        Sets the text for this widget to the inputed text, converting it based \
        on the current input format if necessary.
        
        :param      text | <str>
        """
        if text is None:
            text = ''
        
        super(XLineEdit, self).setText(self.formatText(text))
    
    def setVisible(self, state):
        """
        Sets the visible state for this line edit.
        
        :param      state | <bool>
        """
        super(XLineEdit, self).setVisible(state)
        
        self.adjustStyleSheet()
        self.adjustTextMargins()
    
    def spacer( self ):
        """
        Returns the spacer that is used to replace spaces when the NoSpaces
        input format is used.
        
        :return     <str>
        """
        return self._spacer
    
    def useHintValue(self):
        """
        This method returns whether or not the value for this line edit should
        use the hint value if no text is found (within the projexui.xwidgetvalue
        plugin system).  When set to True, the value returned will first look
        at the text of the widget, and if it is blank, will then return the
        hint value.  If it is False, only the text value will be returned.
        
        :return     <bool>
        """
        return self._useHintValue
    
    # create Qt properties
    x_hint              = qt.Property(str, hint, setHint)
    x_icon              = qt.Property('QIcon', icon, setIcon)
    x_iconSize          = qt.Property(QSize, iconSize, setIconSize)
    x_hintColor         = qt.Property('QColor', hintColor, setHintColor)
    x_cornerRadius      = qt.Property(int, cornerRadius, setCornerRadius)
    x_inputFormatText   = qt.Property(str, inputFormatText, setInputFormatText)
    x_spacer            = qt.Property(str, spacer, setSpacer)
    x_selectAllOnFocus  = qt.Property(bool, selectAllOnFocus, setSelectAllOnFocus)
    x_useHintValue      = qt.Property(bool, useHintValue, setUseHintValue)
    
    # hack for qt
    setX_icon = setIcon

__designer_plugins__ = [XLineEdit]