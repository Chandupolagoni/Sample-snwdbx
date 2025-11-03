-- Databricks Lakehouse Federation setup for Snowflake
-- Replace the placeholders with your environment-specific values before running.

-- Create a connection to Snowflake using stored credentials.
CREATE CONNECTION IF NOT EXISTS ${connection_name}
TYPE SNOWFLAKE
OPTIONS (
  host = '${snowflake_account}.snowflakecomputing.com',
  user = '${snowflake_user}',
  database = '${snowflake_database}',
  warehouse = '${snowflake_warehouse}',
  role = '${snowflake_role}',
  temp_schema = '${temporary_schema}'
)
COMMENT 'Connection used for federating Snowflake data products into Databricks.';

-- The PAT or OAuth token should be stored securely using Databricks secrets.
-- Example: ALTER CONNECTION ${connection_name} SET CREDENTIALS USING SECRET ${secret_scope} ${secret_key};

-- Create the foreign catalog in Unity Catalog using the defined connection.
CREATE FOREIGN CATALOG IF NOT EXISTS ${foreign_catalog_name}
USING CONNECTION ${connection_name}
OPTIONS (
  database = '${snowflake_database}',
  schema = '${snowflake_schema}'
)
COMMENT 'Snowflake data products exposed in Databricks via Lakehouse Federation.';

-- Grant catalog usage to relevant principals.
GRANT USAGE ON CATALOG ${foreign_catalog_name} TO `data_engineers`;
GRANT SELECT ON ALL FOREIGN TABLES IN SCHEMA ${foreign_catalog_name}.${snowflake_schema} TO `analysts`;
