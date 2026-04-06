"""CLIエントリーポイント"""

import argparse
import os
import sys
from datetime import datetime

from common.config_loader import load_config
from common.logger import setup_logger


def run_collect(config: dict, start_datetime: datetime) -> None:
    """ファイル収集処理を実行する。"""
    from collector.outlook_client import (
        connect_outlook,
        get_target_folder,
        search_emails,
        get_attachments,
        get_received_time,
    )
    from collector.file_saver import save_attachment
    from collector.list_updater import append_to_file_list

    logger = setup_logger(config)
    logger.info("=" * 60)
    logger.info("ファイル収集処理を開始")
    logger.info(f"開始日時: {start_datetime}")

    outlook_config = config["outlook"]
    success_count = 0
    skip_count = 0
    error_count = 0

    try:
        namespace = connect_outlook(config["retry"])
    except Exception:
        logger.error("Outlook接続に失敗したため処理を中断します。")
        return

    try:
        folder = get_target_folder(namespace, outlook_config["target_folder"])
    except Exception as e:
        logger.error(f"Outlookフォルダ取得失敗: {e}")
        return

    emails = search_emails(
        folder, start_datetime, outlook_config["target_addresses"]
    )

    for mail in emails:
        attachments = get_attachments(mail, outlook_config["attachment_extensions"])
        received_time = get_received_time(mail)

        for att in attachments:
            try:
                file_info = save_attachment(
                    att,
                    config["paths"]["folder_a"],
                    received_time,
                    config["data_extraction"]["datetime_sheet"],
                )
                append_to_file_list(file_info, config)
                success_count += 1
            except Exception as e:
                logger.error(f"添付ファイル処理エラー: {att.FileName} - {e}")
                error_count += 1

    logger.info("=" * 60)
    logger.info(
        f"ファイル収集完了 - 成功: {success_count}, "
        f"スキップ: {skip_count}, エラー: {error_count}"
    )


def run_aggregate(config: dict) -> None:
    """ファイル集約処理を実行する。"""
    from aggregator.file_scanner import scan_target_files
    from aggregator.data_extractor import extract_data
    from aggregator.file_writer import write_to_aggregation_file
    from aggregator.file_mover import move_processed_file
    from collector.list_updater import update_flags

    logger = setup_logger(config)
    logger.info("=" * 60)
    logger.info("ファイル集約処理を開始")

    success_count = 0
    skip_count = 0
    error_count = 0

    targets = scan_target_files(config)

    for target in targets:
        filename = target["filename"]
        filepath = os.path.join(config["paths"]["folder_a"], filename)

        # データ抽出
        data = extract_data(filepath, config)
        if data is None:
            skip_count += 1
            continue

        routing_type = data["routing_type"]

        # routing_type の妥当性チェック
        if routing_type not in config["files"]["aggregation_targets"]:
            logger.error(f"不明なrouting_type '{routing_type}': {filename}")
            error_count += 1
            continue

        # 集約ファイルへ追記
        if not write_to_aggregation_file(data, config):
            error_count += 1
            continue

        # 処理済みファイル移動
        if not move_processed_file(filename, routing_type, config):
            error_count += 1
            continue

        # フラグ更新
        try:
            update_flags(filename, routing_type, config)
            success_count += 1
        except Exception as e:
            logger.error(f"フラグ更新エラー: {filename} - {e}")
            error_count += 1

    logger.info("=" * 60)
    logger.info(
        f"ファイル集約完了 - 成功: {success_count}, "
        f"スキップ: {skip_count}, エラー: {error_count}"
    )


def main():
    parser = argparse.ArgumentParser(
        description="メール添付ファイル収集・集約システム"
    )
    subparsers = parser.add_subparsers(dest="command", help="実行するコマンド")

    # collect サブコマンド
    collect_parser = subparsers.add_parser("collect", help="ファイル収集")
    collect_parser.add_argument(
        "--start",
        required=True,
        help="収集開始日時 (YYYY-MM-DD HH:MM:SS)",
    )
    collect_parser.add_argument(
        "--config",
        default="config.yaml",
        help="設定ファイルパス (既定: config.yaml)",
    )

    # aggregate サブコマンド
    aggregate_parser = subparsers.add_parser("aggregate", help="ファイル集約")
    aggregate_parser.add_argument(
        "--config",
        default="config.yaml",
        help="設定ファイルパス (既定: config.yaml)",
    )

    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        sys.exit(1)

    config = load_config(args.config)

    if args.command == "collect":
        try:
            start_datetime = datetime.strptime(args.start, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            print("エラー: --start は 'YYYY-MM-DD HH:MM:SS' 形式で指定してください。")
            sys.exit(1)
        run_collect(config, start_datetime)

    elif args.command == "aggregate":
        run_aggregate(config)


if __name__ == "__main__":
    main()
