import json
from typing import Optional
from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtWidgets import *
from PyQt6.QtWidgets import QMessageBox as QMB

from ParkingLotAnnotTool.utils.geometry import *

class LotsData(QObject):

    data_changed = pyqtSignal()
    selected_idx_changed = pyqtSignal()

    def __init__(self):
        super().__init__()
        self._lots: Optional[list] = []
        self._dirty: bool = False
        self._loaded: bool = False
        self._json_path = None
        self._image_path = None

        self._addable = False
        self._editable = False
        self._selected_idx = None

    def reset(self):
        self.may_save()
        self._lots = []
        self._dirty = False
        self._selected_idx = None
        self.data_changed.emit()

    def load(self) -> bool:
        self.may_save()
        with open(self._json_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
        self._image_path = data['image_path']
        self._lots = data['lots']
        self._dirty = False
        self._loaded = True
        self._selected_idx = None
        self.data_changed.emit()
        return True

    def loaded(self) -> bool:
        return self._loaded

    def is_dirty(self) -> bool:
        return self._dirty

    def is_editable(self):
        return self._editable

    def set_editable(self, value):
        self._editable = value

    def is_addable(self):
        return self._addable

    def set_addable(self, value):
        self._addable = value

    def selected_idx(self):
        return self._selected_idx

    def set_selected_idx(self, idx):
        self._selected_idx = idx
        self.selected_idx_changed.emit()

    def save(self):
        data = {
            "version": "0.1",
            "image_path": self._image_path,
            "lots": self._lots}
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

    def image_path(self):
        return self._image_path

    def set_image_path(self, path):
        self._image_path = path

    def json_path(self):
        return self._json_path

    def set_json_path(self, path):
        self._json_path = path

    def lots(self):
        return self._lots

    def get_lot_by_idx(self, lidx: int):
        lots = self.lots()
        if len(lots) <= lidx:
            return None
        return lots[lidx]

    def get_points_by_idx(self, lidx: int):
        lot = self.get_lot_by_idx(lidx)
        if lot is None:
            return None
        quad = lot['quad']
        return [[quad[0], quad[1]],
                [quad[2], quad[3]],
                [quad[4], quad[5]],
                [quad[6], quad[7]]]

    def set_point_by_idx(self, lidx: int, pidx: int, x: float, y: float):
        lot = self.get_lot_by_idx(lidx)
        if lot is None:
            return
        lot['quad'][pidx * 2 + 0] = x
        lot['quad'][pidx * 2 + 1] = y
        self._dirty = True

    def move_lot_by_idx(self, lidx: int, dx: float, dy: float):
        lot = self.get_lot_by_idx(lidx)
        if lot is None:
            return
        quad = lot['quad']
        quad[0] += dx
        quad[1] += dy
        quad[2] += dx
        quad[3] += dy
        quad[4] += dx
        quad[5] += dy
        quad[6] += dx
        quad[7] += dy
        self._dirty = True

    def delete_selected_area(self):
        if self._selected_idx is None:
            return
        self._lots.pop(self._selected_idx)
        self._selected_idx = None
        self.data_changed.emit()

    def nearest_point(self, x: float, y: float):
        dist, lidx, pidx = None, None, None
        for lidx_tmp, lot in enumerate(self._lots):
            for pidx_tmp, point in enumerate(self.get_points_by_idx(lidx_tmp)):
                dist_tmp = ((point[0] - x)**2 + (point[1] - y)**2)**(1/2)
                if (dist is None) or (dist_tmp < dist):
                    lidx = lidx_tmp
                    pidx = pidx_tmp
                    dist = dist_tmp
        return dist, lidx, pidx

    def intersect(
        self,
        a : Vector2d,
        b : Triangle2d
        ) -> bool:
        s = b.y1 * b.x3 - b.x1 * b.y3 + (b.y3 - b.y1) * a.x + (b.x1 - b.x3) * a.y
        t = b.x1 * b.y2 - b.y1 * b.x2 + (b.y1 - b.y2) * a.x + (b.x2 - b.x1) * a.y
        if (s < 0) != (t < 0):
            return False
        A = -b.y2 * b.x3 + b.y1 * (b.x3 - b.x2) + b.x1 * (b.y2 - b.y3) + b.x2 * b.y3
        if A < 0:
            return (s <= 0) and (s + t >= A)
        else:
            return (s >= 0) and (s + t <= A)

    def is_point_in_quad(self, x: float, y: float):
        for lidx, lot in enumerate(self._lots):
            x1, y1, x2, y2, x3, y3, x4, y4 = lot['quad']
            if self.intersect(Vector2d(x, y), Triangle2d(x1, y1, x2, y2, x3, y3)) or \
               self.intersect(Vector2d(x, y), Triangle2d(x1, y1, x4, y4, x3, y3)):
                return lidx
        return None

    def add_lot(
            self,
            lot_id: str,
            x1: int, y1: int,
            x2: int, y2: int,
            x3: int, y3: int,
            x4: int, y4: int):
        self._lots.append({
            'id': lot_id,
            'quad': [x1, y1, x2, y2, x3, y3, x4, y4]})
        self._dirty = True
        self.data_changed.emit()
