"""集約ファイル(α/β/γ)への追記モジュール"""

import os
import logging

from common.excel_utils import get_or_create_workbook, get_next_row

logger = logging.getLogger("email_attachment_system")

HEADER_ROW = ["受信日時", "B10", "B11", "B12", "B13", "B14", "B15",
              "B16", "B17", "B18", "B19", "B20"]


def write_to_aggregation_file(data: dict, config: dict) -> bool:
    """routing_typeに対応する集約ファイルにデータを追記する。

    Args:
        data: extract_dataで取得したデータ
        config: 設定辞書

    Returns:
        bool: 書き込み成功ならTrue
    """
    routing_type = data["routing_type"]
    aggregation_targets = config["files"]["aggregation_targets"]
    folder_b = config["paths"]["folder_b"]

    if routing_type not in aggregation_targets:
        logger.error(f"不明なrouting_type: {routing_type}")
        return False

    target_filename = aggregation_targets[routing_type]
    target_path = os.path.join(folder_b, target_filename)
    os.makedirs(folder_b, exist_ok=True)

    wb = get_or_create_workbook(target_path)
    ws = wb.active

    # 新規ファイルの場合はヘッダーを追加
    if ws.max_row == 1 and ws.cell(row=1, column=1).value is None:
        for col_idx, header in enumerate(HEADER_ROW, start=1):
            ws.cell(row=1, column=col_idx, value=header)
        logger.info(f"集約ファイル新規作成（ヘッダー付き）: {target_filename}")

    next_row = get_next_row(ws)

    # 受信日時
    ws.cell(row=next_row, column=1, value=data["received_datetime"])

    # B10〜B20の値
    for i, value in enumerate(data["data_values"]):
        ws.cell(row=next_row, column=2 + i, value=value)

    wb.save(target_path)
    wb.close()
    logger.info(f"集約ファイルに追記: {target_filename} (行 {next_row})")
    return True
