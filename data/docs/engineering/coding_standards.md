# Coding Standards & Development Practices

**Document Owner:** Engineering Management  
**Last Updated:** 2025-11-01  
**Version:** 2.8  
**Applies To:** All software development at Gravity Tech Solutions JSC

---

## 1. Language-Specific Standards

### Python

| Tool | Purpose | Configuration |
|---|---|---|
| **Black** | Code formatter | Line length: 88, target Python 3.11+ |
| **Ruff** | Linter | Replaces flake8, isort, pyupgrade; config in `pyproject.toml` |
| **mypy** | Type checking | Strict mode, **type hints required** for all public functions |
| **pytest** | Test framework | With `pytest-cov`, `pytest-asyncio` plugins |

```toml
# pyproject.toml
[tool.black]
line-length = 88
target-version = ['py311']

[tool.ruff]
select = ["E", "F", "W", "I", "N", "UP", "S", "B", "A", "C4", "PT"]
ignore = ["E501"]  # handled by Black

[tool.mypy]
strict = true
python_version = "3.11"
```

### TypeScript / JavaScript

| Tool | Purpose |
|---|---|
| **ESLint** | Linting (with `@typescript-eslint` plugin) |
| **Prettier** | Code formatting (2-space indent, single quotes, trailing commas) |
| **TypeScript** | Strict mode enabled, `noImplicitAny: true` |

### Go

- Follow the official [Go Code Review Comments](https://go.dev/wiki/CodeReviewComments).
- Use `golangci-lint` with the standard config in `.golangci.yml`.
- All exported functions must have doc comments.

## 2. Pull Request Rules

### Requirements for Merging

| Rule | Requirement |
|---|---|
| Minimum reviewers | **2 approvals** required |
| CI checks | **All checks must pass** (green) |
| Force-push to main | **Strictly prohibited** |
| Branch protection | Enabled on `main` and `release/*` branches |
| Linear history | Squash merge preferred, merge commits allowed for large features |

### Code Review SLA

| Priority | Review Turnaround |
|---|---|
| Normal PR | **24 hours** |
| Hotfix PR | **4 hours** |
| Security patch | **2 hours** |

### PR Description Requirements

Every PR must include:

1. **Summary:** What was changed and why.
2. **Testing:** How the change was tested (unit, integration, manual).
3. **Screenshots:** Required for UI changes.
4. **Migration notes:** If database or config changes are involved.
5. **Rollback plan:** For high-risk changes.

### PR Size Guidelines

| Size | Lines Changed | Guideline |
|---|---|---|
| Small | < 100 lines | Ideal; quick review |
| Medium | 100 - 400 lines | Acceptable; include clear description |
| Large | 400 - 1000 lines | Split if possible; requires justification |
| Extra Large | > 1000 lines | Must be split into smaller PRs (exceptions need tech lead approval) |

## 3. Branch Naming Convention

```
feature/JIRA-123-add-payment-gateway
bugfix/JIRA-456-fix-null-pointer-exception
hotfix/JIRA-789-patch-auth-vulnerability
release/2025.11.0
chore/update-dependencies
docs/api-authentication-guide
```

| Prefix | Usage |
|---|---|
| `feature/` | New functionality |
| `bugfix/` | Bug fixes (non-urgent) |
| `hotfix/` | Critical production fixes (bypasses normal flow) |
| `release/` | Release preparation branches |
| `chore/` | Non-functional changes (dependencies, configs) |
| `docs/` | Documentation updates |

## 4. Commit Messages

Follow the **Conventional Commits** specification (v1.0.0):

```
<type>(<scope>): <description>

[optional body]

[optional footer(s)]
```

### Types

| Type | Description |
|---|---|
| `feat` | A new feature |
| `fix` | A bug fix |
| `docs` | Documentation only changes |
| `style` | Formatting, missing semicolons, etc. (no code change) |
| `refactor` | Code change that neither fixes a bug nor adds a feature |
| `perf` | Performance improvement |
| `test` | Adding or correcting tests |
| `chore` | Maintenance tasks |
| `ci` | CI/CD pipeline changes |

### Examples

```
feat(payments): add MoMo wallet integration

Integrate MoMo e-wallet as a payment method for Vietnamese users.
Supports QR code and deep-link payment flows.

Closes JIRA-1234
```

```
fix(auth): resolve token refresh race condition

Multiple concurrent requests could trigger simultaneous token refreshes,
causing 401 errors. Added mutex lock around refresh logic.

Fixes JIRA-5678
```

## 5. Test Coverage

### Coverage Requirements

| Scope | Minimum Coverage |
|---|---|
| New code | **80%** line coverage |
| Critical paths (payments, auth) | **90%** line coverage |
| Overall project | **75%** (aspirational target) |

### Testing Pyramid

| Level | Scope | Expected Count | Run Time |
|---|---|---|---|
| Unit tests | Individual functions/methods | ~70% of tests | < 5 min total |
| Integration tests | Service interactions, DB queries | ~20% of tests | < 15 min total |
| End-to-end tests | Full user workflows | ~10% of tests | < 30 min total |

### Coverage Enforcement

- Coverage is measured by `pytest-cov` (Python) and `istanbul/nyc` (TypeScript).
- PRs that decrease coverage below the threshold are **blocked by CI**.
- Coverage reports are published to Codecov and linked in the PR.

## 6. Security Scanning

### Automated Scanning

| Tool | Trigger | Purpose |
|---|---|---|
| **Snyk** | Every PR | Dependency vulnerability scanning |
| **Trivy** | Docker image build | Container image vulnerability scanning |
| **Semgrep** | Every PR | Static analysis for security patterns |
| **Gitleaks** | Pre-commit hook | Secret detection in code |

### Severity Response

| Vulnerability Severity | Action Required |
|---|---|
| Critical | Block merge, fix immediately |
| High | Block merge, fix before merge |
| Medium | Create Jira ticket, fix within 2 sprints |
| Low | Track in backlog |

## 7. Pre-Commit Hooks

Pre-commit hooks are **mandatory** for all developers. The `.pre-commit-config.yaml` includes:

```yaml
repos:
  - repo: https://github.com/psf/black
    rev: 24.3.0
    hooks:
      - id: black
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.3.0
    hooks:
      - id: ruff
        args: [--fix]
  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.9.0
    hooks:
      - id: mypy
  - repo: https://github.com/gitleaks/gitleaks
    rev: v8.18.0
    hooks:
      - id: gitleaks
```

### Setup

```bash
pip install pre-commit
pre-commit install
pre-commit install --hook-type commit-msg  # for conventional commits
```

Hooks are verified in CI — if pre-commit checks fail in CI, the developer's local hooks are misconfigured.

## 8. Documentation Standards

- All public APIs must have docstrings (Google style for Python, JSDoc for TypeScript).
- Architecture Decision Records (ADRs) for significant technical decisions.
- README.md required in every service repository.
- Runbook required for every production service.

---

*For questions, contact engineering-practices@gravitytech.vn or #engineering-practices on Slack.*
