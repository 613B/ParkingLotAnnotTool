import json
from pathlib import Path
from PyQt6.QtCore import QObject, pyqtSignal, Qt
from PyQt6.QtWidgets import *
from PyQt6.QtWidgets import QMessageBox as QMB


class ConditionsData(QObject):

    current_frame_changed = pyqtSignal()
    current_lot_id_changed = pyqtSignal()

    def __init__(self):
        super().__init__()
        self._json_path = None
        self._video_path: str = None
        self._conditions = []
        self._initial_time = None
        self._day_start_time = None
        self._night_start_time = None
        self._interval = None
        self._dirty: bool = False
        self._loaded: bool = False

        self._current_frame = "00000"
        self._current_time = None

    def reset(self):
        pass

    def load(self) -> bool:
        self.may_save()
        with open(self._json_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
        self._video_path = data['video_path']
        self._conditions = data['conditions']
        self._initial_time = data['initial_time']
        self._day_start_time = data['day_start_time']
        self._night_start_time = data['night_start_time']
        self._interval = data['interval']
        self._dirty = False
        self._loaded = True

        self._current_frame = "00000"
        self.current_frame_changed.emit()
        return True

    def current_frame(self):
        return self._current_frame

    def update_current_frame(self, value):
        self._current_frame = value
        self.current_frame_changed.emit()

    def get_label_find_by_frame(self, frame):
        if frame is None or not self._conditions:
            return None
        for d in self._conditions:
            if d["frame"] == frame:
                return d["label"]

    def current_label(self):
        return self.get_label_find_by_frame(self._current_frame)

    def info(self):
        return {
            "frame": self.current_frame(),
            "label": self.current_label()}

    def parent_dir(self) -> Path:
        return self._json_path.parent

    def raw_data_dir(self) -> Path:
        return self.parent_dir() / "raw"

    def len_frames(self):
        return len(list(self.raw_data_dir().glob("*.jpg")))

    def frame_names(self):
        return [f'{i:05d}.jpg' for i in range(self.len_frames())]

    def add_label(self, label):
        self._conditions.append({
            "frame": self.current_frame(),
            "label": label})

    def loaded(self) -> bool:
        return self._loaded

    def is_dirty(self) -> bool:
        return self._dirty

    def save(self):
        data = {
            "version": "0.1",
            "video_path": str(self._video_path),
            "conditions": self._conditions,
            "initial_time": self._initial_time,
            "day_start_time": self._day_start_time,
            "night_start_time": self._night_start_time,
            "interval": self._interval}
        with open(self._json_path, 'w', encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False, indent=4)
        self._loaded = True
        self._dirty = False

    def may_save(self):
        if not self._dirty:
            return
        msg = 'The preset is unsaved, would you like to save it?'
        ret = QMB.warning(None, 'Attention', msg, QMB.StandardButton.Yes | QMB.StandardButton.No)
        if ret == QMB.StandardButton.Yes:
            self.save()
        if ret == QMB.StandardButton.No:
            pass

    def set_json_path(self, path):
        if   isinstance(path, Path):
            self._json_path = path
        elif isinstance(path, str):
            self._json_path = Path(path)

    def conditions(self):
        return self._conditions

    def initial_time(self):
        return self._initial_time

    def set_initial_time(self, value):
        self._initial_time = value

    def day_start_time(self):
        return self._day_start_time

    def set_day_start_time(self, value):
        self._day_start_time = value

    def night_start_time(self):
        return self._night_start_time

    def set_night_start_time(self, value):
        self._night_start_time = value


class ConditionsDataInfoWidget(QWidget):
    def __init__(self, conditions_data: ConditionsData, parent=None):
        super(ConditionsDataInfoWidget, self).__init__()
        self.conditions_data = conditions_data
        layout, self.line_edits = self.dict_to_layout(self.conditions_data.info())
        self.setLayout(layout)

    def dict_to_layout(self, data):
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

    def update(self):
        for key, value in self.conditions_data.info().items():
            self.line_edits[key].setEnabled(True)
            if value is None:
                self.line_edits[key].setText("None")
            else:
                self.line_edits[key].setText(str(value))
