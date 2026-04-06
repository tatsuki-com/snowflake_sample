"""logger のテスト"""

import logging
import os
import pytest

from common.logger import setup_logger


@pytest.fixture(autouse=True)
def cleanup_logger():
    """テストごとにロガーのハンドラをリセットする。"""
    yield
    logger = logging.getLogger("email_attachment_system")
    logger.handlers.clear()


class TestSetupLogger:
    def test_creates_logger(self, tmp_path):
        config = {
            "logging": {
                "level": "DEBUG",
                "file": str(tmp_path / "test.log"),
                "max_bytes": 1048576,
                "backup_count": 3,
            }
        }
        logger = setup_logger(config)
        assert logger.name == "email_attachment_system"
        assert logger.level == logging.DEBUG
        assert len(logger.handlers) == 2  # file + console

    def test_creates_log_directory(self, tmp_path):
        log_dir = tmp_path / "subdir" / "logs"
        config = {
            "logging": {
                "level": "INFO",
                "file": str(log_dir / "test.log"),
                "max_bytes": 1048576,
                "backup_count": 3,
            }
        }
        setup_logger(config)
        assert log_dir.exists()

    def test_no_duplicate_handlers(self, tmp_path):
        config = {
            "logging": {
                "level": "INFO",
                "file": str(tmp_path / "test.log"),
                "max_bytes": 1048576,
                "backup_count": 3,
            }
        }
        logger1 = setup_logger(config)
        handler_count = len(logger1.handlers)
        logger2 = setup_logger(config)
        assert len(logger2.handlers) == handler_count
