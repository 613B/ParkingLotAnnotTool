#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import argparse
import sys
from pathlib import Path

import cv2
from loguru import logger
from natsort import natsorted

def extract_frames(
    src_dir: Path,
    dst_dir: Path,
    jpeg_quality: int,
) -> None:
    """Extract all frames from every .mp4 in src_dir and save as sequential JPEGs in dst_dir."""
    dst_dir.mkdir(parents=True, exist_ok=True)
    jpeg_params = [int(cv2.IMWRITE_JPEG_QUALITY), jpeg_quality]

    # gather and sort .mp4 files naturally (time order)
    mp4_files = [p for p in src_dir.iterdir() if p.is_file() and p.suffix.lower() == '.mp4']
    mp4_files = natsorted(mp4_files)

    frame_counter = 0
    for video_path in mp4_files:
        start_counter = frame_counter
        logger.info("Processing video '{}' (jpg start {})", video_path.name, start_counter)

        cap = cv2.VideoCapture(str(video_path))
        if not cap.isOpened():
            logger.warning("Failed to open video '{}'", video_path.name)
            continue

        while True:
            ret, frame = cap.read()
            if not ret:
                break
            out_path = dst_dir / f"{frame_counter:05d}.jpg"
            cv2.imwrite(str(out_path), frame, jpeg_params)
            frame_counter += 1

        cap.release()
        end_counter = frame_counter - 1
        logger.info("Finished '{}' (jpg end {})", video_path.name, end_counter)

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
        "--quality", "-q",
        type=int,
        default=95,
        help="JPEG quality (0-100, higher is better)"
    )
    parser.add_argument(
        "--log-file", "-l",
        type=Path,
        default=Path("extract_frames.log"),
        help="path to log file (will overwrite on each run)"
    )
    args = parser.parse_args()

    # overwrite log file on each run
    logger.add(
        args.log_file,
        level="INFO",
        mode="w",
        encoding="utf-8",
        rotation="10 MB"
    )

    logger.info("Command: {}", " ".join(sys.argv))
    logger.info(
        "Arguments: input_dir={}, output_dir={}, quality={}, log_file={} ",
        args.input_dir, args.output_dir, args.quality, args.log_file
    )

    extract_frames(args.input_dir, args.output_dir, args.quality)

    logger.info("Execution finished successfully.")

if __name__ == "__main__":
    main()
