# 🚀 ML API Test Framework — Step-by-Step Guide

This project demonstrates an **end-to-end ML pipeline** for the Ash Test model dataset, including training, validation, drift detection, and serving predictions via a Flask API.

---

## 📂 Project Structure

```
app/
  model_api.py            # Flask API: /health, /predict
data/
  train.csv               # training/reference data
  current.csv             # (optional) latest batch for drift test
model/
  ash_test_model.pkl      # saved sklearn Pipeline (created by training)
  feature_names.json      # raw column order used by the pipeline
preprocessing/
  pipeline.py             # get_preprocessing_pipeline(X)
tests/
  test_data.py
  test_model.py
  test_prediction.py
  test_drift.py
  test_api.py
validation/
  validate_data.py        # Great Expectations checks
mlruns/                   # MLflow runs (created after training)
pytest.ini
requirements.txt
```

---

## 🛠️ Prerequisites

- Python **3.12** (64-bit)
- **Git** (optional)
- Windows PowerShell or macOS/Linux terminal

💡 *macOS/Linux users:* replace activation command with `source .venv3.12/bin/activate`

---

## ⚙️ Setup

```powershell
# Clone repo (if using Git)
git clone <repo-url>
cd <project-folder>

# Create and activate virtual environment
python -m venv .venv3.12
. .\.venv3.12\Scripts\Activate.ps1

# Upgrade essentials
python -m pip install -U pip setuptools wheel

# Install dependencies
pip install --only-binary=:all: -r requirements.txt
```

> If Great Expectations import errors appear:
```powershell
pip install "great-expectations==0.15.50"
```

---

## 📋 Workflow

### 1️⃣ Train Model (creates sklearn Pipeline)
```powershell
python .\train_model.py
```

### 2️⃣ Validate Raw Data
```powershell
python .\validation\validate_data.py
```

### 3️⃣ Run Tests

#### ✅ Data Checks
```powershell
pytest tests/test_data.py -v
```

#### 📊 Model Quality
```powershell
pytest tests/test_model.py -v
```

#### 🔍 Drift Detection
```powershell
Copy-Item .\data\train.csv .\data\current.csv
pytest tests/test_drift.py -v
```

#### 🔄 Prediction Pipeline
```powershell
pytest tests/test_prediction.py -v
```

#### 🌐 API Tests
1. Start API server:
```powershell
python -c "import app.model_api as m; m.app.run(host='127.0.0.1', port=8000, debug=False, use_reloader=False)"
```

2. Health check:
```powershell
curl http://127.0.0.1:8000/health
```

3. Run API tests:
```powershell
pytest tests/test_api.py -v
```

---

## 🔌 API Endpoints

### **GET /health**
Returns readiness and model load info.

Example:
```json
{
  "loaded_as": "Pipeline",
  "model_loaded_sec": 0.056,
  "status": "ok"
}
```

### **POST /predict**

**Payload Options:**
1. Dictionary (recommended)
```json
{
  "features": { "Pclass": 3, "Sex": 0, "Age": 22, "Fare": 7.25 }
}
```
2. List (must match training order in `feature_names.json`)
```json
{
  "features": [3, 0, 22, 7.25]
}
```

**Example Call:**
```powershell
curl -X POST "http://127.0.0.1:8000/predict" -H "Content-Type: application/json" ^
     -d "{"features":{"Pclass":3,"Sex":0,"Age":22,"Fare":7.25}}"
```

---

## 🛠️ Troubleshooting

| Problem | Solution |
|---------|----------|
| **ConnectionRefused** | Ensure API is running: `python -c "import app.model_api as m; m.app.run(...)"` |
| **Feature mismatch** | Retrain and save a Pipeline (`train_model.py`) |
| **Port in use** | Change API port in run command |
| **Missing Evidently** | `pip install evidently==0.7.12` |

---

## 🏁 Quick One-Liner (Windows)
```powershell
python .\train_model.py; `
python .\validation\validate_data.py; `
pytest tests/test_data.py -v; `
pytest tests/test_model.py -v; `
Copy-Item .\data\train.csv .\data\current.csv -Force; `
pytest tests/test_drift.py -v; `
pytest tests/test_prediction.py -v
```

---

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
- IDE Notes (PyCharm Community / VS Code)
- CI Example (GitHub Actions)
- Troubleshooting

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
