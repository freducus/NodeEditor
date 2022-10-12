import os.path

from PyQt5.QtWidgets import *

from node_editor_widget import NodeEditorWidget


class NodeEditorWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.filename = None
        self.initUI()

    def createAct(self, name, shortcut, tooltip, callback):
        act = QAction(name, self)
        act.setShortcut(shortcut)
        act.setToolTip(tooltip)
        act.triggered.connect(callback)
        return act


    def initUI(self):
        menubar = self.menuBar()

        # initialize menu
        fileMenu = menubar.addMenu('&File')

        fileMenu.addAction(self.createAct('&New', 'Ctrl+N', 'Create new graph', self.onFileNew))
        fileMenu.addSeparator()
        fileMenu.addAction(self.createAct('&Open', 'Ctrl+O', 'Open file', self.onFileOpen))
        fileMenu.addAction(self.createAct('&Save', 'Ctrl+S', 'Save file', self.onFileSave))
        fileMenu.addAction(self.createAct('&Save as', 'Ctrl+Shift+S', 'Save file as', self.onFileSaveAs))
        fileMenu.addSeparator()
        fileMenu.addAction(self.createAct('&Exit', 'Ctrl+Q', 'Exit', self.close))

        editMenu = menubar.addMenu('&Edit')
        editMenu.addAction(self.createAct('&Undo', 'Ctrl+Z', 'Undo last operation', self.onEditUndo))
        editMenu.addAction(self.createAct('&Redo', 'Ctrl+Shit+Z', 'Redo last operation', self.onEditRedo))
        editMenu.addSeparator()
        editMenu.addAction(self.createAct('&Delete', 'Del', 'Delete selected', self.onEditDelete))


        nodeeditor = NodeEditorWidget(self)
        self.setCentralWidget(nodeeditor)

        self.statusBar().showMessage('')
        self.status_mouse_position = QLabel('asdf')
        self.statusBar().addPermanentWidget(self.status_mouse_position)
        nodeeditor.view.scenePosChanged.connect(self.onScenePosChanged)

        self.setGeometry(200, 200, 800, 600)
        self.setWindowTitle("Node Editor")
        self.show()

    def onScenePosChanged(self, x, y):
        self.status_mouse_position.setText(f'Scene Pos: [{x},{y}]')

    def onFileNew(self):
        self.centralWidget().scene.clear()

    def onFileOpen(self):
        fname, filter = QFileDialog.getOpenFileName(self, 'Open graph from file')
        if fname == "":
            return
        if os.path.isfile(fname):
            self.centralWidget().scene.loadFromFile(fname)

    def onFileSave(self):
        if self.filename is None:
            return self.onFileSaveAs()
        else:
            self.centralWidget().scene.saveToFile(self.filename)
            self.statusBar().showMessage(f"Successfully saved {self.filename}")

    def onFileSaveAs(self):
        fname, filter = QFileDialog.getSaveFileName(self, 'Save graph from file')
        if fname == "":
            return
        self.filename = fname
        self.onFileSave()


    def onEditUndo(self):
        self.centralWidget().scene.history.undo()

    def onEditRedo(self):
        self.centralWidget().scene.history.redo()

    def onEditDelete(self):
        self.centralWidget().view.deleteSelected()

