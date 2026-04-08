-- ============================================================
-- アクセスロール定義
-- 対象データベース: α
-- ============================================================

-- ============================================================
-- 1. データベースレベル アクセスロール
--    ・利用可能（USAGE）
--    ・権限操作不可（MANAGE GRANTS は付与しない）
--    ・スキーマ作成不可（CREATE SCHEMA は付与しない）
-- ============================================================

CREATE ROLE IF NOT EXISTS AR_DB_ALPHA_USAGE;

GRANT USAGE ON DATABASE α TO ROLE AR_DB_ALPHA_USAGE;

-- MANAGE GRANTS / CREATE SCHEMA は意図的に付与しない


-- ============================================================
-- 2. スキーマレベル アクセスロール（スキーマ作成後に実行）
--    対象スキーマ: α.<schema_name>  ※ <schema_name> を実際のスキーマ名に置換してください
-- ============================================================

-- ----------------------------------------------------------
-- 2-1. 参照ロール（SELECT のみ）
-- ----------------------------------------------------------

CREATE ROLE IF NOT EXISTS AR_SCH_ALPHA_<SCHEMA_NAME>_R;

-- データベース・スキーマへのアクセス
GRANT USAGE ON DATABASE α                    TO ROLE AR_SCH_ALPHA_<SCHEMA_NAME>_R;
GRANT USAGE ON SCHEMA   α.<schema_name>      TO ROLE AR_SCH_ALPHA_<SCHEMA_NAME>_R;

-- 既存オブジェクトへの参照権限
GRANT SELECT ON ALL TABLES          IN SCHEMA α.<schema_name> TO ROLE AR_SCH_ALPHA_<SCHEMA_NAME>_R;
GRANT SELECT ON ALL VIEWS           IN SCHEMA α.<schema_name> TO ROLE AR_SCH_ALPHA_<SCHEMA_NAME>_R;
GRANT SELECT ON ALL EXTERNAL TABLES IN SCHEMA α.<schema_name> TO ROLE AR_SCH_ALPHA_<SCHEMA_NAME>_R;

-- 将来作成されるオブジェクトへの参照権限（FUTURE GRANTS）
GRANT SELECT ON FUTURE TABLES          IN SCHEMA α.<schema_name> TO ROLE AR_SCH_ALPHA_<SCHEMA_NAME>_R;
GRANT SELECT ON FUTURE VIEWS           IN SCHEMA α.<schema_name> TO ROLE AR_SCH_ALPHA_<SCHEMA_NAME>_R;
GRANT SELECT ON FUTURE EXTERNAL TABLES IN SCHEMA α.<schema_name> TO ROLE AR_SCH_ALPHA_<SCHEMA_NAME>_R;


-- ----------------------------------------------------------
-- 2-2. 更新ロール（SELECT / INSERT / UPDATE / DELETE）
-- ----------------------------------------------------------

CREATE ROLE IF NOT EXISTS AR_SCH_ALPHA_<SCHEMA_NAME>_RW;

-- データベース・スキーマへのアクセス
GRANT USAGE ON DATABASE α                    TO ROLE AR_SCH_ALPHA_<SCHEMA_NAME>_RW;
GRANT USAGE ON SCHEMA   α.<schema_name>      TO ROLE AR_SCH_ALPHA_<SCHEMA_NAME>_RW;

-- 既存テーブルへの参照・更新権限
GRANT SELECT, INSERT, UPDATE, DELETE, TRUNCATE
    ON ALL TABLES IN SCHEMA α.<schema_name>  TO ROLE AR_SCH_ALPHA_<SCHEMA_NAME>_RW;

-- 既存ビューへの参照権限
GRANT SELECT ON ALL VIEWS           IN SCHEMA α.<schema_name> TO ROLE AR_SCH_ALPHA_<SCHEMA_NAME>_RW;
GRANT SELECT ON ALL EXTERNAL TABLES IN SCHEMA α.<schema_name> TO ROLE AR_SCH_ALPHA_<SCHEMA_NAME>_RW;

-- 将来作成されるテーブルへの参照・更新権限（FUTURE GRANTS）
GRANT SELECT, INSERT, UPDATE, DELETE, TRUNCATE
    ON FUTURE TABLES IN SCHEMA α.<schema_name> TO ROLE AR_SCH_ALPHA_<SCHEMA_NAME>_RW;

-- 将来作成されるビューへの参照権限（FUTURE GRANTS）
GRANT SELECT ON FUTURE VIEWS           IN SCHEMA α.<schema_name> TO ROLE AR_SCH_ALPHA_<SCHEMA_NAME>_RW;
GRANT SELECT ON FUTURE EXTERNAL TABLES IN SCHEMA α.<schema_name> TO ROLE AR_SCH_ALPHA_<SCHEMA_NAME>_RW;
