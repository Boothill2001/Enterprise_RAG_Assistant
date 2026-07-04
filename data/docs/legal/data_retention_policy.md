# Data Retention and Deletion Policy

**Document Owner:** Legal Department — Data Privacy Office  
**Last Updated:** 2025-11-10  
**Version:** 3.1  
**Policy ID:** LEGAL-DRP-2025-v3.1  
**Applies To:** All departments and systems at Gravity Tech Solutions JSC

---

## 1. Purpose

This policy establishes the retention periods, storage requirements, and deletion procedures for all categories of data processed by Gravity Tech Solutions JSC ("the Company"). It ensures compliance with Vietnamese data protection laws, including the Personal Data Protection Decree (Decree 13/2023/ND-CP), the Accounting Law (Law No. 88/2015/QH13), and the Labor Code (Law No. 45/2019/QH14).

## 2. Data Retention Schedule

### 2.1 Customer Data

| Data Category | Retention Period | Legal Basis |
|---|---|---|
| Customer account information | **3 years after contract termination** | Decree 13/2023/ND-CP, business necessity |
| Transaction records | **10 years** from transaction date | Accounting Law, Article 41 |
| Customer support tickets | **2 years** after ticket closure | Business necessity |
| Customer communications (email, chat) | **1 year** active, **3 years** archived | Business necessity |
| Usage analytics (aggregated) | **5 years** | Business necessity (anonymized) |
| Usage analytics (individual) | **1 year** | Consent-based, PDPA |

**Post-retention action:** Permanent deletion using cryptographic erasure within 30 days of retention period expiry.

### 2.2 Employee Data

| Data Category | Retention Period | Legal Basis |
|---|---|---|
| Employment contracts & amendments | **5 years after termination** | Labor Code, Article 12 |
| Payroll records | **10 years** | Accounting Law |
| Performance reviews | **3 years after termination** | Business necessity |
| Recruitment records (hired) | Duration of employment + **2 years** | Business necessity |
| Recruitment records (not hired) | **6 months** from decision date | Decree 13/2023/ND-CP |
| Training records | **3 years after termination** | Labor Code |
| Disciplinary records | **5 years after termination** | Labor Code |
| Health & safety records | **10 years** | Occupational Safety Law |
| Background check results | **1 year** from hire date | Decree 13/2023/ND-CP |

**Post-retention action:** Permanent deletion within 60 days, with HR department confirmation.

### 2.3 Financial Records

| Data Category | Retention Period | Legal Basis |
|---|---|---|
| Accounting books and records | **10 years** | Accounting Law, Article 41 |
| Tax records and returns | **10 years** from fiscal year end | Tax Administration Law |
| Invoices (e-invoices) | **10 years** | Decree 123/2020/ND-CP |
| Bank statements and reconciliations | **10 years** | Accounting Law |
| Audit reports | **10 years** | Accounting Law |
| Expense reports and receipts | **5 years** | Internal policy |
| Vendor contracts and POs | **10 years** after contract completion | Accounting Law |

### 2.4 Technical and Operational Data

| Data Category | Retention Period | Storage Tier |
|---|---|---|
| Application audit logs | **2 years** | Hot (30 days) → Warm (6 months) → Cold (remainder) |
| Security logs (access, auth) | **3 years** | Hot (90 days) → Cold (remainder) |
| Infrastructure logs | **90 days** | Hot storage only |
| Database backups | **35 days** (rolling) | S3 with cross-region replication |
| Email (corporate) | **1 year auto-archive**, **3 years cold storage** | Exchange Online → Azure Archive |
| Chat messages (Slack) | **1 year** | Slack Enterprise retention |
| Code repositories | Indefinite (active), **5 years** (archived) | GitHub Enterprise |
| CI/CD build artifacts | **90 days** | S3 Standard |

## 3. Data Storage and Classification

### 3.1 Data Classification Levels

| Level | Description | Examples | Storage Requirements |
|---|---|---|---|
| **Restricted** | Highly sensitive, regulatory | PII, financial data, health records | Encrypted at rest (AES-256), encrypted in transit (TLS 1.3), access logging |
| **Confidential** | Business-sensitive | Source code, contracts, strategies | Encrypted at rest, access controls |
| **Internal** | Internal use only | Meeting notes, internal memos | Standard access controls |
| **Public** | Publicly available | Marketing materials, published docs | No special requirements |

### 3.2 Storage Locations

All data must be stored in approved locations:

| Approved Storage | Data Types |
|---|---|
| AWS ap-southeast-1 (Singapore) | Production data, application data |
| AWS ap-southeast-2 (Sydney) | Disaster recovery replicas |
| Google Workspace | Corporate email, documents |
| Slack Enterprise Grid | Internal communications |
| GitHub Enterprise | Source code |

**Prohibited:** Personal devices, personal cloud storage (Google Drive personal, Dropbox), USB drives (exception: encrypted devices approved by IT Security).

## 4. Deletion Methods

### 4.1 Digital Data

| Method | Use Case | Standard |
|---|---|---|
| **Cryptographic erasure** | Primary method for all digital data | Destroy encryption keys rendering data unreadable; NIST SP 800-88 compliant |
| **Secure overwrite** | Legacy systems without encryption | 3-pass overwrite (DoD 5220.22-M standard) |
| **Physical destruction** | Decommissioned storage devices | Degaussing + physical shredding; certificate of destruction required |

### 4.2 Physical Documents

| Method | Use Case |
|---|---|
| **Cross-cut shredding** | All physical documents containing confidential or restricted data |
| **Shred particle size** | DIN 66399 Level P-4 (maximum 2mm x 15mm particles) |
| **Bulk destruction** | Iron Mountain certified destruction service for large volumes |

### 4.3 Deletion Verification

- All deletion events must be logged in the **Data Deletion Register**.
- Quarterly audit of deletion logs by the Data Privacy Officer (DPO).
- Annual third-party audit of deletion processes.
- Certificates of destruction retained for **5 years**.

## 5. PDPA Compliance (Personal Data Protection)

### 5.1 Data Subject Access Requests (DSAR)

| Requirement | Timeline |
|---|---|
| Acknowledge receipt of request | **3 business days** |
| Complete response to data subject | **30 days** from receipt |
| Extension (complex requests) | Additional **30 days** with notification |

### 5.2 Data Subject Rights

The Company supports the following rights under Decree 13/2023/ND-CP:

- **Right to be informed:** Privacy notice provided at data collection.
- **Right of access:** Data subjects may request a copy of their personal data.
- **Right to rectification:** Correction of inaccurate or incomplete data.
- **Right to erasure:** Deletion of personal data (subject to legal retention requirements).
- **Right to restrict processing:** Suspension of data processing activities.
- **Right to data portability:** Provision of data in machine-readable format.
- **Right to object:** Opt-out of specific processing activities (e.g., marketing).
- **Right to withdraw consent:** At any time, without affecting lawfulness of prior processing.

### 5.3 DSAR Workflow

1. Request received via privacy@gravitytech.vn or in-app privacy settings.
2. Identity verification within 3 business days.
3. Request logged in the DSAR tracking system (Jira, `PRIVACY` project).
4. Relevant departments notified and data gathered.
5. Response compiled and reviewed by DPO.
6. Response delivered within 30 days.
7. Case closed and archived.

## 6. Data Breach Notification

### 6.1 Notification Timelines

| Recipient | Timeline | Method |
|---|---|---|
| **Authorities** (Ministry of Public Security, Department of Cybersecurity) | **72 hours** from breach discovery | Written report via official portal |
| **Affected individuals** | **7 days** from breach discovery | Email + in-app notification |
| **Board of Directors** | **24 hours** from breach discovery | Direct communication |
| **Insurance provider** | **48 hours** from breach discovery | Written notification |

### 6.2 Breach Response Team

| Role | Responsibility |
|---|---|
| Data Privacy Officer (DPO) | Coordinates response, regulatory communication |
| CISO | Technical investigation, containment |
| Legal Counsel | Regulatory assessment, liability analysis |
| VP Engineering | Technical remediation |
| Communications Lead | External messaging, customer notification |

### 6.3 Breach Documentation

All breaches must be documented in the **Breach Register**, including:

- Date and time of discovery.
- Nature and scope of the breach.
- Categories and approximate number of data subjects affected.
- Likely consequences.
- Measures taken to contain and remediate.
- Notification actions taken.

## 7. Retention Exceptions

### 7.1 Legal Hold

When litigation, investigation, or regulatory action is pending or reasonably anticipated:

- Normal retention schedules are **suspended** for relevant data.
- Legal hold notices issued by the Legal Department.
- Data under legal hold must not be modified or deleted.
- Legal holds are reviewed **quarterly** and lifted when no longer necessary.

### 7.2 Regulatory Requests

Data may be retained beyond normal periods if required by:

- Court orders or subpoenas.
- Regulatory investigations.
- Tax audits (State Audit Office of Vietnam).

## 8. Roles and Responsibilities

| Role | Responsibility |
|---|---|
| **Data Privacy Officer (DPO)** | Policy ownership, compliance monitoring, DSAR oversight |
| **IT Security Team** | Technical implementation of retention and deletion |
| **Department Heads** | Compliance within their departments |
| **All Employees** | Adherence to retention schedules, reporting data concerns |

## 9. Policy Review

- This policy is reviewed **annually** by the DPO and Legal Department.
- Next scheduled review: **March 2026**.
- Ad-hoc reviews triggered by regulatory changes or significant data incidents.

---

*For questions about data retention, contact the Data Privacy Office at privacy@gravitytech.vn or the DPO at dpo@gravitytech.vn.*
