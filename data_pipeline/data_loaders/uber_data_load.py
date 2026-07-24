import pandas as pd

if 'data_loader' not in globals():
    from mage_ai.data_preparation.decorators import data_loader
if 'test' not in globals():
    from mage_ai.data_preparation.decorators import test

@data_loader
def load_data_from_api(*args, **kwargs):
    file_path = r'../data/yellow_tripdata_2026-01.parquet'
    df = pd.read_parquet(file_path)
    return df

@test
def test_output(output, *args) -> None:
    assert output is not None, 'The output is undefined'
