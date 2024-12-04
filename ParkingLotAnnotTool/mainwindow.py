from PyQt6.QtWidgets import QMainWindow
from PyQt6.QtCore import Qt

from core.core import CoreWidget
from messagebox.messagebox import MessageBox
from menubar.menubar import MenuBar


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # WindowSettings
        self.setWindowTitle("ParkingLotAnnotTool v1.0")
        self.setGeometry(100, 100, 800, 600)
        self.setMinimumWidth(1000)

        self.setMenuBar(MenuBar(self))
        self.setCentralWidget(CoreWidget(self))
        self.addDockWidget(Qt.DockWidgetArea.BottomDockWidgetArea, MessageBox("Message Box", self))

