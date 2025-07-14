import argparse
import json
from pathlib import Path
from typing import Union
from pathlib import Path
from loguru import logger

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from ParkingLotAnnotTool.core.classifyscene.scenedata import SceneData


def load_json(source: Union[str, Path]) -> dict:
    """Load JSON from file or string"""
    if isinstance(source, Path) or Path(source).exists():
        with open(source, 'r', encoding='utf-8') as f:
            return json.load(f)
    else:
        return json.loads(source)


def main() -> None:
    parser = argparse.ArgumentParser(description="JSON parser")
    parser.add_argument("scene_json", type=Path, help="Path to scene.json")
    parser.add_argument("--offset", type=int, default=0, help="offset num")
    args = parser.parse_args()

    logger.info("args: {}", args)

    scene_data = load_json(args.scene_json)

    for id, scenes in scene_data["scenes"].items():
        for scene in scenes:
            s = scene["frame"]
            if not int(s):
                continue
            n = int(s) + args.offset
            s_new = str(n).zfill(len(s))
            scene["frame"] = s_new
    
    for id, frames in scene_data["difficult_frames"].items():
        for frame in frames:
            s = frame["frame"]
            if not int(s):
                continue
            n = int(s) + args.offset
            s_new = str(n).zfill(len(s))
            frame["frame"] = s_new

    with args.scene_json.open('w', encoding='utf-8') as f:
        json.dump(scene_data, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()
