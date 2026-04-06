"""処理済ファイルのフォルダ移動モジュール"""

import os
import shutil
import logging
from datetime import datetime

logger = logging.getLogger("email_attachment_system")


def move_processed_file(filename: str, routing_type: str, config: dict) -> bool:
    """処理済みファイルをrouting_typeに対応するフォルダに移動する。

    移動先に同名ファイルが存在する場合はタイムスタンプ付きでリネームする。

    Returns:
        bool: 移動成功ならTrue
    """
    folder_a = config["paths"]["folder_a"]
    folders_move = config["paths"]["folders_move"]

    if routing_type not in folders_move:
        logger.error(f"不明なrouting_typeのため移動先が不明: {routing_type}")
        return False

    dest_folder = folders_move[routing_type]
    os.makedirs(dest_folder, exist_ok=True)

    src_path = os.path.join(folder_a, filename)
    dest_path = os.path.join(dest_folder, filename)

    if not os.path.exists(src_path):
        logger.error(f"移動元ファイルが見つかりません: {src_path}")
        return False

    if os.path.exists(dest_path):
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        name, ext = os.path.splitext(filename)
        new_filename = f"{name}_{timestamp}{ext}"
        dest_path = os.path.join(dest_folder, new_filename)
        logger.warning(f"移動先に同名ファイル存在のためリネーム: {filename} -> {new_filename}")

    try:
        shutil.move(src_path, dest_path)
        logger.info(f"ファイル移動完了: {filename} -> {dest_path}")
        return True
    except Exception as e:
        logger.error(f"ファイル移動失敗: {filename} - {e}")
        return False
