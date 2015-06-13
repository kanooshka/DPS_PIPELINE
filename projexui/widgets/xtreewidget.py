#!/usr/bin/python

""" 
Extends the base QTreeWidget class with additional methods.
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

import datetime
import os
import re
import weakref

from xml.etree import ElementTree

import projex.sorting

from projexui import qt #import Signal, Slot, Property, wrapVariant, unwrapVariant
from PyQt4.QtCore   import Qt, \
                                 QLine, \
                                 QRectF, \
                                 QPoint,\
                                 QRect,\
                                 QSize,\
                                 QMimeData,\
                                 QByteArray,\
                                 QDate,\
                                 QDateTime,\
                                 QTime,\
                                 QTimer

from PyQt4.QtGui    import QApplication,\
                                 QBrush, \
                                 QColor, \
                                 QCursor,\
                                 QDateTimeEdit,\
                                 QDrag,\
                                 QFileDialog,\
                                 QItemDelegate, \
                                 QLinearGradient, \
                                 QMenu,\
                                 QPainter,\
                                 QPalette, \
                                 QPen, \
                                 QPixmap, \
                                 QIcon,\
                                 QTextDocument, \
                                 QFontMetrics,\
                                 QTreeWidget,\
                                 QTreeWidgetItem,\
                                 QTreeView,\
                                 QLabel

import projex.text
from projex.enum import enum
from projexui import resources

from projexui.xexporter import XExporter
from projexui.widgets.xloaderwidget import XLoaderWidget
from projexui.widgets.xpopupwidget import XPopupWidget

import sharedDB

COLUMN_FILTER_EXPR = re.compile('((\w+):([\w,\*]+|"[^"]+"?))')

ARROW_STYLESHEET = """
QTreeView::branch,
QTreeView::branch:has-siblings:!adjoins-item,
QTreeView::branch:has-siblings:adjoins-item {
    image: none;
}
QTreeView::branch:closed:has-children {
    image: url("%s");
}
QTreeView::branch:open:has-children {
    image: url("%s");
}
"""

#------------------------------------------------------------------------------

class XTreeWidgetItem(QTreeWidgetItem):
    SortRole        = Qt.ItemDataRole(128)
    ItemIsHoverable = Qt.ItemFlags(16777216)
    
    def __lt__(self, other):
        # make sure we're comparing apples to apples
        if not isinstance(other, QTreeWidgetItem):
            return 0
            
        tree = self.treeWidget()
        if not tree:
            return 0
        
        col = tree.sortColumn()
        
        # compare sorting data
        mdata = qt.unwrapVariant(self.data(col, self.SortRole))
        odata = qt.unwrapVariant(other.data(col, self.SortRole))
        
        # compare editing data
        if mdata is None or odata is None:
            mdata = qt.unwrapVariant(self.data(col, Qt.EditRole))
            odata = qt.unwrapVariant(other.data(col, Qt.EditRole))
        
        if type(mdata) == type(odata) and not type(mdata) in (str, unicode):
            return mdata < odata
        
        # compare display data by natural sorting mechanisms on a string
        mdata = projex.text.toAscii(self.text(col))
        odata = projex.text.toAscii(other.text(col))
        
        return projex.sorting.natural(mdata, odata) == -1
    
    def __eq__(self, other):
        return id(self) == id(other)
    
    def __ne__(self, other):
        return id(self) != id(other)
    
    def __init__( self, *args ):
        super(XTreeWidgetItem, self).__init__(*args)
        
        # sets the overlay information per column for this item
        self._iconOverlays      = {}
        self._hoverBackground   = {}
        self._hoverIcon         = {}
        self._hoverForeground   = {}
        self._expandedIcon      = {}
        self._dragData          = {}
        self._fixedHeight       = 0
        
        # set whether or not the tree widget is editable
        flags = self.flags() | Qt.ItemIsEditable
        flags ^= Qt.ItemIsDropEnabled
        self.setFlags(flags)
        
        tree = self.treeWidget()
        if tree:
            try:
                height = tree.defaultItemHeight()
            except:
                height = 0
            
            if height:
                self.setFixedHeight(height)
    
    def adjustHeight(self, column):
        """
        Adjusts the height for this item based on the columna and its text.
        
        :param      column | <int>
        """
        tree = self.treeWidget()
        if not tree:
            return
        
        w = tree.width()
        if tree.verticalScrollBar().isVisible():
            w -= tree.verticalScrollBar().width()
        
        doc = QTextDocument()
        doc.setTextWidth(w)
        doc.setHtml(self.text(0))
        height = doc.documentLayout().documentSize().height()
        self.setFixedHeight(height+2)
    
    def children(self):
        """
        Returns the list of child nodes for this item.
        
        :return     [<QTreeWidgetItem>, ..]
        """
        return map(self.child, range(self.childCount()))
    
    def dragData(self, format=None, default=None):
        """
        Returns the drag information that is associated with this tree
        widget item for the given format.
        
        :param      format | <str>
        
        :return     <variant>
        """
        if format is None:
            return self._dragData
        return self._dragData.get(str(format), default)
    
    def expandedIcon( self, column ):
        """
        Returns the icon to be used when the item is expanded.
        
        :param      column | <int>
        
        :return     <QIcon> || None
        """
        return self._expandedIcon.get(column)
    
    def fixedHeight(self):
        """
        Returns the fixed height for this treewidget item.
        
        :return     <int>
        """
        return self._fixedHeight
    
    def hoverBackground( self, column, default = None ):
        """
        Returns the brush to use when coloring when the user hovers over
        the item for the given column.
        
        :param      column | <int>
        
        :return     <QBrush> || None
        """
        return self._hoverBackground.get(column, default)
    
    def hoverIcon( self, column ):
        """
        Returns the icon to use when coloring when the user hovers over
        the item for the given column.
        
        :param      column | <int>
        
        :return     <QIcon> || None
        """
        return self._hoverIcon.get(column)
    
    def hoverForeground( self, column, default = None ):
        """
        Returns the brush to use when coloring when the user hovers over
        the item for the given column.
        
        :param      column | <int>
        
        :return     <QBrush> || None
        """
        return self._hoverForeground.get(column, default)
    
    def iconOverlay(self, column):
        """
        Returns the icon overlay for the given column.
        
        :return     <QIcon> || None
        """
        return self._iconOverlays.get(column)
    
    def initGroupStyle( self ):
        """
        Initialzes this item with a grouping style option.
        """
        flags      = self.flags()
        if flags & Qt.ItemIsSelectable:
            flags ^= Qt.ItemIsSelectable
            self.setFlags(flags)
        
        ico        = QIcon(resources.find('img/treeview/closed.png'))
        expand_ico = QIcon(resources.find('img/treeview/open.png'))
        
        self.setIcon(0, ico)
        self.setExpandedIcon(0, expand_ico)
        
        palette = QApplication.palette()
        
        line_clr = palette.color(palette.Mid)
        base_clr = palette.color(palette.Base).darker(102)
        
        gradient = QLinearGradient()
        
        gradient.setColorAt(0.00, line_clr)
        gradient.setColorAt(0.05, base_clr)
        gradient.setColorAt(0.89, base_clr.darker(105))
        gradient.setColorAt(0.9,  line_clr)
        gradient.setColorAt(1.00, line_clr)
        
        gradient.setStart(0, 0)
        gradient.setFinalStop(0, 24)
        
        brush = QBrush(gradient)
        
        tree = self.treeWidget()
        if tree:
            colcount = tree.columnCount()
        else:
            colcount = self.columnCount()
        
        for i in range(colcount):
            self.setBackground(i, brush)
    
    def setDragData(self, format, value):
        """
        Sets the drag information that is associated with this tree
        widget item for the given format.
        
        :param      format | <str>
                    value  | <variant>
        """
        if value is None:
            self._dragData.pop(str(format), None)
        else:
            self._dragData[str(format)] = value
    
    def setExpandedIcon( self, column, icon ):
        """
        Sets the icon to be used when the item is expanded.
        
        :param      column | <int>
                    icon   | <QIcon> || None
        """
        self._expandedIcon[column] = QIcon(icon)
    
    def setFixedHeight(self, height):
        """
        Sets the fixed height for this item to the inputed height.
        
        :param      height | <int>
        """
        self._fixedHeight = height
    
    def setHoverBackground( self, column, brush ):
        """
        Returns the brush to use when coloring when the user hovers over
        the item for the given column.
        
        :param      column | <int>
                    brush  | <QBrush)
        """
        self._hoverBackground[column] = QBrush(brush)
    
    def setHoverIcon( self, column, icon ):
        """
        Returns the icon to use when coloring when the user hovers over
        the item for the given column.
        
        :param      column | <int>
                    icon   | <QIcon)
        """
        self._hoverIcon[column] = QIcon(icon)
    
    def setHoverForeground( self, column, brush ):
        """
        Returns the brush to use when coloring when the user hovers over
        the item for the given column.
        
        :param      column | <int>
                    brush  | <QBrush>
        """
        self._hoverForeground[column] = QBrush(brush)
    
    def setIconOverlay(self, column, icon):
        """
        Sets the icon overlay for this item at the inputed column to the
        given icon.
        
        :param      column | <int>
                    icon   | <str> || <QIcon>
        """
        self._iconOverlays[column] = QIcon(icon)
    
    def setSizeHint(self, column, hint):
        """
        Sets the size hint for this item to the inputed size.  This will also
        updated the fixed height property if the hieght of the inputed hint
        is larger than the current fixed height.
        
        :param      hint | <QSize>
        """
        self._fixedHeight = max(hint.height(), self._fixedHeight)
        super(XTreeWidgetItem, self).setSizeHint(column, hint)
    
    def setSortData( self, column, data ):
        """
        Sets the sorting information for the inputed column to the given data.
        
        :param      column | <int>
                    data   | <variant>
        """
        self.setData(column, self.SortRole, qt.wrapVariant(data))
    
    def sizeHint(self, column):
        """
        Returns the size hint for this column.  This will return the width
        for the given column, with the maximum height assigned with this item.
        
        :return     <QSize>
        """
        hint = super(XTreeWidgetItem, self).sizeHint(column)
        hint.setHeight(max(hint.height(), self.fixedHeight()))
        return hint
    
    def sortData( self, column ):
        """
        Returns the data to be used when sorting.  If no sort data has been
        explicitly defined, then the value in the EditRole for this item's
        column will be used.
        
        :param      column | <int>
        
        :return     <variant>
        """
        value = qt.unwrapVariant(self.data(column, self.SortRole))
        if value is None:
            return None
        return qt.unwrapVariant(self.data(column, Qt.EditRole))
    
    def takeFromTree(self):
        """
        Takes this item from the tree.
        """
        tree = self.treeWidget()
        parent = self.parent()
        
        if parent:
            parent.takeChild(parent.indexOfChild(self))
        else:
            tree.takeTopLevelItem(tree.indexOfTopLevelItem(self))

#----------------------------------------------------------------------

class XLoaderItem(XTreeWidgetItem):
    def __lt__(self, other):
        tree = self.treeWidget()
        if not isinstance(tree, XTreeWidget):
            return False
        
        return tree.sortOrder() != Qt.AscendingOrder
    
    def __init__(self, *args):
        super(XLoaderItem, self).__init__(*args)
        
        # define custom properties
        self._loading = False
        self._timer   = None
        
        # define standard properties
        self.setFlags(Qt.ItemIsEnabled)
        self.setFirstColumnSpanned(True)
        self.setFixedHeight(30)
        self.setTextAlignment(0, Qt.AlignCenter)
        
        palette = QApplication.palette()
        fg = palette.color(palette.Disabled, palette.Text)
        self.setForeground(0, fg)
    
    def autoload(self, state=True):
        """
        Begins the process for autoloading this item when it becomes visible
        within the tree.
        
        :param      state | <bool>
        """
        if state and not self._timer:
            self._timer = QTimer()
            self._timer.setInterval(500)
            self._timer.timeout.connect(self.testAutoload)
        
        if state and self._timer and not self._timer.isActive():
            self._timer.start()
        elif not state and self._timer and self._timer.isActive():
            self._timer.stop()
    
    def startLoading(self):
        """
        Updates this item to mark the item as loading.  This will create
        a QLabel with the loading ajax spinner to indicate that progress
        is occurring.
        """
        if self._loading:
            return False
        
        tree = self.treeWidget()
        if not tree:
            return
        
        self._loading = True
        self.setText(0, '')
        
        # create the label for this item
        lbl = QLabel(self.treeWidget())
        lbl.setMovie(XLoaderWidget.getMovie())
        lbl.setAlignment(Qt.AlignCenter)
        tree.setItemWidget(self, 0, lbl)
        return True
    
    def finishLoading(self):
        """
        Stops the loader for this item and removes it from the tree.
        """
        self.takeFromTree()
    
    def testAutoload(self):
        """
        Checks to see if this item should begin the loading process.
        """
        tree = self.treeWidget()
        if not tree:
            return
        
        rect = tree.visualItemRect(self)
        if rect.isNull():
            return
        
        center = rect.center()
        if not tree.rect().contains(center):
            return
        
        self.startLoading()
        self._timer.stop()

#------------------------------------------------------------------------------

class XTreeWidgetDelegate(QItemDelegate):
    """ Delegate for additional features to the XTreeWidget. """
    def __init__(self, parent):
        super(XTreeWidgetDelegate, self).__init__(parent)
        
        # set custom properties
        self._gridPen           = QPen()
        self._showGrid          = True
        self._showGridColumns   = True
        self._showGridRows      = True
        self._extendsTree       = True
        self._showRichText      = False
        self._displayMappers    = {}
        self._foreground        = {}
        self._background        = {}
        self._headerIndex       = 0
        self._currentOverlay    = None
        self._currentDisplay    = None
        self._showHighlights    = True
        self._disabledEditingColumns = set()
        
        self._datetimeFormat    = '%m/%d/%y @ %I:%M%p'
        self._timeFormat        = '%I:%M%p'
        self._dateFormat        = '%m/%d/%y'
        
        self._hoverBackground   = None
        self._hoverForeground   = None
        self._hoverIcon         = None
        self._expandIcon        = None
        
        self._useCheckMaps      = False
        self._checkOnMap        = None
        self._checkPartialMap   = None
        self._checkOffMap       = None
        
        # setup defaults
        palette     = parent.palette()
        base_clr    = palette.color(palette.Base)
        avg         = (base_clr.red() + base_clr.green() + base_clr.blue())/3.0
        
        if avg < 80:
            grid_clr = base_clr.lighter(200)
        elif avg < 140:
            grid_clr = base_clr.lighter(140)
        else:
            grid_clr = base_clr.darker(140)
            
        self.setGridPen(grid_clr)

    def background(self, column, default=None):
        """
        Returns the background brush for the given column of this delegate.
        
        :param      column | <int>
                    default | <variant>
        
        :return     <QBrush> || None
        """
        return self._background.get(column, default)

    def checkPartialMap( self ):
        """
        Returns the pixmap to use when rendering a check in the partial state.
        
        :return     <QPixmap> || None
        """
        return self._checkPartialMap
    
    def checkOffMap( self ):
        """
        Returns the pixmap to use when rendering a check in the off state.
        
        :return     <QPixmap> || None
        """
        return self._checkOffMap
    
    def checkOnMap( self ):
        """
        Returns the pixmap to use when rendering a check on state.
        
        :return     <QPixmap> || None
        """
        return self._checkOnMap
    
    def createEditor( self, parent, option, index ):
        """
        Creates a new editor for the given index parented to the inputed widget.
        
        :param      parent | <QWidget>
                    option | <QStyleOption>
                    index  | <QModelIndex>
        
        :return     <QWidget> || None
        """
        if index.column() in self._disabledEditingColumns:
            return None
        
        editor = super(XTreeWidgetDelegate, self).createEditor(parent,
                                                               option,
                                                               index)
        
        if isinstance(editor, QDateTimeEdit):
            editor.setCalendarPopup(True)
        
        return editor
    
    def datetimeFormat(self):
        """
        Returns the datetime format for this delegate.
        
        :return     <str>
        """
        return self._datetimeFormat
    
    def dateFormat(self):
        """
        Returns the date format for this delegate.
        
        :return     <str>
        """
        return self._dateFormat
    
    def disableColumnEditing(self, column):
        """
        Adds the given column to the disabled list for editing.
        
        :param      column | <int>
        """
        self._disabledEditingColumns.add(column)
    
    def displayMapper( self, column ):
        """
        Returns the display mapper for this column.
        
        :param      column | <int>
        
        :return     <callable> || None
        """
        return self._displayMappers.get(column)
    
    def drawBackground( self, painter, opt, rect, brush ):
        """
        Make sure the background extends to 0 for the first item.
        
        :param      painter | <QPainter>
                    rect    | <QRect>
                    brush   | <QBrush.
        """
        if ( not brush ):
            return
        
        painter.setPen(Qt.NoPen)
        painter.setBrush(brush)
        painter.drawRect(rect)
    
    def drawCheck( self, painter, option, rect, state ):
        """
        Renders a check indicator within the rectangle based on the inputed \
        check state.
        
        :param      painter | <QPainter>
                    option  | <QStyleOptionViewItem>
                    rect    | <QRect>
                    state   | <Qt.CheckState>
        """
        if ( not self.useCheckMaps() ):
            return super(XTreeWidgetDelegate, self).drawCheck( painter,
                                                               option,
                                                               rect,
                                                               state)
                                                               
        if ( state == Qt.Checked ):
            pixmap = self.checkOnMap()
        elif ( state == Qt.PartiallyChecked ):
            pixmap = self.checkPartialMap()
        else:
            pixmap = self.checkOffMap()
        
        if ( not pixmap ):
            return
        
        x = rect.x() + (rect.width() - 16) / 2.0
        y = rect.y() + (rect.height() - 16) / 2.0
        
        painter.drawPixmap(x, y, pixmap)
    
    def drawDisplay(self, painter, option, rect, text):
        """
        Overloads the drawDisplay method to render HTML if the rich text \
        information is set to true.
        
        :param      painter | <QPainter>
                    option  | <QStyleOptionItem>
                    rect    | <QRect>
                    text    | <str>
        """
        if self.showRichText():
            # create the document
            doc = QTextDocument()
            doc.setTextWidth(float(rect.width()))
            doc.setHtml(text)
            
            # draw the contents
            painter.translate(rect.x(), rect.y())
            doc.drawContents(painter, QRectF(0, 
                                             0, 
                                             float(rect.width()), 
                                             float(rect.height())))
                                             
            painter.translate(-rect.x(), -rect.y())
        else:
            if type(text).__name__ not in ('str', 'unicode', 'QString'):
                text = str(text)
            
            metrics = QFontMetrics(option.font)
            text = metrics.elidedText(text,
                                      Qt.TextElideMode(option.textElideMode),
                                      rect.width())
            
            painter.setFont(option.font)
            painter.drawText(rect, int(option.displayAlignment), text)
    
    def drawOverlay(self, painter, option, rect, icon):
        """
        Draws the overlay pixmap for this item.
        
        :param      painter | <QPainter>
                    option  | <QSylteOptionIndex>
                    rect    | <QRect>
                    pixmap  | <QIcon>
        """
        if icon and not icon.isNull():
            painter.drawPixmap(rect, icon.pixmap(rect.width(), rect.height()))
    
    def drawGrid(self, painter, opt, rect, index):
        """
        Draws the grid lines for this delegate.
        
        :param      painter | <QPainter>
                    opt     | <QStyleOptionItem>
                    rect    | <QRect>
                    index   | <QModelIndex>
        """
        if ( not self.showGrid() ):
            return
        
        painter.setBrush(Qt.NoBrush)
        painter.setPen(self.gridPen())
        
        size = self.gridPen().width() + 1
        
        # draw the lines
        lines = []
        
        # add the column line
        if self.showGridColumns():
            lines.append(QLine(rect.width() - size, 
                               0, 
                               rect.width() - size, 
                               rect.height() - size))
        
        # add the row line
        if (self.showGridRows()):
            lines.append(QLine(0, 
                               rect.height() - size, 
                               rect.width() - size, 
                               rect.height() - size))
        
        painter.drawLines(lines)

    def enableColumnEditing(self, column):
        """
        Removes the given column from the disabled list for editing.
        
        :param      column | <int>
        """
        try:
            self._disabledEditingColumns.remove(column)
        except KeyError:
            pass
    
    def foreground(self, column, default=None):
        """
        Returns the foreground brush for the given column of this delegate.
        
        :param      column | <int>
                    default | <variant>
        
        :return     <QBrush> || None
        """
        return self._foreground.get(column, default)

    def gridPen( self ):
        """
        Returns the pen that will be used when drawing the grid lines.
        
        :return     <QPen>
        """
        return self._gridPen
    
    def extendsTree( self ):
        """
        Returns whether or not the grid lines should extend through the tree \
        area or not.
        
        :return <bool>
        """
        return self._extendsTree
    
    def paint(self, painter, opt, index):
        """
        Overloads the paint method to draw the grid and other options for \
        this delegate.
        
        :param      painter | <QPainter>
                    opt     | <QStyleOptionItem>
                    index   | <QModelIndex>
        """
        # prepare the painter
        painter.save()
        painter.resetTransform()
        
        # extract data from the tree
        tree         = self.parent()
        column       = index.column()
        item         = tree.itemFromIndex(index)
        is_xtreeitem = isinstance(item, XTreeWidgetItem)
        hovered      = False
        font         = item.font(index.column())
        opt.font     = font
        palette      = tree.palette()
        
        painter.translate(opt.rect.x(), opt.rect.y())
        rect_w = opt.rect.width()
        rect_h = opt.rect.height()
        
        painter.setClipRect(0, 0, rect_w, rect_h)
        
        # grab the check information
        checkState = Qt.Unchecked
        size       = opt.decorationSize
        value      = qt.unwrapVariant(index.data(Qt.CheckStateRole))
        
        if value is not None:
            checkState = item.checkState(index.column())
            check_size = min(size.width(), size.height())
            check_size = min(14, check_size)
            checkRect  = QRect(2, 
                               (rect_h - check_size) / 2.0, 
                               check_size, 
                               check_size)
        else:
            checkRect = QRect()
        
        # determine hovering options
        if tree.hoverMode() != XTreeWidget.HoverMode.NoHover and \
           item.flags() & XTreeWidgetItem.ItemIsHoverable:
            
            # hover particular columns
            if tree.hoverMode() == XTreeWidget.HoverMode.HoverItems and \
               item == tree.hoveredItem() and \
               column == tree.hoveredColumn():
                hovered = True
            
            # hover particular items
            elif tree.hoverMode() == XTreeWidget.HoverMode.HoverRows and \
                 id(item) == id(tree.hoveredItem()):
                hovered = True
        
        # setup the decoration information
        if item.isExpanded() and is_xtreeitem and item.expandedIcon(column):
            icon = item.expandedIcon(column)
        
        elif hovered and tree.hoveredColumn() == column and \
             is_xtreeitem and \
             item.hoverIcon(column):
            icon = item.hoverIcon(column)
        
        else:
            icon = item.icon(column)
        
        if icon and not icon.isNull():
            size    = icon.actualSize(opt.decorationSize)
            pixmap  = icon.pixmap(size)
            
            if checkRect:
                x = checkRect.right() + 2
            else:
                x = 0
            
            y = 0
            w = opt.decorationSize.width()
            h = opt.decorationSize.height()
            
            x += 2
            y += (rect_h - size.height()) / 2.0
            
            decorationRect  = QRect(x, y, w, h)
        else:
            pixmap          = QPixmap()
            overlay         = QIcon()
            decorationRect  = QRect()
        
        if is_xtreeitem:
            overlay = item.iconOverlay(column)
            dec_w = decorationRect.width()
            dec_h = decorationRect.height()
            over_w = int(dec_w / 1.7)
            over_h = int(dec_h / 1.7)
            overlayRect = QRect(decorationRect.right() - over_w,
                                decorationRect.bottom() - over_h,
                                over_w,
                                over_h)
        else:
            overlay = QPixmap()
            overlayRect = QRect()
        
        # setup the coloring information
        bg = None
        fg = None
        
        if self.showHighlights() and tree.selectionModel().isSelected(index):
            palette = tree.palette()
            bg = QBrush(palette.color(palette.Highlight))
            fg = QBrush(palette.color(palette.HighlightedText))
        
        elif hovered:
            bg = tree.hoverBackground()
            fg = tree.hoverForeground()
            
            if ( is_xtreeitem ):
                bg = item.hoverBackground(column, bg)
                fg = item.hoverForeground(column, fg)
        
        if not bg:
            bg_role = qt.unwrapVariant(item.data(column, Qt.BackgroundRole))
            if bg_role is not None:
                bg = item.background(column)
            else:
                bg = self.background(column)
        
        if not fg:
            fg_role = qt.unwrapVariant(item.data(column, Qt.ForegroundRole))
            if fg_role is not None:
                fg = item.foreground(column)
            else:
                fg = self.foreground(column)
        
        if not fg:
            fg = QBrush(palette.color(palette.Text))
        
        # draw custom text
        mapper = self.displayMapper(column)
        if mapper:
            text = mapper(qt.unwrapVariant(index.data(), ''))
        
        # draw specific type text
        else:
            data = qt.unwrapVariant(index.data(Qt.EditRole), None)
            
            # map the data to python
            if type(data) in (QDate, QDateTime, QTime):
                data = data.toPython()
            
            # render a standard date format
            if type(data) == datetime.date:
                text = data.strftime(self.dateFormat())
            
            # render a standard datetime format
            elif type(data) == datetime.time:
                text = data.strftime(self.timeFormat())
            
            # render a standard datetime format
            elif type(data) == datetime.datetime:
                text = data.strftime(self.datetimeFormat())
            
            # draw standard text
            else:
                text = qt.unwrapVariant(index.data(Qt.DisplayRole), '')
        
        opt.displayAlignment = Qt.Alignment(item.textAlignment(index.column()))
        if ( not opt.displayAlignment & (Qt.AlignVCenter | \
                                         Qt.AlignTop | Qt.AlignBottom)):
            opt.displayAlignment |= Qt.AlignVCenter
        
        if decorationRect:
            x = decorationRect.right() + 5
        elif checkRect:
            x = checkRect.right() + 5
        else:
            x = 5
        
        w = rect_w - x - 5
        h = rect_h
        
        displayRect = QRect(x, 0, w, h)
        
        # create the background rect
        backgroundRect = QRect(0, 0, opt.rect.width(), opt.rect.height())
        
        # draw the item
        self.drawBackground( painter, opt, backgroundRect, bg)
        
        painter.setBrush(Qt.NoBrush)
        painter.setPen(fg.color())
        
        self.drawCheck(      painter, opt, checkRect,      checkState)
        self.drawDecoration( painter, opt, decorationRect, pixmap)
        self.drawOverlay(    painter, opt, overlayRect,    overlay)
        self.drawDisplay(    painter, opt, displayRect,    text)
        self.drawGrid(       painter, opt, backgroundRect, index)
        
        painter.restore()
    
    def setBackground(self, column, brush):
        """
        Sets the default item foreground brush.
        
        :param      column | <int>
                    brush  | <QBrush> || None
        """
        if brush:
            self._background[column] = QBrush(brush)
        elif column in self._background:
            self._background.pop(column)
    
    def setCheckOffMap( self, pixmap ):
        """
        Sets the pixmap to be used when rendering a check state in the \
        off state.
        
        :param      pixmap | <QPixmap> || <str> || None
        """
        self._checkOffMap = QPixmap(pixmap)
    
    def setCheckOnMap( self, pixmap ):
        """
        Sets the pixmap to be used when rendering a check state in the \
        on state.
        
        :param      pixmap | <QPixmap> || <str> || None
        """
        self._checkOnMap = QPixmap(pixmap)
    
    def setCheckPartialMap( self, pixmap ):
        """
        Sets the pixmap to be used when rendering a check state in the \
        partial state.
        
        :param      pixmap | <QPixmap> || <str> || None
        """
        self._checkPartialMap = QPixmap(pixmap)
    
    def setDateFormat(self, format):
        """
        Sets the date format for this delegate.
        
        :param      format | <str>
        """
        self._dateFormat = str(format)
    
    def setDatetimeFormat(self, format):
        """
        Sets the datetime format for this delegate.
        
        :param      format | <str>
        """
        self._datetimeFormat = format
    
    def setDisplayMapper( self, column, mapper ):
        """
        Sets the display mapper for this instance.
        
        :param      column | <int>
                    mapper | <callable>
        """
        self._displayMappers[column] = mapper
    
    def setExtendsTree( self, state ):
        """
        Set whether or not this delegate should render its row line through \
        the tree area.
        
        :return     <state>
        """
        self._extendsTree = state
    
    def setGridPen( self, gridPen ):
        """
        Sets the pen that will be used when drawing the grid lines.
        
        :param      gridPen | <QPen> || <QColor>
        """
        self._gridPen = QPen(gridPen)
    
    def setForeground(self, column, brush):
        """
        Sets the default item foreground brush.
        
        :param      brush | <QBrush> || None
        """
        if brush:
            self._foreground[column] = QBrush(brush)
        elif column in self._background:
            self._foreground.pop(column)
    
    def setShowGrid( self, state ):
        """
        Sets whether or not this delegate should draw its grid lines.
        
        :param      state | <bool>
        """
        self._showGrid = state
    
    def setShowGridColumns( self, state ):
        """
        Sets whether or not columns should be rendered when drawing the grid.
        
        :param      state | <bool>
        """
        self._showGridColumns = state
    
    def setShowGridRows( self, state ):
        """
        Sets whether or not the grid rows should be rendered when drawing the \
        grid.
        
        :param      state | <bool>
        """
        self._showGridRows = state
    
    def setShowRichText( self, state ):
        """
        Sets whether or not the delegate should render rich text information \
        as HTML when drawing the contents of the item.
        
        :param      state | <bool>
        """
        self._showRichText = state
    
    def setShowHighlights(self, state):
        """
        Sets whether or not the highlights on this tree should be shown.  When
        off, the selected items in the tree will not look any different from
        normal.
        
        :param      state | <bool>
        """
        self._showHighlights = state
    
    def setTimeFormat(self, format):
        """
        Sets the time format for this delegate.
        
        :param      format | <str>
        """
        self._timeFormat = format
       
    def setUseCheckMaps( self, state ):
        """
        Sets whether or not this delegate should render checked states using \
        the assigned pixmaps or not.
        
        :param      state | <bool>
        """
        self._useCheckMaps = state
    
    def showGrid( self ):
        """
        Returns whether or not this delegate should draw its grid lines.
        
        :return     <bool>
        """
        return self._showGrid
    
    def showGridColumns( self ):
        """
        Returns whether or not this delegate should draw columns when \
        rendering the grid.
        
        :return     <bool>
        """
        return self._showGridColumns
    
    def showGridRows( self ):
        """
        Returns whether or not this delegate should draw rows when rendering \
        the grid.
        
        :return     <bool>
        """
        return self._showGridRows
    
    def showHighlights(self):
        """
        Returns whether or not this tree widget should show its highlights.
        
        :return     <bool>
        """
        return self._showHighlights
    
    def showRichText( self ):
        """
        Returns whether or not the tree is holding richtext information and \
        should render HTML when drawing the data.
        
        :return     <bool>
        """
        return self._showRichText
    
    def sizeHint(self, option, index):
        """
        Returns the size hint for the inputed index.
        
        :param      option  | <QStyleOptionViewItem>
                    index   | <QModelIndex>
        
        :return     <QSize>
        """
        size = super(XTreeWidgetDelegate, self).sizeHint(option, index)
        
        tree = self.parent()
        item = tree.itemFromIndex(index)
        
        try:
            fixed_height = item.fixedHeight()
        except:
            fixed_height = 0
        
        if fixed_height:
            size.setHeight(fixed_height)
        
        return size
    
    def timeFormat(self):
        """
        Returns the time format for this delegate.
        
        :return     <str>
        """
        return self._timeFormat
    
    def useCheckMaps( self ):
        """
        Returns whether or not this delegate should render check maps using \
        the assigned check maps.
        
        :return     <bool>
        """
        return self._useCheckMaps
    
#------------------------------------------------------------------------------

class XTreeWidget(QTreeWidget):
    """ Advanced QTreeWidget class. """
    
    __designer_icon__ = resources.find('img/ui/tree.png')
    
    columnHiddenChanged     = qt.Signal(int, bool)
    headerMenuAboutToShow   = qt.Signal(QMenu, int)
    sortingChanged          = qt.Signal(int, Qt.SortOrder)
    itemCheckStateChanged   = qt.Signal(QTreeWidgetItem, int)
    itemMiddleClicked       = qt.Signal(object, int)
    itemMiddleDoubleClicked = qt.Signal(object, int)
    itemRightDoubleClicked  = qt.Signal(object, int)
    
    HoverMode             = enum('NoHover', 'HoverRows', 'HoverItems')
    
    def __init__( self, parent = None, delegateClass = None ):
        super(XTreeWidget, self).__init__(parent)
        
        if delegateClass is None:
            delegateClass = XTreeWidgetDelegate
        
        # create custom properties
        self._headerMenu            = None
        self._maximumFilterLevel    = None
        self._filteredColumns       = [0]
        self._sortOrder             = Qt.DescendingOrder
        self._dataCollectorRef      = None
        self._dragDropFilterRef     = None
        self._arrowStyle            = False
        self._columnMinimums        = {}
        self._hint                  = ''
        self._useDragPixmaps        = True
        self._usePopupToolTip       = False
        self._lockedView            = None
        self._lockedColumn          = None
        self._editable              = False
        self._defaultItemHeight     = 0
        self._exporters             = {}
        
        # record the down state items
        self._downItem              = None
        self._downState             = None
        self._downColumn            = None
        
        palette = self.palette()
        self._hintColor             = palette.color(palette.Disabled, 
                                                    palette.Text)
        
        ico = resources.find('img/treeview/drag_multi.png')
        self._dragMultiPixmap       = QPixmap(ico)
        
        ico = resources.find('img/treeview/drag_single.png')
        self._dragSinglePixmap      = QPixmap(ico)
        
        # store hovering information
        self._hoveredColumn         = -1
        self._hoveredItem           = None
        self._hoverBackground       = None
        self._hoverForeground       = None
        self._hoverMode             = XTreeWidget.HoverMode.NoHover
        
        # load exporters from the system
        for exporter in XExporter.plugins(XExporter.Flags.SupportsTree):
            self._exporters[exporter.filetype()] = exporter
        
        # create the delegate
        self.setItemDelegate(delegateClass(self))
        self.setMouseTracking(True)
        self.setTabKeyNavigation(True)
        self.setEditTriggers(QTreeWidget.NoEditTriggers)
        
        # setup header
        header = self.header()
        header.setContextMenuPolicy( Qt.CustomContextMenu )
        
        # connect signals
        header.customContextMenuRequested.connect( self.showHeaderMenu )
        header.sectionResized.connect(self.__setUserMinimumSize)
        header.sectionClicked.connect(self.emitSortingChanged)
        
        self.destroyed.connect(self.__destroyLockedView)
    
    def __collectFilterTerms( self, 
                            mapping, 
                            item = None, 
                            level = 0 ):
        """
        Generates a list of filter terms based on the column data for the \
        items in the tree.  If no parent is supplied, then the top level items \
        will be used, otherwise the children will be searched through.  The \
        level value will drive how far down the tree we will look for the terms.
        
        :param      mapping | {<int> column: <set> values, ..}
                    item    | <QTreeWidgetItem> || None
                    level   | <int>
        """
        if ( not mapping ):
            return
        
        max_level = self.maximumFilterLevel()
        if ( max_level != None and level > max_level ):
            return False
        
        if ( not item ):
            for i in range(self.topLevelItemCount()):
                self.__collectFilterTerms(mapping, self.topLevelItem(i))
        else:
            # add the item data to the mapping
            for index in mapping.keys():
                text = str(item.text(index))
                if ( not text ):
                    continue
                    
                mapping[index].add(text)
            
            for c in range(item.childCount()):
                self.__collectFilterTerms(mapping, item.child(c), level + 1)
    
    def __destroyLockedView(self):
        """
        Destroys the locked view from this widget.
        """
        if self._lockedView:
            self._lockedView.close()
            self._lockedView.deleteLater()
            self._lockedView = None
    
    def __filterItems( self, 
                       terms, 
                       autoExpand = True, 
                       caseSensitive = False,
                       parent = None,
                       level = 0):
        """
        Filters the items in this tree based on the inputed keywords.
        
        :param      terms           | {<int> column: [<str> term, ..], ..}
                    autoExpand      | <bool>
                    caseSensitive   | <bool>
                    parent          | <QTreeWidgetItem> || None
        
        :return     <bool> | found
        """
        # make sure we're within our mex level for filtering
        max_level = self.maximumFilterLevel()
        if ( max_level != None and level > max_level ):
            return False
        
        found = False
        items = []
        
        # collect the items to process
        if ( not parent ):
            for i in range(self.topLevelItemCount()):
                items.append(self.topLevelItem(i))
        else:
            for c in range(parent.childCount()):
                items.append(parent.child(c))
        
        for item in items:
            # process all the children first
            cfound = self.__filterItems(terms, 
                                       autoExpand, 
                                       caseSensitive,
                                       item,
                                       level + 1)
            
            # if there is no filter keywords, then all items will be visible
            if ( not any(terms.values()) ):
                found = True
                item.setHidden(False)
                if ( autoExpand ):
                    item.setExpanded(False)
            
            # if there is filter text and children are visible, force this item
            # to be visible always
            elif ( cfound ):
                found = True
                item.setHidden(False)
                if ( autoExpand and item.childCount() ):
                    item.setExpanded(True)
            
            else:
                # match all generic keywords
                generic         = terms.get(-1, [])
                generic_found   = dict((key, False) for key in generic)
                
                # match all specific keywords
                col_found  = dict((col, False) for col in terms if col != -1)
                
                # look for any matches for any column
                mfound = False
                
                for column in self._filteredColumns:
                    # determine the check text based on case sensitivity
                    if ( caseSensitive ):
                        check = str(item.text(column))
                    else:
                        check = str(item.text(column)).lower()
                    
                    specific = terms.get(column, [])
                    
                    # make sure all the keywords match
                    for key in generic + specific:
                        if ( not key ):
                            continue
                        
                        # look for exact keywords
                        elif ( key.startswith('"') and key.endswith('"') ):
                            if ( key.strip('"') == check ):
                                if ( key in generic ):
                                    generic_found[key] = True
                                
                                if ( key in specific ):
                                    col_found[column] = True
                        
                        # look for ending keywords
                        elif ( key.startswith('*') and not key.endswith('*') ):
                            if ( check.endswith(key.strip('*')) ):
                                if ( key in generic ):
                                    generic_found[key] = True
                                if ( key in specific ):
                                    col_found[column] = True
                        
                        # look for starting keywords
                        elif ( key.endswith('*') and not key.startswith('*') ):
                            if ( check.startswith(key.strip('*')) ):
                                if ( key in generic ):
                                    generic_found[key] = True
                                if ( key in specific ):
                                    col_found[column] = True
                        
                        # look for generic keywords
                        elif ( key.strip('*') in check ):
                            if ( key in generic ):
                                generic_found[key] = True
                            if ( key in specific ):
                                col_found[column] = True
                    
                    mfound = all(col_found.values()) and \
                             all(generic_found.values())
                    if ( mfound ):
                        break
                
                item.setHidden(not mfound)
                
                if ( mfound ):
                    found = True
                
                if ( mfound and autoExpand and item.childCount() ):
                    item.setExpanded(True)
        
        return found
    
    def __setUserMinimumSize( self, section, oldSize, newSize ):
        """
        Records the user minimum size for a column.
        
        :param      section | <int>
                    oldSize | <int>
                    newSize | <int>
        """
        if self.isVisible():
            self._columnMinimums[section] = newSize
    
    def __updateLockedSection(self, index, oldSize, newSize):
        if self._lockedView:
            view = self._lockedView
            header = self._lockedView.header()
            
            view.blockSignals(True)
            header.blockSignals(True)
            view.setColumnWidth(index, newSize)
            header.blockSignals(False)
            view.blockSignals(False)
            
            self.__updateLockedView()
    
    def __updateStandardSection(self, index, oldSize, newSize):
        self.blockSignals(True)
        self.header().blockSignals(True)
        self.setColumnWidth(index, newSize)
        self.blockSignals(False)
        self.header().blockSignals(False)
        
        self.__updateLockedView()
    
    def __updateLockedView(self):
        width = 0
        for c in range(self._lockColumn+1):
            width += self.columnWidth(c)
        
        offset_h = self.horizontalScrollBar().height()
        self._lockedView.resize(width, self.height() - offset_h - 4)
    
    def blockAllSignals( self, state ):
        """
        Fully blocks all signals - tree, header signals.
        
        :param      state | <bool>
        """
        self.blockSignals(state)
        self.header().blockSignals(state)
    
    def checkedItems(self, column=0, parent=None, recurse=True):
        """
        Returns a list of the checked items for this tree widget based on
        the inputed column and parent information.
        
        :param      column  | <int>
                    parent  | <QTreeWidget> || None
                    recurse | <bool>
        
        :return     [<QTreeWidgetItem>, ..]
        """
        output = []
        if not parent:
            for i in range(self.topLevelItemCount()):
                item = self.topLevelItem(i)
                if item.checkState(column) == Qt.Checked:
                    output.append(item)
                
                if recurse:
                    output += self.checkedItems(column, item, recurse)
        else:
            for c in range(parent.childCount()):
                item = parent.child(c)
                if item.checkState(column) == Qt.Checked:
                    output.append(item)
                
                if recurse:
                    output += self.checkedItems(column, item, recurse)
        return output
    
    def collectFilterTerms( self, columns = None, ignore = None ):
        """
        Returns a collection of filter terms for this tree widget based on \
        the results in the tree items.  If the optional columns or ignore \
        values are supplied then the specific columns will be used to generate \
        the search terms, and the columns in the ignore list will be stripped \
        out.
        
        :param      columns | [<str> column, ..] || None
                    ignore  | [<str> column, ..] || None
        
        :return     {<str> column: [<str> term, ..]}
        """
        if ( columns == None ):
            columns = self.columns()
            
        if ( ignore ):
            columns = [column for column in columns if not column in ignore]
        
        # this will return an int/set pairing which we will change to a str/list
        terms = {}
        for column in columns:
            index = self.column(column)
            if ( index == -1 ):
                continue
            
            terms[index] = set()
        
        self.__collectFilterTerms(terms)
        return dict([(self.columnOf(i[0]), list(i[1])) for i in terms.items()])
    
    def column( self, name ):
        """
        Returns the index of the column at the given name.
        
        :param      name | <str>
        
        :return     <int> (-1 if not found)
        """
        columns = self.columns()
        if ( name in columns ):
            return columns.index(name)
        else:
            check = projex.text.underscore(name)
            for i, column in enumerate(columns):
                if ( projex.text.underscore(column) == check ):
                    return i
        return -1
    
    def columnOf( self, index ):
        """
        Returns the name of the column at the inputed index.
        
        :param      index | <int>
        
        :return     <str>
        """
        columns = self.columns()
        if ( 0 <= index and index < len(columns) ):
            return columns[index]
        return ''
    
    def columns( self ):
        """
        Returns the list of column names for this tree widget's columns.
        
        :return     [<str>, ..]
        """
        hitem = self.headerItem()
        output = []
        for c in range(hitem.columnCount()):
            text = str(hitem.text(c))
            if ( not text ):
                text = str(hitem.toolTip(c))
            output.append(text)
        return output
    
    def createHeaderMenu(self, index):
        """
        Creates a new header menu to be displayed.
        
        :return     <QMenu>
        """
        menu = QMenu(self)
        #act = menu.addAction("Hide '%s'" % self.columnOf(index))
        #act.triggered.connect( self.headerHideColumn )
        
        '''menu.addSeparator()
        
        act = menu.addAction('Sort Ascending')
        act.setIcon(QIcon(resources.find('img/sort_ascending.png')))
        act.triggered.connect( self.headerSortAscending )
        
        act = menu.addAction('Sort Descending')
        act.setIcon(QIcon(resources.find('img/sort_descending.png')))
        act.triggered.connect( self.headerSortDescending )
        
        act = menu.addAction('Resize to Contents')
        act.setIcon(QIcon(resources.find('img/treeview/fit.png')))
        act.triggered.connect( self.resizeToContents )
        '''
        menu.addSeparator()
        
        #Show/Hide Phases
        phaseFilterMenu = menu.addMenu( 'Show/Hide Phases' )
        phaseFilterMenu.setIcon(QIcon(resources.find('img/columns.png')))
        phaseFilterMenu.addAction('Show All')
        phaseFilterMenu.addAction('Hide All')
        phaseFilterMenu.addSeparator()
        
        hitem = self.headerItem()        
        phases = sharedDB.myPhases
        for phase in sorted(sharedDB.myPhases):
            #col    = self.column(column)
            action = phaseFilterMenu.addAction(phase._name)
            action.setCheckable(True)
            action.setChecked(phase._visible)
        
        phaseFilterMenu.triggered.connect( self.togglePhasesByAction )
        
        '''#Show/Hide Columns
        colmenu = menu.addMenu( 'Show/Hide Columns' )
        colmenu.setIcon(QIcon(resources.find('img/columns.png')))
        colmenu.addAction('Show All')
        colmenu.addAction('Hide All')
        colmenu.addSeparator()
        
        hitem = self.headerItem()
        columns = self.columns()
        for column in sorted(columns):
            col    = self.column(column)
            action = colmenu.addAction(column)
            action.setCheckable(True)
            action.setChecked(not self.isColumnHidden(col))
        
        colmenu.triggered.connect( self.toggleColumnByAction )'''
        
        #menu.addSeparator()
        #export = menu.addAction('Export as...')
        #export.setIcon(QIcon(resources.find('img/export.png')))
        #export.triggered.connect(self.exportAs)
        
        return menu
    
    def dataCollector( self ):
        """
        Returns a method or function that will be used to collect mime data \
        for a list of treewidgetitems.  If set, the method should accept a \
        single argument for a list of items and then return a QMimeData \
        instance.
        
        :usage      |from PyQt4.QtCore import QMimeData, QWidget
                    |from projexui.widgets.xtreewidget import XTreeWidget
                    |
                    |def collectData(tree, items):
                    |   data = QMimeData()
                    |   data.setText(','.join(map(lambda x: x.text(0), items)))
                    |   return data
                    |
                    |class MyWidget(QWidget):
                    |   def __init__( self, parent ):
                    |       super(MyWidget, self).__init__(parent)
                    |       
                    |       self._tree = XTreeWidget(self)
                    |       self._tree.setDataCollector(collectData)
                    
        
        :return     <function> || <method> || None
        """
        func = None
        if self._dataCollectorRef:
            func = self._dataCollectorRef()
        if not func:
            self._dataCollectorRef = None
        return func
    
    def defaultItemHeight(self):
        """
        Returns the default item height for this instance.
        
        :return     <int>
        """
        return self._defaultItemHeight
    
    def dragEnterEvent( self, event ):
        """
        Processes the drag drop event using the filter set by the \
        setDragDropFilter
        
        :param      event | <QDragEvent>
        """
        filt = self.dragDropFilter()
        if not filt:
            super(XTreeWidget, self).dragEnterEvent(event)
            return
            
        filt(self, event)
        
    def dragMoveEvent( self, event ):
        """
        Processes the drag drop event using the filter set by the \
        setDragDropFilter
        
        :param      event | <QDragEvent>
        """
        filt = self.dragDropFilter()
        if not filt:
            super(XTreeWidget, self).dragMoveEvent(event)
            return
        
        filt(self, event)
    
    def dragMultiPixmap( self ):
        """
        Returns the pixmap used to show multiple items dragged.
        
        :return     <QPixmap>
        """
        return self._dragMultiPixmap
    
    def dragSinglePixmap( self ):
        """
        Returns the pixmap used to show single items dragged.
        
        :return     <QPixmap>
        """
        return self._dragSinglePixmap
    
    def dragDropFilter( self ):
        """
        Returns a drag and drop filter method.  If set, the method should \
        accept 2 arguments: a QWidget and a drag/drop event and process it.
        
        :usage      |from PyQt4.QtCore import QEvent
                    |
                    |class MyWidget(QWidget):
                    |   def __init__( self, parent ):
                    |       super(MyWidget, self).__init__(parent)
                    |       
                    |       self._tree = XTreeWidget(self)
                    |       self._tree.setDragDropFilter(MyWidget.handleDragDrop)
                    |   
                    |   @staticmethod
                    |   def handleDragDrop(object, event):
                    |       if ( event.type() == QEvent.DragEnter ):
                    |           event.acceptProposedActions()
                    |       elif ( event.type() == QEvent.Drop ):
                    |           print 'dropping'
        
        :return     <function> || <method> || None
        """
        filt = None
        if self._dragDropFilterRef:
            filt = self._dragDropFilterRef()
        
        if not filt:
            self._dragDropFilterRef = None
            
        return filt
     
    def dropEvent( self, event ):
        """
        Processes the drag drop event using the filter set by the \
        setDragDropFilter
        
        :param      event | <QDropEvent>
        """
        filt = self.dragDropFilter()
        if not filt:
            super(XTreeWidget, self).dropEvent(event)
            return
        
        filt(self, event)
    
    def edit(self, index, trigger, event):
        """
        Prompts the edit for the inputed index given a trigger and event.
        
        :param      index   | <QModelIndex>
                    trigger | <EditTrigger>
                    event   | <QEvent>
        """
        # disable right-click editing
        if trigger in (self.SelectedClicked, self.DoubleClicked) and \
           event.button() in (Qt.RightButton, Qt.MidButton):
            return False
        
        return super(XTreeWidget, self).edit(index, trigger, event)
    
    def emitSortingChanged( self, index ):
        """
        Emits the sorting changed signal if the user clicks on a sorting
        column.
        
        :param      index | <int>
        """
        if ( not self.signalsBlocked() and self.isSortingEnabled() ):
            self.sortingChanged.emit(index, self.header().sortIndicatorOrder())
    
    def export(self, filename):
        """
        Exports the data from this tree to the given filename.
        
        :param      filename | <str>
        """
        filename = str(filename)
        ext = os.path.splitext(filename)[1]
        
        exporter = self.exporter(ext)
        if exporter:
            return exporter.exportTree(self, filename)
        else:
            return False
    
    def exporter(self, ext):
        """
        Returns the exporter for this tree for the given extension.
        
        :param      ext | <str>
        """
        return self._exporters.get(ext)
    
    def exporters(self):
        """
        Returns a list of exporters associated with this tree widget.
        
        :return     [<projexui.xexporter.XExporter>, ..]
        """
        return self._exporters.values()
    
    def exportAs(self):
        """
        Prompts the user to export the information for this tree based on the
        available exporters.
        """
        exporters = self.exporters()
        if not exporters:
            return False
            
        ftypes = ';;'.join(['{0} Files (*{1})'.format(ex.name(), ex.filetype())\
                             for ex in exporters])
        
        filename = QFileDialog.getSaveFileName(self.window(),
                                               'Export Data',
                                               '',
                                               ftypes)
        
        if type(filename) == tuple:
            filename = filename[0]
        
        if filename:
            return self.export(str(filename))
        return False
    
    def viewportEvent( self, event ):
        """
        Displays the help event for the given index.
        
        :param      event  | <QHelpEvent>
                    view   | <QAbstractItemView>
                    option | <QStyleOptionViewItem>
                    index  | <QModelIndex>
        
        :return     <bool>
        """
        # intercept tooltips to use the XPopupWidget when desired
        if event.type() == event.ToolTip and self.usePopupToolTip():
            index = self.indexAt(event.pos())
            item  = self.itemAt(event.pos())
            
            if not (index and item):
                event.ignore()
                return False
            
            tip   = item.toolTip(index.column())
            rect  = self.visualRect(index)
            point = QPoint(rect.left() + 5, rect.bottom() + 1)
            point = self.viewport().mapToGlobal(point)
            
            if tip:
                XPopupWidget.showToolTip(tip, 
                                         anchor = XPopupWidget.Anchor.TopLeft,
                                         point  = point,
                                         parent = self)
            
            event.accept()
            return True
        else:
            return super(XTreeWidget, self).viewportEvent(event)
    
    def filteredColumns( self ):
        """
        Returns the columns that are used for filtering for this tree.
        
        :return     [<int>, ..]
        """
        return self._filteredColumns
    
    @qt.Slot(str)
    def filterItems( self, 
                     terms, 
                     autoExpand = True, 
                     caseSensitive = False ):
        """
        Filters the items in this tree based on the inputed text.
        
        :param      terms           | <str> || {<str> column: [<str> opt, ..]}
                    autoExpand      | <bool>
                    caseSensitive   | <bool>
        """
        # create a dictionary of options
        if ( type(terms) != dict ):
            terms = {'*': str(terms)}
        
        # create a dictionary of options
        if ( type(terms) != dict ):
            terms = {'*': str(terms)}
        
        # validate the "all search"
        if ( '*' in terms and type(terms['*']) != list ):
            sterms = str(terms['*'])
            
            if ( not sterms.strip() ):
                terms.pop('*')
            else:
                dtype_matches = COLUMN_FILTER_EXPR.findall(sterms)
                
                # generate the filter for each data type
                for match, dtype, values in dtype_matches:
                    sterms = sterms.replace(match, '')
                    terms.setdefault(dtype, [])
                    terms[dtype] += values.split(',')
                
                keywords = sterms.replace(',', '').split()
                while ( '' in keywords ):
                    keywords.remove('')
                
                terms['*'] = keywords
        
        # filter out any columns that are not being searched
        filtered_columns = self.filteredColumns()
        filter_terms = {}
        for column, keywords in terms.items():
            index = self.column(column)
            if ( column != '*' and not index in filtered_columns ):
                continue
            
            if ( not caseSensitive ):
                keywords = [str(keyword).lower() for keyword in keywords]
            else:
                keywords = map(str, keywords)
            
            filter_terms[index] = keywords
        
        self.__filterItems(filter_terms, autoExpand, caseSensitive, 0)
    
    def gridPen( self ):
        """
        Returns the pen that will be used when drawing the grid lines.
        
        :return     <QPen>
        """
        delegate = self.itemDelegate()
        if ( isinstance(delegate, XTreeWidgetDelegate) ):
            return delegate.gridPen()
        return QPen()
    
    def extendsTree( self ):
        """
        Returns whether or not the grid lines should extend through the tree \
        area or not.
        
        :return <bool>
        """
        delegate = self.itemDelegate()
        if ( isinstance(delegate, XTreeWidgetDelegate) ):
            return delegate.extendsTree()
        return False
    
    def headerHideColumn( self ):
        """
        Hides the current column set by the header index.
        """
        self.setColumnHidden(self._headerIndex, True)
        
        # ensure we at least have 1 column visible
        found = False
        for col in range(self.columnCount()):
            if ( not self.isColumnHidden(col) ):
                found = True
                break
        
        if ( not found ):
            self.setColumnHidden(0, False)
    
    def headerMenu(self):
        """
        Returns the menu to be displayed for this tree's header menu request.
        
        :return     <QMenu> || None
        """
        return self._headerMenu
    
    def headerMenuColumn(self):
        """
        Returns the index of the column that is being edited for the header
        menu.
        
        :return     <int>
        """
        return self._headerIndex
    
    def headerSortAscending( self ):
        """
        Sorts the column at the current header index by ascending order.
        """
        self.setSortingEnabled(True)
        self.sortByColumn(self._headerIndex, Qt.AscendingOrder)
    
    def headerSortDescending( self ):
        """
        Sorts the column at the current header index by descending order.
        """
        self.setSortingEnabled(True)
        self.sortByColumn(self._headerIndex, Qt.DescendingOrder)
    
    def hiddenColumns( self ):
        """
        Returns a list of the hidden columns for this tree.
        
        :return     [<str>, ..]
        """
        output  = []
        columns = self.columns()
        for c, column in enumerate(columns):
            if ( not self.isColumnHidden(c) ):
                continue
            output.append(column)
        return output
    
    def highlightByAlternate(self):
        """
        Sets the palette highlighting for this tree widget to use a darker
        version of the alternate color vs. the standard highlighting.
        """
        palette = QApplication.palette()
        palette.setColor(palette.HighlightedText, palette.color(palette.Text))
        
        clr = palette.color(palette.AlternateBase)
        palette.setColor(palette.Highlight, clr.darker(110))
        self.setPalette(palette)
    
    def hint( self ):
        """
        Returns the hint that will be rendered for this tree if there are no
        items defined.
        
        :return     <str>
        """
        return self._hint
    
    def hintColor( self ):
        """
        Returns the color used for the hint rendering.
        
        :return     <QColor>
        """
        return self._hintColor
    
    def hoverBackground( self ):
        """
        Returns the default hover background for this tree widget.
        
        :return     <QBrush> || None
        """
        return self._hoverBackground
        
    def hoverForeground( self ):
        """
        Returns the default hover foreground for this tree widget.
        
        :return     <QBrush> || None
        """
        return self._hoverForeground
    
    def hoverMode( self ):
        """
        Returns the hover mode for this tree widget.
        
        :return     <XTreeWidget.HoverMode>
        """
        return self._hoverMode
    
    def hoveredColumn( self ):
        """
        Returns the currently hovered column.  -1 will be returned if no
        column is hovered.
        
        :return     <int>
        """
        return self._hoveredColumn
    
    def hoveredItem( self ):
        """
        Returns the currently hovered item.
        
        :return     <QTreeWidgetItem> || None
        """
        out = None
        if ( self._hoveredItem is not None ):
            out = self._hoveredItem()
            
            if ( out is None ):
                self._hoveredItem = None
        
        return out
    
    def isArrowStyle( self ):
        """
        Returns whether or not the stylesheet is using arrows to group.
        
        :return     <bool>
        """
        return self._arrowStyle
    
    def isEditable( self ):
        """
        Returns whether or not this tree widget is editable or not.
        
        :return     <bool>
        """
        return self._editable
    
    def leaveEvent( self, event ):
        """
        Dismisses the hovered item when the tree is exited.
        
        :param      event | <QEvent>
        """
        hitem = self.hoveredItem()
        hcol  = self.hoveredColumn()
        
        if ( hitem != None ):
            self._hoveredItem   = None
            self._hoveredColumn = -1
            
            rect = self.visualItemRect(hitem)
            rect.setWidth(self.viewport().width())
            self.viewport().update(rect)
        
        super(XTreeWidget, self).leaveEvent(event)
    
    def lockToColumn(self, index):
        """
        Sets the column that the tree view will lock to.  If None is supplied,
        then locking will be removed.
        
        :param      index | <int> || None
        """
        self._lockColumn = index
        
        if index is None:
            self.__destroyLockedView()
            return
        else:
            if not self._lockedView:
                view = QTreeView(self.parent())
                view.setModel(self.model())
                view.setSelectionModel(self.selectionModel())
                view.setItemDelegate(self.itemDelegate())
                view.setFrameShape(view.NoFrame)
                view.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
                view.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
                view.setRootIsDecorated(self.rootIsDecorated())
                view.setUniformRowHeights(True)
                view.setFocusProxy(self)
                view.header().setFocusProxy(self.header())
                view.setStyleSheet(self.styleSheet())
                view.setAutoScroll(False)
                view.setSortingEnabled(self.isSortingEnabled())
                view.setPalette(self.palette())
                view.move(self.x(), self.y())
                
                self.setAutoScroll(False)
                self.setUniformRowHeights(True)
                
                view.collapsed.connect(self.collapse)
                view.expanded.connect(self.expand)
                view.expanded.connect(self.__updateLockedView)
                view.collapsed.connect(self.__updateLockedView)
                
                view_head = view.header()
                for i in range(self.columnCount()):
                    view_head.setResizeMode(i, self.header().resizeMode(i))
                
                view.header().sectionResized.connect(self.__updateStandardSection)
                self.header().sectionResized.connect(self.__updateLockedSection)
                
                vbar = view.verticalScrollBar()
                self.verticalScrollBar().valueChanged.connect(vbar.setValue)
                
                self._lockedView = view
            
            self.__updateLockedView()
    
    def maximumFilterLevel( self ):
        """
        Returns the maximum level from which the filtering of this tree's \
        items should finish.
        
        :return     <int> || None
        """
        return self._maximumFilterLevel
        
    def mimeData( self, items ):
        """
        Returns the mime data for dragging for this instance.
        
        :param      items | [<QTreeWidgetItem>, ..]
        """
        func = self.dataCollector()
        if func:
            return func(self, items)
        
        # return defined custom data
        if len(items) == 1 and items[0].dragData():
            data = QMimeData()
            for format, value in items[0].dragData().items():
                data.setData(format, QByteArray(value))
            return data
        
        return super(XTreeWidget, self).mimeData(items)
    
    def moveEvent(self, event):
        super(XTreeWidget, self).moveEvent(event)
        
        if self._lockedView:
            self._lockedView.move(self.x() + self.frameWidth(), 
                                  self.y() + self.frameWidth())
    
    def mouseDoubleClickEvent(self, event):
        """
        Overloads when a mouse press occurs.  If in editable mode, and the
        click occurs on a selected index, then the editor will be created
        and no selection change will occur.
        
        :param      event | <QMousePressEvent>
        """
        item = self.itemAt(event.pos())
        column = self.columnAt(event.pos().x())
        
        if event.button() == Qt.MidButton:
            self.itemMiddleDoubleClicked.emit(item, column)
        elif event.button() == Qt.RightButton:
            self.itemRightDoubleClicked.emit(item, column)
        else:
            super(XTreeWidget, self).mouseDoubleClickEvent(event)
    
    def mousePressEvent(self, event):
        """
        Overloads when a mouse press occurs.  If in editable mode, and the
        click occurs on a selected index, then the editor will be created
        and no selection change will occur.
        
        :param      event | <QMousePressEvent>
        """
        item = self.itemAt(event.pos())
        column = self.columnAt(event.pos().x())
        
        if item and column != -1:
            #print "Extending"
            self._downItem   = weakref.ref(item)
            self._downColumn = column
            self._downState  = item.checkState(column)
        
        elif not item:
            self.setCurrentItem(None)
            self.clearSelection()
        
        if event.button() == Qt.MidButton and item and column != -1:
            self.itemMiddleClicked.emit(item, column)
        
        index = self.indexAt(event.pos())
        sel_model = self.selectionModel()
        
        if self.isEditable() and index and sel_model.isSelected(index):
            self.edit(index, self.SelectedClicked, event)
            event.accept()
        else:
            super(XTreeWidget, self).mousePressEvent(event)
    
    def mouseMoveEvent( self, event ):
        """
        Tracks when an item is hovered and exited.
        
        :param      event | <QMoustEvent>
        """
        if ( self.hoverMode() != XTreeWidget.HoverMode.NoHover ):
            item  = self.itemAt(event.pos())
            col   = self.columnAt(event.pos().x())
            hitem = self.hoveredItem()
            hcol  = self.hoveredColumn()
            
            if ( (id(item), col) != (id(hitem), hcol) ):
                if ( item ):
                    self._hoveredItem = weakref.ref(item)
                else:
                    self._hoveredItem = None
                
                self._hoveredColumn = col
                
                rect  = self.visualItemRect(item)
                hrect = self.visualItemRect(hitem)
                
                rect.setWidth(self.viewport().width())
                hrect.setWidth(self.viewport().width())
                
                self.viewport().update(rect)
                self.viewport().update(hrect)
        
        super(XTreeWidget, self).mouseMoveEvent(event)
    
    def mouseReleaseEvent(self, event):
        super(XTreeWidget, self).mouseReleaseEvent(event)
        
        if self._downItem and self._downItem():
            state = self._downItem().checkState(self._downColumn)
            if state != self._downState:
                self.itemCheckStateChanged.emit(self._downItem(), self._downColumn)
        
        self._downItem = None
        self._downState = None
        self._downColumn = None
    
    def moveCursor(self, cursorAction, modifiers):
        """
        Returns a QModelIndex object pointing to the next object in the 
        view, based on the given cursorAction and keyboard modifiers 
        specified by modifiers.
        
        :param      modifiers | <Qt.KeyboardModifiers>
        """
        # moves to the next index
        if cursorAction not in (self.MoveNext,
                                self.MoveRight,
                                self.MovePrevious,
                                self.MoveLeft,
                                self.MoveHome,
                                self.MoveEnd):
            return super(XTreeWidget, self).moveCursor(cursorAction, modifiers)
        
        header = self.header()
        index = self.currentIndex()
        row  = index.row()
        col  = index.column()
        vcol = None
        
        if cursorAction == self.MoveEnd:
            vcol = header.count() - 1
            delta = -1
        elif cursorAction == self.MoveHome:
            vcol = 0
            delta = +1
        elif cursorAction in (self.MoveNext, self.MoveRight):
            delta = +1
        elif cursorAction in (self.MovePrevious, self.MoveLeft):
            delta = -1
        
        if vcol is None:
            vcol = header.visualIndex(col) + delta
        
        ncol = header.count()
        lcol = header.logicalIndex(vcol)
        
        while 0 <= vcol and vcol < ncol and self.isColumnHidden(lcol):
            vcol += delta
            lcol = header.logicalIndex(vcol)
        
        sibling = index.sibling(index.row(), lcol)
        if sibling and sibling.isValid():
            return sibling
        elif delta < 0:
            return index.sibling(index.row() - 1, header.logicalIndex(ncol - 1))
        else:
            return index.sibling(index.row() + 1, header.visualIndex(0))
    
    def paintEvent( self, event ):
        """
        Overloads the paint event to support rendering of hints if there are
        no items in the tree.
        
        :param      event | <QPaintEvent>
        """
        super(XTreeWidget, self).paintEvent(event)
        
        if ( not self.topLevelItemCount() and self.hint() ):
            text    = self.hint()
            rect    = self.rect()
            
            # modify the padding on the rect
            w = min(250, rect.width() - 30)
            x = (rect.width() - w) / 2
            
            rect.setX(x)
            rect.setY(rect.y() + 15)
            rect.setWidth(w)
            rect.setHeight(rect.height() - 30)
            
            align = int(Qt.AlignHCenter | Qt.AlignTop)
            
            # setup the coloring options
            clr     = self.hintColor()
            
            # paint the hint
            painter = QPainter(self.viewport())
            painter.setPen(clr)
            painter.drawText(rect, align | Qt.TextWordWrap, text)
    
    def resizeEvent(self, event):
        super(XTreeWidget, self).resizeEvent(event)
        
        if self._lockedView:
            self.__updateLockedView()
    
    @qt.Slot()
    def resizeToContents( self ):
        """
        Resizes all of the columns for this tree to fit their contents.
        """
        for c in range(self.columnCount()):
            self.resizeColumnToContents(c)
    
    def resizeColumnToContents(self, column):
        """
        Resizes the inputed column to the given contents.
        
        :param      column | <int>
        """
        self.header().blockSignals(True)
        self.setUpdatesEnabled(False)
        
        super(XTreeWidget, self).resizeColumnToContents(column)
        
        min_w = self._columnMinimums.get(column, 0)
        cur_w = self.columnWidth(column)
        if cur_w < min_w:
            self.setColumnWidth(column, min_w)
        
        self.setUpdatesEnabled(True)
        self.header().blockSignals(False)
    
    def restoreXml(self, xml):
        """
        Restores properties for this tree widget from the inputed XML.
        
        :param      xml | <xml.etree.ElementTree.Element>
        
        :return     <bool> success
        """
        if xml is None:
            return False
            
        # restore column data
        header = self.header()
        xcolumns = xml.find('columns')
        if xcolumns is not None:
            for xcolumn in xcolumns:
                name   = xcolumn.get('name')
                index  = self.column(name)
                vindex = int(xcolumn.get('visualIndex', index))
                currvi = header.visualIndex(index)
                
                # restore from name
                if index == -1:
                    continue
                
                if currvi != vindex:
                    header.moveSection(currvi, vindex)
                
                self.setColumnHidden(index, xcolumn.get('hidden') == 'True')
                
                if not self.isColumnHidden(index):
                    width  = int(xcolumn.get('width', self.columnWidth(index)))
                    self.setColumnWidth(index, width)
        
        # restore order data
        sortColumn = int(xml.get('sortColumn', 0))
        sortingEnabled = xml.get('sortingEnabled') == 'True'
        sortOrder = Qt.SortOrder(int(xml.get('sortOrder', 0)))
        
        if sortingEnabled:
            self.setSortingEnabled(sortingEnabled)
            self.sortByColumn(sortColumn, sortOrder)
        
        return True
    
    def saveXml(self, xml):
        """
        Saves the data for this tree to the inputed xml entry.
        
        :param      xml | <xml.etree.ElementTree.Element>
        
        :return     <bool> success
        """
        if xml is None:
            return False
            
        # save column data
        header = self.header()
        xcolumns = ElementTree.SubElement(xml, 'columns')
        
        for index in range(self.columnCount()):
            column = self.headerItem().text(index)
            
            xcolumn = ElementTree.SubElement(xcolumns, 'column')
            xcolumn.set('name', column)
            xcolumn.set('visualIndex', str(header.visualIndex(index)))
            xcolumn.set('hidden', str(self.isColumnHidden(index)))
            
            # hidden columns return a 0 width, don't want to save that...
            if not self.isColumnHidden(index):
                xcolumn.set('width', str(self.columnWidth(index)))
        
        # save order data
        xml.set('sortColumn', str(self.sortColumn()))
        xml.set('sortOrder', str(int(self.sortOrder())))
        xml.set('sortingEnabled', str(self.isSortingEnabled()))
        
        return True
    
    def setArrowStyle( self, state ):
        """
        Sets whether or not to use arrows for the grouping mechanism.
        
        :param      state | <bool>
        """
        self._arrowStyle = state
        
        if ( not state ):
            self.setStyleSheet('')
        else:
            right = resources.find('img/treeview/triangle_right.png')
            down  = resources.find('img/treeview/triangle_down.png')
            opts  = (right.replace('\\', '/'), down.replace('\\', '/'))
            self.setStyleSheet(ARROW_STYLESHEET % opts)
    
    def setColumns( self, columns ):
        """
        Sets the column count and list of columns to the inputed column list.
        
        :param      columns | [<str>, ..]
        """
        self.setColumnCount(len(columns))
        self.setHeaderLabels(columns)
    
    def setDataCollector( self, collector ):
        """
        Sets the method that will be used to collect mime data for dragging \
        items from this tree.
        
        :warning    The data collector is stored as a weak-reference, so using \
                    mutable methods will not be stored well.  Things like \
                    instancemethods will not hold their pointer after they \
                    leave the scope that is being used.  Instead, use a \
                    classmethod or staticmethod to define the collector.
        
        :param      collector | <function> || <method> || None
        """
        if ( collector ):
            self._dataCollectorRef = weakref.ref(collector)
        else:
            self._dataCollectorRef = None
    
    def setDefaultItemHeight(self, height):
        """
        Sets the default item height for this instance.
        
        :param      height | <int>
        """
        self._defaultItemHeight = height
    
    def setDragMultiPixmap( self, pixmap ):
        """
        Returns the pixmap used to show multiple items dragged.
        
        :param      pixmap | <QPixmap>
        """
        self._dragMultiPixmap = pixmap
    
    def setDragSinglePixmap( self, pixmap ):
        """
        Returns the pixmap used to show single items dragged.
        
        :param     pixmap | <QPixmap>
        """
        self._dragSinglePixmap = pixmap
    
    def setDragDropFilter( self, ddFilter ):
        """
        Sets the drag drop filter for this widget.
        
        :warning    The dragdropfilter is stored as a weak-reference, so using \
                    mutable methods will not be stored well.  Things like \
                    instancemethods will not hold their pointer after they \
                    leave the scope that is being used.  Instead, use a \
                    classmethod or staticmethod to define the dragdropfilter.
        
        :param      ddFilter | <function> || <method> || None
        """
        if ddFilter:
            self._dragDropFilterRef = weakref.ref(ddFilter)
        else:
            self._dragDropFilterRef = None
    
    def setEditable( self, state ):
        """
        Sets the editable state for this instance.
        
        :param      state | <bool>
        """
        self._editable = state
        
        if not state:
            self.setEditTriggers(QTreeWidget.NoEditTriggers)
        else:
            triggers  = QTreeWidget.DoubleClicked
            triggers |= QTreeWidget.AnyKeyPressed
            triggers |= QTreeWidget.EditKeyPressed
            
            self.setEditTriggers(triggers)
    
    def setExtendsTree( self, state ):
        """
        Set whether or not this delegate should render its row line through \
        the tree area.
        
        :return     <state>
        """
        delegate = self.itemDelegate()
        if ( isinstance(delegate, XTreeWidgetDelegate) ):
            delegate.setExtendsTree(state)
    
    def setFilteredColumns( self, columns ):
        """
        Sets the columns that will be used for filtering of this tree's items.
        
        :param      columns | [<int>, ..]
        """
        self._filteredColumns = columns
    
    def setGridPen( self, gridPen ):
        """
        Sets the pen that will be used when drawing the grid lines.
        
        :param      gridPen | <QPen> || <QColor>
        """
        delegate = self.itemDelegate()
        if ( isinstance(delegate, XTreeWidgetDelegate) ):
            delegate.setGridPen(gridPen)
    
    def setColumnHidden( self, column, state ):
        """
        Sets the hidden state for the inputed column.
        
        :param      column | <int>
                    state  | <bool>
        """
        super(XTreeWidget, self).setColumnHidden(column, state)
        
        if ( not self.signalsBlocked() ):
            self.columnHiddenChanged.emit(column, state)
            self.executeDelayedItemsLayout()
    
    def setHeaderMenu(self, menu):
        """
        Sets the menu to be displayed for this tree's header menu request.
        
        :return     menu | <QMenu> || None
        """
        self._headerMenu = menu
    
    def setHoverBackground( self, brush ):
        """
        Sets the default hover background for this tree widget.
        
        :param      brush | <QBrush> || None
        """
        self._hoverBackground = QBrush(brush)
        
    def setHoverForeground( self, brush ):
        """
        Sets the default hover foreground for this tree widget.
        
        :param      brush | <QBrush> || None
        """
        self._hoverForeground = QBrush(brush)
    
    def setHoverMode( self, mode ):
        """
        Sets the hover mode for this tree widget.
        
        :param      mode | <XTreeWidget.HoverMode>
        """
        self._hoverMode = mode
    
    def setHiddenColumns(self, hidden):
        """
        Sets the columns that should be hidden based on the inputed list of \
        names.
        
        :param      columns | [<str>, ..]
        """
        colnames = self.columns()
        for c, column in enumerate(colnames):
            self.setColumnHidden(c, column in hidden)
    
    def setHint( self, hint ):
        """
        Sets the hint text that will be rendered when no items are present.
        
        :param      hint | <str>
        """
        self._hint = hint
    
    def setHintColor( self, color ):
        """
        Sets the color used for the hint rendering.
        
        :param      color | <QColor>
        """
        self._hintColor = color
    
    def setMaximumFilterLevel( self, level ):
        """
        Sets the maximum level from which the filtering of this tree's \
        items should finish.
        
        :param     level | <int> || None
        """
        self._maximumFilterLevel = level
    
    def setShowGrid( self, state ):
        """
        Sets whether or not this delegate should draw its grid lines.
        
        :param      state | <bool>
        """
        delegate = self.itemDelegate()
        if ( isinstance(delegate, XTreeWidgetDelegate) ):
            delegate.setShowGrid(state)
    
    def setShowGridColumns( self, state ):
        """
        Sets whether or not columns should be rendered when drawing the grid.
        
        :param      state | <bool>
        """
        delegate = self.itemDelegate()
        if ( isinstance(delegate, XTreeWidgetDelegate) ):
            delegate.setShowGridColumns(state)
    
    def setShowGridRows( self, state ):
        """
        Sets whether or not the grid rows should be rendered when drawing the \
        grid.
        
        :param      state | <bool>
        """
        delegate = self.itemDelegate()
        if ( isinstance(delegate, XTreeWidgetDelegate) ):
            delegate.setShowGridRows(state)
    
    def setShowHighlights(self, state):
        """
        Sets whether or not to displa the highlighted color scheme for
        the items in this widget.
        
        :param      state | <bool>
        """
        self.itemDelegate().setShowHighlights(state)
    
    def setShowRichText( self, state ):
        """
        Sets whether or not the delegate should render rich text information \
        as HTML when drawing the contents of the item.
        
        :param      state | <bool>
        """
        delegate = self.itemDelegate()
        if ( isinstance(delegate, XTreeWidgetDelegate) ):
            delegate.setShowRichText(state)
    
    def setVisibleColumns(self, visible):
        """
        Sets the list of visible columns for this widget.  This method will
        take any column in this tree's list NOT found within the inputed column
        list and hide them.
        
        :param      columns | [<str>, ..]
        """
        colnames = self.columns()
        for c, column in enumerate(colnames):
            self.setColumnHidden(c, column not in visible)
    
    def setUseDragPixmaps( self, state ):
        """
        Returns whether or not to use the drag pixmaps when dragging.
        
        :param     state | <bool>
        """
        self._useDragPixmaps = state
    
    def setUsePopupToolTip( self, state ):
        """
        Sets whether or not the XPopupWidget should be used when displaying 
        a tool tip vs. the standard tooltip.
        
        :param      state | <bool>
        """
        self._usePopupToolTip = state
    
    def showGrid( self ):
        """
        Returns whether or not this delegate should draw its grid lines.
        
        :return     <bool>
        """
        delegate = self.itemDelegate()
        if ( isinstance(delegate, XTreeWidgetDelegate) ):
            return delegate.showGrid()
        return False
    
    def showGridColumns( self ):
        """
        Returns whether or not this delegate should draw columns when \
        rendering the grid.
        
        :return     <bool>
        """
        delegate = self.itemDelegate()
        if ( isinstance(delegate, XTreeWidgetDelegate) ):
            return delegate.showGridColumns()
        return False
    
    def showGridRows( self ):
        """
        Returns whether or not this delegate should draw rows when rendering \
        the grid.
        
        :return     <bool>
        """
        delegate = self.itemDelegate()
        if ( isinstance(delegate, XTreeWidgetDelegate) ):
            return delegate.showGridRows()
        return None
    
    def showHeaderMenu( self, pos):
        """
        Displays the header menu for this tree widget.
        
        :param      pos | <QPoint> || None
        """
        header = self.header()
        index  = header.logicalIndexAt(pos)
        self._headerIndex = index
        
        # show a pre-set menu
        if self._headerMenu:
            menu = self._headerMenu
        else:
            menu = self.createHeaderMenu(index)
        
        # determine the point to show the menu from
        if pos is not None:
            point = header.mapToGlobal(pos)
        else:
            point = QCursor.pos()
        
        self.headerMenuAboutToShow.emit(menu, index)
        menu.exec_(point)
    
    def showHighlights(self):
        """
        Returns whether or not to displa the highlighted color scheme for
        the items in this widget.
        
        :return     <bool>
        """
        return self.itemDelegate().showHighlights()
    
    def showRichText( self ):
        """
        Returns whether or not the tree is holding richtext information and \
        should render HTML when drawing the data.
        
        :return     <bool>
        """
        delegate = self.itemDelegate()
        if ( isinstance(delegate, XTreeWidgetDelegate) ):
            return delegate.showRichText()
        return None
    
    def smartResizeColumnsToContents( self ):
        """
        Resizes the columns to the contents based on the user preferences.
        """
        self.blockSignals(True)
        self.setUpdatesEnabled(False)
        
        header = self.header()
        header.blockSignals(True)
        
        columns = range(self.columnCount())
        sizes = [self.columnWidth(c) for c in columns]
        header.resizeSections(header.ResizeToContents)
        
        for col in columns:
            width = self.columnWidth(col)
            if ( width < sizes[col] ):
                self.setColumnWidth(col, sizes[col])
        
        header.blockSignals(False)
        
        self.setUpdatesEnabled(True)
        self.blockSignals(False)
    
    def sortByColumn( self, column, order = Qt.AscendingOrder ):
        """
        Overloads the default sortByColumn to record the order for later \
        reference.
        
        :param      column | <int>
                    order  | <Qt.SortOrder>
        """
        super(XTreeWidget, self).sortByColumn(column, order)
        self._sortOrder = order
    
    def sortByColumnName( self, name, order = Qt.AscendingOrder ):
        """
        Sorts the tree by the inputed column name's index and the given order.
        
        :param      name    | <str>
                    order   | <Qt.SortOrder>
        """
        self.setSortingEnabled(True)
        self.sortByColumn(self.column(name), order)
    
    def sortOrder( self ):
        """
        Returns the sort order used by this tree widget.
        
        :return     <Qt.SortOrder>
        """
        return self._sortOrder
    
    def startDrag( self, supportedActions ):
        """
        Starts a new drag event for this tree widget.  Overloading from the
        default QTreeWidget class to define a better pixmap option when
        dragging many items.
        
        :param      supportedActions | <Qt.DragActions>
        """
        if ( not self.useDragPixmaps() ):
            return super(XTreeWidget, self).startDrag(supportedActions)
        
        filt  = lambda x: x.flags() & Qt.ItemIsDragEnabled
        items = filter(filt, self.selectedItems())
        if ( not items ):
            return
        
        data = self.mimeData(items)
        if ( not data ):
            return
        
        if ( len(items) > 1 ):
            pixmap = self.dragMultiPixmap()
        else:
            pixmap = self.dragSinglePixmap()
        
        # create the drag event
        drag = QDrag(self)
        drag.setMimeData(data)
        drag.setPixmap(pixmap)
        
        drag.exec_(supportedActions, Qt.MoveAction)
    
    def toggleColumnByAction( self, action ):
        """
        Toggles whether or not the column at the inputed action's name should \
        be hidden.
        `
        :param      action | <QAction>
        """
        if ( action.text() == 'Show All' ):
            self.blockSignals(True)
            self.setUpdatesEnabled(False)
            for col in range(self.columnCount()):
                self.setColumnHidden(col, False)
            self.setUpdatesEnabled(True)
            self.blockSignals(False)
            
            self.setColumnHidden(0, False)
            
        elif ( action.text() == 'Hide All' ):
            self.blockSignals(True)
            self.setUpdatesEnabled(False)
            for col in range(self.columnCount()):
                self.setColumnHidden(col, True)
                
            # ensure we have at least 1 column visible
            self.blockSignals(False)
            self.setUpdatesEnabled(True)
            
            self.setColumnHidden(0, False)
            
        else:
            col     = self.column(action.text())
            state   = not action.isChecked()
            self.setColumnHidden(col, state)
            if ( state ):
                self.resizeColumnToContents(col)
            
            # ensure we at least have 1 column visible
            found = False
            for col in range(self.columnCount()):
                if ( not self.isColumnHidden(col) ):
                    found = True
                    break
            
            if not found:
                self.setColumnHidden(0, False)
        
        self.resizeToContents()
        self.update()
        
    def togglePhasesByAction( self, action ):
        """
        Toggles whether or not the column at the inputed action's name should \
        be hidden.
        `
        :param      action | <QAction>
        """
        if ( action.text() == 'Show All' ):
            #print "Showing All Phases"
            sharedDB.calendarview._myXGanttWidget.updatePhaseVisibility(True)

            
        elif ( action.text() == 'Hide All' ):
            sharedDB.calendarview._myXGanttWidget.updatePhaseVisibility(False)
            #print "Hiding All Phases"    
        else:
            state   = action.isChecked()
            #print (action.text() + " = " + str(state))
            sharedDB.calendarview._myXGanttWidget.updatePhaseVisibility(state,action.text())
            
        
        self.resizeToContents()
        self.update()
    
    def topLevelItems(self):
        """
        Returns the list of top level nodes for this tree.
        
        :return     [<QTreeWidgetItem>, ..]
        """
        return map(self.topLevelItem, range(self.topLevelItemCount()))
    
    def useDragPixmaps( self ):
        """
        Returns whether or not to use the drag pixmaps when dragging.
        
        :return     <bool>
        """
        return self._useDragPixmaps
    
    def usePopupToolTip( self ):
        """
        Returns whether or not the tooltips should be the standard one or
        the XPopupWidget.
        
        :return     <bool>
        """
        return self._usePopupToolTip
    
    def visibleColumns(self):
        """
        Returns a list of the visible column names for this widget.
        
        :return     [<str>, ..]
        """
        return [self.column(c) for c in range(self.columnCount()) \
                if not self.isColumnHidden(c)]
    
    def visualRect(self, index):
        """
        Returns the visual rectangle for the inputed index.
        
        :param      index | <QModelIndex>
        
        :return     <QRect>
        """
        rect = super(XTreeWidget, self).visualRect(index)
        item = self.itemFromIndex(index)
        if not rect.isNull() and item and item.isFirstColumnSpanned():
            vpos = self.viewport().mapFromParent(QPoint(0, 0))
            rect.setX(vpos.x())
            rect.setWidth(self.width())
            return rect
        return rect
    
    # define Qt properties
    x_arrowStyle        = qt.Property(bool, isArrowStyle, setArrowStyle)
    x_defaultItemHeight = qt.Property(int,  defaultItemHeight, setDefaultItemHeight)
    x_hint              = qt.Property(str,  hint, setHint)
    x_showGrid          = qt.Property(bool, showGrid, setShowGrid)
    x_showGridRows      = qt.Property(bool, showGridRows, setShowGridRows)
    x_showRichText      = qt.Property(bool, showRichText, setShowRichText)
    x_editable          = qt.Property(bool, isEditable, setEditable)
    x_extendsTree       = qt.Property(bool, extendsTree,  setExtendsTree)
    x_useDragPixmaps    = qt.Property(bool, useDragPixmaps, setUseDragPixmaps)
    x_usePopupToolTip   = qt.Property(bool, 
                                       usePopupToolTip, 
                                       setUsePopupToolTip)
    x_showGridColumns   = qt.Property(bool, 
                                       showGridColumns, 
                                       setShowGridColumns)
    x_showHighlights    = qt.Property(bool, showHighlights, setShowHighlights)
                                       
    x_maximumFilterLevel = qt.Property(int, 
                                        maximumFilterLevel, 
                                        setMaximumFilterLevel)

# define the designer properties
__designer_plugins__ = [XTreeWidget]