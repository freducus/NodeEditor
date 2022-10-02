import math

from PyQt5 import QtGui
from PyQt5.QtGui import QPainter
from PyQt5.QtWidgets import QGraphicsView
from PyQt5.QtCore import *
from PyQt5.QtGui import *

from node_edge import EDGE_TYPE_BEZIER, Edge
from node_graphics_socket import QDMGraphicsSocket
from node_graphics_edge import QDMGraphicsEdge

MODE_NOOP = 1
MODE_EDGE_DRAG = 2

EDGE_DRAG_STARET_THRESHOLD = 4

DEBUG = True


class QDMGraphicsView(QGraphicsView):

    def __init__(self, grScene, parent=None):
        super().__init__(parent)
        self.dragEdge = None
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
        self.setDragMode(QGraphicsView.RubberBandDrag)


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

        if DEBUG: print("LMB click on", item, self.debug_modifiers(event))
        if hasattr(item, 'node')  or isinstance(item, QDMGraphicsEdge) or item is None:
            if event.modifiers() & Qt.ShiftModifier:
                if DEBUG: print("LMB + Shift on", item)
                event.ignore()
                fakeEvent = QMouseEvent(QEvent.MouseButtonPress, event.localPos(), event.screenPos(),
                                        Qt.LeftButton, event.buttons() | Qt.LeftButton,
                                        event.modifiers() | Qt.ControlModifier)
                super().mousePressEvent(fakeEvent)
                return

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

        item = self.getItemAtClick(event)
        if DEBUG:
            if isinstance(item, QDMGraphicsEdge): print(
                f'RMB: {item.edge} connecting sockets: {item.edge.start_socket}<-->{item.edge.end_socket}')
            if isinstance(item, QDMGraphicsSocket): print(f'RMB: {item.socket} has edge {item.socket.edge}')
            if item is None:
                print('SCENE:')
                print('  Nodes:')
                for node in self.grScene.scene.nodes:
                    print(f'    {node}')
                print('  Edges:')
                for edge in self.grScene.scene.edges:
                    print(f'    {edge}')

    def edgeDragStart(self, item):
        self.mode = MODE_EDGE_DRAG
        if DEBUG: print('View:edgeDragStart - Start dragging edge')
        if DEBUG: print(f'View:edgeDragStart - Assign Start socket to {item.socket}')
        self.previousEdge = item.socket.edge
        self.last_start_socket = item.socket
        self.dragEdge = Edge(self.grScene.scene, item.socket, None, EDGE_TYPE_BEZIER)
        if DEBUG: print(f'View:edgeDragStart - dragEdge: {self.dragEdge}')

    def edgeDragEnd(self, item):
        self.mode = MODE_NOOP
        if type(item) is QDMGraphicsSocket:
            if item.socket.hasEdge():
                item.socket.edge.remove()
            if DEBUG: print(f'View:edgeDragEnd -ass End sock {item}')
            if self.previousEdge is not None: self.previousEdge.remove()
            if DEBUG: print(f'View:edgeDragEnd -previous edge removed')
            self.dragEdge.start_socket = self.last_start_socket
            self.dragEdge.end_socket = item.socket
            self.dragEdge.start_socket.setConnectedEdge(self.dragEdge)
            self.dragEdge.end_socket.setConnectedEdge(self.dragEdge)
            if DEBUG: print(f'View:edgeDragEnd - ass start and end sockets')
            self.dragEdge.updatePosition()
            return True
        if DEBUG: print('View:edgeDragEnd - End dragging edge')
        self.dragEdge.remove()
        self.dragEdge = None
        if DEBUG: print("View:edgeDragEnd - about to set socket to previous edge:", self.previousEdge)
        if self.previousEdge is not None:
            self.previousEdge.start_socket_edge = self.previousEdge
        if DEBUG: print("View:edgeDragEnd - everything is done")

        return False

    def distanceBetweenClickAndReleaseIsOff(self, event):
        new_lmb_release_scene_pos = self.mapToScene(event.pos())

        dist_scene = new_lmb_release_scene_pos - self.last_lmb_click_scene_pos
        dist_scene = math.sqrt(QPointF.dotProduct(dist_scene, dist_scene))
        return dist_scene > EDGE_DRAG_STARET_THRESHOLD * EDGE_DRAG_STARET_THRESHOLD

    def leftMouseButtonRelease(self, event):
        item = self.getItemAtClick(event)

        if hasattr(item, 'node') or isinstance(item, QDMGraphicsEdge) or item is None:
            if event.modifiers() & Qt.ShiftModifier:
                event.ignore()
                fakeEvent = QMouseEvent(event.type(), event.localPos(), event.screenPos(),
                                        Qt.LeftButton, Qt.NoButton,
                                        event.modifiers() | Qt.ControlModifier)
                super().mouseReleaseEvent(fakeEvent)
                return

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

    def mouseMoveEvent(self, event: QtGui.QMouseEvent) -> None:
        if self.mode==MODE_EDGE_DRAG:
            pos = self.mapToScene(event.pos())
            self.dragEdge.grEdge.setDestination(pos.x(), pos.y())
            self.dragEdge.grEdge.update()
        super().mouseMoveEvent(event)

    def debug_modifiers(self, event):
        out = "MODS: "
        if event.modifiers() & Qt.ShiftModifier: out += "SHIFT"
        if event.modifiers() & Qt.ControlModifier: out += "CTRL"
        if event.modifiers() & Qt.AltModifier: out += "ALT"

        return out

    def getItemAtClick(self, event):
        pos = event.pos()
        obj = self.itemAt(pos)
        return obj
