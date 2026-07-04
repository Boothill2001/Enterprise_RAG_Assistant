# Deployment Guide

**Document Owner:** DevOps & Release Engineering  
**Last Updated:** 2025-11-20  
**Version:** 3.5  
**Applies To:** All production deployments at Gravity Tech Solutions JSC

---

## 1. Environments

| Environment | Purpose | URL Pattern | Deploy Method |
|---|---|---|---|
| **dev** | Development and experimentation | `*.dev.gravitytech.vn` | Auto-deploy on push to feature branches |
| **staging** | Pre-production validation | `*.staging.gravitytech.vn` | Auto-deploy on merge to `main` |
| **production** | Live customer-facing | `*.gravitytech.vn` | Manual approval via ArgoCD |

### Environment Parity

- Staging mirrors production configuration as closely as possible.
- Staging uses the same Kubernetes node types, database engine versions, and service mesh configuration.
- Differences: staging uses smaller instance sizes (50% of production capacity) and synthetic test data.

## 2. Deployment Schedule

| Target | Frequency | Days | Time (ICT) |
|---|---|---|---|
| **Staging** | Daily | Monday - Friday | Automatic on merge |
| **Production** | 2x per week | **Tuesday and Thursday** | 10:00 - 12:00 ICT |

### Deploy Windows

- Production deployments must occur between **10:00 and 12:00 ICT** (UTC+7).
- No production deployments on **Fridays, weekends, or Vietnamese public holidays**.
- Hotfixes are exempt from the deploy window but require VP Engineering approval.

### Deploy Freeze Periods

| Period | Reason |
|---|---|
| **2 weeks before major releases** | Stabilization and regression testing |
| **December 20 - January 5** | Year-end freeze, reduced staffing |
| Vietnamese Tet holiday (±3 days) | National holiday, skeleton crew only |
| During active SEV1 incidents | No deploys until incident is resolved |

## 3. Canary Deployment

All production deployments use a **canary rollout strategy**:

### Canary Process

1. **Initial canary:** Deploy new version to **5% of traffic** for **30 minutes**.
2. **Monitoring window:** Observe error rates, latency, and business metrics.
3. **Gradual rollout:** If canary is healthy:
   - 5% → 25% (hold 10 minutes)
   - 25% → 50% (hold 10 minutes)
   - 50% → 100% (full rollout)
4. **Total rollout time:** Approximately 60-80 minutes from start to full deployment.

### Canary Health Criteria

| Metric | Threshold | Action if Exceeded |
|---|---|---|
| HTTP 5xx error rate | **> 1%** | **Automatic rollback** |
| p95 latency | **> 2 seconds** | **Automatic rollback** |
| p99 latency | > 5 seconds | Alert + manual review |
| CPU utilization | > 80% | Alert + manual review |
| Memory utilization | > 85% | Alert + manual review |

### Canary Configuration

```yaml
# argo-rollouts canary strategy
strategy:
  canary:
    steps:
      - setWeight: 5
      - pause: {duration: 30m}
      - setWeight: 25
      - pause: {duration: 10m}
      - setWeight: 50
      - pause: {duration: 10m}
      - setWeight: 100
    canaryMetadata:
      labels:
        role: canary
    analysis:
      templates:
        - templateName: error-rate-check
        - templateName: latency-check
```

## 4. Rollback Procedures

### Automated Rollback

Rollback is triggered automatically when:

- HTTP 5xx error rate exceeds **1%** during canary.
- p95 response latency exceeds **2 seconds** during canary.
- Health check failures on more than 2 pods.

Automated rollback completes in under **2 minutes**.

### Manual Rollback

For issues discovered after full rollout:

```bash
# Via ArgoCD CLI
argocd app rollback <app-name> --revision <previous-revision>

# Via kubectl (emergency)
kubectl rollout undo deployment/<deployment-name> -n <namespace>
```

### Rollback Decision Matrix

| Scenario | Action | Who Decides |
|---|---|---|
| Canary metrics exceed threshold | Automatic rollback | System (Argo Rollouts) |
| Bug discovered post-deploy, < 1 hour | Manual rollback | On-call engineer |
| Bug discovered post-deploy, > 1 hour | Hotfix forward | Team lead + on-call |
| Data corruption detected | Immediate rollback + incident | VP Engineering |

## 5. Feature Flags

### Platform

All user-facing changes must be gated behind **LaunchDarkly** feature flags.

### Requirements

| Requirement | Detail |
|---|---|
| Flag naming | `<team>.<feature>.<variant>` (e.g., `payments.momo-wallet.enabled`) |
| Default state | **Off** in production, **On** in staging |
| Documentation | Each flag must have a description and owner in LaunchDarkly |
| Cleanup | Flags must be removed within **30 days** of full rollout |
| Kill switch | Every flag must support instant disable without deployment |

### Flag Types

| Type | Use Case | Example |
|---|---|---|
| Boolean | Simple on/off toggle | `platform.new-dashboard.enabled` |
| Multivariate | A/B testing, gradual rollout | `search.algorithm.variant` (values: v1, v2, v3) |
| User-targeted | Beta testing with specific users | `enterprise.advanced-analytics.enabled` |

### Rollout Strategy with Flags

1. Deploy code with flag **off** in production.
2. Enable for **internal users** (Gravity Tech employees).
3. Enable for **beta customers** (opt-in).
4. Gradual rollout: 10% → 25% → 50% → 100% over 1-2 weeks.
5. Remove flag and dead code within 30 days.

## 6. Database Migrations

### Core Principles

- Migrations must be **backward-compatible** (old code must work with new schema).
- Migrations must be **run separately before application deployment**.
- Each migration must be **reversible** (include `down` migration).

### Migration Process

1. Create migration file using Alembic (Python) or Flyway (Java/Go).
2. Test migration on a **staging database snapshot**.
3. Measure migration duration on staging; if > 5 minutes, requires DBA review.
4. Run migration in production **before** deploying application code.
5. Verify migration success via health checks.
6. Deploy application code.

### Prohibited Migration Patterns

| Pattern | Reason | Alternative |
|---|---|---|
| `DROP COLUMN` (immediate) | Breaks running application | Add new column → migrate data → deploy code → drop old column |
| `ALTER TABLE ... ADD NOT NULL` (without default) | Locks table, breaks inserts | Add nullable column → backfill → add constraint |
| `RENAME COLUMN` (immediate) | Breaks running application | Add new column → dual-write → migrate reads → drop old |
| Large data backfills in migration | Locks table for extended period | Background job with batching |

### Migration Approval

| Migration Type | Approval Required |
|---|---|
| Add column (nullable) | Standard PR review |
| Add index | DBA review (check table size and impact) |
| Modify column type | DBA review + staging test |
| Drop table/column | Tech lead + DBA review |
| Data backfill > 1M rows | DBA review + off-peak execution |

## 7. Pre-Deployment Checklist

Before every production deployment, the release engineer must verify:

- [ ] All CI checks passing on the release commit.
- [ ] Staging deployment successful and smoke tests passing.
- [ ] Database migrations (if any) tested on staging.
- [ ] Feature flags configured correctly in LaunchDarkly.
- [ ] Rollback plan documented and tested.
- [ ] On-call engineer aware of the deployment.
- [ ] No active SEV1/SEV2 incidents.
- [ ] Not within a deploy freeze period.
- [ ] Relevant runbooks updated (if infrastructure changes).
- [ ] Customer communication drafted (if user-facing changes).

## 8. Hotfix Process

For critical production issues requiring immediate fix:

1. Branch from `main`: `hotfix/JIRA-XXX-description`.
2. Implement fix with **minimum viable change**.
3. Requires **1 reviewer** (reduced from normal 2).
4. Code review SLA: **4 hours**.
5. Deploy directly to production (skip staging soak time).
6. Canary at 5% for **15 minutes** (reduced from 30).
7. Post-deploy: backfill tests, update documentation.

---

*For questions, contact the DevOps team at devops@gravitytech.vn or #deployments on Slack.*
