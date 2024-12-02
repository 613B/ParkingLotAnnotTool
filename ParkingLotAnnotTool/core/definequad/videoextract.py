import cv2
import os
from PyQt6.QtCore import QThread, pyqtSignal

class VideoExtractWorker(QThread):
    progress = pyqtSignal(int)
    finished = pyqtSignal()
    canceled = pyqtSignal()

    def __init__(self, video_path, output_dir, interval, quality=95):
        super().__init__()
        self.video_path = video_path
        self.output_dir = output_dir
        self.interval = interval
        self.quality = quality
        self._is_canceled = False

    def run(self):
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

        cap = cv2.VideoCapture(self.video_path)
        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_interval = int(fps * self.interval)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

        frame_indices = range(0, total_frames, frame_interval)
        saved_count = 0

        for frame_idx in frame_indices:
            if self._is_canceled:
                cap.release()
                self.canceled.emit()
                return

            cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
            ret, frame = cap.read()
            if not ret:
                break
            frame_filename = os.path.join(self.output_dir, f'{saved_count:05d}.jpg')
            cv2.imwrite(frame_filename, frame, [cv2.IMWRITE_JPEG_QUALITY, self.quality])
            saved_count += 1

            progress = int((frame_idx / total_frames) * 100)
            self.progress.emit(progress)

        cap.release()
        self.finished.emit()

    def cancel(self):
        self._is_canceled = True
