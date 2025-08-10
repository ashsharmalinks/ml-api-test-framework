import pandas as pd
import pandera as pa
from pandera import Column, DataFrameSchema

def test_input_schema():
    schema = DataFrameSchema({
        "Pclass": Column(int),
        "Sex": Column(int),
        "Age": Column(float),
        "Fare": Column(float)
    })
    df = pd.DataFrame([{"Pclass": 3, "Sex": 1, "Age": 25, "Fare": 8.5}])
    schema.validate(df)
