# ML / API Test Framework — now with UI (Behave + Playwright + POM)

End-to-end UI tests now live alongside your existing ML/API tests.  
Stack: **Behave** (Gherkin), **Playwright** (Chromium/Firefox/WebKit), and a clean **Page Object Model (POM)**.

---

## Contents
- Overview
- Requirements
- Install
- Project Structure
- Configuration
- Running Tests
- Page Object Model (POM)
- Reporting (Allure) & Artifacts
---

## Overview
This repo supports:
- **API/ML testing** (existing).
- **UI E2E testing** using Behave + Playwright with POM, living under `tests/ui_bdd` and `pages/`.

Goals:
- Keep **steps thin** (business language).
- Put UI logic in **page objects** (selectors, waits, retries).
- Run locally and in CI with **headless browsers**.
- Optional **Allure** reports, screenshots, and Playwright **tracing**.

---

## Requirements
- Python **3.10+**
- **pip** + **venv**
- (Optional) **Allure** commandline for viewing reports

> Playwright browsers are installed via `playwright install` (no NodeJS required).

---

## Install
```bash
python -m venv .venv
# Windows:
.venv\Scripts ctivate
# macOS/Linux:
source .venv/bin/activate

pip install -r requirements.txt
# or minimal:
pip install behave playwright allure-behave
playwright install
```

---

## Project Structure
```
tests/
  ui_bdd/
    features/
      login.feature
      environment.py         # Behave hooks: starts Playwright, makes context.page, screenshots, tracing, etc.
      steps/
        login_steps.py       # Thin step bindings calling POM methods
pages/
  __init__.py
  base_page.py               # Common helpers (safe click/fill, ARIA-first locators, section utils)
  login_page.py
  account_summary_page.py
utils/ ...                   # (your existing helpers)
helpers/ ...                 # (your constants)
```

> Behave **requires** the `features/steps/` layout. Keep hooks in `features/environment.py`.

---

## Configuration

### Environment variables (recommended)
```bash
# PowerShell examples
$env:APP_BASE_URL="https://your-app"
$env:APP_USERNAME="user"
$env:APP_PASSWORD="pass"
$env:HEADLESS="true"
$env:BROWSER="chromium"         # chromium|firefox|webkit
```

### Behave userdata (CLI flags)
```bash
behave tests/ui_bdd/features   -D base_url="https://your-app"   -D username="user" -D password="pass"
```
Make your `environment.py` read `context.config.userdata` first, then env vars, then defaults.

### Optional: `behave.ini` (project root)
```ini
[behave]
paths = tests/ui_bdd/features
format = pretty
```

### Optional: `details.ini`
If you keep one for extra settings (read by `configparser` in hooks):
```ini
[app]
base_url = https://your-app
browser  = chromium
headless = true

[auth]
username = user
password = pass

[elk]               ; optional metrics/log push
enabled = false
url = http://localhost:9200
index = behave-tests
```

---

## Running Tests

### All UI features
```bash
behave tests/ui_bdd/features -f pretty
```

### Single feature
```bash
behave tests/ui_bdd/features/login.feature -f pretty
```

### Single scenario (by name/regex)
```bash
behave tests/ui_bdd/features/login.feature -n "Successful login and account summary verification"
# or
behave tests/ui_bdd/features/login.feature -n ".*account summary.*"
```

### By tag
```bash
behave tests/ui_bdd/features -t @ui
```

### Headed / choose browser
```bash
$env:HEADLESS="false"; $env:BROWSER="firefox"
behave tests/ui_bdd/features/login.feature -f pretty
```

### Dry-run (validate bindings without running the browser)
```bash
behave tests/ui_bdd/features --dry-run -f plain
```

---

## Page Object Model (POM)

**`pages/base_page.py`** (core helpers)
- ARIA-first locators: `by_role`, `by_label`, `by_test_id`
- Safe `click`/`fill` with waits + small retry
- Section utilities: `first_following_container_of_heading`, `count_items_with_text`
- Diagnostics: `screenshot`, `assert_nav_links_work`

**`pages/login_page.py`**
- `open()` → navigates to login/home as needed
- `click_sign_in_button()` → robust fallback (ID → role button → role link)
- `enter_credentials(username, password)` → fills fields, doesn’t log secrets
- `submit()` → clicks submit

**`pages/account_summary_page.py`**
- `visible()` → wait for “Account Summary”
- `cash_savings_count_is(n)`
- `investment_brokerage_count_is(n)`
- `navigation_links_work()`

> Steps should **only** call POM methods. Keep selectors in page classes, not steps.

---

## Reporting (Allure) & Artifacts

### Generate Allure results
```bash
behave tests/ui_bdd/features   -f allure_behave.formatter:AllureFormatter -o reports/allure_results -f pretty
```

### View report
```bash
allure serve reports/allure_results
```

### Artifacts
- **Screenshots** on failure (saved by hooks), e.g. `artifacts/screenshots/…`
- **Playwright tracing** (optional) `artifacts/traces/trace.zip`

---