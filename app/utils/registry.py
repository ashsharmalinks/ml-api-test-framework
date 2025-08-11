# app/utils/registry.py
from __future__ import annotations

import json
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

import joblib
import pandas as pd
import yaml
from sklearn.pipeline import Pipeline


@dataclass
class LoadedModel:
    """Container for a loaded model + metadata."""
    name: str
    obj: Any
    feature_names: List[str]
    loaded_sec: float
    is_pipeline: bool
    fallback_preprocessor: Optional[Any]  # fitted preprocessor if obj is not a full pipeline
    train_csv_path: Path


class ModelRegistry:
    """
    Loads models defined in config/config.yaml on demand and keeps them cached.
    Config shape:
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
    """

    def __init__(self, config_path: Path):
        self.root = Path(config_path).resolve().parent.parent  # project root
        self.config_path = Path(config_path).resolve()
        with open(self.config_path, "r", encoding="utf-8") as f:
            self.config = yaml.safe_load(f) or {}

        self.api_cfg: Dict[str, Any] = self.config.get("api", {}) or {}
        self._model_cfgs: Dict[str, Dict[str, Any]] = self.config.get("models", {}) or {}
        self._cache: Dict[str, LoadedModel] = {}

    # ----------------------------- public API -----------------------------

    def list_models(self) -> Dict[str, Dict[str, str]]:
        """Return a lightweight view of configured models."""
        out: Dict[str, Dict[str, str]] = {}
        for name, cfg in self._model_cfgs.items():
            out[name] = {
                "model_path": str(self._abs(cfg.get("model_path"))),
                "feature_names_path": str(self._abs(cfg.get("feature_names_path"))) if cfg.get("feature_names_path") else "",
                "train_csv_path": str(self._abs(cfg.get("train_csv_path"))),
                "target_col": str(cfg.get("target_col", "")),
            }
        return out

    def get(self, name: str) -> LoadedModel:
        """Get a loaded model (cache hit if already loaded)."""
        if name in self._cache:
            return self._cache[name]
        if name not in self._model_cfgs:
            raise KeyError(f"Model '{name}' not found in config.")
        lm = self._load_model(name, self._model_cfgs[name])
        self._cache[name] = lm
        return lm

    # ----------------------------- internals -----------------------------

    def _load_model(self, name: str, cfg: Dict[str, Any]) -> LoadedModel:
        model_path = self._abs_required(cfg, "model_path")
        feature_names_path = self._abs_optional(cfg, "feature_names_path")
        train_csv_path = self._abs_required(cfg, "train_csv_path")
        target_col = cfg.get("target_col", None)

        # 1) load object
        t0 = time.time()
        obj = joblib.load(str(model_path))
        loaded_sec = time.time() - t0

        # 2) feature names
        feature_names = self._load_feature_names(feature_names_path, train_csv_path, target_col)

        # 3) if not a pipeline, fit a fallback preprocessor on training raw X
        is_pipeline = isinstance(obj, Pipeline)
        fallback_preprocessor = None
        if not is_pipeline:
            fallback_preprocessor = self._fit_fallback_preprocessor(train_csv_path, target_col, feature_names)

        return LoadedModel(
            name=name,
            obj=obj,
            feature_names=feature_names,
            loaded_sec=loaded_sec,
            is_pipeline=is_pipeline,
            fallback_preprocessor=fallback_preprocessor,
            train_csv_path=train_csv_path,
        )

    def _load_feature_names(
        self,
        feature_names_path: Optional[Path],
        train_csv_path: Path,
        target_col: Optional[str],
    ) -> List[str]:
        # Prefer explicit JSON file
        if feature_names_path and feature_names_path.exists():
            try:
                return json.loads(feature_names_path.read_text(encoding="utf-8"))
            except Exception as e:
                print(f"[ModelRegistry] Failed to read feature_names.json at {feature_names_path}: {e}. Falling back to CSV.")

        # Fallback: derive from train CSV (all cols except target)
        df = pd.read_csv(train_csv_path)
        cols = list(df.columns)
        if target_col and target_col in cols:
            cols.remove(target_col)
        return cols

    def _fit_fallback_preprocessor(
        self,
        train_csv_path: Path,
        target_col: Optional[str],
        feature_names: List[str],
    ):
        """
        Fit the project's preprocessing pipeline on raw X (from train CSV).
        This is used when the persisted object is NOT a full sklearn Pipeline.
        """
        # Import lazily to avoid import cycles
        from preprocessing.pipeline import get_preprocessing_pipeline  # type: ignore

        df = pd.read_csv(train_csv_path)
        X = df[feature_names].copy()
        prep = get_preprocessing_pipeline(X)
        prep.fit(X)
        return prep

    # ----------------------------- path helpers -----------------------------

    def _abs(self, maybe_path: Optional[str | Path]) -> Path:
        if not maybe_path:
            return self.root  # harmless default
        p = Path(maybe_path)
        return (self.root / p).resolve() if not p.is_absolute() else p

    def _abs_required(self, cfg: Dict[str, Any], key: str) -> Path:
        val = cfg.get(key, None)
        if not val:
            raise ValueError(f"Missing '{key}' in model config.")
        p = self._abs(val)
        if not p.exists():
            raise FileNotFoundError(f"Configured path for '{key}' does not exist: {p}")
        return p

    def _abs_optional(self, cfg: Dict[str, Any], key: str) -> Optional[Path]:
        val = cfg.get(key, None)
        if not val:
            return None
        p = self._abs(val)
        return p if p.exists() else None
