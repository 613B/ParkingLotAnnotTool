# canvas.py
from PyQt6.QtWidgets import QTabWidget

from .classifyconditions.classifyconditions import ClassifyConditionsWidget
from .classifyscene.classifyscene import ClassifySceneWidget
from .definequad.definequad import DefineQuadWidget

class CoreWidget(QTabWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.addTab(DefineQuadWidget(), 'Define Quad')
        self.addTab(ClassifyConditionsWidget(), 'Classify Conditions')
        self.addTab(ClassifySceneWidget(), 'Classify Scene')
        self.setMinimumSize(200, 200)
