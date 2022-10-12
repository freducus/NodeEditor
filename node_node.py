from collections import OrderedDict
from node_serializable import Serializable
from node_graphics_node import QDMGraphicsNode
from node_content_widget import QDMNodeContentWidget
from node_socket import *

DEBUG = True
class Node(Serializable):
    def __init__(self, scene, title="Undefined Node", inputs=[], outputs=[]):
        super().__init__()
        self.scene = scene

        self._title = None
        self.content = QDMNodeContentWidget()
        self.grNode = QDMGraphicsNode(self)

        self.scene.addNode(self)


        self.title = title

        self.inputs = []
        self.outputs = []
        counter = 0
        for item in inputs:
            socket = Socket(self, counter, position=LEFT_BOTTOM, socket_type=item)
            counter += 1
            self.inputs.append(socket)

        counter = 0
        for item in outputs:
            socket = Socket(self, counter, position=RIGHT_TOP, socket_type=item)
            counter += 1
            self.outputs.append(socket)

    def setPosition(self, x, y):
        self.grNode.setPos(x, y)

    @property
    def pos(self):
        return self.grNode.pos()

    @property
    def title(self):
        return self._title

    @title.setter
    def title(self, value):
        self._title = value
        self.grNode.title = self._title

    def getSocketPosition(self, index, position):
        if position in (LEFT_TOP, LEFT_BOTTOM):
            x=0
        else:
            x=self.grNode.width
        if position in (LEFT_TOP, RIGHT_TOP):
            y = index * 20 + self.grNode.title_height + self.grNode.edge_size
        else:
            y = - index * 20 + self.grNode.height - self.grNode.edge_size - self.grNode._padding

        return [x,y]

    def updateConectedEdges(self):
        for socket in self.inputs + self.outputs:
            if socket.hasEdge():
                socket.edge.updatePosition()

    def __str__(self):
        return f'<Node {hex(id(self))[2:5]:s}..{hex(id(self))[-3:]:s}>'

    def remove(self):
        if DEBUG: print("Removing Node", self)
        if DEBUG: print(" - removing all edges from socket")
        for socket in self.inputs+self.outputs:
            if socket.hasEdge():
                socket.edge.remove()
        if DEBUG: print(" - removing grNode")
        self.scene.grScene.removeItem(self.grNode)
        self.grNode = None
        if DEBUG: print(" - removing Node from the scene")
        self.scene.removeNode(self)
        if DEBUG: print(" - everything was done")

    def serialize(self):
        inputs, outputs = [], []
        for socket in self.inputs: inputs.append(socket.serialize())
        for socket in self.outputs: outputs.append(socket.serialize())
        ser_content = self.content.serialize() if isinstance(self.content, Serializable) else {}
        return OrderedDict([
            ('id', self.id),
            ('title', self.title),
            ('pos_x', self.grNode.scenePos().x()),
            ('pos_y', self.grNode.scenePos().y()),
            ('inputs', inputs),
            ('outputs', outputs),
            ('content', ser_content),
        ])


    def deserialize(self, data, hashmap={}):
        self.id = data['id']
        hashmap[data['id']] = self

        self.title = data['title']
        self.setPosition(data['pos_x'], data['pos_y'])

        data['inputs'].sort(key=lambda socket: socket['index'] + socket['position'] * 10000)
        data['outputs'].sort(key=lambda socket: socket['index'] + socket['position'] * 10000)

        self.inputs = []
        for socket_data in data['inputs']:
            new_socket = Socket(node=self, index=socket_data['index'], position=socket_data['position'],
                                socket_type=socket_data['socket_type'])
            new_socket.deserialize(socket_data, hashmap)
            self.inputs.append(new_socket)

        for socket_data in data['outputs']:
            new_socket = Socket(node=self, index=socket_data['index'], position=socket_data['position'],
                                socket_type=socket_data['socket_type'])
            new_socket.deserialize(socket_data, hashmap)
            self.outputs.append(new_socket)

        return True