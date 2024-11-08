import argparse
import cv2
import json
import os
import sys
from pathlib import Path
from PIL import Image
from tqdm import tqdm

from PyQt6.QtCore import QCoreApplication

sys.path.append(str(Path(__file__).parents[3]))
from ParkingLotAnnotTool.core.definequad.videoextract import VideoExtractWorker
from ParkingLotAnnotTool.core.definequad.imgcrop import ImageCropWorker

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('cmd', type=str)
    parser.add_argument('--input_video', type=str)
    parser.add_argument('--input_json', type=str)
    parser.add_argument('--interval', type=int, default=60)
    parser.add_argument('--output_dir', type=str)
    args = parser.parse_args()

    app = QCoreApplication(sys.argv)
    progress_bar = tqdm(total=100)

    if   args.cmd=="extract_frames":
        worker = VideoExtractWorker(Path(args.input_video), Path(args.output_dir), args.interval)
        worker.progress.connect(progress_bar.update)
        worker.finished.connect(app.quit)
        worker.start()
    elif args.cmd=="crop_images":
        worker = ImageCropWorker(Path(args.input_json))
        worker.progress.connect(progress_bar.update)
        worker.finished.connect(app.quit)
        worker.start()

    sys.exit(app.exec())

if __name__ == "__main__":
    main()