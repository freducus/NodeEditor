import json
import os.path

from PyQt5 import QtGui
from PyQt5.QtWidgets import *

from node_editor_widget import NodeEditorWidget


class NodeEditorWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.filename = None
        self.initUI()

        QApplication.instance().clipboard().dataChanged.connect(self.onClipboardChanged)

    def onClipboardChanged(self):
        clip = QApplication.instance().clipboard()
        print("Clipboard changed: ", clip.text())

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
        fileMenu.addAction(self.createAct('E&xit', 'Ctrl+Q', 'Exit', self.close))

        editMenu = menubar.addMenu('&Edit')
        editMenu.addAction(self.createAct('&Undo', 'Ctrl+Z', 'Undo last operation', self.onEditUndo))
        editMenu.addAction(self.createAct('&Redo', 'Ctrl+Shit+Z', 'Redo last operation', self.onEditRedo))
        editMenu.addSeparator()
        editMenu.addAction(self.createAct('Cu&t', 'Ctrl+X', 'Cut', self.onEditCut))
        editMenu.addAction(self.createAct('Copy', 'Ctrl+C', 'Copy', self.onEditCopy))
        editMenu.addAction(self.createAct('Paste', 'Ctrl+V', 'Paste', self.onEditPaste))
        editMenu.addSeparator()
        editMenu.addAction(self.createAct('&Delete', 'Del', 'Delete selected', self.onEditDelete))


        nodeeditor = NodeEditorWidget(self)
        nodeeditor.scene.addHasBeenModifiedListener(self.changeTitle)
        self.setCentralWidget(nodeeditor)

        self.statusBar().showMessage('')
        self.status_mouse_position = QLabel('asdf')
        self.statusBar().addPermanentWidget(self.status_mouse_position)
        nodeeditor.view.scenePosChanged.connect(self.onScenePosChanged)

        self.setGeometry(200, 200, 800, 600)
        self.changeTitle()
        self.show()

    def changeTitle(self):
        title = "Node Editor - "
        if self.filename is None:
            title += "New"
        else:
            title += os.path.basename(self.filename)

        if self.centralWidget().scene.has_been_modified:
            title += '*'
        self.setWindowTitle(title)

    def closeEvent(self, event: QtGui.QCloseEvent) -> None:
        if self.maybeSave():
            event.accept()
        else:
            event.ignore()

    def maybeSave(self):
        if not self.isModified():
            return True

        res = QMessageBox.warning(self, "About to loose your work",
                                  "The document has been modified.\n Do you want to save your changes?",
                                  QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel)

        if res == QMessageBox.Save:
            return self.onFileSave()
        elif res == QMessageBox.Cancel:
            return False
        else:
            return True

    def isModified(self):
        return self.centralWidget().scene.has_been_modified
    def onScenePosChanged(self, x, y):
        self.status_mouse_position.setText(f'Scene Pos: [{x},{y}]')

    def onFileNew(self):
        if self.maybeSave():
            self.centralWidget().scene.clear()
            self.filename = None
            self.changeTitle()

    def onFileOpen(self):
        fname, filter = QFileDialog.getOpenFileName(self, 'Open graph from file')
        if fname == "":
            return
        if os.path.isfile(fname):
            self.centralWidget().scene.loadFromFile(fname)
            self.filename = fname
            self.changeTitle()

    def onFileSave(self):
        if self.filename is None:
            return self.onFileSaveAs()
        else:
            self.centralWidget().scene.saveToFile(self.filename)
            self.statusBar().showMessage(f"Successfully saved {self.filename}")
            return True

    def onFileSaveAs(self):
        fname, filter = QFileDialog.getSaveFileName(self, 'Save graph from file')
        if fname == "":
            return False
        self.filename = fname
        self.onFileSave()
        return True

    def onEditUndo(self):
        self.centralWidget().scene.history.undo()

    def onEditRedo(self):
        self.centralWidget().scene.history.redo()

    def onEditDelete(self):
        self.centralWidget().view.deleteSelected()

    def onEditCut(self):
        data = self.centralWidget().scene.clipboard.serializeSelected(delete=True)
        str_data = json.dumps(data, indent=4)
        QApplication.instance().clipoard().setText(str_data)
    def onEditCopy(self):
        data = self.centralWidget().scene.clipboard.serializeSelected(delete=False)
        str_data = json.dumps(data, indent=4)
        QApplication.instance().clipboard().setText(str_data)

    def onEditPaste(self):
        raw_data = QApplication.instance().clipboard().text()

        try:
            data = json.loads(raw_data)
        except ValueError as e:
            print("Pasting of not valid json data!", e)
            return

        # check if the jason data are correct
        if 'nodes' not in data:
            print("JSON does not contain any nodes")
            return

        self.centralWidget().scene.clipboard.deserializeFromClipboard(data)