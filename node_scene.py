import json
from collections import OrderedDict
from node_serializable import Serializable
from node_graphics_scene import QDMGraphicsScene

class Scene(Serializable):
    def __init__(self):
        super(Scene, self).__init__()
        self.nodes =[]
        self.edges =[]

        self.scene_width = 64000
        self.scene_height = 64000

        self.initUI()

    def initUI(self):
        self.grScene = QDMGraphicsScene(self)
        self.grScene.setScene(self.scene_width, self.scene_height)

    def addNode(self, node):
        self.nodes.append(node)
        self.grScene.addItem(node.grNode)

    def addEdge(self, edge):
        self.edges.append(edge)

    def removeNode(self, node):
        self.nodes.remove(node)

    def removeEdge(self, edge):
        self.edges.remove(edge)

    def saveToFile(self, filename):
        with open(filename, 'w') as file:
            file.write(json.dumps(self.serialize(), indent=4))
        print('Saving to scene to file')

    def loadFromFile(self, filename):
        with open(filename, 'r') as file:
            raw_data = file.read()
            data = json.loads(raw_data, encoding='utf')
            self.desiarlizable(data)
    def serialize(self):
        nodes, edges = [], []
        for node, edge in zip(self.nodes, self.edges):
            nodes.append(node.serialize())
            edges.append(edge.serialize())
        return OrderedDict({
            'id': self.id,
            'scene_width': self.scene_width,
            'scene_height': self.scene_height,
            'nodes': nodes,
            'edges': edges
        })

    def deserialize(self, data, hashmap=[]):
        print("deserialization data", data)

