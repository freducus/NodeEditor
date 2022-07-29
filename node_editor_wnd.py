from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

from node_node import Node
from node_scene import Scene
from node_graphics_view import QDMGraphicsView

class NodeEditorWnd(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.styleSheet_filename = 'qss/nodestyle.qss'
        self.loadStyleSheet(self.styleSheet_filename)

        self.initUI()

    def initUI(self):
        self.setGeometry(200, 200, 600, 600)

        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0,0,0,0)
        self.setLayout(self.layout)

        # Graphics Scene
        self.scene = Scene()

        node = Node(self.scene, "My awesome node", [1,2,3], [1])
        # Graphics View
        self.view = QDMGraphicsView(self.scene.grScene, self)
        self.layout.addWidget(self.view)

        self.setWindowTitle("Node Editor")
        self.show()

        # self.addDebugContent()

    def addDebugContent(self):
        greenBrush = QBrush(Qt.green)
        outlinePen = QPen(Qt.white)
        outlinePen.setWidth(2)

        rect = self.grScene.addRect(0, 0, 100, 100, outlinePen, greenBrush)
        rect.setFlag(QGraphicsItem.ItemIsMovable, True)

        text = self.grScene.addText("This is my text", font=QFont("arial"))
        text.setFlag(QGraphicsItem.ItemIsMovable)
        text.setDefaultTextColor(QColor("white"))

        widget1 = QPushButton("Hello World")
        proxy1 = self.grScene.addWidget(widget1)
        proxy1.setPos(0,30)
        proxy1.setFlag(QGraphicsItem.ItemIsMovable)

        widget2 = QTextEdit()
        proxy2 = self.grScene.addWidget(widget2)
        proxy2.setFlag(QGraphicsItem.ItemIsSelectable)
        proxy2.setFlag(QGraphicsItem.ItemIsMovable)
        proxy2.setPos(0, 60)

        line = self.grScene.addLine(-200, -200, 400, -100, outlinePen)
        line.setFlag(QGraphicsItem.ItemIsMovable)
        line.setFlag(QGraphicsItem.ItemIsSelectable)

    def loadStyleSheet(self, filename):
        print("STYLE loadin:", filename )
        file = QFile(filename)
        file.open(QFile.ReadOnly | QFile.Text)
        stylesheet = file.readAll()
        QApplication.instance().setStyleSheet(str(stylesheet, encoding='utf-8'))
