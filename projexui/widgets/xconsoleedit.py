#!/usr/bin/python

""" Defines an interactive python interpreter console. """

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

import __main__
import inspect
import logging
import os
import re
import sys

import projex.text
from projexui.qt import Signal
from PyQt4.QtCore import QObject,\
                               QPoint,\
                               Qt
                         
from PyQt4.QtGui import QApplication,\
                              QCursor,\
                              QFont,\
                              QTextCursor,\
                              QToolTip,\
                              QTreeWidget,\
                              QTreeWidgetItem,\
                              QFontMetrics,\
                              QSyntaxHighlighter,\
                              QTextCharFormat,\
                              QColor
                              

import projexui.resources

from projexui.widgets.xloggerwidget import XLoggerWidget

INPUT_EXPR = re.compile('^(>>> |... )([^#]*)')
KEYWORDS = ('def', 'import', 'from', 'with', 'if', 'elif', 'else', 'for',
            'while', 'class', 'None', 'not', 'is', 'in', 'print')

class XConsoleHighlighter(QSyntaxHighlighter):
    def highlightBlock(self, text):
        """
        Highlights the inputed text to show the wiki text format.
        
        :param      text | <str>
        """
        # setup global format options
        palette = QApplication.palette()
        
        # define the keyword format
        keyword_format = QTextCharFormat()
        keyword_format.setForeground(QColor('blue'))
        
        # define the comment format
        comment_format = QTextCharFormat()
        comment_format.setForeground(QColor('green'))
        
        # define the string format
        string_format = QTextCharFormat()
        string_format.setForeground(QColor('brown'))
        
        # format keywords
        for keyword in KEYWORDS:
            for match in re.finditer('[^\w]%s[^\w]' % keyword, text):
                start, end = match.span()
                self.setFormat(start, end - start, keyword_format)
        
        # format strings
        for match in re.finditer('"[^\"]+"?', text):
            start, end = match.span()
            self.setFormat(start, end - start, string_format)
        
        for match in re.finditer("'[^\']+'?", text):
            start, end = match.span()
            self.setFormat(start, end - start, string_format)
        
        # format comments
        result = re.search('#.*', text)
        if result:
            start, end = result.span()
            self.setFormat(start, end - start, comment_format)

#----------------------------------------------------------------------

class XStream(QObject):
    _stdout = None
    _stderr = None
    
    messageWritten = Signal(object)
    
    def __init__( self, name, stream ):
        super(XStream, self).__init__()
        
        self._name       = name
        self._stream     = stream
    
    def __del__( self ):
        if ( name == 'stdout' ):
            sys.stdout = self._stream
            
        elif ( name == 'stderr' ):
            sys.stderr = self._stream
    
    def flush( self ):
        """
        Emits the flush requested signal.
        """
        try:
            self._stream.flush()
        except IOError:
            pass
    
    def fileno( self ):
        """
        Returns the file number for this stream.
        
        :return     <int>
        """
        try:
            return self._stream.fileno()
        except IOError:
            return -1
    
    def write( self, msg ):
        """
        Writes the inputed message to the system.
        
        :param      msg | <str>
        """
        try:
            self._stream.write(msg)
        except IOError:
            pass
        
        self.messageWritten.emit(msg)
        
    @staticmethod
    def stdout():
        """
        Returns the standard out stream for this system.
        
        :return     <XStream>
        """
        if not XStream._stdout:
            XStream._stdout = XStream('stdout', sys.stdout)
            
            if ( os.getenv('XUI_DISABLE_CONSOLE') != '1' ):
                sys.stdout = XStream._stdout
        
        return XStream._stdout
    
    @staticmethod
    def stderr():
        """
        Returns the standard error stream for this system.
        
        :return     <XStream>
        """
        if ( not XStream._stderr ):
            XStream._stderr = XStream('stderr', sys.stderr)
            
            if ( os.getenv('XUI_DISABLE_CONSOLE') != '1' ):
                sys.stderr = XStream._stderr
        
        return XStream._stderr

#------------------------------------------------------------------------------

class XConsoleEdit(XLoggerWidget):
    __designer_icon__ = projexui.resources.find('img/ui/console.png')
    
    def __init__( self, parent ):
        super(XConsoleEdit, self).__init__(parent)
        
        self.setLogger(logging.getLogger())
        
        # create custom properties
        self._completerTree = None
        self._commandStack = []
        self._highlighter = XConsoleHighlighter(self.document())
        
        # set properties
        font = QFont('Courier New')
        font.setPointSize(9)
        self.setFont(font)
        self.setReadOnly(False)
        self.waitForInput()
        metrics = QFontMetrics(font)
        self.setTabStopWidth(4 * metrics.width(' '))
        
        # create connections
        XStream.stdout().messageWritten.connect( self.information )
        XStream.stderr().messageWritten.connect( self.error )
    
    def __del__( self ):
        XStream.stdout().messageWritten.disconnect( self.information )
        XStream.stderr().messageWritten.disconnect( self.error )
    
    def acceptCompletion( self ):
        """
        Accepts the current completion and inserts the code into the edit.
        
        :return     <bool> accepted
        """
        tree = self._completerTree
        if not tree:
            return False
            
        tree.hide()
        
        item = tree.currentItem()
        if not item:
            return False
        
        # clear the previously typed code for the block
        cursor  = self.textCursor()
        text    = cursor.block().text()
        col     = cursor.columnNumber()
        end     = col
        
        while col:
            col -= 1
            if text[col] == '.':
                col += 1
                break
        
        # insert the current text
        cursor.setPosition(cursor.position() - (end-col), cursor.KeepAnchor)
        cursor.removeSelectedText()
        self.insertPlainText(item.text(0))
        return True
    
    def applyCommand( self ):
        """
        Applies the current line of code as an interactive python command.
        """
        # grab the command from the current line
        block   = self.textCursor().block().text()
        match   = INPUT_EXPR.match(projex.text.toUtf8(block))
        
        # if there is no command, then wait for the input
        if not match:
            self.waitForInput()
            return
        
        self.executeCommand(match.group(2).rstrip(), match.group(1).strip())
    
    def cancelCompletion( self ):
        """
        Cancels the current completion.
        """
        if ( self._completerTree ):
            self._completerTree.hide()
    
    def clear( self ):
        """
        Clears the current text and starts a new input line.
        """
        super(XConsoleEdit, self).clear()
        self.waitForInput()
    
    def closeEvent( self, event ):
        """
        Disconnects from the stderr/stdout on close.
        
        :param      event | <QCloseEvent>
        """
        if ( self.clearOnClose() ):
            XStream.stdout().messageWritten.disconnect( self.information )
            XStream.stderr().messageWritten.disconnect( self.error )
        
        super(XConsoleEdit, self).closeEvent(event)
    
    def completerTree( self ):
        """
        Returns the completion tree for this instance.
        
        :return     <QTreeWidget>
        """
        if ( not self._completerTree ):
            self._completerTree = QTreeWidget(self)
            self._completerTree.setWindowFlags(Qt.Popup)
            self._completerTree.setAlternatingRowColors( True )
            self._completerTree.installEventFilter(self)
            self._completerTree.itemClicked.connect( self.acceptCompletion )
            self._completerTree.setRootIsDecorated(False)
            self._completerTree.header().hide()
            
        return self._completerTree
    
    def eventFilter( self, obj, event ):
        """
        Filters particular events for a given QObject through this class. \
        Will use this to intercept events to the completer tree widget while \
        filtering.
        
        :param      obj     | <QObject>
                    event   | <QEvent>
        
        :return     <bool> consumed
        """
        if ( not obj == self._completerTree ):
            return False
        
        if ( event.type() != event.KeyPress ):
            return False
            
        if ( event.key() == Qt.Key_Escape ):
            QToolTip.hideText()
            self.cancelCompletion()
            return False
        
        elif ( event.key() in (Qt.Key_Enter, Qt.Key_Return, Qt.Key_Tab) ):
            self.acceptCompletion()
            return False
        
        elif ( event.key() in (Qt.Key_Up, 
                               Qt.Key_Down) ):
            
            return False
        
        else:
            self.keyPressEvent(event)
            
            # update the completer
            cursor   = self.textCursor()
            text     = projex.text.toUtf8(cursor.block().text())
            text     = text[:cursor.columnNumber()].split(' ')[-1]
            text     = text.split('.')[-1]
            
            self._completerTree.blockSignals(True)
            self._completerTree.setUpdatesEnabled(False)
            
            self._completerTree.setCurrentItem(None)
            
            for i in range(self._completerTree.topLevelItemCount()):
                item = self._completerTree.topLevelItem(i)
                if projex.text.toUtf8(item.text(0)).startswith(text):
                    self._completerTree.setCurrentItem(item)
                    break
            
            self._completerTree.blockSignals(False)
            self._completerTree.setUpdatesEnabled(True)
            
            return True
    
    def executeCommand(self, command, mode='>>>'):
        """
        Executes the inputed command in the global scope.
        
        :param      command | <unicode>
        
        :return     <variant>
        """
        # check to see if we're starting a new line
        if mode == '...' and not command.strip():
            command = '\n'.join(self._commandStack)
        
        elif command.endswith(':') or mode == '...':
            self._commandStack.append(command)
            self.insertPlainText('\n... ')
            return
        
        # if we're not at the end of the console, then add it to the end
        elif not self.textCursor().atEnd():
            self.waitForInput()
            self.insertPlainText(command)
            return
        
        self._commandStack = []
        
        # insert a new line
        self.insertPlainText('\n')
        cmdresult = None
        
        try:
            cmdresult = eval(command, __main__.__dict__, __main__.__dict__)
        except SyntaxError:
            exec(command) in __main__.__dict__, __main__.__dict__
        
        # print the resulting commands
        if cmdresult != None:
            self.information(projex.text.toUtf8(cmdresult))
        
        self.waitForInput()
    
    def highlighter(self):
        """
        Returns the console highlighter for this widget.
        
        :return     <XConsoleHighlighter>
        """
        return self._highlighter
    
    def gotoHome( self ):
        """
        Navigates to the home position for the edit.
        """
        mode = QTextCursor.MoveAnchor
        
        # select the home
        if QApplication.instance().keyboardModifiers() == Qt.ShiftModifier:
            mode = QTextCursor.KeepAnchor
        
        cursor = self.textCursor()
        block  = projex.text.toUtf8(cursor.block().text())
        
        cursor.movePosition( QTextCursor.StartOfBlock, mode )
        if ( block.startswith('>>> ') ):
            cursor.movePosition( QTextCursor.Right, mode, 4 )
            
        self.setTextCursor(cursor)
    
    def keyPressEvent( self, event ):
        """
        Overloads the key press event to control keystroke modifications for \
        the console widget.
        
        :param      event | <QKeyEvent>
        """
        # enter || return keys will apply the command
        if event.key() in (Qt.Key_Return, Qt.Key_Enter):
            self.applyCommand()
        
        # home key will move the cursor to the home position
        elif event.key() == Qt.Key_Home:
            self.gotoHome()
        
        elif event.key() in (Qt.Key_Backspace, Qt.Key_Delete):
            super(XConsoleEdit, self).keyPressEvent(event)
            
            # update the completer
            cursor   = self.textCursor()
            text     = projex.text.toUtf8(cursor.block().text())
            text     = text[:cursor.columnNumber()].split(' ')[-1]
            
            if not '.' in text:
                self.cancelCompletion()
            
        # period key will trigger a completion popup
        elif event.key() == Qt.Key_Period:
            self.startCompletion()
            super(XConsoleEdit, self).keyPressEvent(event)
        
        # space, tab, backspace and delete will cancel the completion
        elif event.key() == Qt.Key_Space:
            self.cancelCompletion()
            super(XConsoleEdit, self).keyPressEvent(event)
        
        # left parenthesis will start method help
        elif event.key() == Qt.Key_ParenLeft:
            self.cancelCompletion()
            self.showMethodToolTip()
            super(XConsoleEdit, self).keyPressEvent(event)
        
        # otherwise, handle the event like normal
        else:
            super(XConsoleEdit, self).keyPressEvent(event)
    
    def objectAtCursor( self ):
        """
        Returns the python object that the text is representing.
        
        :return     <object> || None
        """
        
        # determine the text block
        cursor = self.textCursor()
        text    = projex.text.toUtf8(cursor.block().text())
        col     = cursor.columnNumber()
        end     = col
        
        while ( col ):
            col -= 1
            if ( re.match('[^a-zA-Z\._\(\)]', text[col]) ):
                break
        
        symbol = text[col:end].rstrip('.(')
        try:
            return eval(symbol, __main__.__dict__, __main__.__dict__)
        except:
            return None
    
    def showMethodToolTip( self ):
        """
        Pops up a tooltip message with the help for the object under the \
        cursor.
        
        :return     <bool> success
        """
        self.cancelCompletion()
        
        obj = self.objectAtCursor()
        if ( not obj ):
            return False
        
        docs = inspect.getdoc(obj)
        if ( not docs ):
            return False
        
        # determine the cursor position
        rect   = self.cursorRect()
        cursor = self.textCursor()
        point  = QPoint(rect.left(), rect.top() + 18)
        
        QToolTip.showText( self.mapToGlobal(point), docs, self )
        
        return True
    
    def startCompletion( self ):
        """
        Starts a new completion popup for the current object.
        
        :return     <bool> success
        """
        # add the top level items
        tree = self.completerTree()
        tree.clear()
        
        # make sure we have a valid object
        obj = self.objectAtCursor()
        if ( obj is None ):
            return False
            
        # determine the cursor position
        rect   = self.cursorRect()
        cursor = self.textCursor()
        point  = QPoint(rect.left(), rect.top() + 18)
        
        try:
            o_keys = obj.__dir__()
        except (AttributeError, TypeError):
            o_keys = dir(obj)
        
        keys = [key for key in sorted(o_keys) if not key.startswith('_')]
        if ( not keys ):
            return False
        
        for key in keys:
            tree.addTopLevelItem(QTreeWidgetItem([key]))
        
        tree.move(self.mapToGlobal(point))
        tree.show()
        
        return True
    
    def waitForInput( self ):
        """
        Inserts a new input command into the console editor.
        """
        if ( self.isReadOnly() ):
            return
            
        self.moveCursor( QTextCursor.End )
        
        if ( self.textCursor().block().text() == '>>> ' ):
            return
        
        # if there is already text on the line, then start a new line
        newln = '>>> '
        if projex.text.toUtf8(self.textCursor().block().text()):
            newln = '\n' + newln
        
        # insert the text
        self.setCurrentMode('standard')
        self.insertPlainText(newln)
        self.scrollToEnd()
        
        self._blankCache = ''

__designer_plugins__ = [XConsoleEdit]