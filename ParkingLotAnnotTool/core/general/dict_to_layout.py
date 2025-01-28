from PyQt6.QtWidgets import *
from PyQt6.QtCore import Qt

def dict_to_layout(data):
        layout = QVBoxLayout()
        line_edits = {}
        for key, value in data.items():
            label = QLabel(str(key))
            line_edit = QLineEdit()
            if value is None:
                line_edit.setText("None")
            else:
                line_edit.setText(str(value))
            line_edit.setMinimumWidth(len(str(value)) * 10)
            line_edit.setAlignment(Qt.AlignmentFlag.AlignRight)
            line_edit.setEnabled(False)
            line_edits[key] = line_edit
            _layout = QHBoxLayout()
            _layout.addWidget(label)
            _layout.addWidget(line_edit)
            layout.addLayout(_layout)
        layout.addStretch()
        return layout, line_edits
