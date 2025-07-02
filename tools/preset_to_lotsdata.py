import argparse
import json
from pathlib import Path
from typing import Any, Union
from pathlib import Path
from loguru import logger

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from ParkingLotAnnotTool.core.definequad.lotsdata import LotsData


def load_json(source: Union[str, Path]) -> dict:
    """Load JSON from file or string"""
    if isinstance(source, Path) or Path(source).exists():
        with open(source, 'r', encoding='utf-8') as f:
            return json.load(f)
    else:
        return json.loads(source)


def get_nested_value(data: dict, keys: list[str]) -> Any:
    """Access nested value with list of keys"""
    for key in keys:
        data = data[key]
    return data


def main() -> None:
    parser = argparse.ArgumentParser(description="JSON parser")
    parser.add_argument("input_file", type=Path, help="Path to input JSON file")
    parser.add_argument("output_dir", type=Path, help="Path to output directory")
    args = parser.parse_args()

    logger.info("args: {}", args)

    data = load_json(args.input_file)
    output_dir: Path = args.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)

    for camera in data["cameras"]:
        lots_data = LotsData()
        name: str = camera["name"]
        logger.info("camera: {}", name)
        output_file = (output_dir / name).with_suffix(".json")
        lots_data.set_json_path(output_file)
        presets = camera["presets"][0]
        lots = get_nested_value(presets, ["config_preset", "lots"])
        for i, lot in enumerate(lots):
            q = lot["quad"]
            lots_data.add_lot(
                lot_id=lot["id"],
                x1=q[0], y1=q[1],
                x2=q[2], y2=q[3],
                x3=q[4], y3=q[5],
                x4=q[6], y4=q[7])
        lots_data.save()
        logger.info("lots saved to {}", output_file)


if __name__ == "__main__":
    main()
