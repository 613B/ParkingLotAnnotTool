from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

from canvas.canvas import CanvasWidget
from messagebox.messagebox import MessageBox
from menubar.menubar import MenuBar


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # WindowSettings
        self.setWindowTitle("ParkingLotAnnotTool v1.0")
        self.setGeometry(100, 100, 800, 600)

        self.setMenuBar(MenuBar(self))
        self.setCentralWidget(CanvasWidget(self))
        self.addDockWidget(Qt.DockWidgetArea.BottomDockWidgetArea, MessageBox("Message Box", self))

