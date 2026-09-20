"""
Logging utility for Exchange Control Desk.
"""

import logging
import os
import sys
from typing import Optional

_LOGGER: Optional[logging.Logger] = None


def setup_logger(name: str = "ExchangeControlDesk", level: int = logging.INFO) -> logging.Logger:
    """Configures a standardized console and file logger."""
    global _LOGGER
    if _LOGGER is not None:
        return _LOGGER

    os.makedirs("logs", exist_ok=True)

    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.propagate = False

    # Clear existing handlers if any
    if logger.hasHandlers():
        logger.handlers.clear()

    formatter = logging.Formatter(
        "[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    console_handler.setLevel(level)
    logger.addHandler(console_handler)

    # File handler
    file_handler = logging.FileHandler("logs/exchange_control_desk.log", encoding="utf-8")
    file_handler.setFormatter(formatter)
    file_handler.setLevel(level)
    logger.addHandler(file_handler)

    _LOGGER = logger
    return logger


def get_logger() -> logging.Logger:
    """Returns the active logger instance."""
    if _LOGGER is None:
        return setup_logger()
    return _LOGGER
