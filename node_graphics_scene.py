import math

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

class QDMGraphicsScene(QGraphicsScene):
    def __init__(self, scene, parent=None):
        super().__init__(parent)

        self.scene = scene
        # settings
        self.gridSize = 20
        self.gridSquares = 5
        self._color_background = QColor("#393939")
        self._color_light = QColor("#2f2f2f")
        self._color_dark = QColor("#292929")

        self._pen_light = QPen(self._color_light)
        self._pen_light.setWidth(1)
        self._pen_dark = QPen(self._color_dark)
        self._pen_dark.setWidth(2)

        self.setBackgroundBrush(self._color_background)

    def setScene(self, width, height):
        self.setSceneRect(-width // 2, -height // 2, width, height)

    def drawBackground(self, painter, rect):
        super().drawBackground(painter, rect)

        # Create grid
        left = int(math.floor(rect.left()))
        right = int(math.floor(rect.right()))
        top = int(math.floor(rect.top()))
        bottom = int(math.floor(rect.bottom()))

        first_left = left - left%self.gridSize
        first_top = top - top%self.gridSize

        # Compute lines
        lines_light = []
        lines_dark = []
        for x in range(first_left, right, self.gridSize):
            if x % (self.gridSize * self.gridSquares) != 0:
                lines_light.append(QLine(x, top, x, bottom))
            else: lines_dark.append(QLine(x, top, x, bottom))
        for y in range(first_top, bottom, self.gridSize):
            if y % (self.gridSize*self.gridSquares) != 0:
                lines_light.append(QLine(left, y, right, y))
            else: lines_dark.append(QLine(left, y, right, y))

        # Draw lines
        painter.setPen(self._pen_light)
        try:
            painter.drawLines(*lines_light)  # supporting PyQt5
        except TypeError:
            painter.drawLines(lines_light)  # supporting PySide2

        painter.setPen(self._pen_dark)
        try:
            painter.drawLines(*lines_dark)  # supporting PyQt5
        except TypeError:
            painter.drawLines(lines_dark)  # supporting PySide2

