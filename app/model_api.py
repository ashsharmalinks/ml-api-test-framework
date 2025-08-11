# app/model_api.py
from __future__ import annotations

from pathlib import Path
from flask import Flask, request, jsonify
from werkzeug.exceptions import HTTPException
import traceback
import pandas as pd

from app.utils.registry import ModelRegistry

# --------------------------------------------------------------------------------------
# Setup
# --------------------------------------------------------------------------------------
ROOT = Path(__file__).resolve().parent.parent
REGISTRY = ModelRegistry(config_path=ROOT / "config" / "config.yaml")

app = Flask(__name__)

# Minimal vs full Titanic raw schemas
MINIMAL_FEATURES = ["Pclass", "Sex", "Age", "Fare"]
FULL_TITANIC_FEATURES = [
    "PassengerId", "Pclass", "Name", "Sex", "Age", "SibSp",
    "Parch", "Ticket", "Fare", "Cabin", "Embarked",
]

# --------------------------------------------------------------------------------------
# Helpers
# --------------------------------------------------------------------------------------
def _normalize_minimal_dict(d: dict) -> dict:
    """Ensure minimal dict uses consistent types/values."""
    out = dict(d)
    # Sex can be 0/1 or string
    sex = out.get("Sex")
    if isinstance(sex, (int, float)):
        out["Sex"] = "male" if int(sex) == 0 else "female"
    elif isinstance(sex, str):
        s = sex.strip().lower()
        if s in ("0", "male", "m"):
            out["Sex"] = "male"
        elif s in ("1", "female", "f"):
            out["Sex"] = "female"
        else:
            out["Sex"] = s
    else:
        out["Sex"] = "male"  # safe default

    # Light coercion
    out["Pclass"] = int(out.get("Pclass", 3) or 3)
    out["Age"] = float(out.get("Age", 0) or 0)
    out["Fare"] = float(out.get("Fare", 0) or 0)
    return out


def _expand_minimal_to_full(mini: dict) -> dict:
    mini = _normalize_minimal_dict(mini)
    return {
        "PassengerId": 0,
        "Pclass": mini["Pclass"],
        "Name": "",
        "Sex": mini["Sex"],
        "Age": mini["Age"],
        "SibSp": 0,
        "Parch": 0,
        "Ticket": "",
        "Fare": mini["Fare"],
        "Cabin": "",
        "Embarked": "S",
    }


def _flex_build_one_row_df(features, feature_names: list[str]):
    """
    Accept dict or list. Robust to both 4-col and full 11-col requests.
    - dict: if exactly minimal keys, expand to full; else reindex to model's feature_names.
    - list: if length == model feature count, use directly; if length==4, return two candidates.
    """
    # dict payload
    if isinstance(features, dict):
        f = features
        if set(f.keys()) == set(MINIMAL_FEATURES):
            f = _expand_minimal_to_full(f)
        return pd.DataFrame([f]).reindex(columns=feature_names)

    # list payload
    if isinstance(features, list):
        if len(features) == len(feature_names):
            return pd.DataFrame([features], columns=feature_names)

        if len(features) == 4:
            mini = dict(zip(MINIMAL_FEATURES, features))
            mini_full = _expand_minimal_to_full(mini)
            df_minimal = pd.DataFrame([mini]).reindex(
                columns=[c for c in feature_names if c in MINIMAL_FEATURES]
            )
            df_full = pd.DataFrame([mini_full]).reindex(columns=feature_names)
            return {"_candidates": [df_minimal, df_full]}

        raise ValueError(
            f"Feature length mismatch. Got {len(features)} items; "
            f"expected {len(feature_names)} or 4 (minimal)."
        )

    raise ValueError("features must be a dict or list")


def _predict_one(lm, df: pd.DataFrame) -> int:
    """Predict a single row DataFrame with either pipeline or (preproc + model)."""
    if lm.is_pipeline:
        return int(lm.obj.predict(df)[0])
    X = lm.fallback_preprocessor.transform(df)
    return int(lm.obj.predict(X)[0])


# --------------------------------------------------------------------------------------
# Error handling
# --------------------------------------------------------------------------------------
@app.errorhandler(Exception)
def handle_exception(e):
    if isinstance(e, HTTPException):
        return jsonify(error=e.description), e.code
    # dev-friendly 500; trim traceback in prod if you want
    return jsonify(error=str(e), traceback=traceback.format_exc()), 500


# --------------------------------------------------------------------------------------
# Health & metadata
# --------------------------------------------------------------------------------------
@app.get("/health")
def health():
    return jsonify(
        status="ok",
        models=list(REGISTRY.list_models().keys()),
    )


@app.get("/v1/models")
def list_models():
    return jsonify(REGISTRY.list_models())


@app.get("/v1/schema/<model_name>")
def schema(model_name: str):
    lm = REGISTRY.get(model_name)
    return jsonify(
        model=model_name,
        expected_raw_features=lm.feature_names,
        is_pipeline=lm.is_pipeline,
    )


# --------------------------------------------------------------------------------------
# Prediction (single)
# --------------------------------------------------------------------------------------
@app.post("/v1/predict/<model_name>")
def predict(model_name: str):
    lm = REGISTRY.get(model_name)
    data = request.get_json(silent=True) or {}
    if "features" not in data:
        return jsonify(error="Missing 'features'"), 400

    built = _flex_build_one_row_df(data["features"], lm.feature_names)

    # If two candidate shapes were returned (for 4-item list), try both
    candidates = built["_candidates"] if isinstance(built, dict) and "_candidates" in built else [built]

    last_err = None
    for df in candidates:
        try:
            y = _predict_one(lm, df)
            return jsonify(
                model=model_name,
                prediction=y,
                model_loaded_sec=lm.loaded_sec,
                is_pipeline=lm.is_pipeline,
            )
        except Exception as e:
            last_err = str(e)
            continue

    return jsonify(error=f"All candidate shapes failed. Last error: {last_err}"), 500


# --------------------------------------------------------------------------------------
# Prediction (batch)
# --------------------------------------------------------------------------------------
@app.post("/v1/batch_predict/<model_name>")
def batch_predict(model_name: str):
    """
    Accept JSON with either:
    - {"rows": [ {col:value, ...}, ... ]}  (list of dicts)
    - {"matrix": [ [..], [..] ]}           (list of lists, must match feature order)
    """
    lm = REGISTRY.get(model_name)
    data = request.get_json(silent=True) or {}

    if "rows" in data:
        df = pd.DataFrame(data["rows"]).reindex(columns=lm.feature_names)
    elif "matrix" in data:
        df = pd.DataFrame(data["matrix"], columns=lm.feature_names)
    else:
        return jsonify(error="Provide either 'rows' (list of dicts) or 'matrix' (list of lists)."), 400

    if lm.is_pipeline:
        preds = lm.obj.predict(df)
    else:
        X = lm.fallback_preprocessor.transform(df)
        preds = lm.obj.predict(X)

    return jsonify(
        model=model_name,
        predictions=[int(p) for p in preds],
        count=int(len(preds)),
    )


# Convenience alias used by some tests / docs
@app.post("/v1/predict/titanic")
def predict_titanic_alias():
    return predict("titanic")


# --------------------------------------------------------------------------------------
if __name__ == "__main__":
    host = REGISTRY.api_cfg.get("host", "127.0.0.1")
    port = int(REGISTRY.api_cfg.get("port", 8000))
    debug = bool(REGISTRY.api_cfg.get("debug", False))
    app.run(host=host, port=port, debug=debug)
