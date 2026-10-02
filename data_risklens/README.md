# RiskLens AI Data Directory

This directory contains the core structured datasets required for account health analysis, risk signal detection, and historical ticket context:

1. **`accounts.json`**:
   - Master account registry containing enterprise customer metadata.
   - Fields:
     - `account_id` (str): Unique customer identifier (e.g. `ACC-3336`, `ACC-4654`).
     - `name` (str): Account / organization legal name.
     - `tier` (str): Service subscription tier (`Enterprise`, `Pro`, etc.).
     - `arr` (int/float): Annual Recurring Revenue in USD.
     - `status` (str): Current contract status (`Active`, `At Risk`, etc.).
     - `renewal_date` (str): Contract renewal date in ISO `YYYY-MM-DD` format.
     - `tam` (str): Assigned Technical Account Manager name.
     - `support_plan` (str): Support SLA tier (`Mission Critical`, `Premier`, etc.).

2. **`tickets.json`**:
   - Historical and active support tickets linked to accounts.
   - Fields:
     - `ticket_id` (str): Unique ticket identifier (e.g. `TIC-101`).
     - `account_id` (str): Foreign key to `accounts.json`.
     - `created_at` (str): Timestamp of creation (ISO 8601).
     - `company` (str): Organization name.
     - `subject` (str): Short summary of the reported incident.
     - `body` (str): Full text of customer communication.
     - `product` (str): Specific RiskLens module (`SecureVault`, `AnalyticsHub`, etc.).
     - `product_area` (str): Functional area (`SSO`, `Sync`, `RBAC`, etc.).
     - `category` (str): Classification (`technical_issue`, `billing`, `how_to`, etc.).
     - `urgency` (str): Stated or detected urgency level.
     - `status` (str): Current ticket lifecycle state (`open`, `pending_customer`, `resolved`).
     - `priority` (str): Internal SLA priority (`P1`, `P2`, `P3`, `P4`).
