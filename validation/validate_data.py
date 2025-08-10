import os
import pandas as pd
import great_expectations as ge
# from aws_utils.env_loader import AWS_CONFIG

# Local or S3 flag
USE_S3 = False



if USE_S3:
    s3_path = "s3://your-bucket-name/data/train.csv"
    df = pd.read_csv(s3_path)  # requires s3fs to be installed
else:
    local_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "train.csv"))
    df = pd.read_csv(local_path)
    
# Convert to Great Expectations DataFrame
ge_df = ge.from_pandas(df)

# Expectations
ge_df.expect_column_values_to_not_be_null("Age", mostly=0.8)
ge_df.expect_column_values_to_be_between("Fare", min_value=0, max_value=600)
ge_df.expect_column_values_to_be_in_set("Sex", ["male", "female"])

# Validate
results = ge_df.validate()

# Output
if results["success"]:
    print("✅ Data validation passed!")
else:
    print("❌ Data validation failed:")
    print(results)
