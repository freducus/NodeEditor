from node_graphics_edge import *

DEBUG=True

EDGE_TYPE_DIRECT = 1
EDGE_TYPE_BEZIER = 2
class Edge:

    def __init__(self, scene, start_socket, end_socket, edge_type=EDGE_TYPE_DIRECT):

        self.scene = scene

        self.start_socket = start_socket
        self.start_socket.edge = self

        self.end_socket = end_socket
        if end_socket is not None:
            self.end_socket.edge = self

        self.grEdge = QDMGraphicsEdgeDirect(self) if edge_type == EDGE_TYPE_DIRECT else QDMGraphicsEdgeBezier(self)

        self.updatePosition()
        self.scene.grScene.addItem(self.grEdge)
        self.scene.addEdge(self)

    def updatePosition(self):
        source_pos = self.start_socket.getSocketPosition()
        source_pos[0] += self.start_socket.node.grNode.pos().x()
        source_pos[1] += self.start_socket.node.grNode.pos().y()
        self.grEdge.setSource(*source_pos)
        if self.end_socket is not None:
            dest_pos = self.end_socket.getSocketPosition()
            dest_pos[0] += self.end_socket.node.grNode.pos().x()
            dest_pos[1] += self.end_socket.node.grNode.pos().y()
            self.grEdge.setDestination(*dest_pos)
        else:
            self.grEdge.setDestination(*source_pos)
        self.grEdge.update()
    def remove_from_sockets(self):
        if self.start_socket is not None:
            self.start_socket.edge = None
        if self.end_socket is not None:
            self.end_socket.edge = None

        self.end_socket = None
        self.start_socket = None

    def remove(self):
        if DEBUG: print("# Removing Edge", self)
        if DEBUG: print(" - removing Edge from all sockets")
        self.remove_from_sockets()
        if DEBUG: print(" - removing grEdge")
        self.scene.grScene.removeItem(self.grEdge)
        self.grEdge = None
        if DEBUG: print(" - removing Edge from scene")
        try:
            self.scene.removeEdge(self)
        except ValueError:
            pass
        if DEBUG: print(" - everything is done")

    def __str__(self):
        return f'<Edge {hex(id(self))[2:5]:s}..{hex(id(self))[-3:]:s}>'
