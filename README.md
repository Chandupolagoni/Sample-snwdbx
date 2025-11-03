# Sample-snwdbx

This repository contains sample assets for configuring Databricks Lakehouse Federation with Snowflake.

## Contents
- `lakehouse_federation/create_snowflake_foreign_catalog.sql`: SQL template for creating the Unity Catalog connection and foreign catalog that exposes Snowflake data products.
- `lakehouse_federation/deploy.py`: Automation script that uses the Databricks SDK to create the connection and foreign catalog programmatically.
- `lakehouse_federation/README.md`: Detailed deployment guidance and automation tips.

Use these artifacts as a starting point and replace placeholder values with details from your environment before running in production.
