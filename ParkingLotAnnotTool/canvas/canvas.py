# canvas.py
from PyQt5.QtWidgets import QWidget

class CanvasWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(200, 200)  # 必要に応じてサイズを設定