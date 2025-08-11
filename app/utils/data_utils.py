import pandas as pd
import json
from pathlib import Path

def load_feature_names(model_name: str):
    """Load feature names from a JSON file in model/<model_name>/feature_names.json"""
    feature_file = Path(f"model/{model_name}/feature_names.json")
    if not feature_file.exists():
        raise FileNotFoundError(f"Feature names file not found for {model_name}: {feature_file}")
    with open(feature_file, "r") as f:
        return json.load(f)

def build_one_row_df(features, feature_names):
    """Convert dict or list into a one-row DataFrame with correct columns."""
    if isinstance(features, dict):
        df = pd.DataFrame([features]).reindex(columns=feature_names)
    elif isinstance(features, list):
        if len(features) != len(feature_names):
            raise ValueError(f"Expected {len(feature_names)} features, got {len(features)}")
        df = pd.DataFrame([features], columns=feature_names)
    else:
        raise ValueError("Features must be a dict or list.")
    return df
