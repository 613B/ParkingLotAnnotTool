from PyQt6.QtWidgets import QMenuBar
from PyQt6.QtGui import QAction

class MenuBar(QMenuBar):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # ファイルメニューを作成
        help_menu = self.addMenu("Help")
        
        license_action = QAction("License", self)
        help_menu.addAction(license_action)
