from node_graphics_socket import QDMGraphicsSocket
from collections import OrderedDict
from node_serializable import Serializable

LEFT_TOP = 1
LEFT_BOTTOM = 2
RIGHT_TOP = 3
RIGHT_BOTTOM = 4


class Socket(Serializable):
    def __init__(self, node, index=0, position=LEFT_TOP, socket_type=1):

        super().__init__()
        self.node = node
        self.index = index
        self.position = position
        self.socket_type = socket_type

        self.grSocket = QDMGraphicsSocket(self, self.node.grNode, socket_type)

        self.grSocket.setPos(*self.node.getSocketPosition(self.index, self.position))

        self.edge = None

    def getSocketPosition(self):
        return self.node.getSocketPosition(self.index, self.position)
    def setConnectedEdge(self, edge=None):
        self.edge = edge

    def hasEdge(self):
        return self.edge is not None

    def __str__(self):
        return f'<Socket {hex(id(self))[2:5]:s}..{hex(id(self))[-3:]:s}>'

    def serialize(self) -> OrderedDict:
        return OrderedDict([
            ('id', self.id),
            ('index', self.index),
            ('position', self.position),
            ('socket_type', self.socket_type),
        ])

    def deserialize(self, data, hashmap=[]):
        print("deserialization data", data)
