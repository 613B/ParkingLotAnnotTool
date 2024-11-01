import json
from pathlib import Path
from typing import Optional
from PyQt6.QtWidgets import *
from PyQt6.QtWidgets import QMessageBox as QMB

from ParkingLotAnnotTool.utils.filesystem import list_by_ext

class SceneData:

    def __init__(self):
        self.video_path: str = None
        self.lots: Optional[list] = []
        self.dirty: bool = False
        self._loaded: bool = False
        self.json_path = None
        self.parent_dir = None
        self.raw_data_dir = None
        self.lot_dirs = []
        self.len_frames = None
        self.frame_names = []
        self.scenes = []

    def reset(self):
        self.may_save()
        self.video_path = None
        self.lots = []
        self.parent_dir = None
        self.raw_data_dir = None
        self.len_frames = None
        self.dirty = False

    def load(self) -> bool:
        self.may_save()
        with open(self.json_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
        self.video_path = data['video_path']
        self.lots = data['lots']
        self.parent_dir = self.json_path.parent
        self.raw_data_dir = self.parent_dir / "raw"
        self.lot_dirs = [self.parent_dir / lot['id'] for lot in self.lots]
        self.len_frames = len(list_by_ext(self.raw_data_dir, ".jpg"))
        self.frame_names = [f'{i:05d}.jpg' for i in range(self.len_frames)]
        self.scenes = data['scenes']
        self.dirty = False
        self._loaded = True
        return True

    def loaded(self) -> bool:
        return self._loaded

    def is_dirty(self) -> bool:
        return self.dirty

    def save(self):
        data = {
            "version": "0.1",
            "lots": self.lots,
            "scenes": self.scenes}
        with open(self.json_path, 'w', encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False, indent=4)
        self._loaded = True
        self.dirty = False

    def may_save(self):
        if not self.dirty:
            return
        msg = 'The preset is unsaved, would you like to save it?'
        ret = QMB.warning(None, 'Attention', msg, QMB.StandardButton.Yes | QMB.StandardButton.No)
        if ret == QMB.StandardButton.Yes:
            self.save()
        if ret == QMB.StandardButton.No:
            pass

    def get_lots(self):
        return self.lots
    
    def get_frame_names(self):
        return self.frame_names

    def set_json_path(self, path):
        if   isinstance(path, Path):
            self.json_path = path
        elif isinstance(path, str):
            self.json_path = Path(path)