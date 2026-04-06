"""paths_loader のテスト"""

import os
import pytest

from openpyxl import Workbook

from common.paths_loader import load_paths_from_file_list


def _make_config(file_list_path):
    return {
        "files": {"file_list_path": file_list_path},
        "paths_sheet": {"name": "設定"},
    }


def _create_file_list_with_paths(filepath, rows):
    wb = Workbook()
    ws = wb.active
    ws.title = "設定"
    ws.append(["項目", "パス"])
    for row in rows:
        ws.append(row)
    wb.save(filepath)
    wb.close()


class TestLoadPathsFromFileList:
    def test_loads_all_paths(self, tmp_path):
        filepath = str(tmp_path / "filelist.xlsx")
        _create_file_list_with_paths(filepath, [
            ["folder_a", "./collected"],
            ["folder_b", "./aggregated"],
            ["type_1", "./completed/D"],
            ["type_2", "./completed/E"],
        ])

        config = _make_config(filepath)
        paths = load_paths_from_file_list(config)

        assert paths["folder_a"] == "./collected"
        assert paths["folder_b"] == "./aggregated"
        assert paths["folders_move"]["type_1"] == "./completed/D"
        assert paths["folders_move"]["type_2"] == "./completed/E"

    def test_missing_folder_a(self, tmp_path):
        filepath = str(tmp_path / "filelist.xlsx")
        _create_file_list_with_paths(filepath, [
            ["folder_b", "./aggregated"],
            ["type_1", "./completed/D"],
        ])

        config = _make_config(filepath)
        with pytest.raises(KeyError, match="folder_a"):
            load_paths_from_file_list(config)

    def test_missing_folder_b(self, tmp_path):
        filepath = str(tmp_path / "filelist.xlsx")
        _create_file_list_with_paths(filepath, [
            ["folder_a", "./collected"],
            ["type_1", "./completed/D"],
        ])

        config = _make_config(filepath)
        with pytest.raises(KeyError, match="folder_b"):
            load_paths_from_file_list(config)

    def test_file_not_found(self, tmp_path):
        config = _make_config(str(tmp_path / "nonexistent.xlsx"))
        with pytest.raises(FileNotFoundError):
            load_paths_from_file_list(config)

    def test_missing_settings_sheet(self, tmp_path):
        filepath = str(tmp_path / "filelist.xlsx")
        wb = Workbook()
        wb.save(filepath)
        wb.close()

        config = _make_config(filepath)
        with pytest.raises(ValueError, match="設定シート"):
            load_paths_from_file_list(config)

    def test_skips_empty_rows(self, tmp_path):
        filepath = str(tmp_path / "filelist.xlsx")
        _create_file_list_with_paths(filepath, [
            ["folder_a", "./collected"],
            [None, None],
            ["folder_b", "./aggregated"],
            ["", ""],
        ])

        config = _make_config(filepath)
        paths = load_paths_from_file_list(config)
        assert paths["folder_a"] == "./collected"
        assert paths["folder_b"] == "./aggregated"
        assert len(paths["folders_move"]) == 0

    def test_no_move_folders(self, tmp_path):
        filepath = str(tmp_path / "filelist.xlsx")
        _create_file_list_with_paths(filepath, [
            ["folder_a", "./collected"],
            ["folder_b", "./aggregated"],
        ])

        config = _make_config(filepath)
        paths = load_paths_from_file_list(config)
        assert paths["folders_move"] == {}
