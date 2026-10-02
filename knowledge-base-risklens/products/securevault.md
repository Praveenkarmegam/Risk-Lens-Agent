# securevault - Comprehensive Knowledge Base

## 1. Introduction
SecureVault is the enterprise-grade cryptographic secrets management, key lifecycle, and zero-trust data protection engine for RiskLens. It provides centralized storage, hardware security module (HSM) backing, automated encryption key rotation, and dynamic credential generation for database passwords, API tokens, and TLS certificates.

Key security controls include:
- Envelope encryption using customer-managed keys (CMK) via AWS KMS, Azure Key Vault, or Google Cloud KMS.
- Automated secret and key rotation without service downtime.
- Granular zero-trust access policies with mutual TLS (mTLS) enforcement.
- Immutable, tamper-evident audit logging streamed to customer SIEM platforms (Splunk, Datadog, Sentinel).

## 2. Prerequisites
- **Vault Administrator Role**: Dedicated `Vault Admin` role with MFA hardware token authorization.
- **KMS Key ARN**: Customer-provided or RiskLens-managed KMS Master Key with `kms:Decrypt`, `kms:GenerateDataKey`, and `kms:DescribeKey` policies.
- **TLS 1.3 Communication**: SecureVault strictly enforces TLS 1.3 with approved cipher suites.

## 3. Step-by-Step Procedures

### 3.1 Setup Phase
1. Log into RiskLens and navigate to **SecureVault > Vault Configuration**.
2. Select KMS Provider (AWS KMS, GCP KMS, Azure Key Vault, or Native HSM).
3. Enter Key ARN and perform cryptographic handshake test via **Test KMS Integration**.
4. Configure Secret Access Policy and define maximum token TTL (recommended: 1 hour).

### 3.2 Execution Phase
- **Creating a Secret**:
  1. Go to **SecureVault > Secrets Engine > New Secret**.
  2. Choose Secret Type: *Key-Value Pair*, *Dynamic Database Credential*, or *Certificate*.
  3. Enter Secret Name (e.g., `prod/databridge/db_credentials`) and secret payload.
  4. Set auto-rotation interval (e.g., 90 days).
  5. Click **Save Secret**.
- **Enabling Automated Encryption Key Rotation**:
  1. Open **Vault Configuration > Key Management**.
  2. Select the active Master Key and toggle **Enable 90-Day Auto-Rotation**.
  3. Confirm that re-encryption policies allow existing ciphertext to be decrypted using past key versions.

### 3.3 Verification Phase
1. Retrieve a secret using the RiskLens CLI: `risklens-vault read prod/databridge/db_credentials`.
2. Verify in **Audit Logs** that the secret read event was recorded with Timestamp, User ID, IP Address, and Action.
3. Validate that expired secrets trigger automated rotation notifications to system administrators.

## 4. Common Issues & Troubleshooting
- **Issue: Key Rotation Permission Denied or Decryption Failure**:
  - *Symptom*: Applications throw `KMS_DECRYPT_FAILED: Access Denied on KMS Key ID arn:aws:kms:...`.
  - *Resolution*: This occurs when the KMS Key Policy has been modified upstream or the IAM Role attached to SecureVault has lost KMS grant permissions. Verify in AWS/GCP/Azure console that the SecureVault service principal has `kms:Decrypt` and `kms:GenerateDataKey` permissions.
- **Issue: Expired Secret Access Token / 401 Unauthorized**:
  - *Symptom*: Pipelines or services report `VAULT_TOKEN_EXPIRED`.
  - *Resolution*: Short-lived tokens expire automatically. The client application must implement periodic token renewal via `POST /vault/v1/auth/token/renew-self` prior to the TTL expiry window.
- **Issue: Audit Log Sync Delay to SIEM**:
  - *Symptom*: SIEM dashboard shows missing audit events.
  - *Resolution*: Inspect the SIEM webhook endpoint status in **SecureVault > Audit Forwarding**. If the SIEM returned 5xx responses, SecureVault buffers logs locally for up to 72 hours and retries with exponential backoff.

## 5. References & Related Documents
- [CloudSync Multi-Cloud Storage](file:///knowledge-base-risklens/products/cloudsync.md)
- [Authentication and SSO Troubleshooting](file:///knowledge-base-risklens/troubleshooting/authentication-sso.md)
- [Performance and Integrations Guide](file:///knowledge-base-risklens/troubleshooting/performance-and-integrations.md)

## 6. Change Log
- 2026-10-02: Added KMS policy troubleshooting, token renewal patterns, and SIEM buffering details.
