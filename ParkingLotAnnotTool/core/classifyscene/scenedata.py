import json
from pathlib import Path
from typing import Optional
from PyQt6.QtWidgets import *
from PyQt6.QtWidgets import QMessageBox as QMB

class SceneData:

    def __init__(self):
        self._json_path = None
        self._video_path: str = None
        self._lots: Optional[list] = []
        self._scenes = {}
        self._dirty: bool = False
        self._loaded: bool = False

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
        return True

    def parent_dir(self) -> Path:
        return self._json_path.parent
    
    def raw_data_dir(self) -> Path:
        return self.parent_dir() / "raw"
    
    def lot_dirs(self) -> Path:
        return [self.parent_dir() / lot['id'] for lot in self._lots]

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