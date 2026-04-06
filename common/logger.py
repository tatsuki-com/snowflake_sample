"""ロガー設定（ローテーション付き）モジュール"""

import logging
import os
from logging.handlers import RotatingFileHandler


def setup_logger(config: dict) -> logging.Logger:
    """設定に基づいてロガーを構築して返す。"""
    log_config = config["logging"]
    level = getattr(logging, log_config["level"].upper(), logging.INFO)
    log_file = log_config["file"]
    max_bytes = log_config["max_bytes"]
    backup_count = log_config["backup_count"]

    log_dir = os.path.dirname(log_file)
    if log_dir:
        os.makedirs(log_dir, exist_ok=True)

    logger = logging.getLogger("email_attachment_system")
    logger.setLevel(level)

    if logger.handlers:
        return logger

    formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(name)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    file_handler = RotatingFileHandler(
        log_file, maxBytes=max_bytes, backupCount=backup_count, encoding="utf-8"
    )
    file_handler.setLevel(level)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    return logger
