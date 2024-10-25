from PyQt6.QtWidgets import QWidget

class ClassifySceneWidget(QWidget):
    def __init__(self, parent=None):
        super(ClassifySceneWidget, self).__init__(parent)
        self.setMinimumSize(200, 200)  # 必要に応じてサイズを設定