import pandas as pd

if 'data_loader' not in globals():
    from mage_ai.data_preparation.decorators import data_loader
if 'test' not in globals():
    from mage_ai.data_preparation.decorators import test


@data_loader
def load_data_from_api(*args, **kwargs):
    """
    Loading the Uber data from the local parquet file
    """
    # Make sure this path matches exactly where your file is!
    file_path = r'C:\Users\Mansi\OneDrive\Desktop\Uber\yellow_tripdata_2026-01.parquet'
    
    # Read the parquet file into a Pandas DataFrame
    df = pd.read_parquet(file_path)
    
    return df


@test
def test_output(output, *args) -> None:
    """
    Template code for testing the output of the block.
    """
    assert output is not None, 'The output is undefined'
