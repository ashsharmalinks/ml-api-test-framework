# validation/validate_data.py
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
import great_expectations as ge

import pandas as pd

# Great Expectations (modern Validator API)
from great_expectations.core.batch import Batch
from great_expectations.execution_engine.pandas_execution_engine import PandasExecutionEngine
from great_expectations.validator.validator import Validator


# -------------------------- Config --------------------------
REPO_ROOT = Path(__file__).resolve().parents[1]
LOCAL_DEFAULT_CSV = REPO_ROOT / "data" / "raw" / "train.csv"

# Expectations target columns in the *raw Titanic* CSV
REQUIRED_COLUMNS = ["Pclass", "Sex", "Age", "Fare"]


# ---------------------- Helper functions --------------------
def load_dataframe(use_s3: bool, s3_uri: str | None) -> pd.DataFrame:
    """Load the Titanic dataframe either from local path or S3."""
    if use_s3:
        if s3_uri is None:
            raise ValueError("When --use-s3 is set you must provide --s3-uri like s3://bucket/path/train.csv")
        # Requires: pip install s3fs
        try:
            import s3fs  # noqa: F401  (import just to check it's installed)
        except Exception as e:
            raise RuntimeError("Reading from S3 requires the 's3fs' package. Install it via: pip install s3fs") from e
        df = pd.read_csv(s3_uri)
    else:
        csv_path = os.fspath(LOCAL_DEFAULT_CSV)
        if not os.path.exists(csv_path):
            raise FileNotFoundError(f"Local CSV not found: {csv_path}")
        df = pd.read_csv(csv_path)
    return df


def assert_columns_present(df: pd.DataFrame, columns: list[str]) -> None:
    missing = [c for c in columns if c not in df.columns]
    if missing:
        raise ValueError(f"Input CSV is missing required columns: {missing}. Available columns: {list(df.columns)}")


def run_expectations(df: pd.DataFrame) -> dict:
    """
    Build a minimal in-memory GE Validator and run expectations against the DataFrame.
    Returns the validation result as a dict.
    """
    ge.get_context(mode="ephemeral")
    engine = PandasExecutionEngine()
    batch = Batch(data=df)
    validator = Validator(execution_engine=engine, batches=[batch])

    # --- Expectations (tweak as needed) ---
    # 1) Age mostly present
    validator.expect_column_values_to_not_be_null("Age", mostly=0.8)

    # 2) Fare within a realistic range
    validator.expect_column_values_to_be_between("Fare", min_value=0, max_value=600)

    # 3) Sex values are male/female (raw Titanic csv uses strings)
    validator.expect_column_values_to_be_in_set("Sex", ["male", "female"])

    # You can add more, e.g.
    # validator.expect_column_values_to_be_between("Age", min_value=0, max_value=100)
    # validator.expect_table_row_count_to_be_between(min_value=100, max_value=100000)

    # Run validation
    result = validator.validate()
    # Convert to plain dict for printing/saving
    try:
        return result.to_json_dict()
    except AttributeError:
        # Very old GE objects sometimes are already dict-like
        return dict(result)


def print_summary(result_dict: dict) -> None:
    success = bool(result_dict.get("success", False))
    stats = result_dict.get("statistics", {}) or {}
    n_exp = stats.get("evaluated_expectations", "n/a")
    n_succ = stats.get("successful_expectations", "n/a")
    pct = stats.get("success_percent", "n/a")

    if success:
        print(f"✅ Data validation passed! ({n_succ}/{n_exp} expectations, success={pct}%)")
    else:
        print(f"❌ Data validation failed. ({n_succ}/{n_exp} expectations, success={pct}%)")
        # Print first few failed expectations for quick debugging
        for res in (result_dict.get("results") or [])[:5]:
            if not res.get("success", False):
                exp_type = res.get("expectation_config", {}).get("expectation_type")
                kwargs = res.get("expectation_config", {}).get("kwargs", {})
                print(f"  - Failed: {exp_type} with kwargs={kwargs}")


# --------------------------- Main ---------------------------
def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate raw Titanic data with Great Expectations (in-memory).")
    parser.add_argument("--use-s3", action="store_true", help="Read CSV from S3 (requires s3fs).")
    parser.add_argument("--s3-uri", type=str, default=None, help="S3 URI for the CSV, e.g. s3://bucket/path/train.csv")
    parser.add_argument("--save-json", type=Path, default=REPO_ROOT / "reports" / "ge_validation_result.json",
                        help="Where to save the validation result JSON.")
    args = parser.parse_args(argv)

    # Ensure reports dir exists
    args.save_json.parent.mkdir(parents=True, exist_ok=True)

    # Load
    df = load_dataframe(use_s3=args.use_s3, s3_uri=args.s3_uri)

    # Basic schema presence check (fast fail)
    assert_columns_present(df, REQUIRED_COLUMNS)

    # Run GE
    result = run_expectations(df)

    # Save and print
    with open(args.save_json, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)
    print(f"📝 Validation report saved to: {args.save_json}")

    print_summary(result)

    # Exit code for CI
    return 0 if result.get("success", False) else 1


if __name__ == "__main__":
    sys.exit(main())
