import os
import yaml
from pathlib import Path
from typing import Tuple


def load_config(config_path: str = "config.yaml") -> dict:
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)


def get_project_root() -> Path:
    return Path(__file__).parent.parent


def ensure_directory(path: str):
    os.makedirs(path, exist_ok=True)


def calculate_distance(bounding_box_height: float, frame_height: int, config: dict) -> Tuple[str, float]:
    height_ratio = bounding_box_height / frame_height
    
    if height_ratio >= config['distance']['bounding_box_threshold_small']:
        distance_feet = config['distance']['very_close_feet']
        category = "very_close"
    elif height_ratio >= config['distance']['bounding_box_threshold_large']:
        distance_feet = config['distance']['close_feet']
        category = "close"
    else:
        distance_feet = config['distance']['medium_feet']
        category = "medium"
    
    return category, distance_feet


def format_distance_message(distance_category: str, distance_feet: float, direction: str = None) -> str:
    direction_text = f" from your {direction}" if direction else ""
    return f"{distance_feet:.0f} feet{direction_text}"

