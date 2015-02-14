#!/usr/bin/python

"""
Defines the most basic Connection class type for creating
nodes within the projex node scene system.
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

from PyQt4.QtCore   import  Qt, \
                                  QPointF, \
                                  QRectF

from PyQt4.QtGui    import  QColor, \
                                  QGraphicsPathItem, \
                                  QPainterPath, \
                                  QPen, \
                                  QPolygonF, \
                                  QTransform,\
                                  QApplication,\
                                  QGraphicsTextItem,\
                                  QFontMetrics

from projex.enum    import enum

from projexui.widgets.xnodewidget.xnodelayer      import XNodeLayer

# create the common enumerated types needed
XConnectionStyle        = enum( 'Linear',
                                'Block',
                                'Smooth')
                                
XConnectionLocation     = enum( 'Top',
                                'Bottom',
                                'Left',
                                'Right' )

class XNodeConnection( QGraphicsPathItem ):
    """ 
    Defines the base graphics item class that is used to draw a connection
    between two nodes.
    """
    def __init__( self, scene ):
        self._visible               = True
        
        super(XNodeConnection, self).__init__()
        
        # define custom properties
        self._textItem              = None
        self._polygons              = []
        self._style                 = XConnectionStyle.Linear
        self._padding               = 20
        self._squashThreshold       = 2 * scene.cellWidth()
        self._showDirectionArrow    = False
        self._highlightPen          = QPen(QColor('yellow'))
        self._disabledPen           = QPen(QColor(100, 100, 100))
        self._disableWithLayer      = False
        self._enabled               = True
        self._dirty                 = True
        self._customData            = {}
        self._layer                 = None
        self._font                  = QApplication.instance().font()
        self._text                  = ''
        
        self._inputNode                     = None
        self._inputFixedY                   = None
        self._inputFixedX                   = None
        self._inputPoint                    = QPointF()
        self._inputLocation                 = XConnectionLocation.Left
        self._autoCalculateInputLocation    = False
        self._showInputArrow                = False
        
        self._outputNode                    = None
        self._outputFixedX                  = None
        self._outputFixedY                  = None
        self._outputPoint                   = QPointF()
        self._outputLocation                = XConnectionLocation.Right
        self._autoCalculateOutputLocation   = False
        self._showOutputArrow               = False
        
        # set standard properties
        self.setFlags( self.ItemIsSelectable )
        self.setZValue(-1)
        self.setPen( QColor('white') )
        self.setLayer( scene.currentLayer() )
        
    def autoCalculateInputLocation( self ):
        """
        :remarks    Returns whether or not to auto calculate the input
                    location based on the proximity to the output node
                    or point.
        
        :return     <bool>
        """
        return self._autoCalculateInputLocation
    
    def autoCalculateOutputLocation( self ):
        """
        :remarks    Returns whether or not to auto calculate the input
                    location based on the proximity to the output node
                    or point.
        
        :return     <bool>
        """
        return self._autoCalculateOutputLocation
    
    def connectSignals( self, node ):
        """
        :remarks    Connects to signals of the inputed node, if the node
                    is a valid XNode type.
        
        :param      node    <XNode> || None
        
        :return     <bool> success
        """
        from projexui.widgets.xnodewidget.xnode import XNode
        
        # make sure we're connecting to a valid node
        if ( not isinstance(node, XNode) ):
            return False
        
        node.dispatch.geometryChanged.connect(  self.setDirty )
        node.dispatch.visibilityChanged.connect(self.setDirty)
        node.dispatch.removed.connect(          self.forceRemove )
        return True
    
    def controlPoints( self ):
        """
        :remarks    Generates the control points for this path
        
        :return     <list> [ <tuple> ( <float> x, <float> y), .. ]
        """
        
        # calculate the positions
        outputPoint  = self.outputPoint()
        inputPoint   = self.inputPoint()
        
        points = []
        
        x0 = outputPoint.x()
        y0 = outputPoint.y()
        
        xN = inputPoint.x()
        yN = inputPoint.y()
        
        xC = (x0 + xN) / 2.0
        yC = (y0 + yN) / 2.0
        
        points.append((x0, y0))
        
        oloc    = self.outputLocation()
        iloc    = self.inputLocation()
        left    = XConnectionLocation.Left
        right   = XConnectionLocation.Right
        bot     = XConnectionLocation.Bottom
        top     = XConnectionLocation.Top
        
        # create a right-to-left
        if ( (oloc & right) and (iloc & left) ):
            if ( xN < (x0 + self.squashThreshold()) ):
                points.append((x0+self.padding(), y0))
                points.append((x0+self.padding(), yC))
                points.append((xN-self.padding(), yC))
                points.append((xN-self.padding(), yN))
            else:
                points.append((xC, y0))
                points.append((xC, yN))
        
        # create a left-to-right
        elif ( (oloc & left) and (iloc & right) ):
            if ( (x0 - self.squashThreshold()) < xN ):
                points.append((x0-self.padding(), y0))
                points.append((x0-self.padding(), yC))
                points.append((xN+self.padding(), yC))
                points.append((xN+self.padding(), yN))
            else:
                points.append((xC, y0))
                points.append((xC, yN))
        
        # create a bottom-to-top
        elif ( (oloc & bot) and (iloc & top) ):
            if ( yN < (y0 + self.squashThreshold()) ):
                points.append((x0, y0+self.padding()))
                points.append((xC, y0+self.padding()))
                points.append((xC, yN-self.padding()))
                points.append((xN, yN-self.padding()))
            else:
                points.append((x0, yC))
                points.append((xN, yC))
        
        # create a top-to-bottom
        elif ( (oloc & top) and (iloc & bot) ):
            if ( (y0 - self.squashThreshold()) < yN ):
                points.append((x0, y0-self.padding()))
                points.append((xC, y0-self.padding()))
                points.append((xC, yN+self.padding()))
                points.append((xN, yN+self.padding()))
            else:
                points.append((x0, yC))
                points.append((xN, yC))
        
        # create a left-to-left
        elif ( (oloc & left) and (iloc & left) ):
            xMin = min(x0-self.padding(), xN-self.padding())
            points.append((xMin, y0))
            points.append((xMin, yN))
        
        # create a right-to-right
        elif ( (oloc & right) and (iloc & right) ):
            xMax = max(x0+self.padding(), xN+self.padding())
            points.append((xMax, y0))
            points.append((xMax, yN))
        
        # create a bottom-to-bottom
        elif ( (oloc & top) and (iloc & top) ):
            yMin = min(y0-self.padding(), yN-self.padding())
            points.append((x0, yMin))
            points.append((xN, yMin))
        
        # create a bottom-to-bottom
        elif ( (oloc & bot) and (iloc & bot) ):
            yMax = max(y0+self.padding(), yN+self.padding())
            points.append((x0, yMax))
            points.append((xN, yMax))
        
        # create a bottom-to-left or left-to-bottom
        elif (  ((oloc & bot) and (iloc & left)) or 
                ((oloc & left) and (iloc & bot)) ):
            points.append((x0, yN))
        
        # create a bottom-to-right or right-to-bottom
        elif (  ((oloc & bot) and (iloc & right)) or 
                ((oloc & right) and (iloc & bot)) ):
            points.append((x0, y0))
        
        # create a top-to-left or left-to-top
        elif (  ((oloc & top) and (iloc & left)) or 
                ((oloc & left) and (iloc & top)) ):
            points.append((xN, yN))
            
        # create a top-to-right or right-to-top
        elif (  ((oloc & top) and (iloc & right)) or 
                ((oloc & right) and (iloc & top)) ):
            points.append((xN, y0))
        
        points.append((xN, yN))
        
        return points
    
    def customData( self, key, default = None ):
        """
        Returns custom defined data that can be tracked per connection.
        
        :param      key         <str>
        :param      default     <variant>
        
        :return     <variant>
        """
        return self._customData.get(str(key), default)
    
    def direction( self ):
        """
        Returns the output-to-input direction as a tuple of the output \
        and input locations.
        
        :return     (<XConnectionLocation> output, <XConnectionLocation> input)
        """
        return (self.outputLocation(), self.inputLocation())
    
    def disabledPen( self ):
        """
        Returns the pen that should be used when rendering a disabled \
        connection.
        
        :return     <QPen>
        """
        return self._disabledPen
    
    def disableWithLayer( self ):
        """
        Returns whether or not this connection's enabled state should be \
        affected by its layer.
        
        :return     <bool>
        """
        return self._disableWithLayer
    
    def disconnectSignals( self, node ):
        """
        Disconnects from signals of the inputed node, if the node is a \
        valid XNode type.
        
        :param      node    <XNode> || None
        
        :return     <bool> success
        """
        from projexui.widgets.xnodewidget.xnode import XNode
        
        # make sure we're disconnecting from a valid node
        if ( not isinstance(node, XNode) ):
            return False
        
        node.dispatch.geometryChanged.disconnect(   self.setDirty )
        node.dispatch.removed.disconnect(           self.forceRemove )
        return True
    
    def forceRemove( self ):
        """
        Removes the object from the scene by queuing it up for removal.
        """
        scene = self.scene()
        if ( scene ):
            scene.forceRemove(self)
    
    def font( self ):
        """
        Returns the font for this connection.
        
        :return     <QFont>
        """
        return self._font
    
    def hasCustomData( self, key ):
        """
        Returns whether or not there is the given key in the custom data.
        
        :param      key | <str>
        
        :return     <bool>
        """
        return str(key) in self._customData
    
    def highlightPen( self ):
        """
        Return the highlight pen for this connection.
        
        :return     <QPen>
        """
        return self._highlightPen
    
    def inputLocation( self ):
        """
        Returns the input location for this connection.
        
        :return     <XConnectionLocation>
        """
        if ( not self.autoCalculateInputLocation() ):
            return self._inputLocation
        
        # auto calculate directions based on the scene
        if ( self._outputNode ):
            outputRect = self._outputNode.sceneRect()
        else:
            y = self._outputPoint.y()
            outputRect = QRectF( self._outputPoint.x(), y, 0, 0 )
        
        if ( self._inputNode ):
            inputRect  = self._inputNode.sceneRect()
        else:
            y = self._inputPoint.y()
            inputRect  = QRectF( self._inputPoint.x(), y, 0, 0 )
        
        # use the input location as potential places where it can be
        iloc    = self._inputLocation
        left    = XConnectionLocation.Left
        right   = XConnectionLocation.Right
        top     = XConnectionLocation.Top
        bot     = XConnectionLocation.Bottom
        
        if ( self._inputNode == self._outputNode ):
            if ( iloc & right ):
                return right
            elif ( iloc & left ):
                return left
            elif ( iloc & top ):
                return top
            else:
                return bot
                
        elif ( (iloc & left)    and outputRect.right() < inputRect.left() ):
            return left
        elif ( (iloc & right)   and inputRect.right() < outputRect.left() ):
            return right
        elif ( (iloc & top)     and outputRect.bottom() < inputRect.top() ):
            return top
        elif ( (iloc & bot) ):
            return bot
        elif ( (iloc & left) ):
            return left
        elif ( (iloc & right) ):
            return right
        elif ( (iloc & top) ):
            return top
        else:
            return left
    
    def inputNode( self ):
        """
        Returns the input node that is connected to this connection.
        
        :return     <XNode>
        """
        return self._inputNode
    
    def inputFixedX( self ):
        """
        Returns the fixed X value for the input option
        
        :return     <float> || None
        """
        return self._inputFixedX
    
    def inputFixedY( self ):
        """
        Returns the fixed Y value for the input option.
        
        :return     <float> || None
        """
        return self._inputFixedY
    
    def inputPoint( self ):
        """
        Returns a scene space point that the connection \
        will draw to as its input target.  If the connection \
        has a node defined, then it will calculate the input \
        point based on the position of the node, factoring in \
        preference for input location and fixed information. \
        If there is no node connected, then the point defined \
        using the setInputPoint method will be used.
        
        :return     <QPointF>
        """
        node = self.inputNode()
        
        # return the set point
        if ( not node ):
            return self._inputPoint
        
        # otherwise, calculate the point based on location and fixed info
        ilocation   = self.inputLocation()
        ifixedx     = self.inputFixedX()
        ifixedy     = self.inputFixedY()
        return node.positionAt( ilocation, ifixedx, ifixedy )
    
    def isDirection( self, outputLocation, inputLocation ):
        """
        Checks to see if the output and input locations match the settings \
        for this item.
        
        :param      outputLocation      | <XConnectionLocation>
        :param      inputLocation       | <XConnectionLocation>
        
        :return     <bool>
        """
        return (self.isOutputLocation(outputLocation) and 
               self.isInputLocation(inputLocation))
    
    def isDirty( self ):
        """
        Returns whether or not this path object is dirty and needs to \
        be rebuilt.
        
        :return     <bool>
        """
        return self._dirty
    
    def isEnabled( self ):
        """
        Returns whether or not this connection is enabled.
        
        :sa     disableWithLayer
        
        :return     <bool>
        """
        if self._disableWithLayer and self._layer:
            lenabled = self._layer.isEnabled()
        elif self._inputNode and self._outputNode:
            lenabled = self._inputNode.isEnabled() and self._outputNode.isEnabled()
        else:
            lenabled = True
        
        return self._enabled and lenabled
    
    def isInputLocation( self, location ):
        """
        Returns whether or not the inputed location value matches the \
        given input location.
        
        :param      location    | <XConnectionLocation>
        
        :return     <bool>
        """
        return (self.inputLocation() & location) != 0
    
    def isOutputLocation( self, location ):
        """
        Returns whether or not the inputed location value matches the \
        given output location.
        
        :param      location    | <XConnectionLocation>
        
        :return     <bool>
        """
        return (self.outputLocation() & location) != 0
    
    def isStyle( self, style ):
        """
        Return whether or not the connection is set to a particular style.
        
        :param      style       | <XConnectionStyle>
        
        :return     <bool>
        """
        return (self._style & style) != 0
    
    def isVisible( self ):
        """
        Returns whether or not this connection is visible.  If either node it is
        connected to is hidden, then it should be as well.
        
        :return     <bool>
        """
        in_node  = self.inputNode()
        out_node = self.outputNode()
        
        if ( in_node and not in_node.isVisible() ):
            return False
        
        if ( out_node and not out_node.isVisible() ):
            return False
        
        return self._visible
    
    def layer( self ):
        """
        Returns the layer that this node is assigned to.
        
        :return     <XNodeLayer> || None
        """
        return self._layer
    
    def mappedPolygon( self, polygon, path = None, percent = 0.5 ):
        """
        Maps the inputed polygon to the inputed path \
        used when drawing items along the path.  If no \
        specific path is supplied, then this object's own \
        path will be used.  It will rotate and move the \
        polygon according to the inputed percentage.
        
        :param      polygon     <QPolygonF>
        :param      path        <QPainterPath>
        :param      percent     <float>
        
        :return     <QPolygonF> mapped_poly
        """
        translatePerc   = percent
        anglePerc       = percent
        
        # we don't want to allow the angle percentage greater than 0.85
        # or less than 0.05 or we won't get a good rotation angle
        if ( 0.95 <= anglePerc ):
            anglePerc = 0.98
        elif ( anglePerc <= 0.05 ):
            anglePerc = 0.05
        
        if ( not path ):
            path = self.path()
        if ( not (path and path.length()) ):
            return QPolygonF()
        
        # transform the polygon to the path
        point   = path.pointAtPercent(translatePerc)
        angle   = path.angleAtPercent(anglePerc)
        
        # rotate about the 0 axis
        transform   = QTransform().rotate(-angle)
        polygon     = transform.map(polygon)
        
        # move to the translation point
        transform   = QTransform().translate(point.x(), point.y())
        
        # create the rotated polygon
        mapped_poly = transform.map(polygon)
        self._polygons.append(mapped_poly)
        
        return mapped_poly
    
    def mousePressEvent( self, event ):
        """
        Overloads the mouse press event to handle special cases and \
        bypass when the scene is in view mode.
        
        :param      event   <QMousePressEvent>
        """
        # ignore events when the scene is in view mode
        scene = self.scene()
        if ( scene and scene.inViewMode() ):
            event.ignore()
            return
        
        # block the selection signals
        if ( scene ):
            scene.blockSelectionSignals(True)
            
            # clear the selection
            if ( not (self.isSelected() or 
                      event.modifiers() == Qt.ControlModifier) ):
                for item in scene.selectedItems():
                    if ( item != self ):
                        item.setSelected(False)
        
        # try to start the connection
        super(XNodeConnection, self).mousePressEvent(event)
        
    def mouseMoveEvent( self, event ):
        """
        Overloads the mouse move event to ignore the event when \
        the scene is in view mode.
        
        :param      event   <QMouseMoveEvent>
        """
        # ignore events when the scene is in view mode
        scene = self.scene()
        if ( scene and (scene.inViewMode() or scene.isConnecting()) ):
            event.ignore()
            return
        
        # call the base method
        super(XNodeConnection, self).mouseMoveEvent(event)
    
    def mouseReleaseEvent( self, event ):
        """
        Overloads the mouse release event to ignore the event when the \
        scene is in view mode, and release the selection block signal.
         
         :param     event   <QMouseReleaseEvent>
        """
        # ignore events when the scene is in view mode
        scene = self.scene()
        if ( scene and (scene.inViewMode() or scene.isConnecting()) ):
            event.ignore()
            return
        
        # emit the scene's connection menu requested signal if
        # the button was a right mouse button
        if ( event.button() == Qt.RightButton and scene ):
            scene.emitConnectionMenuRequested(self)
            event.accept()
        else:
            super(XNodeConnection, self).mouseReleaseEvent(event)
        
        # unblock the selection signals
        if ( scene ):
            scene.blockSelectionSignals(False)
    
    def opacity( self ):
        """
        Returns the opacity amount for this connection.
        
        :return     <float>
        """
        in_node     = self.inputNode()
        out_node    = self.outputNode()
        
        if ( in_node and out_node and \
             (in_node.isIsolateHidden() or out_node.isIsolateHidden()) ):
            return 0.1
        
        opacity = super(XNodeConnection, self).opacity()
        layer = self.layer()
        if ( layer ):
            return layer.opacity() * opacity
        
        return opacity
    
    def outputLocation( self ):
        """
        Returns the location for the output source position.
        
        :return     <XConnectionLocation>
        """
        if ( not self.autoCalculateOutputLocation() ):
            return self._outputLocation
        
        # auto calculate directions based on the scene
        if ( self._outputNode ):
            outputRect = self._outputNode.sceneRect()
        else:
            y = self._outputPoint.y()
            outputRect = QRectF( self._outputPoint.x(), y, 0, 0 )
        
        if ( self._inputNode ):
            inputRect  = self._inputNode.sceneRect()
        else:
            y = self._inputPoint.y()
            inputRect  = QRectF( self._inputPoint.x(), y, 0, 0 )
            
        oloc    = self._outputLocation
        left    = XConnectionLocation.Left
        right   = XConnectionLocation.Right
        top     = XConnectionLocation.Top
        bot     = XConnectionLocation.Bottom
        
        if ( self._inputNode == self._outputNode ):
            if ( oloc & right ):
                return right
            elif ( oloc & left ):
                return left
            elif ( oloc & top ):
                return top
            else:
                return bot
                
        elif ( (oloc & right)   and outputRect.right() < inputRect.left() ):
            return right
        elif ( (oloc & left)    and inputRect.right() < outputRect.left() ):
            return left
        elif ( (oloc & bot)     and outputRect.bottom() < inputRect.top() ):
            return bot
        elif ( (oloc & top) ):
            return top
        elif ( (oloc & right) ):
            return right
        elif ( (oloc & left) ):
            return left
        elif ( (oloc & bot) ):
            return bot
        else:
            return right
    
    def outputNode( self ):
        """
        Returns the output source node that this connection is currently \
        connected to.
        
        :return     <XNode> || None
        """
        return self._outputNode
    
    def outputFixedX( self ):
        """
        Returns the fixed X position for the output component of this \
        connection.
                    
        :return     <float> || None
        """
        return self._outputFixedX
    
    def outputFixedY( self ):
        """
        Returns the fixed Y position for the output component of this \
        connection.
                    
        :return     <float> || None
        """
        return self._outputFixedY
    
    def outputPoint( self ):
        """
        Returns a scene space point that the connection \
        will draw to as its output source.  If the connection \
        has a node defined, then it will calculate the output \
        point based on the position of the node, factoring in \
        preference for output location and fixed positions.  If \ 
        there is no node connected, then the point defined using \
        the setOutputPoint method will be used.
        
        :return     <QPointF>
        """
        node = self.outputNode()
        
        # return the set point
        if ( not node ):
            return self._outputPoint
        
        # otherwise, calculate the point based on location and fixed positions
        olocation   = self.outputLocation()
        ofixedx     = self.outputFixedX()
        ofixedy     = self.outputFixedY()
        return node.positionAt( olocation, ofixedx, ofixedy )
    
    def padding( self ):
        """
        Returns the amount of padding to be used when drawing a connection \
        that will be drawn backwards.
        
        :return     <float>
        """
        return self._padding
    
    def paint( self, painter, option, widget ):
        """
        Overloads the paint method from QGraphicsPathItem to \
        handle custom drawing of the path using this items \
        pens and polygons.
        
        :param      painter     <QPainter>
        :param      option      <QGraphicsItemStyleOption>
        :param      widget      <QWidget>
        """
        # following the arguments required by Qt
        # pylint: disable-msg=W0613
        
        painter.setOpacity(self.opacity())
        
        # show the connection selected
        if ( not self.isEnabled() ):
            pen = QPen(self.disabledPen())
        elif ( self.isSelected() ):
            pen = QPen(self.highlightPen())
        else:
            pen = QPen(self.pen())
        
        if ( self._textItem ):
            self._textItem.setOpacity(self.opacity())
            self._textItem.setDefaultTextColor(pen.color().darker(110))
        
        # rebuild first if necessary
        if ( self.isDirty() ):
            self.setPath(self.rebuild())
        
        # store the initial hint
        hint = painter.renderHints()
        painter.setRenderHint( painter.Antialiasing )
        
        pen.setWidthF(1.25)
        painter.setPen(pen)
        painter.drawPath(self.path())
        
        # redraw the polys to force-fill them
        for poly in self._polygons:
            if ( not poly.isClosed() ):
                continue
            
            painter.setBrush(pen.color())
            painter.drawPolygon(poly)
        
        # restore the render hints
        painter.setRenderHints(hint)
    
    def prepareToRemove( self ):
        """
        Handles any code that needs to run to cleanup the connection \
        before it gets removed from the scene.
        
        :return     <bool> success
        """
        # disconnect the signals from the input and output nodes
        for node in (self._outputNode, self._inputNode):
            self.disconnectSignals(node)
        
        # clear the pointers to the nodes
        self._inputNode     = None
        self._outputNode    = None
        
        return True
    
    def rebuild( self ):
        """
        Rebuilds the path for this connection based on the given connection \
        style parameters that have been set.
        
        :return     <QPainterPath>
        """
        # create the path
        path            = self.rebuildPath()
        self._polygons  = self.rebuildPolygons(path)
        
        if ( self._textItem ):
            point   = path.pointAtPercent(0.5)
            metrics = QFontMetrics(self._textItem.font())
            
            point.setY(point.y() - metrics.height() / 2.0)
            
            self._textItem.setPos(point)
        
        # create the path for the item
        for poly in self._polygons:
            path.addPolygon(poly)
        
        # unmark as dirty
        self.setDirty(False)
        
        return path
    
    def rebuildPath( self ):
        """
        Rebuilds the path for the given style options based on the currently \
        set parameters.
        
        :return     <QPainterPath>
        """
        # rebuild linear style
        if ( self.isStyle( XConnectionStyle.Linear ) ):
            return self.rebuildLinear()
        
        # rebuild block style
        elif ( self.isStyle( XConnectionStyle.Block ) ):
            return self.rebuildBlock()
        
        # rebuild smooth style
        elif ( self.isStyle( XConnectionStyle.Smooth ) ):
            return self.rebuildSmooth()
        
        # otherwise, we have an invalid style, or a style
        # defined by a subclass
        else:
            return QPainterPath()
    
    def rebuildPolygons( self, path ):
        """
        Rebuilds the polygons that will be used on this path.
        
        :param      path    | <QPainterPath>
        
        :return     <list> [ <QPolygonF>, .. ]
        """
        output = []
        
        # create the input arrow
        if ( self.showInputArrow() ):
            a = QPointF(-10, -3)
            b = QPointF(0, 0)
            c = QPointF(-10, 3)
            
            mpoly = self.mappedPolygon(QPolygonF([a, b, c, a]), path, 1.0 )
            output.append( mpoly )
        
        # create the direction arrow
        if ( self.showDirectionArrow() ):
            a = QPointF(-5, -3)
            b = QPointF(5, 0)
            c = QPointF(-5, 3)
            
            mpoly = self.mappedPolygon(QPolygonF([a, b, c, a]), path, 0.5 )
            output.append( mpoly )
        
        # create the output arrow
        if ( self.showOutputArrow() ):
            a = QPointF(10, -3)
            b = QPointF(0, 0)
            c = QPointF(10, 3)
            
            mpoly = self.mappedPolygon(QPolygonF([a, b, c, a]), path, 0 )
            output.append( mpoly )
        
        return output
        
    def rebuildLinear( self ):
        """ 
        Rebuilds a linear path from the output to input points.
        
        :return     <QPainterPath>
        """
        
        points = self.controlPoints()
        
        x0, y0 = points[0]
        xN, yN = points[-1]
        
        # create a simple line between the output and
        # input points
        path = QPainterPath()
        path.moveTo(x0, y0)
        path.lineTo(xN, yN)
        
        return path
    
    def rebuildBlock( self ):
        """
        Rebuilds a blocked path from the output to input points.
        
        :return     <QPainterPath>
        """
        # collect the control points
        points = self.controlPoints()
        
        # create the path
        path = QPainterPath()
        for i, point in enumerate(points):
            if ( not i ):
                path.moveTo( point[0], point[1] )
            else:
                path.lineTo( point[0], point[1] )
        
        return path
    
    def rebuildSmooth( self ):
        """
        Rebuilds a smooth path based on the inputed points and set \
        parameters for this item.
        
        :return     <QPainterPath>
        """
        # collect the control points
        points = self.controlPoints()
        
        # create the path
        path = QPainterPath()
        
        if ( len(points) == 3 ):
            x0, y0 = points[0]
            x1, y1 = points[1]
            xN, yN = points[2]
            
            path.moveTo(x0, y0)
            path.quadTo(x1, y1, xN, yN)
        
        elif ( len(points) == 4 ):
            x0, y0 = points[0]
            x1, y1 = points[1]
            x2, y2 = points[2]
            xN, yN = points[3]
            
            path.moveTo(x0, y0)
            path.cubicTo(x1, y1, x2, y2, xN, yN)
            
        elif ( len(points) == 6 ):
            x0, y0 = points[0]
            x1, y1 = points[1]
            x2, y2 = points[2]
            x3, y3 = points[3]
            x4, y4 = points[4]
            xN, yN = points[5]
            
            xC      = (x2+x3) / 2.0
            yC      = (y2+y3) / 2.0
            
            path.moveTo(x0, y0)
            path.cubicTo(x1, y1, x2, y2, xC, yC)
            path.cubicTo(x3, y3, x4, y4, xN, yN)
            
        else:
            x0, y0 = points[0]
            xN, yN = points[-1]
            
            path.moveTo(x0, y0)
            path.lineTo(xN, yN)
        
        return path
    
    def refreshVisible( self ):
        """
        Refreshes whether or not this node should be visible based on its
        current visible state.
        """
        super(XNodeConnection, self).setVisible(self.isVisible())
    
    def setAutoCalculateInputLocation( self, state = True ):
        """
        Sets whether or not to auto calculate the input location based on \
        the proximity to the output node or point.
        
        :param     state       | <bool>
        """
        self._autoCalculateInputLocation = state
        self.setDirty()
    
    def setAutoCalculateOutputLocation( self, state = True ):
        """
        Sets whether or not to auto calculate the input location based on \
        the proximity to the output node or point.
        
        :param     state       | <bool>
        """
        self._autoCalculateOutputLocation = state
        self.setDirty()
    
    def setCustomData( self, key, value ):
        """
        Stores the inputed value as custom data on this connection for \
        the given key.
        
        :param      key     | <str>
        :param      value   | <variant>
        """
        self._customData[str(key)] = value
    
    def setDirection( self, outputLocation, inputLocation ):
        """
        Sets the output-to-input direction by setting both the locations \
        at the same time.
        
        :param      outputLocation      | <XConnectionLocation>
        :param      inputLocation       | <XConnectionLocation>
        """
        self.setOutputLocation(outputLocation)
        self.setInputLocation(inputLocation)
    
    def setDirty( self, state = True ):
        """
        Flags the connection as being dirty and needing a rebuild.
        
        :param      state   | <bool>
        """
        self._dirty = state
        
        # set if this connection should be visible
        if ( self._inputNode and self._outputNode ):
            vis = self._inputNode.isVisible() and self._outputNode.isVisible()
            self.setVisible(vis)
    
    def setDisabledPen( self, pen ):
        """
        Sets the disabled pen that will be used when rendering a connection \
        in a disabled state.
        
        :param      pen | <QPen>
        """
        self._disabledPen = QPen(pen)
    
    def setDisableWithLayer( self, state ):
        """
        Sets whether or not this connection's layer's current state should \
        affect its enabled state.
        
        :param      state | <bool>
        """
        self._disableWithLayer = state
        self.setDirty()
    
    def setEnabled( self, state ):
        """
        Sets whether or not this connection is enabled or not.
        
        :param      state | <bool>
        """
        self._enabled = state
    
    def setFont( self, font ):
        """
        Sets the font for this connection to the inputed font.
        
        :param      font | <QFont>
        """
        self._font = font
    
    def setHighlightPen( self, pen ):
        """
        Sets the pen to be used when highlighting a selected connection.
        
        :param      pen     | <QPen> || <QColor>
        """
        self._highlightPen = QPen(pen)
    
    def setInputLocation( self, location ):
        """
        Sets the input location for where this connection should point to.
        
        :param      location       | <XConnectionLocation>
        """
        self._inputLocation = location
        self.setDirty()
    
    def setInputNode( self, node ):
        """
        Sets the node that will be recieving this connection as an input.
        
        :param      node    | <XNode>
        """
        # if the node already matches the current input node, ignore
        if ( self._inputNode == node ):
            return
        
        # disconnect from the existing node
        self.disconnectSignals( self._inputNode )
        
        # store the node
        self._inputNode = node
        
        # connect to the new node
        self.connectSignals( self._inputNode )
        
        # force the rebuilding of the path
        self.setPath(self.rebuild())
    
    def setInputFixedX( self, x ):
        """
        Sets the fixed x position for the input component of this connection.
        
        :param      x       | <float> || None
        """
        self._inputFixedX = x
        self.setDirty()
    
    def setInputFixedY( self, y ):
        """
        Sets the fixed y position for the input component of this connection.
        
        :param      y       | <float> || None
        """
        self._inputFixedY = y
        self.setDirty()
        
    def setInputPoint( self, point ):
        """
        Sets the scene level input point position to draw the connection to. \
        This is used mainly by the scene when drawing a user connection - \
        it will only be used when there is no connected input node.
        
        :param      point       | <QPointF>
        """
        self._inputPoint = point
        self.setPath(self.rebuild())
    
    def setLayer( self, layer ):
        """
        Sets the layer that this node is associated with to the given layer.
        
        :param      layer       | <XNodeLayer> || None
        
        :return     <bool> changed
        """
        if ( layer == self._layer ):
            return False
        
        self._layer = layer
        self.syncLayerData()
        
        return True
    
    def setOutputLocation( self, location ):
        """
        Sets the location for the output part of the connection to generate \
        from.
        
        :param      location      | <XConnectionLocation>
        """
        self._outputLocation = location
        self.setDirty()
    
    def setOutputNode( self, node ):
        """
        Sets the node that will be generating the output information for \
        this connection.
        
        :param      node         | <XNode>
        """
        # if the output node matches the current, ignore
        if ( node == self._outputNode ):
            return
        
        # disconnect from an existing node
        self.disconnectSignals( self._outputNode )
        
        # set the current node
        self._outputNode = node
        self.connectSignals( self._outputNode )
        
        # force the rebuilding of the path
        self.setPath( self.rebuild() )
    
    def setOutputFixedX( self, x ):
        """
        Sets the fixed x position for the output component of this connection.
        
        :param      x       | <float> || None
        """
        self._outputFixedX = x
        self.setDirty()
    
    def setOutputFixedY( self, y ):
        """
        Sets the fixed y position for the output component of this connection.
        
        :param      y       | <float> || None
        """
        self._outputFixedY = y
        self.setDirty()
        
    def setOutputPoint( self, point ):
        """
        Sets the scene space point for where this connection should draw \
        its output from.  This value will only be used if no output \
        node is defined.
        
        :param      point      | <QPointF>
        """
        self._outputPoint = point
        self.setPath( self.rebuild() )
    
    def setPadding( self, padding ):
        """
        Sets the padding amount that will be used when drawing a connection \
        whose points will overlap.
        
        :param      padding    | <float>
        """
        self._padding = padding
        self.setDirty()
    
    def setShowDirectionArrow( self, state = True ):
        """
        Marks whether or not an arrow in the center of the path should be \
        drawn, showing the direction that the connection is flowing in.
        
        :param      state      | <bool>
        """
        self._showDirectionArrow = state
        self.setDirty()
    
    def setShowInputArrow( self, state = True ):
        """
        :remarks    Marks whether or not an arrow should be shown pointing
                    at the input node.
        
        :param      state       <bool>
        """
        self._showInputArrow = state
        self.setDirty()
    
    def setShowOutputArrow( self, state = True ):
        """
        :remarks    Marks whether or not an arrow should be shown pointing at
                    the output node.
        
        :param      state       <bool>
        """
        self._showOutputArrow = state
        self.setDirty()
    
    def setSquashThreshold( self, amount ):
        """
        :remarks    Sets the threshold limit of when the connection should
                    start 'squashing', calculated based on the distance between
                    the input and output points when rebuilding.
        
        :param      amount      <float>
        """
        self._squashThreshold = amount
        self.setDirty()
    
    def setStyle( self, style ):
        """
        :remarks    Sets the style of the connection that will be used.
        
        :param      style       <XConnectionStyle>
        """
        self._style = style
        self.setDirty()
        self.update()
    
    def setVisible( self, state ):
        """
        Sets whether or not this connection's local visibility should be on.
        
        :param      state | ,bool>
        """
        self._visible = state
        
        super(XNodeConnection, self).setVisible(self.isVisible())
    
    def setZValue( self, value ):
        """
        Sets the z value for this connection, also updating the text item to 
        match the value if one is defined.
        
        :param      value | <int>
        """
        super(XNodeConnection, self).setZValue(value)
        
        if ( self._textItem ):
            self._textItem.setZValue(value)
    
    def showDirectionArrow( self ):
        """
        :remarks    Return whether or not the direction arrow is visible
                    for this connection.
        
        :return     <bool>
        """
        return self._showDirectionArrow
    
    def showInputArrow( self ):
        """
        :remarks    Return whether or not the input arrow is visible
                    for this connection.
        
        :return     <bool>
        """
        return self._showInputArrow
    
    def showOutputArrow( self ):
        """
        :remarks    Return whether or not the output arrow is visible
                    for this connection.
        
        :return     <bool>
        """
        return self._showOutputArrow
    
    def squashThreshold( self ):
        """
        :remarks    Returns the sqash threshold for when the line
                    should be squashed based on the input and output
                    points becoming too close together.
        
        :return     <float>
        """
        return self._squashThreshold
    
    def setText( self, text ):
        """
        Sets the text for this connection to the inputed text.
        
        :param      text | <str>
        """
        self._text = text
        
        if ( text ):
            if ( self._textItem is None ):
                self._textItem = QGraphicsTextItem()
                self._textItem.setParentItem(self)
            
            self._textItem.setPlainText(text)
            
        elif ( self._textItem ):
            self.scene().removeItem(self._textItem)
            self._textItem = None
    
    def style( self ):
        """
        :remarks    Returns the style of the connection that is being drawn.
        
        :return     style       <XConnectionStyle>
        """
        return self._style
    
    def syncLayerData( self, layerData = None ):
        """
        Syncs the layer information for this item from the given layer data.
        
        :param      layerData | <dict>
        """
        if ( not self._layer ):
            return
        
        if ( not layerData ):
            layerData = self._layer.layerData()
        
        self.setVisible( layerData.get('visible', True) )
        
        if ( layerData.get('current') ):
            # set the default parameters
            self.setFlags( self.ItemIsSelectable )
            self.setAcceptHoverEvents(True)
            self.setZValue(99)
            
        else:
            # set the default parameters
            self.setFlags(  self.GraphicsItemFlags(0) )
            self.setAcceptHoverEvents(True)
            self.setZValue(layerData.get('zValue', 0)-1)
    
    def text( self ):
        """
        Returns the text for this connection.
        
        :return     <str>
        """
        return self._text