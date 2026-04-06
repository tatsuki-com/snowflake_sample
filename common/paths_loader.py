"""ファイル一覧.xlsm の設定シートからフォルダパス定義を読み込むモジュール"""

import logging
import os

from common.excel_utils import open_workbook, get_sheet

logger = logging.getLogger("email_attachment_system")

RESERVED_KEYS = {"folder_a", "folder_b"}


def load_paths_from_file_list(config: dict) -> dict:
    """ファイル一覧.xlsmの設定シートからパス定義を読み込み、config["paths"]として返す。

    設定シートのレイアウト:
        A列: 項目キー (folder_a, folder_b, または routing_type名)
        B列: フォルダパス

    Returns:
        dict: paths辞書
            - folder_a: 添付ファイル保存先
            - folder_b: 集約ファイル配置先
            - folders_move: {routing_type: 移動先パス} のマッピング
    """
    file_list_path = config["files"]["file_list_path"]
    sheet_name = config["paths_sheet"]["name"]

    if not os.path.exists(file_list_path):
        raise FileNotFoundError(f"ファイル一覧が見つかりません: {file_list_path}")

    wb = open_workbook(file_list_path, read_only=True)
    ws = get_sheet(wb, sheet_name)

    if ws is None:
        wb.close()
        raise ValueError(
            f"ファイル一覧に設定シート '{sheet_name}' が存在しません"
        )

    paths = {"folders_move": {}}

    for row in ws.iter_rows(min_row=2):  # ヘッダー行をスキップ
        key = row[0].value
        value = row[1].value

        if key is None or value is None:
            continue

        key = str(key).strip()
        value = str(value).strip()

        if key in RESERVED_KEYS:
            paths[key] = value
        else:
            paths["folders_move"][key] = value

    wb.close()

    # 必須キーの検証
    for required in RESERVED_KEYS:
        if required not in paths:
            raise KeyError(
                f"設定シートに必須キーがありません: {required}"
            )

    if not paths["folders_move"]:
        logger.warning("設定シートに移動先フォルダの定義がありません")

    logger.info(
        f"パス設定を読み込みました: folder_a={paths['folder_a']}, "
        f"folder_b={paths['folder_b']}, "
        f"移動先={len(paths['folders_move'])}件"
    )
    return paths
