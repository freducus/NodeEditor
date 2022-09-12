import math

from PyQt5.QtGui import QPainter
from PyQt5.QtWidgets import QGraphicsView
from PyQt5.QtCore import *
from PyQt5.QtGui import *

from node_graphics_socket import QDMGraphicsSocket

MODE_NOOP = 1
MODE_EDGE_DRAG = 2

EDGE_DRAG_STARET_THRESHOLD = 4

class QDMGraphicsView(QGraphicsView):

    def __init__(self, grScene, parent=None):
        super().__init__(parent)
        self.last_lmb_click_scene_pos = None
        self.grScene = grScene

        self.initUI()

        self.setScene(grScene)

        self.mode = MODE_NOOP

        self.zoomInFactor = 1.25
        self.zoom = 10
        self.zoomStep = 1
        self.zoomRange = [0, 30]

    def initUI(self):
        self.setRenderHints(
            QPainter.Antialiasing | QPainter.HighQualityAntialiasing | QPainter.TextAntialiasing | QPainter.SmoothPixmapTransform)
        self.ViewportUpdateMode(QGraphicsView.FullViewportUpdate)

        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MiddleButton:
            self.middleMouseButtonPress(event)
        elif event.button() == Qt.LeftButton:
            self.leftMouseButtonPress(event)
        elif event.button() == Qt.RightButton:
            self.rightMouseButtonPress(event)

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MiddleButton:
            self.middleMouseButtonRelease(event)
        elif event.button() == Qt.LeftButton:
            self.leftMouseButtonRelease(event)
        elif event.button() == Qt.RightButton:
            self.rightMouseButtonRelease(event)

    def middleMouseButtonPress(self, event):
        # releaseEvent = QMouseEvent(QEvent.MouseButtonRelease, event.localPos(), event.screenPos(),
        #                            Qt.MiddleButton, event.buttons(), event.modifiers())
        # super().mouseReleaseEvent(releaseEvent)
        self.setDragMode(QGraphicsView.ScrollHandDrag)

        fakeEvent = QMouseEvent(event.type(), event.localPos(), event.screenPos(),
                                   Qt.LeftButton, event.buttons(), event.modifiers())
        super().mousePressEvent(fakeEvent)

    def middleMouseButtonRelease(self, event):
        self.setDragMode(QGraphicsView.NoDrag)
        
    def leftMouseButtonPress(self, event):
        item = self.getItemAtClick(event)
        self.last_lmb_click_scene_pos = self.mapToScene(event.pos())
        if type(item) is QDMGraphicsSocket:
            if self.mode == MODE_NOOP:
                self.edgeDragStart(item)
                return
        if self.mode == MODE_EDGE_DRAG:
            res = self.edgeDragEnd(item)
            if res: return

        super().mousePressEvent(event)

    def rightMouseButtonPress(self, event):
        super().mousePressEvent(event)

    def edgeDragStart(self, item):
        self.mode = MODE_EDGE_DRAG
        print('Start dragging edge')
        print(' Assign Start socket')

    def edgeDragEnd(self, item):
        self.mode = MODE_NOOP
        print('End dragging edge')

        if type(item) is QDMGraphicsSocket:
            print(' ass End sock')
            return True

        return False

    def distanceBetweenClickAndReleaseIsOff(self, event):
        new_lmb_release_scene_pos = self.mapToScene(event.pos())

        dist_scene = new_lmb_release_scene_pos - self.last_lmb_click_scene_pos
        dist_scene = math.sqrt(QPointF.dotProduct(dist_scene, dist_scene))
        return dist_scene > EDGE_DRAG_STARET_THRESHOLD*EDGE_DRAG_STARET_THRESHOLD

    def leftMouseButtonRelease(self, event):
        item = self.getItemAtClick(event)

        if self.mode == MODE_EDGE_DRAG:
            if self.distanceBetweenClickAndReleaseIsOff(event):
                res = self.edgeDragEnd(item)
                if res: return

        super().mouseReleaseEvent(event)

    def rightMouseButtonRelease(self, event):
        super().mouseReleaseEvent(event)
            
    def wheelEvent(self, event: QWheelEvent) -> None:
        zoomOutFactor = 1 / self.zoomInFactor

        if event.angleDelta().y() > 0:
            zoomFactor = self.zoomInFactor
            self.zoom += self.zoomStep
        else:
            zoomFactor = zoomOutFactor
            self.zoom -= self.zoomStep

        self.scale(zoomFactor, zoomFactor)

    def getItemAtClick(self, event):
        pos = event.pos()
        obj = self.itemAt(pos)
        return obj