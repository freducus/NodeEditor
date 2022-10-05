import math

from qtpy import QtGui
from qtpy.QtGui import QPainter
from qtpy.QtWidgets import QGraphicsView, QApplication
from qtpy.QtCore import *
from qtpy.QtGui import *

from node_edge import EDGE_TYPE_BEZIER, Edge
from node_graphics_cutline import QDMCutLine
from node_graphics_socket import QDMGraphicsSocket
from node_graphics_edge import QDMGraphicsEdge

MODE_NOOP = 1
MODE_EDGE_DRAG = 2
MODE_EDGE_CUT = 3

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

        self.cutline = QDMCutLine()
        self.grScene.addItem(self.cutline)
        self.cutline.update()

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
            try:
                print(item.node)
            except Exception:
                pass
            if event.modifiers() & Qt.ShiftModifier:
                if DEBUG: print("LMB + Shift on", item)
                event.ignore()
                fakeEvent = QMouseEvent(QEvent.MouseButtonPress, event.localPos(), event.screenPos(),
                                        Qt.LeftButton, event.buttons() | Qt.LeftButton,
                                        event.modifiers() | Qt.ControlModifier)
                super().mousePressEvent(fakeEvent)
                return
        else:
            print('Clear selection')
            self.grScene.clearSelection()

        if type(item) is QDMGraphicsSocket:
            if self.mode == MODE_NOOP:
                self.edgeDragStart(item)
                return
        if self.mode == MODE_EDGE_DRAG:
            res = self.edgeDragEnd(item)
            if res: return

        if item is None:
            if event.modifiers() & Qt.ControlModifier:
                self.mode = MODE_EDGE_CUT
                fakeEvent = QMouseEvent(QEvent.MouseButtonRelease, event.localPos(), event.screenPos(),
                                        Qt.LeftButton, Qt.NoButton, event.modifiers())
                super().mouseReleaseEvent(fakeEvent)
                QApplication.setOverrideCursor(Qt.CrossCursor)
                return
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
            if item.socket != self.last_start_socket:
                if DEBUG: print(f'View:edgeDragEnd -previous edge {item}')
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

        if self.mode == MODE_EDGE_CUT:
            self.cutIntersectingEdges()
            self.cutline.prepareGeometryChange()
            self.cutline.line_points = []
            QApplication.setOverrideCursor(Qt.ArrowCursor)
            self.mode = MODE_NOOP
            fakeEvent = QMouseEvent(event.type(), event.localPos(), event.screenPos(),
                                    Qt.LeftButton, Qt.NoButton,
                                    event.modifiers() | Qt.ControlModifier)
            super().mouseReleaseEvent(fakeEvent)
            return

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
        if self.mode == MODE_EDGE_DRAG:
            pos = self.mapToScene(event.pos())
            self.dragEdge.grEdge.setDestination(pos.x(), pos.y())
            self.dragEdge.grEdge.update()

        if self.mode == MODE_EDGE_CUT:
            pos = self.mapToScene(event.pos())
            self.cutline.prepareGeometryChange()
            self.cutline.line_points.append(pos)

        super().mouseMoveEvent(event)

    def keyPressEvent(self, event: QtGui.QKeyEvent) -> None:
        if event.key() == Qt.Key_Delete:
            self.deleteSelected()
        else:
            super(QDMGraphicsView, self).keyPressEvent(event)

    def cutIntersectingEdges(self):

        for ix in range(len(self.cutline.line_points)-1):
            p1 = self.cutline.line_points[ix]
            p2 = self.cutline.line_points[ix+1]

            for edge in self.grScene.scene.edges:
                if edge.grEdge.intersectWith(p1, p2):
                    edge.remove()
    def deleteSelected(self):
        for item in self.grScene.selectedItems():
            if isinstance(item, QDMGraphicsEdge):
                item.edge.remove()
            elif hasattr(item, 'node'):
                item.node.remove()

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
