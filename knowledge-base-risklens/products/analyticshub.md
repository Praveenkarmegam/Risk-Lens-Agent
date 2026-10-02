# analyticshub - Comprehensive Knowledge Base

## 1. Introduction
AnalyticsHub is the primary analytics and executive visualization module of the RiskLens platform. It aggregates operational telemetry, risk indicators, security posture metrics, and compliance audits into real-time interactive dashboards, scheduled reports, and exportable data digests.

Key capabilities include:
- Executive Risk Scoring with Monte Carlo risk simulation models.
- Custom widget designer supporting tabular, timeseries, heatmaps, and funnel charts.
- Automated report scheduling (daily, weekly, monthly) delivered via secure PDF, CSV, or direct Slack/Teams webhooks.
- Multi-tenant data isolation with role-governed dashboard access.

## 2. Prerequisites
- **Product License**: Active license for `AnalyticsHub` under the tenant plan.
- **Role Permissions**: `Analytics Admin` or `Dashboard Designer` to create or edit dashboards; `Viewer` to access published reports.
- **Underlying Data Ingestion**: Verified incoming data streams from `DataBridge Pro` or direct API data collectors.

## 3. Step-by-Step Procedures

### 3.1 Setup Phase
1. Open the RiskLens dashboard and select **AnalyticsHub** from the top navigation bar.
2. Select **Data Sources > Ingestion Status** to ensure upstream telemetry pipelines are healthy and updated within the last 15 minutes.
3. Configure default dashboard refresh intervals (recommended: 5 minutes for operational views, 1 hour for executive summaries).

### 3.2 Execution Phase
- **Creating a Custom Dashboard**:
  1. Click **Dashboards > New Dashboard**.
  2. Enter dashboard name and select a layout template (e.g., *Executive Risk Overview* or *Security Operations*).
  3. Drag and drop widgets from the library (e.g., *Top 10 Vulnerabilities*, *SLA Adherence*, *Cost Exposure*).
  4. Define dataset filters (Date Range, Business Unit, Severity Thresholds).
  5. Click **Save & Publish**.
- **Configuring Scheduled PDF/CSV Report Exports**:
  1. Open the target dashboard and select **Export > Schedule Recurring Report**.
  2. Select output format (`PDF Report` or `CSV Raw Metrics`).
  3. Enter recipient email addresses and delivery cadence (e.g., every Monday at 08:00 UTC).
  4. Click **Activate Schedule**.

### 3.3 Verification Phase
1. Confirm newly published dashboards load within 3 seconds for standard date ranges (past 30 days).
2. Trigger a test export delivery using the **Send Test Now** button and confirm receipt in the recipient's inbox.
3. Verify that restricted metrics (such as financial ARR or sensitive asset tags) are masked for unauthorized viewer roles.

## 4. Common Issues & Troubleshooting
- **Issue: Dashboard Query Timeout or Slow Loading (>30s)**:
  - *Symptom*: Dashboard displays spinning wheel or error `QUERY_TIMEOUT_EXCEEDED: Data query exceeded 30 seconds threshold`.
  - *Resolution*: This occurs when querying raw high-cardinality event tables over expansive date ranges (>90 days) without index filters. Enable **Cached Aggregates** in widget settings, or restrict time windows to 7-30 days. For massive historical datasets, run queries via scheduled background materialized views.
- **Issue: PDF Export Blank or Truncated Charts**:
  - *Symptom*: Scheduled PDF reports contain blank widget placeholders or missing timeseries lines.
  - *Resolution*: Ensure headless browser rendering has finished loading dynamic canvas elements before capture. In **Admin > Analytics Settings**, increase the PDF Render Wait Time from 2000ms to 5000ms.
- **Issue: Stale Data Cache / Numbers Not Matching Source DB**:
  - *Symptom*: Widgets display data older than the upstream database timestamp.
  - *Resolution*: Clear the AnalyticsHub tenant Redis cache by clicking **Settings > Clear Dashboard Cache**, or add `?force_refresh=true` to the URL.

## 5. References & Related Documents
- [DataBridge Pro ETL Guide](file:///knowledge-base-risklens/products/databridge-pro.md)
- [WorkflowEngine Automation Guide](file:///knowledge-base-risklens/products/workflowengine.md)
- [Performance and Integrations Troubleshooting](file:///knowledge-base-risklens/troubleshooting/performance-and-integrations.md)

## 6. Change Log
- 2026-10-02: Added query timeout mitigation, cached aggregation rules, and PDF rendering delay troubleshooting.
