# billing-and-plans - Comprehensive Knowledge Base

## 1. Introduction
The RiskLens Billing and Subscription system provides centralized management for customer account tiers, seat licensing, automated invoicing, and add-on module provisioning. It ensures transparent cost attribution, predictable renewals, and role-based access to financial statements across all RiskLens products (AnalyticsHub, CloudSync, DataBridge Pro, SecureVault, and WorkflowEngine).

RiskLens offers three primary plan tiers:
- **Starter Tier**: Designed for small teams up to 50 active seats with single-connector ETL and standard 8x5 support.
- **Pro Tier**: Scalable for mid-market organizations up to 500 seats with multi-cloud connectors, 24x7 email support, and 4-hour SLA.
- **Enterprise Tier**: Dedicated enterprise deployments with unlimited seats, custom ARR terms, dedicated Technical Account Manager (TAM), 1-hour critical response SLA, and custom audit retention.

## 2. Prerequisites
- **Administrative Privileges**: Only users assigned the `Billing Admin` or `Owner` role can view invoices, modify payment details, or change seat counts.
- **Valid Payment Instrument**: Valid corporate credit card or verified ACH / Wire Transfer arrangement for Enterprise invoicing contracts.
- **Tax Identification**: Valid VAT / Tax Registration ID for non-US entities to prevent erroneous tax withholdings.

## 3. Step-by-Step Procedures

### 3.1 Setup Phase
1. Navigate to **Admin Settings > Billing & Subscriptions** in the RiskLens management console.
2. Confirm current company legal name, billing address, and primary financial contact email.
3. Configure the primary payment method under **Payment Methods > Add Credit Card / ACH**.

### 3.2 Execution Phase
- **Adding or Removing Seat Licenses**:
  1. Open **Billing & Subscriptions > License Management**.
  2. Select **Adjust Seat Count**.
  3. Enter the desired active seats. Additional seats are billed prorated for the remainder of the active billing cycle.
  4. Review the prorated billing summary and click **Confirm Seat Allocation**.
- **Downloading Invoices and Receipts**:
  1. Navigate to the **Invoice History** tab.
  2. Locate the relevant invoice by Date, Invoice ID, or Amount.
  3. Click **Download PDF** for official receipt or **Export CSV** for accounting reconciliation.

### 3.3 Verification Phase
1. Confirm the newly allocated seats immediately reflect in **Admin Settings > Users > Available Seats**.
2. Verify that the primary billing contact receives an automated confirmation receipt via email within 5 minutes.
3. Validate that current usage statistics remain below the newly established license thresholds.

## 4. Common Issues & Troubleshooting
- **Issue: Inadequate Seat Allocation / License Limit Exceeded Error**:
  - *Symptom*: New user invitations fail with `LICENSE_LIMIT_EXCEEDED: Available seats exhausted`.
  - *Resolution*: Billing admin must increase seat count via License Management, or de-provision inactive/suspended accounts under User Management.
- **Issue: Credit Card Payment Failure (Payment Past Due)**:
  - *Symptom*: Account health transitions to `At Risk` or warning banner displays `Payment Failed: 402 Card Declined`.
  - *Resolution*: Verify card expiration, CVV, or daily transaction limits with issuing bank. Update payment details under **Payment Methods** and select **Retry Charge Now**.
- **Issue: Invoice Discrepancy or Unrecognized Overage Charge**:
  - *Symptom*: Invoiced amount exceeds standard plan base subscription.
  - *Resolution*: Inspect **DataBridge Pro Ingestion Overages** or **SecureVault KMS Key API quotas** in the line-item breakdown. Tier overages are charged at standard burst rates if data exceeds monthly plan volume.
- **Issue: Annual Renewal Notification and Inquiries**:
  - *Symptom*: Customer requests contract renewal quote or terms review prior to expiration date.
  - *Resolution*: Notify the assigned TAM and Account Executive 60-90 days prior to `renewal_date`. For self-service plans, annual renewals recur automatically unless 30-day written cancellation notice is submitted.

## 5. References & Related Documents
- [Onboarding Guide](file:///knowledge-base-risklens/onboarding/onboarding-guide.md)
- [DataBridge Pro Product Manual](file:///knowledge-base-risklens/products/databridge-pro.md)
- Internal SLA and Subscription Terms of Service

## 6. Change Log
- 2026-10-02: Comprehensive overhaul with detailed tier breakdowns, license troubleshooting, and payment procedures.
