from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

class QDMGraphicsSocket(QGraphicsItem):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.radius = 6.0
        self.outline_width = 1.0
        self._color_bakground = QColor("#FFFF7700")
        self._color_outline = QColor("#FF000000")

        self._pen = QPen(self._color_outline)
        self._pen.setWidthF(self.outline_width)
        self._brush = QBrush(self._color_bakground)

    def paint(self, painter: QPainter, QStyleOptionGraphicsItem, widget=None):
        painter.setBrush(self._brush)
        painter.setPen(self._pen)
        painter.drawEllipse(-self.radius, -self.radius, 2*self.radius, 2*self.radius)

    def boundingRect(self):
        return QRectF(-self.radius,
                      -self.radius,
                      2*self.radius,
                      2*self.radius)






