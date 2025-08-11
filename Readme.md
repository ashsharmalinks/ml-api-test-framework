# ML API Test Framework 🧪🚀

End-to-end template for:
1) validating data,  
2) training a model,  
3) serving predictions with a REST API (Flask), and  
4) testing everything (pytest), including drift checks (Evidently) and data checks (Great Expectations).

---

## ✨ five commands

```powershell
# 1) Create & activate env (Windows PowerShell)
py -3.12 -m venv .venv3.12
. .\.venv3.12\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt

# 2) Validate data
python validation/validate_data.py

# 3) Train the model (saves pipeline + feature names)
python -m trains.train_ash_test_model

# 4) Run API (keep this terminal open)
$env:PYTHONPATH="."
python -m app.model_api

# 5) In a second terminal: run tests
. .\.venv3.12\Scripts\Activate.ps1
pytest -q
```

---

## 🧱 Project layout

```
ml-api-test-framework/
├─ app/
│  ├─ model_api.py               # Flask app (REST API)
│  └─ utils/
│     ├─ data_utils.py           # helpers: load feature names, row builders
│     └─ registry.py             # ModelRegistry (loads models from config)
├─ config/
│  └─ config.yaml                # API host/port and model registry
├─ data/
│  └─ raw/
│     ├─ train.csv               # training data
│     └─ test.csv                # (optional) test data
├─ model/
│  └─ ash_test_model/
│     ├─ ash_test_model.pkl      # trained sklearn Pipeline
│     └─ feature_names.json      # raw feature order used by API
├─ preprocessing/
│  └─ pipeline.py                # get_preprocessing_pipeline(...)
├─ reports/
│  └─ ge_validation_result.json  # Great Expectations run output
├─ tests/
│  ├─ test_api.py
│  ├─ test_data.py
│  ├─ test_drift.py
│  ├─ test_model.py
│  └─ test_prediction.py
├─ trains/
│  └─ train_ash_test_model.py    # training script
├─ validation/
│  └─ validate_data.py           # Great Expectations validation
├─ requirements.txt
├─ pytest.ini
└─ README.md
```

---

## 🛠 Setup

1) **Python 3.12** (Windows):
```powershell
py -3.12 -m venv .venv3.12
. .\.venv3.12\Scripts\Activate.ps1
python -m pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
```

2) **Check files exist**
- `data/raw/train.csv` (required)
- `config/config.yaml` (see below)
- `preprocessing/pipeline.py` present

---

## ✅ Validate the raw data (Great Expectations)

Runs a few sanity checks (nulls, ranges, categories) and writes a JSON report.

```powershell
python validation/validate_data.py
```

You should see:
- `reports/ge_validation_result.json` written
- A “✅ Data validation passed!” message when expectations succeed

> To customize checks, open `validation/validate_data.py` and add/change expectations.

---

## 🎯 Train the model

Trains a **sklearn Pipeline** (preprocessing + classifier) and saves:
- `model/ash_test_model/ash_test_model.pkl`
- `model/ash_test_model/feature_names.json`

```powershell
python -m trains.train_ash_test_model
```

You’ll see training metrics in the console.  
(If MLflow is configured locally, artifacts will go to `mlruns/`.)

---

## 🌐 Run the API

Make sure your terminal’s working directory is the project root.

```powershell
$env:PYTHONPATH="."
python -m app.model_api
```

You should see:
```
* Running on http://127.0.0.1:8000
```

### Health & metadata
- Health: `GET http://127.0.0.1:8000/health`
- List models: `GET http://127.0.0.1:8000/v1/models`
- Schema: `GET http://127.0.0.1:8000/v1/schema/titanic`

### Single prediction
**PowerShell:**
```powershell
curl http://127.0.0.1:8000/v1/predict/titanic `
  -Method POST -ContentType "application/json" `
  -Body '{"features":{"Pclass":3,"Sex":0,"Age":22,"Fare":7.25}}'
```

**Bash:**
```bash
curl -s http://127.0.0.1:8000/v1/predict/titanic \
  -H "Content-Type: application/json" \
  -d '{"features":{"Pclass":3,"Sex":0,"Age":22,"Fare":7.25}}'
```

### Batch prediction
**PowerShell:**
```powershell
curl http://127.0.0.1:8000/v1/batch_predict/titanic `
  -Method POST -ContentType "application/json" `
  -Body '{"rows":[{"Pclass":3,"Sex":0,"Age":22,"Fare":7.25},{"Pclass":1,"Sex":1,"Age":40,"Fare":80}]}'
```

---

## 🧪 Run tests (end-to-end)

> Keep the API **running** in one terminal while you test in another.

```powershell
. .\.venv3.12\Scripts\Activate.ps1
pytest -q
```

What they cover:
- `test_data.py` → schema & simple validations
- `test_model.py` → model loads, basic accuracy
- `test_drift.py` → data drift via Evidently (threshold tuned)
- `test_api.py` → /v1/predict/titanic happy path
- `test_prediction.py` → API edge cases (missing fields, wrong counts, etc.)

All should pass ✅.

---

## ⚙️ Config (registry)

`config/config.yaml` declares API host/port and models (you can have many):

```yaml
api:
  host: 127.0.0.1
  port: 8000
  debug: false

models:
  titanic:
    model_path: model/ash_test_model/ash_test_model.pkl
    feature_names_path: model/ash_test_model/feature_names.json
    train_csv_path: data/raw/train.csv
    target_col: Survived
```

**Tip:** The *model name* used in URLs is the key under `models:` (here: `titanic`).

---

## ➕ Add another model (future-proofing)

1) **Create a training script** (e.g., `trains/train_my_model.py`) that:
   - builds a **Pipeline** (preprocess + estimator),
   - saves `model/my_model/my_model.pkl`,
   - writes `model/my_model/feature_names.json` (raw feature order).

2) **Register it** in `config/config.yaml`:
```yaml
models:
  my_model:
    model_path: model/my_model/my_model.pkl
    feature_names_path: model/my_model/feature_names.json
    train_csv_path: data/raw/train.csv
    target_col: Survived
```

3) **Restart the API**, then:
   - `GET /v1/models` to confirm it appears,
   - `POST /v1/predict/my_model` to predict.

> If you **don’t** save a Pipeline (you save just an estimator), the API’s `ModelRegistry` will auto-fit a **fallback preprocessor** on your training CSV so predictions still work.

---

## 🧰 Troubleshooting

- **`ConnectionRefusedError` / tests 404/500**
  - API probably not running or wrong URL. Start with:
    ```powershell
    $env:PYTHONPATH="."
    python -m app.model_api
    ```
  - Tests expect `http://127.0.0.1:8000` and route `/v1/predict/titanic`.

- **500: “X has N features but expecting M”**
  - If you send only four fields (`Pclass, Sex, Age, Fare`) while your model expects the **full Titanic schema**, the API will auto-expand the minimal form. Use the JSON examples above.

- **Great Expectations “DataContextRequiredError”**
  - Already addressed in `validation/validate_data.py` by acquiring a context with `ge.get_context()`.

- **PowerShell `curl` is not GNU curl**
  - It’s an alias for `Invoke-WebRequest`. For JSON you can also use:
    ```powershell
    irm http://127.0.0.1:8000/health
    ```

- **Warnings noise in pytest**
  - We filter common ones in `pytest.ini`. To silence more, add:
    ```ini
    [pytest]
    filterwarnings =
        ignore:`result_format` configured at the Validator-level.*:UserWarning:great_expectations
        ignore:pkg_resources is deprecated as an API.*:UserWarning
    ```

---

## 🧭 Recommended order

1. **Validate data** → `python validation/validate_data.py`  
2. **Train model** → `python -m trains.train_ash_test_model`  
3. **Run API** → `python -m app.model_api`  
4. **Run tests** → `pytest -q`  
   - `test_data.py` (input shape)
   - `test_model.py` (load & score)
   - `test_drift.py` (drift %)
   - `test_api.py` (smoke/happy path)
   - `test_prediction.py` (edge cases)

---
