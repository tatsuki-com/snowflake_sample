"""ファイル一覧.xlsm 追記/フラグ更新モジュール"""

import logging

from common.excel_utils import (
    get_or_create_workbook,
    get_or_create_sheet,
    get_next_row,
    write_cell,
)

logger = logging.getLogger("email_attachment_system")


def append_to_file_list(file_info: dict, config: dict) -> None:
    """ファイル一覧.xlsmに収集結果を1行追記する。"""
    file_list_path = config["files"]["file_list_path"]
    sheet_name = config["file_list_sheet"]["name"]
    columns = config["file_list_sheet"]["columns"]

    wb = get_or_create_workbook(file_list_path, keep_vba=True)
    ws = get_or_create_sheet(wb, sheet_name)
    row = get_next_row(ws)

    write_cell(ws, row, columns["filename"], file_info["filename"])
    write_cell(ws, row, columns["original_filename"], file_info["original_filename"])
    write_cell(ws, row, columns["received_datetime"], file_info["received_datetime"])
    write_cell(ws, row, columns["collected_datetime"], file_info["collected_datetime"])
    write_cell(ws, row, columns["duplicate_flag"], 1 if file_info["is_duplicate"] else 0)
    write_cell(ws, row, columns["updated_flag"], 0)
    write_cell(ws, row, columns["routing_type"], "")
    write_cell(ws, row, columns["remarks"], file_info.get("remarks", ""))

    wb.save(file_list_path)
    wb.close()
    logger.info(f"ファイル一覧に追記: {file_info['filename']} (行 {row})")


def update_flags(filename: str, routing_type: str, config: dict) -> None:
    """ファイル一覧のF列(更新済みフラグ)=1、G列(振り分け先)を更新する。"""
    file_list_path = config["files"]["file_list_path"]
    sheet_name = config["file_list_sheet"]["name"]
    columns = config["file_list_sheet"]["columns"]

    wb = get_or_create_workbook(file_list_path, keep_vba=True)
    ws = wb[sheet_name]

    filename_col = columns["filename"]
    updated_col = columns["updated_flag"]
    routing_col = columns["routing_type"]

    for row in range(1, ws.max_row + 1):
        cell_value = ws[f"{filename_col}{row}"].value
        if cell_value == filename:
            write_cell(ws, row, updated_col, 1)
            write_cell(ws, row, routing_col, routing_type)
            logger.info(f"フラグ更新: {filename} -> 更新済み=1, 振り分け先={routing_type}")
            break

    wb.save(file_list_path)
    wb.close()
