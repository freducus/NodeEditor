from collections import OrderedDict

from qtpy.QtWidgets import *
from node_serializable import Serializable


class QDMNodeContentWidget(QWidget, Serializable):

    def __init__(self, parent=None):
        super(QDMNodeContentWidget, self).__init__(parent)

        self.initUI()

    def initUI(self):
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.layout)

        self.wdg_label = QLabel("Some title")
        self.layout.addWidget(self.wdg_label)
        self.layout.addWidget(QPushButton())
        self.layout.addWidget(QTextEdit())

    def serialize(self) -> OrderedDict:
        return OrderedDict([
        ])

    def deserialize(self, data: dict, hashmap: dict = {}, restore_id: bool = True) -> bool:
        return True
