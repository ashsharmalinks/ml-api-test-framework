import pandas as pd

def preprocess_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Cleans and encodes input Titanic dataset.
    - Fills missing Age values with mean.
    - Maps 'Sex' to numerical (male: 0, female: 1).

    Args:
        df (pd.DataFrame): Raw input dataframe.

    Returns:
        pd.DataFrame: Preprocessed dataframe.
    """
    df = df.copy()
    df["Age"].fillna(df["Age"].mean().astype("float"))
    df["Sex"] = df["Sex"].map({"male": 0, "female": 1})
    df["Pclass"] = df["Pclass"].astype("int64")  # Optional, for clarity

    return df

def load_and_preprocess_data(file_path: str) -> tuple[pd.DataFrame, pd.Series]:
    """
    Loads CSV file, applies preprocessing, and returns features and target.

    Args:
        file_path (str): Path to Titanic CSV file.

    Returns:
        Tuple of:
            - X (pd.DataFrame): Feature matrix.
            - y (pd.Series): Target vector.
    """
    df = pd.read_csv(file_path)
    df = preprocess_data(df)
    X = df[["Pclass", "Sex", "Age", "Fare"]]
    y = df["Survived"]
    return X, y

if __name__ == "__main__":
    # Example usage if run directly
    X, y = load_and_preprocess_data("data/train.csv")
    print("✅ Preprocessed data loaded")
    print(X.head())
