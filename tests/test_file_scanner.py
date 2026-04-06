"""file_scanner のテスト"""

import os
import pytest

from openpyxl import Workbook

from aggregator.file_scanner import scan_target_files


def _make_config(tmp_path):
    folder_a = str(tmp_path / "collected")
    os.makedirs(folder_a, exist_ok=True)
    return {
        "paths": {"folder_a": folder_a},
        "files": {
            "file_list": "filelist.xlsx",
            "naming_pattern": "^.+\\.(xlsx|xlsm)$",
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
    }


def _create_file_list(path, rows):
    wb = Workbook()
    ws = wb.active
    ws.title = "一覧"
    # ヘッダー行
    ws.append(["ファイル名", "元ファイル名", "受信日時", "収集日時", "重複", "更新済", "振り分け", "備考"])
    for row in rows:
        ws.append(row)
    wb.save(path)
    wb.close()


class TestScanTargetFiles:
    def test_returns_unprocessed_files(self, tmp_path):
        config = _make_config(tmp_path)
        file_list_path = os.path.join(config["paths"]["folder_a"], config["files"]["file_list"])

        _create_file_list(file_list_path, [
            ["report.xlsx", "report.xlsx", None, None, 0, 0, "", ""],
            ["data.xlsx", "data.xlsx", None, None, 0, 1, "type_1", ""],  # 処理済み
            ["dup.xlsx", "dup.xlsx", None, None, 1, 0, "", ""],  # 重複
        ])

        targets = scan_target_files(config)
        assert len(targets) == 1
        assert targets[0]["filename"] == "report.xlsx"

    def test_filters_by_naming_pattern(self, tmp_path):
        config = _make_config(tmp_path)
        file_list_path = os.path.join(config["paths"]["folder_a"], config["files"]["file_list"])

        _create_file_list(file_list_path, [
            ["report.xlsx", "report.xlsx", None, None, 0, 0, "", ""],
            ["readme.txt", "readme.txt", None, None, 0, 0, "", ""],
        ])

        targets = scan_target_files(config)
        assert len(targets) == 1
        assert targets[0]["filename"] == "report.xlsx"

    def test_empty_list(self, tmp_path):
        config = _make_config(tmp_path)
        file_list_path = os.path.join(config["paths"]["folder_a"], config["files"]["file_list"])

        _create_file_list(file_list_path, [])
        targets = scan_target_files(config)
        assert len(targets) == 0

    def test_file_not_found(self, tmp_path):
        config = _make_config(tmp_path)
        targets = scan_target_files(config)
        assert targets == []
