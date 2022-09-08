from node_graphics_node import QDMGraphicsNode
from node_content_widget import QDMNodeContentWidget
from node_socket import *

class Node():
    def __init__(self, scene, title="Undefined Node", inputs=[], outputs=[]):
        self.scene = scene

        self.title = title

        self.content = QDMNodeContentWidget()
        self.grNode = QDMGraphicsNode(self)

        self.scene.addNode(self)


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