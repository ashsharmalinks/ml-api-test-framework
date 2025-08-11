# tests/test_drift.py
import pandas as pd
from evidently.report import Report
from evidently.metric_preset import DataDriftPreset

TRAIN_DATA_PATH = "data/raw/train.csv"
CURRENT_DATA_PATH = "data/processed/current.csv"  # Replace with your latest batch

# Threshold: percentage of features allowed to drift before failing test
DRIFT_THRESHOLD = 0.3  # 30% of features

def test_data_drift():
    # Load reference (training) and current datasets
    reference_df = pd.read_csv(TRAIN_DATA_PATH)
    current_df = pd.read_csv(CURRENT_DATA_PATH)

    # Align columns
    common_cols = list(set(reference_df.columns) & set(current_df.columns))
    reference_df = reference_df[common_cols]
    current_df = current_df[common_cols]

    # Generate Evidently drift report
    drift_report = Report(metrics=[DataDriftPreset(drift_share=0.3)])  # adjust threshold
    drift_report.run(reference_data=reference_df, current_data=current_df)

    # Extract drift metrics
    report_dict = drift_report.as_dict()
    drift_metrics = report_dict['metrics'][0]['result']
    drift_share = drift_metrics['drift_share']

    print(f"📊 Drift share: {drift_share:.2f}")
    assert drift_share <= DRIFT_THRESHOLD, (
        f"❌ Data drift detected! {drift_share*100:.1f}% features drifted, "
        f"threshold is {DRIFT_THRESHOLD*100:.0f}%."
    )
