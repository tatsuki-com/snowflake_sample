"""config_loader のテスト"""

import os
import tempfile
import pytest
import yaml

from common.config_loader import load_config, _validate_required_keys


def _make_valid_config():
    return {
        "outlook": {
            "target_addresses": ["test@example.com"],
            "target_folder": "受信トレイ",
            "attachment_extensions": [".xlsx"],
        },
        "paths": {
            "folder_a": "./collected",
            "folder_b": "./aggregated",
            "folders_move": {"type_1": "./completed/D"},
        },
        "files": {
            "file_list": "ファイル一覧.xlsm",
            "naming_pattern": "^.+\\.xlsx$",
            "aggregation_targets": {"type_1": "alpha.xlsx"},
        },
        "data_extraction": {
            "datetime_sheet": "_get_datetime",
            "datetime_cell": "A1",
            "data_range": {"column": "B", "start_row": 10, "end_row": 20},
            "routing_cell": "B11",
        },
        "file_list_sheet": {
            "name": "一覧",
            "columns": {
                "filename": "A",
                "original_filename": "B",
                "received_datetime": "C",
                "collected_datetime": "D",
                "duplicate_flag": "E",
                "updated_flag": "F",
                "routing_type": "G",
                "remarks": "H",
            },
        },
        "logging": {
            "level": "INFO",
            "file": "./logs/process.log",
            "max_bytes": 10485760,
            "backup_count": 5,
        },
        "retry": {"max_attempts": 3, "wait_seconds": 5},
    }


class TestLoadConfig:
    def test_load_valid_config(self, tmp_path):
        config_data = _make_valid_config()
        config_file = tmp_path / "config.yaml"
        config_file.write_text(yaml.dump(config_data, allow_unicode=True), encoding="utf-8")

        result = load_config(str(config_file))
        assert result["outlook"]["target_folder"] == "受信トレイ"
        assert result["paths"]["folder_a"] == "./collected"

    def test_file_not_found(self):
        with pytest.raises(FileNotFoundError):
            load_config("/nonexistent/config.yaml")

    def test_empty_config(self, tmp_path):
        config_file = tmp_path / "config.yaml"
        config_file.write_text("", encoding="utf-8")

        with pytest.raises(ValueError, match="設定ファイルが空です"):
            load_config(str(config_file))

    def test_missing_required_key(self, tmp_path):
        config_data = _make_valid_config()
        del config_data["outlook"]["target_addresses"]
        config_file = tmp_path / "config.yaml"
        config_file.write_text(yaml.dump(config_data, allow_unicode=True), encoding="utf-8")

        with pytest.raises(KeyError, match="outlook.target_addresses"):
            load_config(str(config_file))


class TestValidateRequiredKeys:
    def test_valid_config(self):
        _validate_required_keys(_make_valid_config())

    def test_missing_top_level_key(self):
        config = _make_valid_config()
        del config["retry"]
        with pytest.raises(KeyError, match="retry.max_attempts"):
            _validate_required_keys(config)
