"""一覧から対象ファイル抽出モジュール"""

import os
import re
import logging

from common.excel_utils import open_workbook, col_letter_to_index

logger = logging.getLogger("email_attachment_system")


def scan_target_files(config: dict) -> list:
    """ファイル一覧から集約対象のファイルレコードを抽出する。

    条件:
      - 更新済みフラグ (F列) = 0
      - 重複フラグ (E列) = 0
      - ファイル名が naming_pattern に一致

    Returns:
        list[dict]: 対象ファイルのリスト
    """
    file_list_path = os.path.join(
        config["paths"]["folder_a"], config["files"]["file_list"]
    )
    sheet_name = config["file_list_sheet"]["name"]
    columns = config["file_list_sheet"]["columns"]
    naming_pattern = re.compile(config["files"]["naming_pattern"])

    if not os.path.exists(file_list_path):
        logger.error(f"ファイル一覧が見つかりません: {file_list_path}")
        return []

    wb = open_workbook(file_list_path, read_only=True)
    ws = wb[sheet_name]

    filename_col = col_letter_to_index(columns["filename"])
    duplicate_col = col_letter_to_index(columns["duplicate_flag"])
    updated_col = col_letter_to_index(columns["updated_flag"])

    targets = []
    for row in ws.iter_rows(min_row=2):  # ヘッダー行をスキップ
        filename = row[filename_col - 1].value
        if filename is None:
            continue

        duplicate_flag = row[duplicate_col - 1].value
        updated_flag = row[updated_col - 1].value

        if updated_flag != 0:
            continue
        if duplicate_flag != 0:
            continue
        if not naming_pattern.match(filename):
            continue

        targets.append({
            "filename": filename,
            "row_number": row[0].row,
        })

    wb.close()
    logger.info(f"集約対象ファイル: {len(targets)} 件")
    return targets
