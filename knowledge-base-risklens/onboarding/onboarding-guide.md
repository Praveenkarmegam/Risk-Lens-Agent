# onboarding-guide - Comprehensive Knowledge Base

## 1. Introduction
The RiskLens Onboarding Guide outlines the end-to-end implementation framework for onboarding new customer tenants, configuring core integrations, establishing role-based access control (RBAC), and validating deployment readiness. A structured onboarding process accelerates time-to-value, prevents post-go-live configuration drift, and ensures adherence to enterprise security baselines.

The typical customer onboarding lifecycle spans three stages:
1. **Tenant Initialization**: Establishing the isolated cloud tenant and administrator credentials.
2. **Identity & Connector Integration**: Connecting corporate Identity Providers (IdP) via SAML 2.0 / SCIM and establishing database or cloud storage endpoints.
3. **Pilot & Cutover Verification**: Testing sample data pipelines, validating dashboards, and conducting user enablement workshops.

## 2. Prerequisites
- **Tenant Activation Email**: Welcome link containing temporary root admin credentials and tenant domain slug.
- **Corporate Identity System**: Access to corporate IdP (Okta, Microsoft Entra ID / Azure AD, PingFederate, or Google Workspace) with permission to register enterprise applications.
- **Network and Firewall Clearances**: Whitelisting RiskLens outbound IP addresses (`52.14.88.0/24`, `34.212.19.0/24`) for data pipeline ingress.

## 3. Step-by-Step Procedures

### 3.1 Setup Phase
1. Log in to the RiskLens management console using the root activation URL.
2. Complete company identity verification and configure multi-factor authentication (MFA) for the initial administrator account.
3. Define the corporate domain name (e.g., `@example.com`) to enforce tenant identity boundaries.

### 3.2 Execution Phase
- **Configuring User Provisioning (SCIM 2.0)**:
  1. Go to **Security & Access > Identity Providers**.
  2. Generate a SCIM Bearer Token and copy the Base SCIM URL: `https://api.risklens.io/scim/v2`.
  3. In your IdP, configure SCIM provisioning with attributes: `userName`, `name.givenName`, `name.familyName`, `emails[primary eq true]`, and `roles`.
- **Establishing Default Workspace Roles**:
  1. Map corporate IdP security groups to RiskLens roles:
     - `RiskLens_Admins` -> `Tenant Administrator`
     - `RiskLens_Security_Team` -> `Security Analyst`
     - `RiskLens_Standard_Users` -> `Viewer`

### 3.3 Verification Phase
1. Perform a test user sync from the IdP and verify user creation under **Admin Settings > Users**.
2. Verify group mapping rules accurately grant expected workspace module permissions.
3. Run the automated tenant pre-flight check by navigating to **System Diagnostics > Tenant Health Check**.

## 4. Common Issues & Troubleshooting
- **Issue: Invitation Email Delivery Failure or Expired Link**:
  - *Symptom*: Users report not receiving initial onboarding emails or links return `TOKEN_EXPIRED`.
  - *Resolution*: Check corporate spam/security filters for emails from `no-reply@risklens.io`. Administrators can resend invitations from **Users > Actions > Resend Invitation**, which regenerates a fresh 24-hour token.
- **Issue: Domain Collision or Claim Conflict**:
  - *Symptom*: Administrator receives error `DOMAIN_ALREADY_REGISTERED` when entering corporate domain.
  - *Resolution*: This occurs if a sub-team previously registered a trial tenant with the same domain. The TAM or RiskLens Support must initiate a domain verification TXT record challenge in the customer's DNS zone to reassign ownership.
- **Issue: SCIM User Provisioning Sync Delay**:
  - *Symptom*: Users added to Okta or Entra groups do not immediately appear in RiskLens.
  - *Resolution*: Verify SCIM token validity. By default, IdP push intervals occur every 40 minutes. Trigger an immediate "Push Now" sync from the IdP console.

## 5. References & Related Documents
- [Authentication and SSO Troubleshooting](file:///knowledge-base-risklens/troubleshooting/authentication-sso.md)
- [Billing and Plans Guide](file:///knowledge-base-risklens/billing/billing-and-plans.md)
- [SecureVault Key Management](file:///knowledge-base-risklens/products/securevault.md)

## 6. Change Log
- 2026-10-02: Enhanced with SCIM provisioning steps, domain collision resolution, and pre-flight validation checklist.
