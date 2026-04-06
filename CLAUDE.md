# CLAUDE.md

This file provides guidance for AI assistants working with this repository.

## Repository Overview

This is a Snowflake SQL sample/scratch repository containing SQL code examples that demonstrate stored procedures and views in Snowflake's SQL dialect. It appears to be a personal learning or experimentation workspace rather than a production codebase.

## Repository Structure

```
snowflake_sample/
├── README.md              # Minimal placeholder (project title only)
├── CLAUDE.md              # This file
└── snowflake_sampe.txt    # Main SQL file (note: filename has a typo — missing 'l')
```

## File Contents

### `snowflake_sampe.txt`

Contains iterative SQL development in Snowflake's Scripting (Snowpark SQL) dialect:

**Stored Procedures:**

| Procedure | Signature | Purpose |
|-----------|-----------|---------|
| `output_message` | `(message VARCHAR) → VARCHAR` | Returns the input message as-is |
| `return_greater` | `(number_1 INTEGER, number_2 INTEGER) → INTEGER` | Returns the larger of two integers using IF/ELSE |
| `find_invoice_by_id` | `(code VARCHAR, code2 VARCHAR) → TABLE` | Queries NUMBERS table and returns rows; evolved through multiple iterations |

**Views:**

| View | Description |
|------|-------------|
| `v1` | INNER JOIN between `PROC.PROCS.NUMBERS` and `LINKSERVERTEST_SNOWFLAKE.ALTERS."ALTER"` |
| `v2` | INNER JOIN between `PROC.PROCS.NUMBERS` and `PROC.aaa.aaatable` |

**Referenced Database Objects:**

- `PROC.PROCS.NUMBERS` — columns: `code`, `namea`, `yeara`, `datea`
- `PROC.PROCS.RESULT` — columns: `CODE`, `naMeA`; used as a scratch/staging table
- `LINKSERVERTEST_SNOWFLAKE.ALTERS."ALTER"` — columns: `code`, `nameb`
- `PROC.aaa.aaatable` — column: `code`, `nameb`

## Known Issues in the SQL File

1. **Filename typo**: The file is named `snowflake_sampe.txt` (should be `snowflake_sample.txt`). Do not rename without considering any external references.

2. **Syntax error on line 44**: `BEGINPROC.PROCS.RESULT` is a malformed line — `BEGIN` and the table reference are concatenated without a newline or space. This is a draft artifact from iterative editing.

3. **Incomplete second version of `find_invoice_by_id`** (lines 38–48): Contains the syntax error above and appears to be an intermediate draft that was superseded by the third version (lines 52–63).

4. **Inappropriate test call on line 9**: `CALL output_message('fuck');` — this is a test artifact.

5. **No schema qualification in procedure bodies**: The procedures reference `NUMBERS` and `RESULT` without fully qualified names, relying on the active database/schema context at execution time.

## Development Conventions

Since this is a scratch/sample repository, there are no enforced conventions. However, the code reflects these patterns:

- **Snowflake Scripting syntax**: Uses `BEGIN...END`, `DECLARE`, `RESULTSET`, and `RETURN TABLE(res)` — specific to Snowflake's procedural SQL.
- **`CREATE OR REPLACE`**: Used for procedures to allow re-running scripts without errors.
- **Iterative refinement**: The file shows multiple versions of the same procedure in sequence, with later versions superseding earlier ones.
- **Inline test calls**: `CALL` statements follow each procedure definition for quick testing.

## Snowflake-Specific Notes

- Procedures use `LANGUAGE SQL` (Snowflake Scripting), not JavaScript or Python variants.
- `RESULTSET` is a Snowflake-specific cursor type; it cannot be used in standard SQL dialects.
- The `RETURN TABLE(res)` pattern is specific to Snowflake stored procedures returning tabular results.
- View `v1` references a quoted identifier `"ALTER"` — quoting is required because `ALTER` is a reserved keyword.
- Fully qualified object names follow the pattern: `<database>.<schema>.<table>`.

## Workflow

There is no build system, test framework, CI/CD pipeline, or package manager. To work with this code:

1. Connect to a Snowflake account with access to the referenced databases (`PROC`, `LINKSERVERTEST_SNOWFLAKE`).
2. Set the appropriate database and schema context before running procedures that use unqualified table names.
3. Execute statements directly in the Snowflake worksheet UI or via `snowsql` CLI.
4. The file can be run top-to-bottom, though the intermediate broken version of `find_invoice_by_id` (lines 38–48) will cause a parse error if executed.

## Git Branches

- `main` — primary branch
- `claude/add-claude-documentation-bIwA5` — documentation feature branch (active)

## What This Repository Is NOT

- Not a production application
- Not a dbt project (no `dbt_project.yml`, models, or macros)
- Not a data pipeline with scheduling or orchestration
- Not tested with any SQL linting or formatting tools
