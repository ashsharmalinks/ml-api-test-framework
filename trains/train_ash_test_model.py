# train_ash_test_model.py
import os
import json
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
import joblib
import mlflow
import matplotlib.pyplot as plt
import seaborn as sns
import tempfile

from preprocessing.pipeline import get_preprocessing_pipeline

# Log runs locally (no server needed)
mlflow.set_tracking_uri("file:./mlruns")
mlflow.set_experiment("titanic_model_experiment")

os.makedirs("../model", exist_ok=True)

# 1) Load raw data
df = pd.read_csv("data/raw/train.csv")
X = df.drop(columns=["Survived"])
y = df["Survived"]

# 2) Build preprocessing
preprocessor = get_preprocessing_pipeline(X)

# 3) Build a full pipeline: raw -> preprocess -> model
clf = RandomForestClassifier(n_estimators=100, random_state=42)
pipe = Pipeline([("prep", preprocessor), ("clf", clf)])

# 4) Train/test split on RAW X (pipeline will handle preprocessing)
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

with mlflow.start_run():
    mlflow.set_tag("env", "local")
    mlflow.set_tag("framework", "sklearn")
    mlflow.set_tag("project", "titanic_model")

    pipe.fit(X_train, y_train)
    preds = pipe.predict(X_test)
    acc = accuracy_score(y_test, preds)

    mlflow.log_param("n_estimators", 100)
    mlflow.log_metric("accuracy", acc)

    # Save pipeline (includes preprocessing + model)
    model_path = "model/ash_test_model/ash_test_model.pkl"  # <-- your new name
    joblib.dump(pipe, model_path)
    mlflow.log_artifact(model_path)

    # Save feature names (raw column order) for API to build DataFrame
    feature_names = list(X.columns)
    with open("model/ash_test_model/feature_names.json", "w") as f:
        json.dump(feature_names, f)
    mlflow.log_artifact("model/ash_test_model/feature_names.json")

    # Report
    print(f"✅ Trained pipeline accuracy: {acc:.2f}")
    print("\n📊 Classification Report:\n", classification_report(y_test, preds))

    # Confusion matrix
    cm = confusion_matrix(y_test, preds)
    plt.figure(figsize=(6, 4))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
                xticklabels=["Not Survived", "Survived"],
                yticklabels=["Not Survived", "Survived"])
    plt.xlabel("Predicted"); plt.ylabel("Actual"); plt.title("Confusion Matrix")
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
        plt.savefig(tmp.name)
        mlflow.log_artifact(tmp.name, artifact_path="plots")
    plt.close()
