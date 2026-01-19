# WorkFlow Pro - QA Automation Framework

<div align="center">

![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)
![Playwright](https://img.shields.io/badge/Playwright-1.40+-green.svg)
![pytest](https://img.shields.io/badge/pytest-7.4+-yellow.svg)
![License](https://img.shields.io/badge/License-MIT-purple.svg)

**A comprehensive test automation framework for the WorkFlow Pro B2B SaaS platform**

</div>

---

## 📋 Table of Contents

- [Overview](#overview)
- [Assignment Background](#assignment-background)
- [Project Structure](#project-structure)
- [Installation](#installation)
- [Running Tests](#running-tests)
- [Framework Architecture](#framework-architecture)
- [Part 1: Flaky Test Debugging](#part-1-flaky-test-debugging)
- [Part 2: Framework Design](#part-2-framework-design)
- [Part 3: Integration Testing](#part-3-integration-testing)
- [Configuration](#configuration)
- [Test Categories](#test-categories)
- [Best Practices](#best-practices)

---

## Overview

This repository contains a complete **QA Automation Framework** built for **WorkFlow Pro**, a fictional B2B project management SaaS platform. The framework demonstrates:

- ✅ **Browser Automation** using Playwright
- ✅ **API Testing** using requests with retry mechanisms
- ✅ **Multi-tenant Support** for B2B SaaS testing
- ✅ **Page Object Model** for maintainable UI tests
- ✅ **Cross-platform Testing** with BrowserStack integration
- ✅ **CI/CD Ready** configuration

---

## Assignment Background

This project is a solution to a **QA Automation Engineering Case Study** with three parts:

### Part 1: Debugging Flaky Tests (30 min)
- Identify issues in flaky Playwright tests
- Explain root causes (CI/CD vs local differences)
- Implement reliable fixes with proper waits

### Part 2: Framework Design (25 min)
- Design a scalable test automation framework
- Handle multi-tenant environments
- Support web and mobile testing
- Implement configuration management

### Part 3: API + UI Integration Testing (35 min)
- Create end-to-end project creation flow
- Combine API and UI verification
- Validate tenant isolation (security)
- Handle edge cases and cleanup

---

## Project Structure

```
QA_Task/
├── README.md                       # This file
├── SUBMISSION.md                   # Assignment submission document
├── requirements.txt                # Python dependencies
├── pytest.ini                      # pytest configuration
├── conftest.py                     # Shared pytest fixtures
│
├── pages/                          # Page Object Model
│   ├── __init__.py
│   ├── base_page.py                # Base class with common methods
│   ├── login_page.py               # Login page interactions
│   └── dashboard_page.py           # Dashboard page interactions
│
├── tests/
│   ├── unit/                       # Unit tests (no backend needed)
│   │   └── test_framework_components.py
│   ├── api/                        # API endpoint tests
│   │   └── test_create_project_api.py
│   ├── ui/                         # UI/Browser tests
│   │   ├── test_login.py           # Login functionality
│   │   └── test_dashboard.py       # Dashboard functionality
│   └── integration/                # End-to-end tests
│       └── test_project_creation_flow.py
│
└── utils/                          # Utility modules
    ├── __init__.py
    ├── config.py                   # Configuration management
    ├── auth.py                     # Authentication/token handling
    └── api_client.py               # REST API client
```

---

## Installation

### Prerequisites

- Python 3.11 or higher
- pip (Python package manager)

### Setup

```bash
# Clone or navigate to the project
cd QA_Task

# Install dependencies
pip install -r requirements.txt

# Install Playwright browsers
playwright install chromium

# (Optional) Install all browsers
playwright install
```

### Verify Installation

```bash
# Run unit tests to verify setup
py -m pytest tests/unit/ -v
```

---

## Running Tests

### Unit Tests (Always Pass)

```bash
# Run all unit tests
py -m pytest tests/unit/ -v

# Expected: 22 passed
```

### All Tests

```bash
# Run entire test suite
py -m pytest -v

# Note: API/UI/Integration tests require a real backend
```

### Specific Test Categories

```bash
# API tests only
py -m pytest tests/api/ -v

# UI tests only
py -m pytest tests/ui/ -v

# Integration tests only
py -m pytest tests/integration/ -v

# Tests with specific marker
py -m pytest -m tenant_isolation -v
```

### Test Options

```bash
# Parallel execution (faster)
py -m pytest -n auto

# Stop on first failure
py -m pytest -x

# Generate HTML report
py -m pytest --html=report.html

# Verbose with short tracebacks
py -m pytest -v --tb=short
```

---

## Framework Architecture

### Design Principles

```
┌─────────────────────────────────────────────────────────────┐
│                      TEST LAYER                              │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │  API Tests  │  │  UI Tests   │  │  Integration Tests  │  │
│  └─────────────┘  └─────────────┘  └─────────────────────┘  │
└───────────────────────────┬─────────────────────────────────┘
                            │
┌───────────────────────────▼─────────────────────────────────┐
│                    PAGE OBJECT LAYER                         │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │  BasePage   │──│  LoginPage  │  │    DashboardPage    │  │
│  └─────────────┘  └─────────────┘  └─────────────────────┘  │
└───────────────────────────┬─────────────────────────────────┘
                            │
┌───────────────────────────▼─────────────────────────────────┐
│                    UTILITY LAYER                             │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │   Config    │  │ AuthManager │  │     APIClient       │  │
│  └─────────────┘  └─────────────┘  └─────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

### Key Components

| Component | File | Purpose |
|-----------|------|---------|
| **Config** | `utils/config.py` | Environment, browser, tenant configuration |
| **AuthManager** | `utils/auth.py` | Token caching, refresh, multi-tenant auth |
| **APIClient** | `utils/api_client.py` | REST client with retries and error handling |
| **BasePage** | `pages/base_page.py` | Common page methods (click, fill, wait) |
| **Fixtures** | `conftest.py` | Shared browser, API client, cleanup fixtures |

---

## Part 1: Flaky Test Debugging

### Original Flaky Code Issues

```python
# ❌ Issue 1: No headless mode (fails in CI)
browser = p.chromium.launch()

# ❌ Issue 2: Exact URL match (fails with redirects)
assert page.url == "https://app.workflowpro.com/dashboard"

# ❌ Issue 3: No wait (race condition)
assert page.locator(".welcome-message").is_visible()
```

### Fixed Code

```python
# ✅ Fix 1: Headless for CI environments
browser = p.chromium.launch(headless=True)

# ✅ Fix 2: Pattern matching with timeout
page.wait_for_url("**/dashboard**", timeout=15000)

# ✅ Fix 3: Explicit wait with expect API
expect(page.locator(".welcome-message")).to_be_visible(timeout=10000)
```

### Root Causes (CI vs Local)

| Issue | Local | CI/CD |
|-------|-------|-------|
| Display | Has monitor | No display (headless required) |
| Network | Fast/stable | Variable latency |
| Resources | Full | Shared/limited |
| Browser | One version | Multiple versions |

---

## Part 2: Framework Design

### Configuration Management

The framework supports multiple environments via environment variables:

```bash
# Set environment (local, staging, production)
export TEST_ENV=staging

# Set browser (chromium, firefox, webkit)
export TEST_BROWSER=chromium

# Enable/disable headless
export HEADLESS=true

# BrowserStack credentials (for mobile testing)
export BROWSERSTACK_USERNAME=your_username
export BROWSERSTACK_ACCESS_KEY=your_key
```

### Multi-Tenant Support

Each tenant has isolated configuration:

```python
from utils.config import Config

# Get tenant-specific config
tenant = Config.get_tenant("company1")
print(tenant.base_url)       # https://company1.workflowpro.com
print(tenant.admin_email)    # admin@company1.com
```

### Available Tenants

| Tenant ID | Subdomain | Admin Email |
|-----------|-----------|-------------|
| company1 | company1 | admin@company1.com |
| company2 | company2 | admin@company2.com |
| company3 | company3 | admin@company3.com |

---

## Part 3: Integration Testing

### Test Flow

```
┌──────────────────┐
│  1. API Request  │  Create project via POST /api/v1/projects
└────────┬─────────┘
         ▼
┌──────────────────┐
│  2. UI Verify    │  Login as Company1, verify project visible
└────────┬─────────┘
         ▼
┌──────────────────┐
│  3. Security     │  Login as Company2, verify project NOT visible
└────────┬─────────┘
         ▼
┌──────────────────┐
│  4. Cleanup      │  Delete project via API
└──────────────────┘
```

### Tenant Isolation Test

```python
def test_project_creation_full_flow(self):
    # Create project as Company1
    project = company1_api.create_project(payload)
    
    # Verify visible to Company1
    login.login(tenant1.admin_email, tenant1.admin_password)
    assert dashboard.is_project_visible(project_name)
    
    # SECURITY: Verify NOT visible to Company2
    login2.login(tenant2.admin_email, tenant2.admin_password)
    assert not dashboard2.is_project_visible(project_name)
```

---

## Configuration

### pytest.ini

```ini
[pytest]
testpaths = tests
python_files = test_*.py
markers =
    slow: marks tests as slow running
    mobile: marks tests requiring mobile device
    browserstack: marks tests requiring BrowserStack
    tenant_isolation: marks security tests
```

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `TEST_ENV` | staging | Environment (local/staging/production) |
| `TEST_BROWSER` | chromium | Browser (chromium/firefox/webkit) |
| `HEADLESS` | true | Run headless mode |
| `BROWSERSTACK_USERNAME` | - | BrowserStack username |
| `BROWSERSTACK_ACCESS_KEY` | - | BrowserStack access key |

---

## Test Categories

### Unit Tests (22 tests) ✅

Tests that **always pass** - verify framework components work:

- `TestConfigUnit` - Configuration loading
- `TestAuthManagerUnit` - Token management
- `TestAPIClientUnit` - API client initialization
- `TestPageObjectsUnit` - Page object instantiation
- `TestFrameworkIntegrity` - Module imports

### API Tests (10 tests)

Tests for REST API endpoints:

- Project CRUD operations
- Error handling
- Tenant isolation at API level

### UI Tests (12 tests)

Browser-based tests:

- Login functionality
- Dashboard loading
- Responsive design (4 viewports)
- Tenant data isolation

### Integration Tests (6 tests)

End-to-end flows:

- Full project creation flow
- Mobile testing (BrowserStack)
- Cross-tenant security

---

## Best Practices

### Page Object Pattern

```python
# Good: Use page objects
login_page = LoginPage(page)
login_page.login(email, password)

# Bad: Direct selectors in tests
page.fill("#email", email)
page.click("#login-btn")
```

### Explicit Waits

```python
# Good: Explicit waits
page.wait_for_url("**/dashboard**", timeout=15000)
expect(locator).to_be_visible(timeout=10000)

# Bad: Implicit waits or sleep
time.sleep(5)
```

### Test Cleanup

```python
# Good: Use fixtures for cleanup
@pytest.fixture(autouse=True)
def setup(self):
    # Setup
    yield
    # Cleanup runs even if test fails
    api.delete_project(project_id)
```

### Tenant Isolation

```python
# Good: Fresh browser context per tenant
context1 = browser.new_context()  # Company1
context2 = browser.new_context()  # Company2

# Bad: Same context for different tenants
```

---

## Technologies Used

| Technology | Version | Purpose |
|------------|---------|---------|
| Python | 3.11+ | Programming language |
| Playwright | 1.40+ | Browser automation |
| pytest | 7.4+ | Test framework |
| requests | 2.31+ | HTTP client for API tests |
| pytest-xdist | 3.5+ | Parallel test execution |
| allure-pytest | 2.13+ | Test reporting |

---

## Troubleshooting

### Tests Fail with "Connection Error"

The API/UI tests require a real WorkFlow Pro backend. For demonstration, run only unit tests:

```bash
py -m pytest tests/unit/ -v
```

### Playwright Not Found

```bash
pip install playwright
playwright install chromium
```

### Permission Denied on Windows

Run PowerShell as Administrator or use:

```bash
py -m playwright install chromium
```

---

## License

This project is created for educational/assessment purposes.

---

## Author

**QA Automation Engineering Case Study Solution**

Built with ❤️ using Python, Playwright, and pytest
