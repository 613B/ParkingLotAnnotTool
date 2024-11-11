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

    def __init__(self, scene_json_path: Path, quality=100):
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

    def imgcrop(self, image: Image, contours: List[Tuple[int, int]]) -> Image:
        xmin = self.get_xmin(contours)
        xmax = self.get_xmax(contours)
        ymin = self.get_ymin(contours)
        ymax = self.get_ymax(contours)
        w = xmax - xmin
        h = ymax - ymin

        img_cropped = image.crop((xmin, ymin, xmax, ymax))
        aspect_ratio = w / h
        if w > h:
            w_r = self.MODEL_WIDTH
            h_r = int(self.MODEL_HEIGHT / aspect_ratio)
        else:
            h_r = self.MODEL_HEIGHT
            w_r = int(self.MODEL_WIDTH / aspect_ratio)
        img_cropped_r = img_cropped.resize((w_r, h_r))
        contours_r = self.get_resized_contours(contours, (w_r, h_r), offset=True)
        mask = Image.new("L", (w_r, h_r), 0)
        draw = ImageDraw.Draw(mask)
        draw.polygon(contours_r, fill=255, outline=None)
        black =  Image.new("RGB", (w_r, h_r), (0, 0, 0))
        crop_polygon = Image.composite(img_cropped_r, black, mask)
        black_square = Image.new("RGB", (self.MODEL_WIDTH, self.MODEL_HEIGHT), (0, 0, 0))
        offset = ((self.MODEL_WIDTH - w_r) // 2, (self.MODEL_HEIGHT - h_r) // 2)
        black_square.paste(crop_polygon, offset)
        return black_square

    def get_resized_contours(self, contours, size, offset=False):
        xmin = self.get_xmin(contours)
        xmax = self.get_xmax(contours)
        ymin = self.get_ymin(contours)
        ymax = self.get_ymax(contours)
        height = ymax - ymin
        width = xmax - xmin
        if offset:
            x_offset = xmin
            y_offset = ymin
        else:
            x_offset = 0
            y_offset = 0
        h_scale = (size[1]/height)
        w_scale = (size[0]/width)
        return [(((x - x_offset) * w_scale), ((y - y_offset) * h_scale)) for x, y in contours]

