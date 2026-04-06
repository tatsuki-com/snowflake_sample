"""Outlook COM操作（メール検索・添付取得）モジュール"""

import time
import logging
from datetime import datetime

import win32com.client
import pywintypes

logger = logging.getLogger("email_attachment_system")


def connect_outlook(retry_config: dict):
    """Outlookに接続し、Namespaceオブジェクトを返す。リトライ付き。"""
    max_attempts = retry_config["max_attempts"]
    wait_seconds = retry_config["wait_seconds"]

    for attempt in range(1, max_attempts + 1):
        try:
            outlook = win32com.client.Dispatch("Outlook.Application")
            namespace = outlook.GetNamespace("MAPI")
            logger.info("Outlook接続成功")
            return namespace
        except pywintypes.com_error as e:
            logger.warning(f"Outlook接続失敗 (試行 {attempt}/{max_attempts}): {e}")
            if attempt < max_attempts:
                time.sleep(wait_seconds)
            else:
                logger.error("Outlook接続に失敗しました。リトライ上限に達しました。")
                raise


def get_target_folder(namespace, folder_name: str):
    """指定名のOutlookフォルダを取得する。"""
    # 6 = olFolderInbox
    inbox = namespace.GetDefaultFolder(6)
    if folder_name == "受信トレイ":
        return inbox
    # サブフォルダを探索
    for folder in inbox.Folders:
        if folder.Name == folder_name:
            return folder
    raise ValueError(f"Outlookフォルダが見つかりません: {folder_name}")


def search_emails(folder, start_datetime: datetime, target_addresses: list) -> list:
    """指定日時以降のメールから、宛先が対象アドレスに該当するものを抽出する。"""
    start_str = start_datetime.strftime("%Y/%m/%d %H:%M")
    restriction = f"[ReceivedTime] >= '{start_str}'"
    items = folder.Items.Restrict(restriction)
    items.Sort("[ReceivedTime]", True)

    target_set = {addr.lower() for addr in target_addresses}
    result = []

    for item in items:
        try:
            if not hasattr(item, "Attachments"):
                continue
            recipients = _get_recipients(item)
            if recipients & target_set:
                result.append(item)
        except Exception as e:
            logger.warning(f"メール読み取りエラー: {e}")
            continue

    logger.info(f"対象メール {len(result)} 件を検出 (開始日時: {start_str})")
    return result


def get_attachments(mail_item, allowed_extensions: list) -> list:
    """メールから対象拡張子の添付ファイル情報を返す。"""
    attachments = []
    for i in range(1, mail_item.Attachments.Count + 1):
        att = mail_item.Attachments.Item(i)
        filename = att.FileName
        if any(filename.lower().endswith(ext.lower()) for ext in allowed_extensions):
            attachments.append(att)
    return attachments


def get_received_time(mail_item) -> datetime:
    """メールの受信日時を返す。"""
    return datetime(
        mail_item.ReceivedTime.year,
        mail_item.ReceivedTime.month,
        mail_item.ReceivedTime.day,
        mail_item.ReceivedTime.hour,
        mail_item.ReceivedTime.minute,
        mail_item.ReceivedTime.second,
    )


def _get_recipients(mail_item) -> set:
    """メールの宛先（To/CC）アドレスを小文字のセットで返す。"""
    addresses = set()
    for i in range(1, mail_item.Recipients.Count + 1):
        recip = mail_item.Recipients.Item(i)
        try:
            addr = recip.PropertyAccessor.GetProperty(
                "http://schemas.microsoft.com/mapi/proptag/0x39FE001E"
            )
            addresses.add(addr.lower())
        except Exception:
            if recip.Address:
                addresses.add(recip.Address.lower())
    return addresses
