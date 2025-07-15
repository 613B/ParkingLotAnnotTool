#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import argparse
import sys
import re
from pathlib import Path

import cv2
from loguru import logger
from natsort import natsorted

def extract_frames(
    src_dir: Path,
    dst_dir: Path,
    jpeg_quality: int,
    use_text_names: bool,
) -> None:
    """Extract all frames from every .mp4 in src_dir and save as JPEGs in dst_dir.
    If use_text_names is True, use corresponding .txt file for naming frames by timestamp.
    """
    dst_dir.mkdir(parents=True, exist_ok=True)
    jpeg_params = [int(cv2.IMWRITE_JPEG_QUALITY), jpeg_quality]

    # gather and sort .mp4 files naturally (time order)
    mp4_files = [p for p in src_dir.iterdir() if p.is_file() and p.suffix.lower() == '.mp4']
    mp4_files = natsorted(mp4_files)

    frame_counter = 0
    for video_path in mp4_files:
        logger.info("Processing video '{}'", video_path.name)
        cap = cv2.VideoCapture(str(video_path))
        if not cap.isOpened():
            logger.warning("Failed to open video '{}', skipping", video_path.name)
            continue

        # Prepare naming list if requested
        names = []
        if use_text_names:
            text_path = video_path.with_suffix('.txt')
            if not text_path.exists():
                logger.warning("Text file '{}' not found, falling back to sequential naming", text_path.name)
            else:
                with text_path.open('r', encoding='utf-8') as f:
                    for line in f:
                        match = re.search(r"record/([^/]+)/raw\.jpg", line)
                        if match:
                            names.append(match.group(1))
                        else:
                            logger.warning("Line didn't match expected pattern: {}", line.strip())

        local_idx = 0
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            if use_text_names and local_idx < len(names):
                out_name = f"{names[local_idx]}.jpg"
            else:
                out_name = f"{frame_counter:05d}.jpg"
                if use_text_names and local_idx >= len(names):
                    logger.warning(
                        "More frames than names for '{}', using sequential for remaining", video_path.name
                    )

            out_path = dst_dir / out_name
            cv2.imwrite(str(out_path), frame, jpeg_params)

            frame_counter += 1
            local_idx += 1

        cap.release()
        logger.info("Finished '{}' (total frames so far {})", video_path.name, frame_counter)


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
    parser.add_argument(
        "--use-text-names", "-u",
        action="store_true",
        help="use corresponding text files to name frames by timestamp"
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
        "Arguments: input_dir={}, output_dir={}, quality={}, log_file={}, use_text_names={} ",
        args.input_dir, args.output_dir, args.quality, args.log_file, args.use_text_names
    )

    extract_frames(
        args.input_dir,
        args.output_dir,
        args.quality,
        args.use_text_names,
    )

    logger.info("Execution finished successfully.")

if __name__ == "__main__":
    main()
