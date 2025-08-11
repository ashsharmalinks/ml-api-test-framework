# tests/test_model.py
from pathlib import Path
import joblib
import pandas as pd
from sklearn.pipeline import Pipeline
from sklearn.metrics import accuracy_score

ROOT = Path(__file__).resolve().parents[1]
MODEL_PATH = ROOT / "model" / "ash_test_model" / "ash_test_model.pkl"
DATA_PATH = ROOT / "data" / "raw" / "train.csv"

def test_model_accuracy():
    model = joblib.load(MODEL_PATH)
    df = pd.read_csv(DATA_PATH)

    X = df.drop("Survived", axis=1)
    y = df["Survived"]

    if isinstance(model, Pipeline):
        # Model already contains preprocessing – pass RAW features
        preds = model.predict(X)
    else:
        # Legacy estimator – preprocess first
        from preprocessing.pipeline import get_preprocessing_pipeline
        pre = get_preprocessing_pipeline(X)
        Xp = pre.fit_transform(X)
        preds = model.predict(Xp)

    assert accuracy_score(y, preds) > 0.7
