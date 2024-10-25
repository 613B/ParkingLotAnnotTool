from PyQt6.QtWidgets import QMenuBar
from PyQt6.QtGui import QAction

class MenuBar(QMenuBar):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # ファイルメニューを作成
        file_menu = self.addMenu("File")
        
        # アクションを作成
        new_action = QAction("New", self)
        open_action = QAction("Open", self)
        save_action = QAction("Save", self)
        
        # アクションをメニューに追加
        file_menu.addAction(new_action)
        file_menu.addAction(open_action)
        file_menu.addAction(save_action)
