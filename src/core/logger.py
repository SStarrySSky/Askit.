"""Logging setup for PAskit application."""

import sys
from pathlib import Path
from loguru import logger


def setup_logger(log_level: str = "INFO", log_to_file: bool = True) -> None:
    """
    Configure the application logger.

    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_to_file: Whether to log to file in addition to console
    """
    # Remove default handler
    logger.remove()

    # Add console handler with custom format
    logger.add(
        sys.stderr,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level=log_level,
        colorize=True,
    )

    # Add file handler if requested
    if log_to_file:
        log_dir = Path.home() / ".paskit" / "logs"
        log_dir.mkdir(parents=True, exist_ok=True)

        log_file = log_dir / "paskit.log"

        logger.add(
            log_file,
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
            level=log_level,
            rotation="10 MB",
            retention="1 week",
            compression="zip",
        )

    logger.info(f"Logger initialized with level: {log_level}")


def get_logger(name: str):
    """Get a logger instance for a specific module."""
    return logger.bind(name=name)
