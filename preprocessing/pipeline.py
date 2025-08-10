# preprocessing/pipeline.py

import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from typing import Tuple


def split_features_by_type(df: pd.DataFrame) -> Tuple[list, list]:
    """
    Split DataFrame columns into numeric and categorical features.

    Args:
        df (pd.DataFrame): The input DataFrame.

    Returns:
        Tuple[list, list]: Lists of numeric and categorical feature names.
    """
    numeric_features = df.select_dtypes(include=["int64", "float64"]).columns.tolist()
    categorical_features = df.select_dtypes(include=["object", "category"]).columns.tolist()
    return numeric_features, categorical_features


def build_numeric_pipeline() -> Pipeline:
    """
    Build preprocessing pipeline for numeric features.

    Returns:
        Pipeline: Scikit-learn pipeline for numeric preprocessing.
    """
    return Pipeline(steps=[
        ("imputer", SimpleImputer(strategy="mean")),
        ("scaler", StandardScaler())
    ])


def build_categorical_pipeline() -> Pipeline:
    """
    Build preprocessing pipeline for categorical features.

    Returns:
        Pipeline: Scikit-learn pipeline for categorical preprocessing.
    """
    return Pipeline(steps=[
        ("imputer", SimpleImputer(strategy="most_frequent")),
        ("encoder", OneHotEncoder(handle_unknown="ignore"))
    ])


def get_preprocessing_pipeline(df: pd.DataFrame) -> ColumnTransformer:
    """
    Constructs a ColumnTransformer with preprocessing steps for numeric and categorical features.

    Args:
        df (pd.DataFrame): The input dataset to analyze feature types.

    Returns:
        ColumnTransformer: A transformer that can be applied to training or test datasets.
    """
    numeric_features, categorical_features = split_features_by_type(df)

    preprocessor = ColumnTransformer(transformers=[
        ("num", build_numeric_pipeline(), numeric_features),
        ("cat", build_categorical_pipeline(), categorical_features)
    ])

    return preprocessor
