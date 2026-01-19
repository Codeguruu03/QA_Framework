# WorkFlow Pro QA Automation - Submission Document

## Overview

This submission addresses all three parts of the QA Automation Engineering Case Study for the WorkFlow Pro B2B SaaS platform.

---

## Part 1: Debugging Flaky Test Code

### Issues Identified

| Issue | Root Cause | CI/CD Impact |
|-------|------------|--------------|
| No `headless=True` | CI has no display | Test fails on startup |
| Direct URL assertion | Redirects add query params | URL never matches exactly |
| No explicit waits | Race condition | Dynamic content not loaded |
| No timeout configuration | CI has variable latency | Random timeouts |
| No cleanup in errors | Resource leak | Browser processes pile up |

### Fixes Applied (see `tests/ui/test_login.py`)

```python
# ✅ Headless for CI
browser = p.chromium.launch(headless=True)

# ✅ Pattern matching with timeout
page.wait_for_url("**/dashboard**", timeout=15000)

# ✅ Explicit visibility wait
expect(page.locator(".welcome-message")).to_be_visible(timeout=10000)

# ✅ try/finally for cleanup
```

---

## Part 2: Test Framework Design

### Folder Structure

```
QA_Task/
├── conftest.py              # Shared fixtures
├── pytest.ini               # pytest config
├── requirements.txt         # Dependencies
├── pages/
│   ├── base_page.py         # Base Page Object
│   ├── login_page.py        # Login Page Object
│   └── dashboard_page.py    # Dashboard Page Object
├── tests/
│   ├── api/                 # API tests
│   ├── ui/                  # UI tests
│   └── integration/         # End-to-end tests
└── utils/
    ├── config.py            # Environment config
    ├── auth.py              # Token management
    └── api_client.py        # REST client
```

### Configuration Management

- **Environments**: LOCAL, STAGING, PRODUCTION via `TEST_ENV`
- **Browsers**: Chromium, Firefox, WebKit via `TEST_BROWSER`
- **Tenants**: company1, company2, company3 with separate configs
- **Credentials**: Environment variables for security

### Missing Requirements Questions

1. **Test Data**: How is test data seeded? Is there a test database reset mechanism?
2. **2FA**: Which users have 2FA? How to get test OTP codes?
3. **Parallel Execution**: Can tests run in parallel across tenants?
4. **Data Cleanup**: Auto-cleanup or manual? Retention policy?
5. **Reporting**: Allure? HTML? Integration with CI dashboards?
6. **Mobile**: Real devices or emulators acceptable?

---

## Part 3: API + UI Integration Test

### Implementation (see `tests/integration/test_project_creation_flow.py`)

```python
def test_project_creation_full_flow():
    # 1. API: Create project for Company1
    project = company1_api.create_project(payload)
    
    # 2. Web UI: Verify visible to Company1
    login.login(tenant1.admin_email, tenant1.admin_password)
    assert dashboard.is_project_visible(project_name)
    
    # 3. Security: New session for Company2
    login2.login(tenant2.admin_email, tenant2.admin_password)  
    assert not dashboard2.is_project_visible(project_name)
    
    # 4. Cleanup: Delete project after test
```

### Key Design Decisions

1. **Separate browser contexts** for tenant isolation testing
2. **Unique project names** (UUID) to avoid conflicts
3. **Fixture-based cleanup** to ensure data doesn't persist
4. **Mobile tests** marked as skippable if BrowserStack not configured

---

## Assumptions Made

1. API returns `{"id": int, "name": str, "status": str}` on project creation
2. Login uses `#email`, `#password`, `#login-btn` selectors
3. Dashboard shows projects in `.project-card` elements
4. Tenant isolation enforced at API layer (403/404 for cross-tenant access)
5. BrowserStack credentials via environment variables
6. Test passwords are `password123` for demo (would be env vars in production)

---

## Technologies Used

| Tool | Purpose |
|------|---------|
| **pytest** | Test framework with fixtures |
| **Playwright** | Browser automation |
| **requests** | API testing |
| **BrowserStack** | Cross-platform cloud testing |

---

## Running the Tests

```bash
# Install dependencies
pip install -r requirements.txt
playwright install

# Run all tests
pytest

# Run specific test types
pytest tests/api/ -v
pytest tests/ui/ -v
pytest tests/integration/ -v

# Run with specific browser
TEST_BROWSER=firefox pytest tests/ui/

# Run tenant isolation tests
pytest -m tenant_isolation
```
