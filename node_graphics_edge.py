import math

from qtpy.QtWidgets import *
from qtpy.QtCore import *
from qtpy.QtGui import *

from node_socket import RIGHT_TOP, RIGHT_BOTTOM, LEFT_BOTTOM, LEFT_TOP

EDGE_CP_ROUNDNESS = 100

class QDMGraphicsEdge(QGraphicsPathItem):

    def __init__(self, edge, parent=None):
        super(QDMGraphicsEdge, self).__init__(parent)

        self._color = QColor("#001000")
        self._color_selected = QColor("#00ff00")
        self._pen = QPen(self._color)
        self._pen_selected = QPen(self._color_selected)
        self._pen_dragging = QPen(self._color)
        self._pen_dragging.setStyle(Qt.DashLine)
        self._pen.setWidth(2)
        self._pen_selected.setWidth(2)
        self._pen_dragging.setWidth(2)
        self.edge = edge

        self.setFlag(QGraphicsItem.ItemIsSelectable)
        self.setZValue(-1)

        self.posSource = [self.edge.start_socket,0]
        self.posDestination = [200,100]

    def setSource(self, x, y):
        self.posSource = (x, y)

    def setDestination(self, x, y):
        self.posDestination = (x, y)
    def paint(self, painter, QStyleOptionGraphicsItem, widget=None):
        self.setPath(self.calcPath())

        if self.edge.end_socket is None:
            painter.setPen(self._pen_dragging)
        else:
            painter.setPen(self._pen if not self.isSelected() else self._pen_selected)
        painter.setBrush(Qt.NoBrush)
        painter.drawPath(self.path())

    def calcPath(self):
        raise NotImplemented

    def intersectWith(self, p1, p2):
        cutpath = QPainterPath(p1)
        cutpath.lineTo(p2)
        path = self.calcPath()
        return cutpath.intersects(path)

class QDMGraphicsEdgeDirect(QDMGraphicsEdge):

    def calcPath(self):
        path = QPainterPath(QPoint(self.posSource[0], self.posSource[1]))
        path.lineTo(self.posDestination[0], self.posDestination[1])
        return path

class QDMGraphicsEdgeBezier(QDMGraphicsEdge):

    def calcPath(self):
        s = self.posSource
        d = self.posDestination
        dist = (d[0] - s[0])*0.5

        cpx_s = +dist
        cpx_d = -dist
        cpy_s = 0
        cpy_d = 0

        sspos = self.edge.start_socket.position
        if (s[0] > d[0]) and sspos in (RIGHT_TOP, RIGHT_BOTTOM) or (s[0] < d[0]) and sspos in (LEFT_BOTTOM, LEFT_TOP):
            cpx_d *= -1
            cpx_s *= -1

            cpy_d = ((s[1]-d[1])/math.fabs((s[1]-d[1]) if (s[1]-d[1])!=0 else 0.0001)) * EDGE_CP_ROUNDNESS
            cpy_s = ((d[1]-s[1])/math.fabs((d[1]-s[1]) if (d[1]-s[1])!=0 else 0.0001)) * EDGE_CP_ROUNDNESS

        path = QPainterPath(QPoint(self.posSource[0], self.posSource[1]))
        path.cubicTo(s[0]+cpx_s, s[1] + cpy_s, d[0]+cpx_d, d[1] + cpy_d,
            self.posDestination[0], self.posDestination[1])
        return path