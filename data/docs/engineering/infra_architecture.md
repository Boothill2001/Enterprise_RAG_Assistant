# Infrastructure Architecture Overview

**Document Owner:** Cloud Infrastructure Team  
**Last Updated:** 2025-12-01  
**Version:** 5.0  
**Applies To:** All production and staging environments at Gravity Tech Solutions JSC

---

## 1. Cloud Platform

### Primary Region

- **Cloud Provider:** Amazon Web Services (AWS)
- **Primary Region:** `ap-southeast-1` (Singapore)
- **Disaster Recovery Region:** `ap-southeast-2` (Sydney)

### Multi-Region Strategy

| Aspect | Primary (ap-southeast-1) | DR (ap-southeast-2) |
|---|---|---|
| Role | Active (serves all traffic) | Passive (warm standby) |
| RTO | N/A | **< 30 minutes** |
| RPO | N/A | **< 5 minutes** |
| Data replication | Source | Async replica |
| Failover trigger | Automatic (Route 53 health checks) + manual confirmation |

DR failover drills are conducted **quarterly**. Last successful drill: 2025-09-28.

## 2. Kubernetes (EKS)

### Cluster Configuration

- **Service:** Amazon Elastic Kubernetes Service (EKS)
- **Kubernetes version:** 1.29
- **Cluster name:** `gravity-prod-eks-01`

### Node Groups

| Node Group | Instance Type | Min / Max Nodes | Purpose |
|---|---|---|---|
| **general** | m6i.2xlarge (8 vCPU, 32 GB) | 3 / 15 | API servers, web backends, worker services |
| **compute** | c6i.4xlarge (16 vCPU, 32 GB) | 2 / 10 | Data processing, batch jobs, ML inference preprocessing |
| **gpu** | g5.2xlarge (1 GPU, 8 vCPU, 32 GB) | 1 / 5 | ML model serving, image/video processing |

### Key Configurations

- **Cluster autoscaler** enabled with 60-second scan interval.
- **Pod disruption budgets** enforced for all Tier-1 services (minAvailable: 2).
- **Namespace isolation** per team: `platform`, `payments`, `ml`, `data`, `internal-tools`.
- **Resource quotas** enforced per namespace.
- **Istio service mesh** for inter-service communication, mTLS enforced.

## 3. Databases & Data Stores

### Aurora PostgreSQL (Primary Database)

| Parameter | Value |
|---|---|
| Engine | Aurora PostgreSQL 15.4 |
| Instance class | db.r6g.2xlarge |
| Storage | Auto-scaling up to 128 TB |
| Read replicas | 2 (in ap-southeast-1) |
| Cross-region replica | 1 (in ap-southeast-2) |
| Connection pooling | PgBouncer (max 500 connections per instance) |
| Encryption | AES-256, AWS KMS managed keys |

### ElastiCache Redis (Caching Layer)

| Parameter | Value |
|---|---|
| Engine | Redis 7.0 |
| Cluster mode | Enabled (3 shards, 2 replicas per shard) |
| Instance type | cache.r6g.xlarge |
| Max memory policy | allkeys-lru |
| Encryption in transit | TLS 1.3 |
| Use cases | Session storage, API response caching, rate limiting counters, feature flags |

### OpenSearch (Log & Search)

| Parameter | Value |
|---|---|
| Version | OpenSearch 2.11 |
| Data nodes | 3x r6g.2xlarge.search |
| Master nodes | 3x m6g.large.search (dedicated) |
| Storage | 2 TB gp3 per data node |
| Index retention | 30 days hot, 90 days warm (UltraWarm), 365 days cold (S3) |
| Use cases | Application logs, audit logs, full-text search |

### Additional Data Stores

| Service | Technology | Purpose |
|---|---|---|
| Object storage | S3 (Standard + Glacier) | File uploads, backups, ML datasets |
| Message queue | Amazon SQS + SNS | Async job processing, event notifications |
| Event streaming | Amazon MSK (Kafka 3.5) | Real-time event streaming, CDC |
| Document store | DynamoDB | User preferences, feature flags, session data |

## 4. CI/CD Pipeline

### Pipeline Overview

```
GitHub (source) → GitHub Actions (build & test) → ECR (container registry) → ArgoCD (GitOps) → EKS (deploy)
```

### Detailed Flow

1. **Source Control:** GitHub Enterprise, `main` branch protected.
2. **Build:** GitHub Actions workflow triggered on PR merge to `main`.
   - Unit tests, integration tests, linting.
   - Docker image built and tagged with git SHA.
   - Security scan via Snyk and Trivy.
3. **Container Registry:** Amazon ECR, images scanned on push.
   - Image retention: 90 days for non-production tags, indefinite for production.
4. **Deployment:** ArgoCD watches the `k8s-manifests` repository.
   - Helm charts for all services.
   - Auto-sync enabled for `dev` and `staging`.
   - Manual sync (with approval) required for `production`.
5. **Verification:** Post-deploy smoke tests and synthetic monitoring.

### Pipeline Metrics (Last 30 Days)

| Metric | Value |
|---|---|
| Average build time | 4 minutes 30 seconds |
| Average deploy time (staging) | 2 minutes 15 seconds |
| Deploy success rate | 99.2% |
| Mean time to production (from merge) | 18 minutes |

## 5. Monitoring & Alerting

### Monitoring Stack

| Component | Tool | Purpose |
|---|---|---|
| Metrics | **Prometheus** | Time-series metrics collection |
| Dashboards | **Grafana** | Visualization and dashboards |
| Alerting | **PagerDuty** | Alert routing and on-call management |
| Logging | **OpenSearch + Fluentd** | Centralized log aggregation |
| Tracing | **Jaeger** | Distributed request tracing |
| Uptime | **Synthetic monitoring (Checkly)** | External endpoint monitoring |

### Key Dashboards

- `Platform Overview` — aggregate health of all services.
- `SRE > Error Budget Tracker` — error budget consumption per service tier.
- `Database > Aurora Performance` — query performance, connections, replication lag.
- `Kubernetes > Cluster Health` — node utilization, pod status, autoscaler activity.

### Alert Routing

| Severity | Channel | Notification |
|---|---|---|
| Critical (SEV1) | PagerDuty → Phone call + SMS | Immediate |
| High (SEV2) | PagerDuty → Push notification | Within 5 min |
| Medium (SEV3) | Slack #alerts | During business hours |
| Low (SEV4) | Slack #alerts-low | Best effort |

## 6. Networking

### VPC Architecture

```
VPC: 10.0.0.0/16
├── Public Subnets (10.0.1.0/24, 10.0.2.0/24, 10.0.3.0/24)
│   ├── Application Load Balancer
│   ├── NAT Gateway (one per AZ)
│   └── Bastion host (SSM-managed, no SSH)
├── Private Subnets (10.0.10.0/24, 10.0.11.0/24, 10.0.12.0/24)
│   ├── EKS worker nodes
│   └── Application services
└── Database Subnets (10.0.20.0/24, 10.0.21.0/24, 10.0.22.0/24)
    ├── Aurora PostgreSQL
    ├── ElastiCache Redis
    └── OpenSearch
```

### CDN & Edge

- **CloudFront** CDN for static assets and API acceleration.
- **AWS WAF** attached to CloudFront and ALB.
- **AWS Shield Advanced** for DDoS protection.
- Edge locations: Singapore, Ho Chi Minh City, Hanoi, Jakarta, Bangkok.

### DNS

- **Route 53** for DNS management.
- Health check-based failover between primary and DR regions.
- TTL: 60 seconds for critical endpoints, 300 seconds for static content.

## 7. Backup & Disaster Recovery

### Backup Strategy

| Resource | Method | Frequency | Retention |
|---|---|---|---|
| Aurora PostgreSQL | Automated snapshots | **Daily** | **35 days** |
| Aurora PostgreSQL | Manual snapshots | Before major changes | 1 year |
| S3 buckets | **Cross-region replication** | Continuous | Same as source lifecycle |
| EKS cluster config | Velero backup | Daily | 30 days |
| Secrets Manager | Cross-region replication | Continuous | N/A |
| DynamoDB | Point-in-time recovery | Continuous (35-day window) | 35 days |

### Recovery Procedures

| Scenario | RTO | RPO | Procedure |
|---|---|---|---|
| Single AZ failure | < 5 min | 0 (multi-AZ) | Automatic failover |
| Region failure | < 30 min | < 5 min | Route 53 failover to DR |
| Database corruption | < 1 hour | < 1 hour | Restore from snapshot |
| Accidental deletion (S3) | < 15 min | 0 | S3 versioning recovery |

## 8. Cost Management

- Monthly infrastructure budget: **$45,000 USD** (approximately 1.1B VND).
- Cost alerts at 80% and 100% of monthly budget.
- Reserved Instances for baseline capacity (1-year term, partial upfront).
- Spot instances for batch processing and non-critical workloads (60% cost savings).
- Quarterly cost optimization review with the Finance team.

---

*For questions, contact the Cloud Infrastructure team at infra@gravitytech.vn or #infrastructure on Slack.*
