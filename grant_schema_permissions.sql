-- ============================================================
-- スキーマ権限付与サンプル（ロールベース推奨）
-- 対象スキーマへの DML・DDL 権限をロール経由でユーザに付与する
-- ============================================================
-- 変数（実際の値に置き換えてください）
--   my_database  : 対象データベース名
--   my_schema    : 対象スキーマ名
--   my_warehouse : 使用するウェアハウス名
--   my_role      : 付与先ロール名
--   my_user      : 付与先ユーザ名
-- ============================================================

-- ロール作成（既存ロールに付与する場合はスキップ）
CREATE ROLE IF NOT EXISTS my_role;

-- ============================================================
-- アクセスの前提条件
-- ============================================================
GRANT USAGE ON DATABASE  my_database            TO ROLE my_role;
GRANT USAGE ON SCHEMA    my_database.my_schema  TO ROLE my_role;
GRANT USAGE ON WAREHOUSE my_warehouse           TO ROLE my_role;

-- ============================================================
-- DML 権限：既存オブジェクト
-- ============================================================
GRANT SELECT, INSERT, UPDATE, DELETE, TRUNCATE
    ON ALL TABLES  IN SCHEMA my_database.my_schema TO ROLE my_role;

GRANT SELECT
    ON ALL VIEWS   IN SCHEMA my_database.my_schema TO ROLE my_role;

GRANT SELECT
    ON ALL STREAMS IN SCHEMA my_database.my_schema TO ROLE my_role;

GRANT MONITOR, OPERATE
    ON ALL TASKS   IN SCHEMA my_database.my_schema TO ROLE my_role;

-- ============================================================
-- DML 権限：今後作成されるオブジェクト（FUTURE）
-- ============================================================
GRANT SELECT, INSERT, UPDATE, DELETE, TRUNCATE
    ON FUTURE TABLES  IN SCHEMA my_database.my_schema TO ROLE my_role;

GRANT SELECT
    ON FUTURE VIEWS   IN SCHEMA my_database.my_schema TO ROLE my_role;

GRANT SELECT
    ON FUTURE STREAMS IN SCHEMA my_database.my_schema TO ROLE my_role;

GRANT MONITOR, OPERATE
    ON FUTURE TASKS   IN SCHEMA my_database.my_schema TO ROLE my_role;

-- ============================================================
-- DDL 権限：スキーマ内でのオブジェクト作成
-- ============================================================
GRANT CREATE TABLE,
      CREATE VIEW,
      CREATE STAGE,
      CREATE STREAM,
      CREATE TASK,
      CREATE SEQUENCE,
      CREATE FUNCTION,
      CREATE PROCEDURE
    ON SCHEMA my_database.my_schema TO ROLE my_role;

-- ※ 自分が作成（所有）したオブジェクトは ALTER / DROP が自動的に可能
-- ※ 他ユーザ所有オブジェクトの ALTER / DROP が必要な場合は OWNERSHIP 移譲が必要
--    例: GRANT OWNERSHIP ON TABLE my_database.my_schema.my_table TO ROLE my_role;

-- ============================================================
-- ロールをユーザに付与
-- ============================================================
GRANT ROLE my_role TO USER my_user;
