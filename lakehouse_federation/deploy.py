"""Automate creation of a Databricks Lakehouse Federation foreign catalog for Snowflake.

This script expects the `databricks-sdk` package and uses workspace authentication
configured through environment variables (`DATABRICKS_HOST`, `DATABRICKS_TOKEN`).

Usage:
    python deploy.py --connection-name my_conn --foreign-catalog snowflake_products \
        --snowflake-account ab12345 --snowflake-user svc_databricks --snowflake-role SYSADMIN \
        --snowflake-database PROD --snowflake-schema DATA_PRODUCT --snowflake-warehouse ANALYTICS_WH \
        --temp-schema databricks_temp --secret-scope snowflake --secret-key password --warehouse-id <db-sql-warehouse-id>
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass

from databricks.sdk import WorkspaceClient
from databricks.sdk.errors.platform import NotFound


@dataclass
class FederationConfig:
    connection_name: str
    foreign_catalog_name: str
    snowflake_account: str
    snowflake_user: str
    snowflake_role: str
    snowflake_database: str
    snowflake_schema: str
    snowflake_warehouse: str
    temp_schema: str
    secret_scope: str
    secret_key: str
    warehouse_id: str
    uc_catalog: str | None = None
    uc_schema: str | None = None


def parse_args() -> FederationConfig:
    parser = argparse.ArgumentParser(description="Create Databricks Lakehouse Federation foreign catalog for Snowflake.")
    parser.add_argument("--connection-name", required=True)
    parser.add_argument("--foreign-catalog", required=True)
    parser.add_argument("--snowflake-account", required=True)
    parser.add_argument("--snowflake-user", required=True)
    parser.add_argument("--snowflake-role", required=True)
    parser.add_argument("--snowflake-database", required=True)
    parser.add_argument("--snowflake-schema", required=True)
    parser.add_argument("--snowflake-warehouse", required=True)
    parser.add_argument("--temp-schema", required=True)
    parser.add_argument("--secret-scope", required=True)
    parser.add_argument("--secret-key", required=True)
    parser.add_argument("--warehouse-id", required=True, help="SQL warehouse ID used for statement execution")
    parser.add_argument("--uc-catalog", help="Unity Catalog catalog context for executing SQL statements")
    parser.add_argument("--uc-schema", help="Unity Catalog schema context for executing SQL statements")
    args = parser.parse_args()
    return FederationConfig(
        connection_name=args.connection_name,
        foreign_catalog_name=args.foreign_catalog,
        snowflake_account=args.snowflake_account,
        snowflake_user=args.snowflake_user,
        snowflake_role=args.snowflake_role,
        snowflake_database=args.snowflake_database,
        snowflake_schema=args.snowflake_schema,
        snowflake_warehouse=args.snowflake_warehouse,
        temp_schema=args.temp_schema,
        secret_scope=args.secret_scope,
        secret_key=args.secret_key,
        warehouse_id=args.warehouse_id,
        uc_catalog=args.uc_catalog,
        uc_schema=args.uc_schema,
    )


def ensure_connection(w: WorkspaceClient, cfg: FederationConfig) -> None:
    statement = f"""
    CREATE CONNECTION IF NOT EXISTS {cfg.connection_name}
    TYPE SNOWFLAKE
    OPTIONS (
      host = '{cfg.snowflake_account}.snowflakecomputing.com',
      user = '{cfg.snowflake_user}',
      database = '{cfg.snowflake_database}',
      warehouse = '{cfg.snowflake_warehouse}',
      role = '{cfg.snowflake_role}',
      temp_schema = '{cfg.temp_schema}'
    )
    COMMENT 'Automated connection for Snowflake Lakehouse Federation.'
    """
    execute_statement(w, cfg, statement)

    # Ensure credentials are set using secrets.
    statement = f"""
    ALTER CONNECTION {cfg.connection_name}
    SET CREDENTIALS USING SECRET {cfg.secret_scope} {cfg.secret_key}
    """
    execute_statement(w, cfg, statement)


def ensure_foreign_catalog(w: WorkspaceClient, cfg: FederationConfig) -> None:
    statement = f"""
    CREATE FOREIGN CATALOG IF NOT EXISTS {cfg.foreign_catalog_name}
    USING CONNECTION {cfg.connection_name}
    OPTIONS (
      database = '{cfg.snowflake_database}',
      schema = '{cfg.snowflake_schema}'
    )
    COMMENT 'Snowflake data products exposed in Databricks via Lakehouse Federation.'
    """
    execute_statement(w, cfg, statement)


def execute_statement(w: WorkspaceClient, cfg: FederationConfig, statement: str) -> None:
    result = w.statement_execution.execute(
        warehouse_id=cfg.warehouse_id,
        catalog=cfg.uc_catalog,
        schema=cfg.uc_schema,
        statement=statement,
    )
    final = result.result()
    state = final.status.state
    if state != "SUCCEEDED":
        raise RuntimeError(f"Statement failed with state {state}: {final.status.state_message}")


def main() -> None:
    cfg = parse_args()
    w = WorkspaceClient()

    try:
        ensure_connection(w, cfg)
        ensure_foreign_catalog(w, cfg)
    except NotFound as err:
        raise RuntimeError("Ensure the SQL warehouse ID, catalog, and schema exist before running.") from err


if __name__ == "__main__":
    main()
