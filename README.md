# メール添付ファイル収集・集約システム

## 概要

Outlookから指定アドレス宛のメール添付ファイルを自動収集し、ファイル内のセル値に応じて集約ファイルへ追記・振り分けするPythonシステム。
**ファイル一覧.xlsm** を管理台帳として、収集状態・処理状態・フォルダパス設定を一元管理する。

## 前提条件

- **OS**: Windows（Outlook COM操作のため Windows 専用）
- **Python**: 3.10 以上
- **Outlook**: Microsoft Outlook デスクトップ版がインストール・起動済みであること
- **実行方式**: 手動起動のみ（スケジューラ実行は対象外）
- **排他制御**: なし（複数人が同時に処理を起動する想定はしない）

## セットアップ

```bash
pip install openpyxl pywin32 pyyaml
```

## ディレクトリ構成

```
project/
├── config.yaml              # 全パラメータの外出し設定
├── main.py                  # CLIエントリーポイント
├── vba_caller.py            # VBA連携用（xlsmボタンから呼び出すサンプル含む）
├── README.md
├── .gitignore
├── collector/               # ファイル収集処理
│   ├── outlook_client.py    # Outlook COM操作（メール検索・添付取得）
│   ├── file_saver.py        # 添付ファイル保存・重複検知・リネーム
│   └── list_updater.py      # ファイル一覧.xlsm 追記/フラグ更新
├── aggregator/              # ファイル集約処理
│   ├── file_scanner.py      # 一覧から対象ファイル抽出
│   ├── data_extractor.py    # _get_datetime シート/セル値取得
│   ├── file_writer.py       # 集約ファイル(α/β/γ)への追記
│   └── file_mover.py        # 処理済ファイルのフォルダ移動
├── common/                  # 共通モジュール
│   ├── config_loader.py     # config.yaml読み込み・必須キー検証
│   ├── paths_loader.py      # ファイル一覧.xlsmの設定シートからパス定義を読み込み
│   ├── logger.py            # ロガー設定（ローテーション付き）
│   └── excel_utils.py       # openpyxl共通操作
├── tests/                   # ユニットテスト
│   ├── test_config_loader.py
│   ├── test_paths_loader.py
│   ├── test_logger.py
│   ├── test_excel_utils.py
│   ├── test_file_saver.py
│   ├── test_list_updater.py
│   ├── test_file_scanner.py
│   ├── test_data_extractor.py
│   ├── test_file_writer.py
│   └── test_file_mover.py
└── logs/                    # ログ出力先
```

## 使い方

### CLI から実行

```bash
# ファイル収集（開始日時以降のメールを処理）
python main.py collect --start "2026-04-01 09:00:00"

# ファイル集約
python main.py aggregate

# 設定ファイルを明示指定
python main.py collect --start "2026-04-01 09:00:00" --config ./config.yaml
```

### テストの実行

```bash
pip install pytest
python -m pytest tests/ -v
```

### ファイル一覧.xlsm のボタンから実行

`vba_caller.py` 内にVBAサンプルコードを記載しています。xlsm にボタンを2つ配置し、以下のマクロを割り当ててください。

| ボタン | 呼び出すマクロ | 動作 |
|---|---|---|
| 収集ボタン | `RunCollect` | 開始日時セルの値を引数にPythonのcollectを起動 |
| 集約ボタン | `RunAggregate` | Pythonのaggregateを起動 |

VBAからは `Shell` で `python main.py ...` を実行する最もシンプルな方式を採用しています。

## ファイル仕様

### ファイル一覧.xlsm のシート構成

ファイル一覧.xlsm には以下の2つのシートが必要です。

#### 設定シート（パス定義）

シート名: **設定**（config.yamlの `paths_sheet.name` で変更可能）

フォルダパスの定義を一元管理するシートです。`folder_a` と `folder_b` は必須項目です。それ以外の行は routing_type に対応する処理済みファイルの移動先フォルダとして扱われます。

| A (項目) | B (パス) |
|---|---|
| folder_a | ./collected |
| folder_b | ./aggregated |
| type_1 | ./completed/D |
| type_2 | ./completed/E |
| type_3 | ./completed/F |

| 項目キー | 説明 |
|---|---|
| `folder_a` | **必須** 添付ファイル保存先（フォルダA） |
| `folder_b` | **必須** 集約ファイル配置先（フォルダB） |
| その他 | routing_type に対応する処理済みファイルの移動先フォルダ |

#### 一覧シート（収集・集約管理台帳）

シート名: **一覧**（config.yamlの `file_list_sheet.name` で変更可能）

| 列 | 項目 | 説明 |
|---|---|---|
| A | ファイル名 | フォルダA上の実ファイル名（リネーム後の名前） |
| B | 元ファイル名 | リネーム前のオリジナルファイル名 |
| C | メール受信日時 | Outlookから取得した受信日時 |
| D | 収集処理日時 | 本システムで保存した日時 |
| E | 重複フラグ | 0=通常、1=重複によりリネーム保存 |
| F | 更新済みフラグ | 0=未処理、1=集約済み |
| G | 振り分け先 | 集約処理で判定された routing_type |
| H | 備考 | 重複時のメッセージ等 |

### 収集対象ファイル内の _get_datetime シート

収集処理が各添付ファイルに自動追加するシート。集約処理時に参照する。

| セル | 内容 | 設定者 |
|---|---|---|
| A1 | メール受信日時 | 収集処理が記入 |
| B10〜B20 | 集約対象データ | 業務側で記入（既存仕様） |
| B11 | 振り分け判定キー | 業務側で記入（routing_type） |

## 処理フロー詳細

### 1. ファイル収集

1. **起動**: ファイル一覧.xlsm の収集ボタン押下、または CLI で `python main.py collect --start "YYYY-MM-DD HH:MM:SS"` を実行
2. **パス読み込み**: ファイル一覧.xlsm の設定シートからフォルダパスを取得
3. **メール検索**: Outlook受信トレイから、指定開始日時以降に届いた、宛先が `outlook.target_addresses` のいずれかに該当するメールを抽出
4. **添付取得**: `outlook.attachment_extensions` に該当する拡張子の添付ファイルのみ収集
5. **フォルダAに保存**:
   - 同名ファイルが既に存在しない場合 → そのまま保存
   - 同名ファイルが存在する場合 → WARNINGログを出力し、`<元ファイル名>_<YYYYMMDDHHMMSS>.xlsx` にリネームして保存
6. **_get_datetime シート追加**: 保存したファイルにシートを追加し、A1セルにメール受信日時を記録
7. **ファイル一覧.xlsm に追記**:
   - リネームされた場合はリネーム後の名前で記載
   - 重複リネームされたレコードは E列の重複フラグ = 1
   - F列の更新済みフラグ = 0（未処理）

### 2. ファイル集約

1. **起動**: ファイル一覧.xlsm の集約ボタン押下、または CLI で `python main.py aggregate` を実行
2. **パス読み込み**: ファイル一覧.xlsm の設定シートからフォルダパスを取得
3. **対象ファイル抽出**: ファイル一覧から以下の条件をすべて満たすレコードを抽出
   - 更新済みフラグ (F列) = 0
   - 重複フラグ (E列) = 0
   - ファイル名が `files.naming_pattern` の正規表現に一致
4. **データ取得**: 各ファイルから以下を取得
   - `_get_datetime!A1` … 受信日時
   - `_get_datetime!B10〜B20` … 集約データ
   - メインシートの `B11` … 振り分け判定キー（routing_type）
5. **集約ファイルへ追記**: routing_type の値に基づいて、フォルダB配下の集約ファイル（α/β/γ）の最終行の次の行に追記
6. **処理済ファイル移動**: 処理が完了したファイルを routing_type に対応するフォルダに移動
   - 移動先に同名ファイルがある場合 → タイムスタンプ付きでリネーム
7. **フラグ更新**: ファイル一覧の F列に 1（更新済み）、G列に routing_type を記録

### 振り分けマッピング例

ファイル一覧.xlsm の設定シートおよび config.yaml の設定に基づき、B11 セルの値で以下のように振り分けられます。

| B11 の値 (routing_type) | 集約先ファイル | 移動先フォルダ |
|---|---|---|
| type_1 | フォルダB / alpha.xlsx | ./completed/D |
| type_2 | フォルダB / beta.xlsx | ./completed/E |
| type_3 | フォルダB / gamma.xlsx | ./completed/F |

- **集約先ファイル名** の対応は config.yaml の `files.aggregation_targets` で定義
- **移動先フォルダ** の対応はファイル一覧.xlsm の設定シートで定義

## 設定ファイル（config.yaml）

| セクション | キー | 説明 |
|---|---|---|
| `outlook` | `target_addresses` | 収集対象の宛先メールアドレス（複数可） |
| `outlook` | `target_folder` | 検索対象のOutlookフォルダ（既定: 受信トレイ） |
| `outlook` | `attachment_extensions` | 収集対象の拡張子リスト |
| `files` | `file_list_path` | ファイル一覧.xlsm のファイルパス |
| `files` | `naming_pattern` | 集約対象ファイルの命名規則（正規表現） |
| `files` | `aggregation_targets` | routing_type → 集約ファイル名のマッピング |
| `paths_sheet` | `name` | ファイル一覧.xlsm 内のパス定義シート名（既定: 設定） |
| `data_extraction` | `datetime_sheet` | 受信日時記録シート名（既定: _get_datetime） |
| `data_extraction` | `datetime_cell` | 受信日時セル（既定: A1） |
| `data_extraction` | `data_range` | 集約データ範囲（列・開始行・終了行） |
| `data_extraction` | `routing_cell` | 振り分け判定セル（既定: B11） |
| `file_list_sheet` | `name` | ファイル一覧の管理台帳シート名（既定: 一覧） |
| `file_list_sheet` | `columns` | ファイル一覧の各カラム位置 |
| `logging` | `level, file, max_bytes, backup_count` | ログ設定 |
| `retry` | `max_attempts, wait_seconds` | Outlook接続リトライ設定 |

> **注**: フォルダパス（folder_a, folder_b, 移動先フォルダ）は config.yaml ではなく、ファイル一覧.xlsm の設定シートで管理します。

## エラーハンドリング方針

| 事象 | 動作 |
|---|---|
| Outlook接続失敗 | 設定回数リトライ後、ERRORログを出力して中断 |
| 添付ファイル保存失敗 | ERRORログを出力し、当該ファイルのみスキップ |
| 同名ファイル存在 | WARNINGログ＋タイムスタンプでリネーム保存（処理は継続） |
| _get_datetimeシート不在 | WARNINGログ＋当該ファイルをスキップ |
| 振り分けセル(B11)が空 | WARNINGログ＋当該ファイルをスキップ |
| 不明なrouting_type | ERRORログ＋当該ファイルをスキップ（一覧フラグは更新しない） |
| 集約ファイル(α/β/γ)不在 | 自動で新規作成（ヘッダー付き） |
| 移動先に同名ファイル存在 | WARNINGログ＋タイムスタンプでリネーム移動 |
| 設定シート不在 | エラーを出力して処理を中断 |
| 設定シートに folder_a/folder_b 未定義 | エラーを出力して処理を中断 |

処理結果は最後にサマリー（成功/スキップ/エラー件数）としてログ出力されます。

## ログ

- **出力先**: `./logs/process.log`
- **ローテーション**: 既定 10MB × 5世代
- **レベル**: 既定 INFO（config.yamlで変更可能）
- コンソールとファイルの両方に出力

## テスト

```bash
python -m pytest tests/ -v
```

全51テストケースで以下のモジュールをカバーしています。

| テストファイル | 対象モジュール | テスト数 |
|---|---|---|
| `test_config_loader.py` | config.yaml読み込み・検証 | 6 |
| `test_paths_loader.py` | 設定シートからのパス読み込み | 7 |
| `test_logger.py` | ロガー設定 | 3 |
| `test_excel_utils.py` | openpyxl共通操作 | 11 |
| `test_file_saver.py` | 添付ファイル保存・重複リネーム | 4 |
| `test_list_updater.py` | ファイル一覧追記・フラグ更新 | 3 |
| `test_file_scanner.py` | 対象ファイル抽出 | 4 |
| `test_data_extractor.py` | データ取得 | 5 |
| `test_file_writer.py` | 集約ファイル書き込み | 3 |
| `test_file_mover.py` | ファイル移動 | 5 |

> **注**: `outlook_client.py` はOutlook COM (`win32com`) に依存するため、Linux環境ではテスト対象外です。

## 制約事項

- **Windows専用**: Outlook COM (win32com) を使用するため Linux/macOS では動作しません
- **Outlook起動必須**: 実行時にOutlookデスクトップ版が起動している必要があります
- **手動起動のみ**: タスクスケジューラ等の自動起動は対象外
- **排他制御なし**: ファイル一覧.xlsm を同時に複数プロセスから操作することは想定していません
- **ファイル種別**: 集約対象は Excel ファイル（.xlsx/.xlsm）を想定。他形式は _get_datetime シート追加でエラーになります
