import json
from pathlib import Path
from typing import Optional
from PyQt6.QtCore import QObject, pyqtSignal, Qt
from PyQt6.QtWidgets import *
from PyQt6.QtWidgets import QMessageBox as QMB


class SceneData(QObject):

    current_frame_changed = pyqtSignal()
    current_lot_id_changed = pyqtSignal()

    def __init__(self):
        super().__init__()
        self._json_path = None
        self._video_path: str = None
        self._lots: Optional[list] = []
        self._scenes = {}
        self._dirty: bool = False
        self._loaded: bool = False

        self._current_frame = "00000"
        self._current_lot_id: str = None

    def reset(self):
        pass

    def load(self) -> bool:
        self.may_save()
        with open(self._json_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
        self._video_path = data['video_path']
        self._lots = data['lots']
        self._scenes = data['scenes']
        self._dirty = False
        self._loaded = True

        self._current_lot_id = self.lot_ids()[0]
        self._current_frame = "00000"
        self.current_frame_changed.emit()
        return True

    def current_frame(self):
        return self._current_frame

    def update_current_frame(self, value):
        self._current_frame = value
        self.current_frame_changed.emit()

    def current_lot_id(self):
        return self._current_lot_id

    def update_current_lot_id(self, value):
        self._current_lot_id = value
        self.current_lot_id_changed.emit()

    def scenes_with_current_lot_id(self):
        if self._current_lot_id is None:
            return None
        return self._scenes[self._current_lot_id]

    def get_label_find_by_frame(self, frame):
        scenes = self.scenes_with_current_lot_id()
        if frame is None or not scenes:
            return None
        for d in scenes:
            if d["frame"] == frame:
                return d["label"]
        return self.prev_scene_label()

    def current_label(self):
        return self.get_label_find_by_frame(self._current_frame)

    def get_frames_adjacent_scenes(self, frame):
        scenes = self.scenes_with_current_lot_id()
        if not scenes:
            return None, None
        frames = [d["frame"] for d in scenes]
        sorted_values = sorted(frames)

        for i in range(len(sorted_values) - 1):
            if sorted_values[i] <= frame < sorted_values[i + 1]:
                return sorted_values[i], sorted_values[i + 1]

        if frame < sorted_values[0]:
            return None, sorted_values[0]
        elif frame >= sorted_values[-1]:
            return sorted_values[-1], None

    def next_scene_frame(self):
        prev, next = self.get_frames_adjacent_scenes(self._current_frame)
        return next

    def prev_scene_frame(self):
        prev, next = self.get_frames_adjacent_scenes(self._current_frame)
        return prev

    def next_scene_label(self):
        return self.get_label_find_by_frame(self.next_scene_frame())

    def prev_scene_label(self):
        return self.get_label_find_by_frame(self.prev_scene_frame())

    def info(self):
        return {
            "frame": self.current_frame(),
            "label": self.current_label()}

    def parent_dir(self) -> Path:
        return self._json_path.parent

    def raw_data_dir(self) -> Path:
        return self.parent_dir() / "raw"

    def lot_dirs(self) -> Path:
        return [self.parent_dir() / lot['id'] for lot in self._lots]

    def lot_ids(self):
        return [lot['id'] for lot in self._lots]

    def len_frames(self):
        return len(list(self.raw_data_dir().glob("*.jpg")))

    def frame_names(self):
        return [f'{i:05d}.jpg' for i in range(self.len_frames())]

    def lots(self):
        return self._lots

    def scenes(self):
        return self._scenes

    def add_scene(self, key, scene):
        self._scenes[key].append(scene)

    def remove_scene(self, key, scene):
        self._scenes[key].remove(scene)

    def loaded(self) -> bool:
        return self._loaded

    def is_dirty(self) -> bool:
        return self._dirty

    def save(self):
        data = {
            "version": "0.1",
            "video_path": str(self._video_path),
            "lots": self._lots,
            "scenes": self._scenes}
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


class SceneDataInfoWidget(QWidget):
    def __init__(self, scene_data: SceneData, parent=None):
        super(SceneDataInfoWidget, self).__init__()
        self.scene_data = scene_data
        layout, self.line_edits = self.dict_to_layout(self.scene_data.info())
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
        for key, value in self.scene_data.info().items():
            self.line_edits[key].setEnabled(True)
            if value is None:
                self.line_edits[key].setText("None")
            else:
                self.line_edits[key].setText(str(value))
