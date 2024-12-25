import cv2
import json
from pathlib import Path
from typing import Optional
from PyQt6.QtCore import QObject, pyqtSignal, Qt
from PyQt6.QtWidgets import *
from PyQt6.QtWidgets import QMessageBox as QMB


class SceneData(QObject):

    current_frame_changed = pyqtSignal()
    selected_lot_idx_changed = pyqtSignal()
    selected_scene_idx_changed = pyqtSignal()
    data_loaded = pyqtSignal()
    data_changed = pyqtSignal()

    def __init__(self):
        super().__init__()
        self._json_path = None
        self._video_path: str = None
        self._lots: Optional[list] = []
        self._scenes = {}
        self._dirty: bool = False
        self._loaded: bool = False

        self._current_frame = "00000"
        self._selected_lot_idx = None
        self._selected_scene_idx = None

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

        self._selected_scene_idx = None
        self.set_selected_lot_idx(0)
        self.update_current_frame("00000")
        self.data_loaded.emit()
        return True

    def current_frame(self):
        return self._current_frame

    def update_current_frame(self, value):
        self._current_frame = value
        self.current_frame_changed.emit()

    def selected_lot_idx(self):
        return self._selected_lot_idx

    def set_selected_lot_idx(self, value):
        self._selected_lot_idx = value
        self.selected_lot_idx_changed.emit()

    def current_lot_id(self):
        if self._selected_lot_idx is None:
            return None
        return self.lot_ids()[self._selected_lot_idx]

    def current_lot_img(self):
        return cv2.imread(self.parent_dir() / self.current_lot_id() / (self._current_frame + ".jpg"))

    def selected_scene(self):
        return self.scenes_with_current_lot_id()[self._selected_scene_idx]

    def selected_scene_idx(self):
        return self._selected_scene_idx

    def set_selected_scene_idx(self, value):
        self._selected_scene_idx = value
        if value is not None:
            scene = self.selected_scene()
            self.update_current_frame(scene["frame"])
        self.selected_scene_idx_changed.emit()

    def scenes_with_current_lot_id(self):
        if self.current_lot_id() is None:
            return None
        return self._scenes[self.current_lot_id()]

    def sort_scenes(self):
        scenes = self.scenes_with_current_lot_id()
        if scenes is not None:
            scenes.sort(key=lambda x: x["frame"])

    def current_scene(self):
        return self.prev_scene()

    def current_label(self):
        if self.current_scene() is None:
            return None
        return self.current_scene()["label"]

    def get_adjacent_scenes(self):
        self.sort_scenes()
        scenes = self.scenes_with_current_lot_id()
        if not scenes:
            return None, None

        prev_scene, next_scene = None, None
        for i in range(len(scenes)):
            frame = scenes[i]["frame"]
            if self._current_frame >= frame:
                prev_scene = scenes[i]
            if self._current_frame < frame:
                if (next_scene is not None) and (frame > next_scene["frame"]):
                    break
                next_scene = scenes[i]
        return prev_scene, next_scene

    def next_scene(self):
        prev_scene, next_scene = self.get_adjacent_scenes()
        return next_scene

    def prev_scene(self):
        prev_scene, next_scene = self.get_adjacent_scenes()
        return prev_scene

    def next_scene_frame(self):
        if self.next_scene() is None:
            return None
        return self.next_scene()["frame"]

    def prev_scene_frame(self):
        if self.prev_scene() is None:
            return None
        return self.prev_scene()["frame"]

    def next_scene_label(self):
        if self.next_scene() is None:
            return None
        return self.next_scene()["label"]

    def prev_scene_label(self):
        if self.prev_scene() is None:
            return None
        return self.prev_scene()["label"]

    def num_scenes(self):
        scenes = self.scenes_with_current_lot_id()
        if scenes is None:
            return 0
        return len(scenes)

    def num_occluded_scenes(self):
        scenes = self.scenes_with_current_lot_id()
        if scenes is None:
            return 0
        size = 0
        for scene in scenes:
            if "occluded" in scene["flags"]:
                size += 1
        return size

    def info(self):
        return {
            "frame": self.current_frame(),
            "label": self.current_label(),
            "num scenes": self.num_scenes(),
            "num occluded\nscenes": self.num_occluded_scenes()}

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

    def label_is_exist_in_frame(self, frame):
        scenes = self.scenes_with_current_lot_id()
        for scene in scenes:
            if scene["frame"] == frame:
                return True
        return False

    def add_scene(self, label):
        if self.label_is_exist_in_frame(self._current_frame):
            return
        self.scenes_with_current_lot_id().append(
            {
                "label": label,
                "frame": self._current_frame,
                "flags": []})
        self.sort_scenes()
        self.data_changed.emit()

    def add_occluded_flag(self):
        if self.prev_scene() is None:
            return
        self.prev_scene()["flags"].append("occluded")
        self.data_changed.emit()

    def remove_selected_scene(self):
        scenes = self.scenes_with_current_lot_id()
        if not scenes:
            return
        if self._selected_scene_idx is None:
            return
        scenes.pop(self._selected_scene_idx)
        self.data_changed.emit()

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
        self.scene_data.current_frame_changed.connect(self.update)
        self.scene_data.selected_lot_idx_changed.connect(self.update)
        self.scene_data.selected_scene_idx_changed.connect(self.update)
        self.scene_data.data_changed.connect(self.update)
        layout, self.line_edits = self.dict_to_layout(self.scene_data.info())
        self.setLayout(layout)
        self.adjustSize()

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
