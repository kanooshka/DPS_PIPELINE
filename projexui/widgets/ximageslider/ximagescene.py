""" [desc] """

__author__ = 'Eric Hulser'
__email__ = 'ehulser@teslamotors.com'
__copyright__ = 'Tesla Motors (c) 2013'

import random

from PyQt4.QtCore import Qt, QRectF
from PyQt4.QtGui import QGraphicsScene,\
                              QLinearGradient,\
                              QColor

class XImageScene(QGraphicsScene):
    def __init__(self, slider):
        super(XImageScene, self).__init__()
        
        self._slider = slider
    
    def angle(self, item):
        center = item.pos() + item.boundingRect().center()
        vcenter = self._slider.mapFromScene(center)
        
        dx = vcenter.x() - self._slider.rect().center().x()
        w = item.boundingRect().width()
        
        base = float(w * 2)
        if base == 0:
            return 0
        
        if dx > 0:
            return max(-60, 60 * dx / base)
        else:
            return min(60, 60 * dx / base)
    
    def drawForeground(self, painter, rect):
        palette = self._slider.palette()
        color = palette.color(palette.Base)
        
        trans = self._slider.viewportTransform()
        rect = trans.mapRect(self._slider.rect())
        width = rect.width()
        rect.setX(abs(rect.x()))
        rect.setWidth(width)
        
        clear = QColor(0, 0, 0, 0)
        
        grad = QLinearGradient()
        grad.setStart(rect.left(), 0)
        grad.setFinalStop(rect.right(), 0)
        grad.setColorAt(0.0, color)
        grad.setColorAt(0.3, clear)
        grad.setColorAt(0.7, clear)
        grad.setColorAt(1.0, color)
        
        painter.setBrush(grad)
        painter.setPen(Qt.NoPen)
        
        painter.drawRect(rect)
        
    def recalculate(self):
        pass