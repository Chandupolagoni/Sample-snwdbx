# Databricks Lakehouse Federation for Snowflake

This folder contains example assets for exposing Snowflake data products in Databricks as a Unity Catalog foreign catalog using [Lakehouse Federation](https://docs.databricks.com/en/query/lakehouse-federation/index.html).

## Prerequisites
- A Databricks workspace with Unity Catalog enabled.
- Lakehouse Federation is available in your workspace (requires Premium plan or higher).
- A Snowflake account with network access from Databricks and a user/service principal configured for access.
- Databricks secrets configured to store Snowflake credentials (password, OAuth token, or key pair).

## SQL Deployment
1. Copy `create_snowflake_foreign_catalog.sql` into a Databricks SQL query or notebook.
2. Replace every `${...}` placeholder with values for your environment.
   - `connection_name`: Name for the Unity Catalog connection resource.
   - `snowflake_account`: Snowflake account locator without the `.snowflakecomputing.com` suffix.
   - `snowflake_user`, `snowflake_role`, `snowflake_database`, `snowflake_schema`, `snowflake_warehouse`: Snowflake identifiers to expose.
   - `temporary_schema`: A staging schema in Databricks for query pushdown operations.
   - `secret_scope` and `secret_key`: The Databricks secret scope/key that stores the Snowflake credential.
   - `foreign_catalog_name`: Name of the Unity Catalog foreign catalog that represents the Snowflake schema.
3. Run the SQL statements sequentially to create the connection, set credentials, and create the foreign catalog.
4. Adjust the `GRANT` statements to match your workspace principals.

## Automating with the Databricks SDK
For CI/CD you can automate execution using the [`databricks-sdk`](https://pypi.org/project/databricks-sdk/) Python package. Add the following script or adapt it to your deployment pipelines:

```bash
pip install databricks-sdk
```

```python
from databricks.sdk import WorkspaceClient

w = WorkspaceClient()

sql = w.statement_execution

create_connection = f"""
CREATE CONNECTION IF NOT EXISTS {connection_name}
TYPE SNOWFLAKE
OPTIONS (
  host = '{snowflake_account}.snowflakecomputing.com',
  user = '{snowflake_user}',
  database = '{snowflake_database}',
  warehouse = '{snowflake_warehouse}',
  role = '{snowflake_role}',
  temp_schema = '{temporary_schema}'
)
COMMENT 'Connection used for federating Snowflake data products into Databricks.'
"""

result = sql.execute(warehouse_id=warehouse_id, catalog=uc_catalog, schema=uc_schema, statement=create_connection).result()
print(result.status.state)
```

Replace the variables with appropriate values and repeat for the `ALTER CONNECTION` and `CREATE FOREIGN CATALOG` commands.

## Version Control
Commit the SQL and documentation files to your repository so that lakehouse federation configuration is tracked alongside other infrastructure-as-code assets.
