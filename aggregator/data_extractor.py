"""_get_datetime シート/セル値取得モジュール"""

import os
import logging

from common.excel_utils import open_workbook, get_sheet, read_cell, col_letter_to_index

logger = logging.getLogger("email_attachment_system")


def extract_data(filepath: str, config: dict) -> dict | None:
    """対象ファイルから集約に必要なデータを取得する。

    Returns:
        dict: 抽出データ。取得できない場合は None。
            - received_datetime: 受信日時
            - data_values: B10〜B20の値リスト
            - routing_type: 振り分け判定キー
    """
    extraction = config["data_extraction"]
    datetime_sheet_name = extraction["datetime_sheet"]
    datetime_cell = extraction["datetime_cell"]
    data_range = extraction["data_range"]
    routing_cell = extraction["routing_cell"]

    if not os.path.exists(filepath):
        logger.error(f"ファイルが見つかりません: {filepath}")
        return None

    try:
        wb = open_workbook(filepath, read_only=True)
    except Exception as e:
        logger.error(f"ファイルを開けません: {filepath} - {e}")
        return None

    # _get_datetimeシートから受信日時を取得
    dt_sheet = get_sheet(wb, datetime_sheet_name)
    if dt_sheet is None:
        logger.warning(f"_get_datetimeシートが存在しません: {filepath}")
        wb.close()
        return None

    received_datetime = read_cell(dt_sheet, datetime_cell)

    # データ範囲(B10〜B20)の値を取得
    col = data_range["column"]
    start_row = data_range["start_row"]
    end_row = data_range["end_row"]
    col_idx = col_letter_to_index(col)

    data_values = []
    for row in range(start_row, end_row + 1):
        cell_value = dt_sheet.cell(row=row, column=col_idx).value
        data_values.append(cell_value)

    # メインシートからrouting_typeを取得 (B11)
    main_sheet = wb.worksheets[0]
    routing_type = read_cell(main_sheet, routing_cell)

    wb.close()

    if routing_type is None or str(routing_type).strip() == "":
        logger.warning(f"振り分けセル({routing_cell})が空です: {filepath}")
        return None

    routing_type = str(routing_type).strip()

    return {
        "received_datetime": received_datetime,
        "data_values": data_values,
        "routing_type": routing_type,
    }
