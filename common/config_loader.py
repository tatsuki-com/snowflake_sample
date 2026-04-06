"""config.yaml 読み込み・必須キー検証モジュール"""

import os
import yaml


REQUIRED_KEYS = [
    ("outlook", "target_addresses"),
    ("outlook", "target_folder"),
    ("outlook", "attachment_extensions"),
    ("files", "file_list_path"),
    ("files", "naming_pattern"),
    ("files", "aggregation_targets"),
    ("paths_sheet", "name"),
    ("data_extraction", "datetime_sheet"),
    ("data_extraction", "datetime_cell"),
    ("data_extraction", "data_range"),
    ("data_extraction", "routing_cell"),
    ("file_list_sheet", "name"),
    ("file_list_sheet", "columns"),
    ("logging", "level"),
    ("logging", "file"),
    ("logging", "max_bytes"),
    ("logging", "backup_count"),
    ("retry", "max_attempts"),
    ("retry", "wait_seconds"),
]


def load_config(config_path: str = "config.yaml") -> dict:
    """設定ファイルを読み込み、必須キーの存在を検証して返す。"""
    config_path = os.path.abspath(config_path)
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"設定ファイルが見つかりません: {config_path}")

    with open(config_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    if config is None:
        raise ValueError("設定ファイルが空です")

    _validate_required_keys(config)
    return config


def _validate_required_keys(config: dict) -> None:
    """必須キーが存在するか検証する。"""
    missing = []
    for keys in REQUIRED_KEYS:
        current = config
        for key in keys:
            if not isinstance(current, dict) or key not in current:
                missing.append(".".join(keys))
                break
            current = current[key]

    if missing:
        raise KeyError(f"設定ファイルに必須キーがありません: {', '.join(missing)}")
