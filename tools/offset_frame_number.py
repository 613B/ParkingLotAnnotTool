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

    scene_json = load_json(args.scene_json)

    for id, scenes in scene_json["scenes"].items():
        for scene in scenes:
            s = scene["frame"]
            n = int(s) + args.offset
            s_new = str(n).zfill(len(s))
            scene["frame"] = s_new


if __name__ == "__main__":
    main()
