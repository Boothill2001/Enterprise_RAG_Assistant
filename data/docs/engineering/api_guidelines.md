# REST API Design Guidelines

**Document Owner:** Platform Engineering Team  
**Last Updated:** 2025-11-15  
**Version:** 3.2  
**Applies To:** All backend services at Gravity Tech Solutions JSC

---

## 1. API Versioning

All APIs MUST use **URL path versioning**:

```
https://api.gravitytech.vn/v1/resources
https://api.gravitytech.vn/v2/resources
```

- Major version changes (v1 → v2) indicate breaking changes.
- Minor/patch changes are backward-compatible and do not increment the version.
- A maximum of **2 major versions** may be active simultaneously.
- **Breaking changes require a 90-day deprecation notice** communicated via the `Sunset` HTTP header and the engineering-announcements Slack channel.

## 2. Authentication & Authorization

### OAuth 2.0 + JWT

All APIs must use **OAuth 2.0** with **JWT (JSON Web Tokens)** for authentication.

| Parameter | Value |
|---|---|
| Access token expiry | **1 hour** (3600 seconds) |
| Refresh token expiry | **30 days** |
| Token signing algorithm | RS256 |
| JWKS endpoint | `https://auth.gravitytech.vn/.well-known/jwks.json` |

- Tokens must be passed in the `Authorization: Bearer <token>` header.
- Service-to-service calls use **client credentials grant**.
- User-facing APIs use **authorization code flow with PKCE**.
- Refresh tokens are single-use; a new refresh token is issued on each rotation.

### API Keys

Internal tools and monitoring agents may use API keys as a secondary mechanism. API keys must:
- Be scoped to specific services/endpoints.
- Rotate every **90 days**.
- Never be committed to version control.

## 3. Rate Limiting

| Tier | Limit | Window |
|---|---|---|
| Standard client | **1,000 requests/minute** | Rolling window |
| Premium client | **5,000 requests/minute** | Rolling window |
| Internal service | **10,000 requests/minute** | Rolling window |

Rate limit headers included in every response:

```
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 742
X-RateLimit-Reset: 1700000000
```

When rate-limited, the API returns `429 Too Many Requests` with a `Retry-After` header.

## 4. Request & Response Format

### Content Type

All APIs must accept and return **JSON** (`application/json`).

### Naming Convention

All field names must use **snake_case**:

```json
{
  "user_id": "usr_abc123",
  "first_name": "Minh",
  "created_at": "2025-03-15T10:30:00Z",
  "is_active": true,
  "account_balance": 15000000
}
```

### Date/Time Format

All timestamps must use **ISO 8601** in **UTC**: `2025-03-15T10:30:00Z`.

### Monetary Values

All monetary values are represented in the **smallest currency unit** (VND dong, no decimals).

## 5. Pagination

All list endpoints must implement **cursor-based pagination**:

```json
{
  "data": [...],
  "pagination": {
    "next_cursor": "eyJpZCI6MTAwfQ==",
    "prev_cursor": "eyJpZCI6NTB9",
    "has_more": true,
    "page_size": 25
  }
}
```

- **Maximum page size:** 100 items per page.
- **Default page size:** 25 items.
- Clients specify page size via `?page_size=50`.
- The cursor value is an opaque string; clients must not parse or construct cursors.

## 6. Error Handling

All errors must follow **RFC 7807 Problem Details for HTTP APIs**:

```json
{
  "type": "https://api.gravitytech.vn/errors/insufficient-funds",
  "title": "Insufficient Funds",
  "status": 422,
  "detail": "Account acc_12345 has a balance of 500,000 VND, which is less than the requested 1,000,000 VND.",
  "instance": "/v1/transactions/txn_67890",
  "trace_id": "req_abc123def456"
}
```

### Standard Error Codes

| HTTP Status | Usage |
|---|---|
| 400 | Malformed request syntax or invalid parameters |
| 401 | Missing or invalid authentication credentials |
| 403 | Authenticated but insufficient permissions |
| 404 | Resource not found |
| 409 | Conflict with current resource state |
| 422 | Request understood but semantically invalid |
| 429 | Rate limit exceeded |
| 500 | Internal server error |
| 503 | Service temporarily unavailable |

## 7. Required Headers

Every request must include:

| Header | Purpose | Example |
|---|---|---|
| `X-Request-ID` | Unique identifier for the request | `req_a1b2c3d4e5f6` |
| `X-Correlation-ID` | Trace ID across service boundaries | `corr_x9y8z7w6` |
| `Authorization` | Bearer token | `Bearer eyJhbG...` |
| `Content-Type` | Media type | `application/json` |
| `Accept` | Expected response type | `application/json` |

If `X-Request-ID` is not provided by the client, the API gateway will generate one automatically.

## 8. API Documentation

- All APIs must be documented using **OpenAPI 3.1** specification.
- Documentation is **auto-generated** from code annotations using Swagger/Redoc.
- Live documentation available at: `https://docs.gravitytech.vn/api/`
- Every endpoint must include: description, request/response examples, error scenarios.
- Schema changes must be reflected in documentation before deployment.

## 9. Deprecation Policy

1. Announce deprecation via `Sunset` header and Slack notification.
2. **90-day deprecation window** begins from announcement date.
3. During the window, the deprecated endpoint returns a `Deprecation` header.
4. After 90 days, the endpoint returns `410 Gone`.
5. Usage analytics for deprecated endpoints are reviewed weekly to track migration progress.

## 10. Idempotency

All `POST` and `PATCH` operations that create or modify resources must support **idempotency keys**:

```
Idempotency-Key: idem_unique_string_here
```

- Keys are valid for **24 hours**.
- Duplicate requests within the window return the original response with `304 Not Modified`.

---

*For questions, contact the Platform Engineering team at platform@gravitytech.vn or #platform-eng on Slack.*
