import yaml
import joblib
from pathlib import Path


def load_model(model_name: str):
    """Load model by name from config file."""
    config_path = Path(__file__).resolve().parent.parent.parent / "config" / "config.yaml"
    with open(config_path, "r") as f:
        config = yaml.safe_load(f)

    if model_name not in config["models"]:
        raise ValueError(f"Model '{model_name}' not found in config.yaml")

    model_path = Path(config["models"][model_name]["path"])
    if not model_path.exists():
        raise FileNotFoundError(f"Model file not found: {model_path}")

    return joblib.load(model_path)
