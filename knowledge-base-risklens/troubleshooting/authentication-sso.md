# authentication-sso - Comprehensive Knowledge Base

## 1. Introduction
The RiskLens Authentication and Single Sign-On (SSO) module enables enterprise federated identity management across leading Identity Providers (IdPs) utilizing SAML 2.0 and OpenID Connect (OIDC). Supported identity platforms include Okta, Microsoft Entra ID (Azure AD), Google Workspace, PingFederate, and OneLogin.

SSO centralizes credential governance, enforces corporate Multi-Factor Authentication (MFA), streamlines user provisioning, and minimizes credential theft. When SSO is enforced, local password authentication is disabled for domain users.

## 2. Prerequisites
- **Tenant Administrator Privileges**: Access to the RiskLens Admin Portal under **Security & Access > Single Sign-On**.
- **Identity Provider Administrative Access**: Permissions to configure enterprise SAML applications and issue signing certificates.
- **RiskLens Federation Endpoints**:
  - Assertion Consumer Service (ACS) URL: `https://auth.risklens.io/saml/v2/callback`
  - Entity ID / Audience URI: `https://auth.risklens.io/saml/v2/metadata/{tenant_id}`
  - Supported NameID Format: `urn:oasis:names:tc:SAML:1.1:nameid-format:emailAddress`

## 3. Step-by-Step Procedures

### 3.1 Setup Phase
1. Log into the RiskLens Admin Console and navigate to **Security & Access > SSO Configuration**.
2. Select Identity Protocol: **SAML 2.0** (recommended for enterprise) or **OIDC**.
3. Copy the RiskLens ACS URL and Entity ID to your clipboard.
4. Download the RiskLens SP Signing Certificate if encryption is required.

### 3.2 Execution Phase
- **Configuring IdP (e.g., Okta or Entra ID)**:
  1. Create a new Enterprise SAML 2.0 application in your IdP.
  2. Paste the RiskLens ACS URL and Entity ID.
  3. Set Name ID format to `EmailAddress` and value to `user.email`.
  4. Add SAML Attribute Statements:
     - `email` -> `user.email`
     - `firstName` -> `user.firstName`
     - `lastName` -> `user.lastName`
     - `groups` -> `user.groups`
  5. Download the IdP Metadata XML and x509 Signing Certificate (.cer or .pem).
- **Finalizing Setup in RiskLens**:
  1. Return to the RiskLens SSO console.
  2. Upload the IdP Metadata XML file or manually provide IdP Single Sign-On URL and x509 Certificate.
  3. Toggle **Enable SSO** and optionally **Enforce SSO for All Domain Users**.
  4. Save configuration.

### 3.3 Verification Phase
1. Open an incognito browser window and navigate to `https://app.risklens.io/login`.
2. Enter corporate email; verify immediate redirect to corporate IdP login screen.
3. Authenticate with IdP credentials and verify seamless redirect back to the RiskLens dashboard.
4. Verify user attributes (First Name, Last Name, Email, Assigned Roles) match IdP profile under **Users**.

## 4. Common Issues & Troubleshooting
- **Issue: "Unable to validate SAML response" or Authentication Errors**:
  - *Symptom*: Users encounter error banner `SSO_AUTH_FAILED: Unable to validate SAML response signature` or `401 Unauthorized` when redirected from IdP.
  - *Resolution*: This most frequently occurs when the IdP x509 signing certificate has expired or was rotated in Okta/Entra without updating RiskLens.
    1. Check certificate validity date in IdP.
    2. In RiskLens, go to **Security & Access > SSO Configuration > Signing Certificates**.
    3. Upload the newly active certificate and save.
- **Issue: Clock Skew / SAML Token Not Yet Valid or Expired**:
  - *Symptom*: Users receive `SAML_TIMESTAMP_INVALID: IssueInstant is in the future` or `Assertion has expired`.
  - *Resolution*: Identity provider server clock differs from RiskLens server clock. RiskLens provides a configurable **Clock Skew Tolerance** window. Navigate to **SSO Configuration > Advanced** and increase Clock Skew from 60 seconds to 180 seconds.
- **Issue: User Account Not Found / Mapping Failure**:
  - *Symptom*: Login succeeds at IdP, but RiskLens displays `USER_NOT_PROVISIONED: No account matches NameID`.
  - *Resolution*: Either Just-In-Time (JIT) provisioning is disabled and the user was not pre-created, or the IdP is sending username/UPN instead of an email address. Ensure NameID is configured as `emailAddress` in IdP, or enable **Just-In-Time (JIT) Provisioning** under SSO settings.
- **Issue: SAML Infinite Redirect Loop**:
  - *Symptom*: Browser continuously redirects between `auth.risklens.io` and IdP login page without completing session.
  - *Resolution*: Clear browser cookies and cache. Ensure that the IdP RelayState parameter is not stripped by intermediate corporate proxies or VPN firewalls.

## 5. References & Related Documents
- [Onboarding Guide](file:///knowledge-base-risklens/onboarding/onboarding-guide.md)
- [Performance and Integrations Troubleshooting](file:///knowledge-base-risklens/troubleshooting/performance-and-integrations.md)
- [Billing and License Management](file:///knowledge-base-risklens/billing/billing-and-plans.md)

## 6. Change Log
- 2026-10-02: Added clock skew mitigation, x509 certificate rotation steps, and NameID mapping resolution.
