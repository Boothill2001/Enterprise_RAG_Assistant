# Incident Response Playbook

**Document Owner:** Site Reliability Engineering (SRE) Team  
**Last Updated:** 2025-10-20  
**Version:** 4.1  
**Applies To:** All production services at Gravity Tech Solutions JSC

---

## 1. Severity Levels

| Severity | Definition | Response Time | Examples |
|---|---|---|---|
| **SEV1** | Full service outage affecting all users | **< 15 minutes** | Payment system down, main database unreachable, complete platform unavailability |
| **SEV2** | Partial service degradation, significant user impact | **< 30 minutes** | Search functionality broken, 50%+ API error rate, data sync delays > 30 min |
| **SEV3** | Minor impact, limited user-facing issues | **< 2 hours** | Single non-critical microservice degraded, slow response in non-peak region, minor UI rendering issue |
| **SEV4** | Cosmetic issues, no functional impact | **Next business day** | Typo in error messages, minor styling inconsistency, non-critical log noise |

### Severity Classification Guidelines

- If unsure between two severity levels, **always classify higher** (e.g., choose SEV1 over SEV2).
- Severity may be reclassified during an incident as more information becomes available.
- Only the Incident Commander can downgrade severity.

## 2. On-Call Rotation

### Structure

- **Rotation cycle:** Weekly (Monday 09:00 ICT to Monday 09:00 ICT).
- **Team size:** 2 persons per rotation — **Primary** and **Secondary** on-call.
- Primary on-call is the first responder for all alerts.
- Secondary on-call is backup and assists with SEV1/SEV2 incidents.

### Responsibilities

| Role | Duties |
|---|---|
| **Primary On-Call** | Acknowledge alerts within 5 minutes, initial triage, page secondary if needed |
| **Secondary On-Call** | Available as backup, join SEV1/SEV2 war rooms, assist with investigation |
| **Incident Commander (IC)** | Appointed for SEV1/SEV2; coordinates response, manages communication |

### Scheduling

- On-call schedule is managed in **PagerDuty**.
- Swaps must be arranged at least **48 hours** in advance.
- Each engineer is on-call no more than **1 week per month**.
- Compensatory time off: 1 day off for each week of on-call duty.

## 3. Escalation Procedures

### SEV1 Escalation Chain

| Time Since Detection | Action |
|---|---|
| 0 - 5 minutes | Primary on-call acknowledges and begins triage |
| 5 - 15 minutes | Secondary on-call paged, war room opened |
| **Within 30 minutes** | **VP Engineering + CTO notified** |
| 30 - 60 minutes | If unresolved, all relevant team leads join |
| 60+ minutes | CEO briefed, external communication drafted |

### SEV2 Escalation Chain

| Time Since Detection | Action |
|---|---|
| 0 - 10 minutes | Primary on-call acknowledges |
| 10 - 30 minutes | Team lead notified |
| 60 minutes | VP Engineering notified if unresolved |

### Contact Directory

| Role | Primary Contact | Backup |
|---|---|---|
| VP Engineering | Nguyen Van Huy | Tran Thi Lan |
| CTO | Le Minh Duc | Nguyen Van Huy |
| SRE Team Lead | Pham Quoc Bao | Vo Thanh Son |
| Security Lead | Hoang Thi Mai | Dang Van Tuan |

## 4. Incident Communication

### Internal Communication

- **Primary channel:** Slack `#incidents` (all severity levels).
- **War room:** Dedicated Slack huddle created for SEV1/SEV2 incidents.
- **Naming convention:** `#inc-YYYYMMDD-short-description` for dedicated incident channels.
- **Update frequency:**
  - SEV1: Every **15 minutes** until resolved.
  - SEV2: Every **30 minutes** until resolved.
  - SEV3: Hourly updates.

### External Communication

- **StatusPage** (status.gravitytech.vn) must be updated for all SEV1/SEV2 incidents.
- StatusPage update within **10 minutes** of SEV1 declaration.
- Customer-facing communications are drafted by the IC and approved by the VP Engineering.
- Enterprise clients with SLA agreements receive direct email notifications.

### Status Definitions for StatusPage

| Status | Meaning |
|---|---|
| Investigating | Issue detected, actively investigating root cause |
| Identified | Root cause identified, working on fix |
| Monitoring | Fix deployed, monitoring for stability |
| Resolved | Issue fully resolved, normal operations restored |

## 5. Post-Mortem Process

### Requirements

- **SEV1 and SEV2 incidents** require a post-mortem document within **48 hours** of resolution.
- SEV3 incidents require a brief incident summary (post-mortem optional).
- Post-mortems are stored in Confluence under `Engineering > Incident Post-Mortems`.

### Blameless Culture

> We operate under a **blameless post-mortem culture**. The goal is to understand systemic failures and improve processes, not to assign individual blame. Every incident is an opportunity to make our systems more resilient.

### Post-Mortem Template

1. **Incident Summary:** One-paragraph description.
2. **Timeline:** Minute-by-minute record from detection to resolution.
3. **Root Cause Analysis:** 5 Whys or Fishbone diagram.
4. **Impact:** Number of users affected, revenue impact, duration.
5. **What Went Well:** Actions that helped resolve the incident.
6. **What Went Wrong:** Gaps in tooling, process, or knowledge.
7. **Action Items:** Specific, assigned, with deadlines (tracked in Jira under `POST-MORTEM` epic).

### Post-Mortem Review Meeting

- Held within **5 business days** of the incident.
- Attended by: IC, on-call engineers, team lead, VP Engineering (for SEV1).
- Action items are tracked in Jira and reviewed in weekly SRE standup.

## 6. SLA Targets

| Service Tier | Uptime Target | Measurement Period |
|---|---|---|
| **Tier-1** (core platform, payments, auth) | **99.95%** | Monthly |
| **Tier-2** (search, notifications, reports) | **99.9%** | Monthly |
| **Tier-3** (internal tools, admin dashboards) | **99.5%** | Monthly |

### Error Budget

- Tier-1 services have a monthly error budget of **21.6 minutes** of downtime.
- When error budget is exhausted, the team must focus exclusively on reliability improvements (no new feature work) until the next calendar month.
- Error budget consumption is tracked in Grafana dashboard: `SRE > Error Budget Tracker`.

## 7. Runbooks

Standard runbooks are maintained in the `ops-runbooks` GitHub repository. Key runbooks:

| Runbook | Last Tested |
|---|---|
| Database failover (Aurora) | 2025-09-15 |
| Redis cluster recovery | 2025-08-22 |
| Kubernetes node replacement | 2025-10-01 |
| CDN cache purge | 2025-07-30 |
| DNS failover to DR region | 2025-09-01 |

Runbooks must be tested via **game days** at least once per quarter.

---

*For questions, contact the SRE team at sre@gravitytech.vn or #sre on Slack.*
