from collections import OrderedDict
from node_serializable import Serializable
from node_graphics_edge import *

DEBUG=True

EDGE_TYPE_DIRECT = 1
EDGE_TYPE_BEZIER = 2
class Edge(Serializable):

    def __init__(self, scene, start_socket=None, end_socket=None, edge_type=EDGE_TYPE_DIRECT):

        super().__init__()
        self.scene = scene

        self._start_socket = None
        self._end_socket = None

        self.start_socket = start_socket
        self.end_socket = end_socket

        self.edge_type = edge_type

        self.scene.addEdge(self)

    @property
    def start_socket(self):
        return self._start_socket
    
    @start_socket.setter
    def start_socket(self, value):
        self._start_socket = value
        if self.start_socket is not None:
            self.start_socket.edge = self

    @property
    def end_socket(self):
        return self._end_socket

    @end_socket.setter
    def end_socket(self, value):
        self._end_socket = value
        if self.end_socket is not None:
            self.end_socket.edge = self

    @property
    def edge_type(self):
        return self._edge_type

    @edge_type.setter
    def edge_type(self, value):
        if hasattr(self, 'grEdge') and self.grEdge is not None:
            self.scene.grScene.removeItem(self.grEdge)

        self._edge_type = value
        if self.edge_type == EDGE_TYPE_DIRECT:
            self.grEdge = QDMGraphicsEdgeDirect(self)
        elif self.edge_type == EDGE_TYPE_BEZIER:
            self.grEdge = QDMGraphicsEdgeBezier(self)
        else:
            self.grEdge = QDMGraphicsEdgeBezier(self)

        self.scene.grScene.addItem(self.grEdge)

        if self.start_socket is not None:
            self.updatePosition()

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

    def serialize(self) -> OrderedDict:
        return OrderedDict([
            ('id', self.id),
            ('edge_type', self.edge_type),
            ('start', self.start_socket.id if self.start_socket is not None else None),
            ('end', self.end_socket.id if self.end_socket is not None else None),
        ])

    def deserialize(self, data, hashmap={}):
        self.id = data['id']
        self.start_socket = hashmap[data['start']]
        self.end_socket = hashmap[data['end']]
        self.edge_type = data['edge_type']



