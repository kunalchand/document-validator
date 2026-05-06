import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Optional

_LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def configure_logging(log_level: str = "INFO", log_file: Optional[str] = None) -> None:
    """
    Configure the root logger once at app startup.
    All module-level loggers (via get_logger) inherit these handlers.
    """
    level = getattr(logging, log_level.upper(), logging.INFO)
    formatter = logging.Formatter(fmt=_LOG_FORMAT, datefmt=_DATE_FORMAT)

    root = logging.getLogger()
    root.setLevel(level)

    # Avoid adding duplicate handlers if called more than once
    if root.handlers:
        return

    console = logging.StreamHandler(sys.stdout)
    console.setFormatter(formatter)
    root.addHandler(console)

    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        file_handler = RotatingFileHandler(
            log_path,
            maxBytes=10 * 1024 * 1024,  # 10 MB per file
            backupCount=5,
            encoding="utf-8",
        )
        file_handler.setFormatter(formatter)
        root.addHandler(file_handler)


def get_logger(name: str, level: Optional[str] = None) -> logging.Logger:
    logger = logging.getLogger(name)
    if level:
        logger.setLevel(getattr(logging, level.upper(), logging.INFO))
    return logger
