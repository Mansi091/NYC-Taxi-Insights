import pandas as pd
import os

if 'data_loader' not in globals():
    from mage_ai.data_preparation.decorators import data_loader
if 'test' not in globals():
    from mage_ai.data_preparation.decorators import test

@data_loader
def load_taxi_data(*args, **kwargs):
    file_path = 'data/yellow_tripdata_2026-01.parquet'
    
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File {file_path} not found. Please download the dataset and place it in the data/ folder.")
        
    df = pd.read_parquet(file_path)
    return df

@test
def test_output(output, *args) -> None:
    assert output is not None, 'The output is undefined'
