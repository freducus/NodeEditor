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
            socket = Socket(self, counter, position=LEFT_TOP)
            counter += 1
            self.inputs.append(socket)

        for item in outputs:
            socket = Socket(self, counter, position=RIGHT_TOP)
            counter += 1
            self.outputs.append(socket)
