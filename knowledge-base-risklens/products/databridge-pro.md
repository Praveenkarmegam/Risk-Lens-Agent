# databridge-pro - Comprehensive Knowledge Base

## 1. Introduction
DataBridge Pro is the high-throughput enterprise Extract, Transform, Load (ETL) and data streaming pipeline engine of the RiskLens platform. It connects disparate enterprise databases, API feeds, event buses (Apache Kafka, RabbitMQ), and cloud warehouses (Snowflake, BigQuery, Redshift), enabling reliable data ingestion, real-time transformation, normalization, and bulk archiving.

Key modules include:
- **Data Ingestion Engine**: High-volume batch and real-time streaming ingestion capable of ingesting over 50,000 events/sec.
- **Transformation & Normalization**: SQL-based and Python-based data mapping with schema validation.
- **Bulk Operations & Archival**: Mass export, bulk record archiving, and cold-storage tiering for regulatory compliance.
- **Deduplication Engine**: Windowed deduplication using sliding hash keys to eliminate duplicate payload ingestion.

## 2. Prerequisites
- **Source Database / Feed Access**: Read credentials with network connectivity to source schemas, or active webhook subscriptions.
- **Target Schema Privileges**: DDL and DML permissions on target database staging tables.
- **Memory & Compute Quota**: Sufficient worker instances configured for parallel batch operations.

## 3. Step-by-Step Procedures

### 3.1 Setup Phase
1. Log into RiskLens and select **DataBridge Pro > Ingestion Pipelines**.
2. Click **New Pipeline**, select source type (e.g., PostgreSQL, Kafka, REST Webhook).
3. Provide connection string, credentials, and test connectivity via **Validate Source Schema**.

### 3.2 Execution Phase
- **Configuring Ingestion Pipeline (Batch or Streaming)**:
  1. Define source extraction query or topic name.
  2. Map incoming payload fields to the normalized RiskLens schema (e.g., `ticket_id`, `event_time`, `severity`).
  3. Configure the **Deduplication Window** (default: 60 minutes).
  4. Select write mode: *Append Only*, *Upsert (Merge)*, or *Replace*.
  5. Deploy pipeline to active status.
- **Executing Bulk Archive Operations**:
  1. Navigate to **Data Management > Bulk Operations > Bulk Archive**.
  2. Select the dataset target (e.g., *Historical Audit Logs*, *Closed Support Tickets*).
  3. Define the archive filter criteria (e.g., `status = 'Closed' AND closed_at < NOW() - INTERVAL '365 DAYS'`).
  4. Select destination cold storage bucket (CloudSync connector or S3 Glacier).
  5. Click **Schedule Bulk Archive Job**.
  6. *Workaround note*: If bulk archive UI is unavailable or awaiting feature rollout, operators can manually archive records one-by-one or use the batch CLI utility: `risklens-cli archive --batch-size=500 --before-date=2025-01-01`.

### 3.3 Verification Phase
1. Inspect the **Ingestion Monitor** for incoming message rate, lag, and throughput metrics.
2. Confirm zero schema violation errors in the **Dead Letter Queue (DLQ)**.
3. Validate row count in destination warehouse matches ingested source count.

## 4. Common Issues & Troubleshooting
- **Issue: Data Ingestion Schema Mismatch / Parsing Failure**:
  - *Symptom*: Records dropped to DLQ with error `SCHEMA_MISMATCH: Column 'transaction_id' expected VARCHAR but received INTEGER`.
  - *Resolution*: Open **Pipeline Settings > Schema Validation**. Either update target column data type, or add a type-casting transformation rule (`CAST(transaction_id AS VARCHAR)`) in the pipeline transformer.
- **Issue: Bulk Operations Lag / Workaround Processing**:
  - *Symptom*: Users report lack of bulk multi-selection in older console versions, having to process records one-by-one.
  - *Resolution*: This is a known UI limitation in legacy consoles. The workaround is to use the DataBridge Pro REST API endpoint `POST /api/v2/records/bulk-archive` or the CLI utility, which processes up to 10,000 records in a single payload.
- **Issue: Pipeline Ingestion Timeout Under High Load**:
  - *Symptom*: Pipeline stalls with `INGESTION_TIMEOUT: Database connection pool exhausted`.
  - *Resolution*: Increase worker connection pool limit in **Pipeline > Advanced Settings > Connection Pool** from 10 to 50, and enable exponential backoff retry.
- **Issue: Duplicate Ingestion Alerts**:
  - *Symptom*: Duplicate events detected in downstream analytics.
  - *Resolution*: Ensure the source primary key is mapped to the `Record Hash Identifier` and increase the deduplication sliding window from 15 to 120 minutes.

## 5. References & Related Documents
- [AnalyticsHub Product Manual](file:///knowledge-base-risklens/products/analyticshub.md)
- [CloudSync Multi-Cloud Storage](file:///knowledge-base-risklens/products/cloudsync.md)
- [Performance and Integrations Troubleshooting](file:///knowledge-base-risklens/troubleshooting/performance-and-integrations.md)

## 6. Change Log
- 2026-10-02: Added bulk archive workflow, deduplication troubleshooting, and DLQ handling steps.
