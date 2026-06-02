-- ============================================================
-- スキーマ権限付与サンプル（ロールベース推奨）
-- 対象スキーマへの DML・DDL 権限をロール経由でユーザに付与する
-- ============================================================

-- ============================================================
-- 変数定義（ここだけ書き換えて実行してください）
-- ============================================================
SET db_name        = 'my_database';
SET schema_name    = 'my_schema';
SET warehouse_name = 'my_warehouse';
SET role_name      = 'my_role';
SET user_name      = 'my_user';

-- 結合済み修飾名を生成
SET full_schema = $db_name || '.' || $schema_name;

-- ============================================================
-- ロール作成（既存ロールに付与する場合はスキップ）
-- ============================================================
EXECUTE IMMEDIATE
    'CREATE ROLE IF NOT EXISTS ' || $role_name;

-- ============================================================
-- アクセスの前提条件
-- ============================================================
EXECUTE IMMEDIATE
    'GRANT USAGE ON DATABASE ' || $db_name || ' TO ROLE ' || $role_name;
EXECUTE IMMEDIATE
    'GRANT USAGE ON SCHEMA ' || $full_schema || ' TO ROLE ' || $role_name;
EXECUTE IMMEDIATE
    'GRANT USAGE ON WAREHOUSE ' || $warehouse_name || ' TO ROLE ' || $role_name;

-- ============================================================
-- DML 権限：既存オブジェクト
-- ============================================================

-- テーブル
EXECUTE IMMEDIATE
    'GRANT SELECT, INSERT, UPDATE, DELETE, TRUNCATE ON ALL TABLES IN SCHEMA ' || $full_schema || ' TO ROLE ' || $role_name;

-- ビュー
EXECUTE IMMEDIATE
    'GRANT SELECT ON ALL VIEWS IN SCHEMA ' || $full_schema || ' TO ROLE ' || $role_name;

-- マテリアライズド・ビュー
EXECUTE IMMEDIATE
    'GRANT SELECT ON ALL MATERIALIZED VIEWS IN SCHEMA ' || $full_schema || ' TO ROLE ' || $role_name;

-- 動的テーブル（SELECT:参照 / OPERATE:手動リフレッシュ / MONITOR:状態確認）
EXECUTE IMMEDIATE
    'GRANT SELECT, OPERATE, MONITOR ON ALL DYNAMIC TABLES IN SCHEMA ' || $full_schema || ' TO ROLE ' || $role_name;

-- ストリーム
EXECUTE IMMEDIATE
    'GRANT SELECT ON ALL STREAMS IN SCHEMA ' || $full_schema || ' TO ROLE ' || $role_name;

-- タスク
EXECUTE IMMEDIATE
    'GRANT MONITOR, OPERATE ON ALL TASKS IN SCHEMA ' || $full_schema || ' TO ROLE ' || $role_name;

-- アラート（MONITOR:状態確認 / OPERATE:一時停止・再開）
EXECUTE IMMEDIATE
    'GRANT MONITOR, OPERATE ON ALL ALERTS IN SCHEMA ' || $full_schema || ' TO ROLE ' || $role_name;

-- ファイル・フォーマット（USAGE:クエリ・COPY で利用）
EXECUTE IMMEDIATE
    'GRANT USAGE ON ALL FILE FORMATS IN SCHEMA ' || $full_schema || ' TO ROLE ' || $role_name;

-- パイプ（MONITOR:状態確認 / OPERATE:一時停止・再開）
EXECUTE IMMEDIATE
    'GRANT MONITOR, OPERATE ON ALL PIPES IN SCHEMA ' || $full_schema || ' TO ROLE ' || $role_name;

-- タグ（APPLY:オブジェクトへのタグ付け）
EXECUTE IMMEDIATE
    'GRANT APPLY ON ALL TAGS IN SCHEMA ' || $full_schema || ' TO ROLE ' || $role_name;

-- ノートブック（USAGE:閲覧・実行）
EXECUTE IMMEDIATE
    'GRANT USAGE ON ALL NOTEBOOKS IN SCHEMA ' || $full_schema || ' TO ROLE ' || $role_name;

-- ============================================================
-- DML 権限：今後作成されるオブジェクト（FUTURE）
-- ============================================================

-- テーブル
EXECUTE IMMEDIATE
    'GRANT SELECT, INSERT, UPDATE, DELETE, TRUNCATE ON FUTURE TABLES IN SCHEMA ' || $full_schema || ' TO ROLE ' || $role_name;

-- ビュー
EXECUTE IMMEDIATE
    'GRANT SELECT ON FUTURE VIEWS IN SCHEMA ' || $full_schema || ' TO ROLE ' || $role_name;

-- マテリアライズド・ビュー
EXECUTE IMMEDIATE
    'GRANT SELECT ON FUTURE MATERIALIZED VIEWS IN SCHEMA ' || $full_schema || ' TO ROLE ' || $role_name;

-- 動的テーブル
EXECUTE IMMEDIATE
    'GRANT SELECT, OPERATE, MONITOR ON FUTURE DYNAMIC TABLES IN SCHEMA ' || $full_schema || ' TO ROLE ' || $role_name;

-- ストリーム
EXECUTE IMMEDIATE
    'GRANT SELECT ON FUTURE STREAMS IN SCHEMA ' || $full_schema || ' TO ROLE ' || $role_name;

-- タスク
EXECUTE IMMEDIATE
    'GRANT MONITOR, OPERATE ON FUTURE TASKS IN SCHEMA ' || $full_schema || ' TO ROLE ' || $role_name;

-- アラート
EXECUTE IMMEDIATE
    'GRANT MONITOR, OPERATE ON FUTURE ALERTS IN SCHEMA ' || $full_schema || ' TO ROLE ' || $role_name;

-- ファイル・フォーマット
EXECUTE IMMEDIATE
    'GRANT USAGE ON FUTURE FILE FORMATS IN SCHEMA ' || $full_schema || ' TO ROLE ' || $role_name;

-- パイプ
EXECUTE IMMEDIATE
    'GRANT MONITOR, OPERATE ON FUTURE PIPES IN SCHEMA ' || $full_schema || ' TO ROLE ' || $role_name;

-- タグ
EXECUTE IMMEDIATE
    'GRANT APPLY ON FUTURE TAGS IN SCHEMA ' || $full_schema || ' TO ROLE ' || $role_name;

-- ノートブック
EXECUTE IMMEDIATE
    'GRANT USAGE ON FUTURE NOTEBOOKS IN SCHEMA ' || $full_schema || ' TO ROLE ' || $role_name;

-- ============================================================
-- DDL 権限：スキーマ内でのオブジェクト作成
-- ============================================================
EXECUTE IMMEDIATE
    'GRANT CREATE TABLE,
           CREATE VIEW,
           CREATE MATERIALIZED VIEW,
           CREATE DYNAMIC TABLE,
           CREATE STAGE,
           CREATE STREAM,
           CREATE TASK,
           CREATE ALERT,
           CREATE FILE FORMAT,
           CREATE PIPE,
           CREATE TAG,
           CREATE NOTEBOOK,
           CREATE SEQUENCE,
           CREATE FUNCTION,
           CREATE PROCEDURE
       ON SCHEMA ' || $full_schema || ' TO ROLE ' || $role_name;

-- ※ 自分が作成（所有）したオブジェクトは ALTER / DROP が自動的に可能
-- ※ 他ユーザ所有オブジェクトの ALTER / DROP が必要な場合は OWNERSHIP 移譲が必要
--    例: EXECUTE IMMEDIATE 'GRANT OWNERSHIP ON TABLE ' || $full_schema || '.target_table TO ROLE ' || $role_name;

-- ============================================================
-- ロールをユーザに付与
-- ============================================================
EXECUTE IMMEDIATE
    'GRANT ROLE ' || $role_name || ' TO USER ' || $user_name;
