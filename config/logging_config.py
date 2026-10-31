"""Logging configuration."""

from __future__ import annotations

import logging
from logging.handlers import RotatingFileHandler

from config.settings import LOG_DIR, ensure_directories


def setup_logging(name: str = "indusscript", level: int = logging.INFO) -> logging.Logger:
    ensure_directories()
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger

    logger.setLevel(level)
    logger.propagate = False
    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    stream = logging.StreamHandler()
    stream.setFormatter(formatter)
    logger.addHandler(stream)

    file_handler = RotatingFileHandler(
        LOG_DIR / "indusscript.log",
        maxBytes=5_000_000,
        backupCount=3,
        encoding="utf-8",
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    return logger
