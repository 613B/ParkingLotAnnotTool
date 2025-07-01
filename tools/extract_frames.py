#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import argparse
from pathlib import Path
import cv2
from natsort import natsorted

def extract_frames(
    src_dir: Path,
    dst_dir: Path,
    jpeg_quality: int,
) -> None:
    """Extract all frames from every .mp4 in src_dir and save as sequential JPEGs in dst_dir."""
    dst_dir.mkdir(parents=True, exist_ok=True)
    # OpenCV JPEG parameters
    jpeg_params = [int(cv2.IMWRITE_JPEG_QUALITY), jpeg_quality]

    # gather and sort .mp4 files naturally (time order)
    mp4_files = [
        p for p in src_dir.iterdir()
        if p.is_file() and p.suffix.lower() == '.mp4'
    ]
    mp4_files = natsorted(mp4_files)

    frame_counter = 1
    for video_path in mp4_files:
        cap = cv2.VideoCapture(str(video_path))
        if not cap.isOpened():
            print(f"warning: failed to open {video_path}")
            continue

        while True:
            ret, frame = cap.read()
            if not ret:
                break
            out_path = dst_dir / f"{frame_counter:05d}.jpg"
            cv2.imwrite(str(out_path), frame, jpeg_params)
            frame_counter += 1

        cap.release()

def main():
    parser = argparse.ArgumentParser(
        description="Extract frames from time-sorted mp4 files into one directory"
    )
    parser.add_argument(
        "input_dir",
        type=Path,
        help="directory containing .mp4 files"
    )
    parser.add_argument(
        "output_dir",
        type=Path,
        help="directory to save extracted JPEG frames"
    )
    parser.add_argument(
        "--quality",
        "-q",
        type=int,
        default=95,
        help="JPEG quality (0-100, higher is better)"
    )
    args = parser.parse_args()

    extract_frames(args.input_dir, args.output_dir, args.quality)

if __name__ == "__main__":
    main()
