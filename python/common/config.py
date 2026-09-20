"""
Configuration loading module for Exchange Control Desk.
"""

import os
from pathlib import Path
from typing import Any, Dict
import yaml
from dotenv import load_dotenv

# Load .env variables if present
load_dotenv()


def load_config(config_path: str = "config/project_config.yaml") -> Dict[str, Any]:
    """Loads and validates project configuration from YAML file with environment variable overlays."""
    path = Path(config_path)
    if not path.exists():
        raise FileNotFoundError(f"Configuration file not found at {config_path}")

    with open(path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    # Allow environment variable overrides
    if os.getenv("DB_ENGINE"):
        config["database"]["engine"] = os.getenv("DB_ENGINE")
    if os.getenv("RANDOM_SEED"):
        config["project"]["random_seed"] = int(os.getenv("RANDOM_SEED"))
    if os.getenv("PROJECT_ENV"):
        config["project"]["environment"] = os.getenv("PROJECT_ENV")

    return config
