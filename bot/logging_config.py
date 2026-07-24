"""
Centralized logging configuration.

All API requests, responses, and errors are logged to a rotating log file
(trading_bot.log) as well as the console. This keeps a persistent audit
trail of every order attempt, which is a core requirement of the task.
"""

import logging
import os
from logging.handlers import RotatingFileHandler

LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "logs")
LOG_FILE = os.path.join(LOG_DIR, "trading_bot.log")

_LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"


def setup_logging(level: int = logging.INFO) -> logging.Logger:
    """
    Configure and return the application logger.

    - Writes to logs/trading_bot.log (rotates at 5MB, keeps 5 backups)
    - Also streams to console for immediate feedback
    - Idempotent: calling this multiple times will not duplicate handlers
    """
    os.makedirs(LOG_DIR, exist_ok=True)

    logger = logging.getLogger("trading_bot")
    logger.setLevel(level)

    if logger.handlers:
        # Already configured (e.g. re-imported in same process) — don't duplicate handlers
        return logger

    formatter = logging.Formatter(_LOG_FORMAT)

    file_handler = RotatingFileHandler(
        LOG_FILE, maxBytes=5 * 1024 * 1024, backupCount=5, encoding="utf-8"
    )
    file_handler.setFormatter(formatter)
    file_handler.setLevel(level)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(level)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    logger.propagate = False

    return logger


logger = setup_logging()