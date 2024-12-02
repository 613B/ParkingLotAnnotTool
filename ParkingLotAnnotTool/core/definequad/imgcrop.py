import json
import os
from pathlib import Path
from PIL import Image, ImageDraw
from PyQt6.QtCore import QThread, pyqtSignal
from typing import List, Tuple

from ParkingLotAnnotTool.utils.filesystem import list_by_ext

class ImageCropWorker(QThread):
    MODEL_WIDTH = 224
    MODEL_HEIGHT = 224
    progress = pyqtSignal(int)
    finished = pyqtSignal()
    canceled = pyqtSignal()

    def __init__(self, scene_json_path: Path, quality=95):
        super().__init__()
        self.progress.emit(0)
        self.data = {}
        with open(scene_json_path, 'r', encoding='utf-8') as file:
            self.data = json.load(file)
        self.parent_dir_path = scene_json_path.parent
        self.quality = quality
        self._is_canceled = False

    def run(self):
        lots = self.data['lots']
        for lot in lots:
            os.makedirs((self.parent_dir_path / lot['id']), exist_ok=True)

        raw_frame_paths = list_by_ext(self.parent_dir_path / "raw", ".jpg")
        total_frames = len(raw_frame_paths)
        for i, raw_frame_path in enumerate(raw_frame_paths):
            if self._is_canceled:
                self.canceled.emit()
                return

            image = Image.open(raw_frame_path)
            for lot in lots:
                q = lot['quad']
                contours = [(q[0], q[1]), (q[2], q[3]), (q[4], q[5]), (q[6], q[7])]
                cropped_image = self.imgcrop(image, contours)
                cropped_image.save((self.parent_dir_path / lot['id'] / Path(raw_frame_path).name))

            progress = int((i / total_frames) * 100)
            self.progress.emit(progress)

        self.finished.emit()

    def cancel(self):
        self._is_canceled = True

    def get_xmin(self, contours: List[Tuple[int, int]]):
        return min(contours, key=lambda item: item[0])[0]

    def get_xmax(self, contours: List[Tuple[int, int]]):
        return max(contours, key=lambda item: item[0])[0]

    def get_ymin(self, contours: List[Tuple[int, int]]):
        return min(contours, key=lambda item: item[1])[1]

    def get_ymax(self, contours: List[Tuple[int, int]]):
        return max(contours, key=lambda item: item[1])[1]

    # TODO implement new method
    def imgcrop(self, image: Image, contours: List[Tuple[int, int]]) -> Image:
        up_sample_rate = 1.2

        orig_xmin = self.get_xmin(contours)
        orig_xmax = self.get_xmax(contours)
        orig_ymin = self.get_ymin(contours)
        orig_ymax = self.get_ymax(contours)
        w = orig_xmax - orig_xmin
        h = orig_ymax - orig_ymin
        long_side = max(w, h)
        crop_w = (long_side * up_sample_rate)
        crop_h = crop_w
        xmin = int(orig_xmin) - (crop_w - w) // 2
        ymin = int(orig_ymin) - (crop_h - h) // 2
        xmax = xmin + crop_w
        ymax = ymin + crop_h
        cropped_img = image.crop((xmin, ymin, xmax, ymax))
        offseted_contours = [(p[0] - xmin, p[1] - ymin) for p in contours]
        scale = self.MODEL_WIDTH / cropped_img.size[0]
        resized_contours = [(p[0] * scale, p[1] * scale) for p in offseted_contours]
        dst = cropped_img.resize((self.MODEL_WIDTH, self.MODEL_HEIGHT))
        draw = ImageDraw.Draw(dst)
        draw.polygon(resized_contours, outline="red", width=5)
        return dst
