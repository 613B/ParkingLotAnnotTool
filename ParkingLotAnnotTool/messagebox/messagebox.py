# logger.py
from PyQt5.QtWidgets import QDockWidget, QTextEdit

class MessageBox(QDockWidget):
    def __init__(self, name, parent=None):
        super().__init__(name, parent)
        self.setWidget(QTextEdit())
        self.setFeatures(QDockWidget.DockWidgetFeature.NoDockWidgetFeatures)
