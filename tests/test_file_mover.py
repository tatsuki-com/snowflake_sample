"""file_mover のテスト"""

import os
import pytest

from openpyxl import Workbook

from aggregator.file_mover import move_processed_file


def _make_config(tmp_path):
    folder_a = str(tmp_path / "collected")
    os.makedirs(folder_a, exist_ok=True)
    return {
        "paths": {
            "folder_a": folder_a,
            "folders_move": {
                "type_1": str(tmp_path / "completed" / "D"),
                "type_2": str(tmp_path / "completed" / "E"),
            },
        },
    }


def _create_dummy_file(folder, filename):
    filepath = os.path.join(folder, filename)
    wb = Workbook()
    wb.save(filepath)
    wb.close()
    return filepath


class TestMoveProcessedFile:
    def test_move_file(self, tmp_path):
        config = _make_config(tmp_path)
        _create_dummy_file(config["paths"]["folder_a"], "report.xlsx")

        result = move_processed_file("report.xlsx", "type_1", config)
        assert result is True

        dest = os.path.join(config["paths"]["folders_move"]["type_1"], "report.xlsx")
        assert os.path.exists(dest)
        assert not os.path.exists(os.path.join(config["paths"]["folder_a"], "report.xlsx"))

    def test_move_with_duplicate_at_dest(self, tmp_path):
        config = _make_config(tmp_path)
        _create_dummy_file(config["paths"]["folder_a"], "report.xlsx")

        # 移動先に同名ファイルを事前作成
        dest_folder = config["paths"]["folders_move"]["type_1"]
        os.makedirs(dest_folder, exist_ok=True)
        _create_dummy_file(dest_folder, "report.xlsx")

        result = move_processed_file("report.xlsx", "type_1", config)
        assert result is True

        # リネームされたファイルが存在する
        files = os.listdir(dest_folder)
        assert len(files) == 2
        renamed = [f for f in files if f.startswith("report_")]
        assert len(renamed) == 1

    def test_unknown_routing_type(self, tmp_path):
        config = _make_config(tmp_path)
        _create_dummy_file(config["paths"]["folder_a"], "report.xlsx")

        result = move_processed_file("report.xlsx", "unknown", config)
        assert result is False

    def test_source_file_not_found(self, tmp_path):
        config = _make_config(tmp_path)
        result = move_processed_file("nonexistent.xlsx", "type_1", config)
        assert result is False
