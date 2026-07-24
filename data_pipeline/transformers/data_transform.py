import pandas as pd

if 'transformer' not in globals():
    from mage_ai.data_preparation.decorators import transformer
if 'test' not in globals():
    from mage_ai.data_preparation.decorators import test

@transformer
def transform(df, *args, **kwargs):
    df = df.dropna()
    df = df.drop_duplicates().reset_index(drop=True)
    df['trip_id'] = df.index
    
    payment_dim = df[['payment_type']].copy()
    payment_dim = payment_dim.drop_duplicates().reset_index(drop=True)
    payment_dim.insert(0, "payment_key", payment_dim.index + 1)
    payment_mapping = {
        1: "Credit card",
        2: "Cash",
        3: "No charge",
        4: "Dispute",
        5: "Unknown",
        6: "Voided trip"
    }
    payment_dim["payment_name"] = payment_dim["payment_type"].map(payment_mapping)
    
    datetime_dim = df[['tpep_pickup_datetime']].copy()
    datetime_dim = datetime_dim.drop_duplicates().reset_index(drop=True)
    datetime_dim.insert(0, "datetime_key", datetime_dim.index + 1)
    datetime_dim["tpep_pickup_datetime"] = pd.to_datetime(datetime_dim["tpep_pickup_datetime"])
    datetime_dim["year"] = datetime_dim["tpep_pickup_datetime"].dt.year
    datetime_dim["month"] = datetime_dim["tpep_pickup_datetime"].dt.month
    datetime_dim["day"] = datetime_dim["tpep_pickup_datetime"].dt.day
    datetime_dim["hour"] = datetime_dim["tpep_pickup_datetime"].dt.hour
    datetime_dim["minute"] = datetime_dim["tpep_pickup_datetime"].dt.minute
    datetime_dim["weekday"] = datetime_dim["tpep_pickup_datetime"].dt.day_name()
    datetime_dim["quarter"] = datetime_dim["tpep_pickup_datetime"].dt.quarter
    
    location_ids = pd.concat([df["PULocationID"], df["DOLocationID"]]).drop_duplicates().reset_index(drop=True)
    location_dim = pd.DataFrame({"location_id": location_ids})
    location_dim.insert(0, "location_key", location_dim.index + 1)
    
    vendor_dim = df[['VendorID']].copy()
    vendor_dim = vendor_dim.drop_duplicates().reset_index(drop=True)
    vendor_dim.insert(0, "vendor_key", vendor_dim.index + 1)
    vendor_mapping = {
        1: "Creative Mobile Technologies",
        2: "VeriFone Inc."
    }
    vendor_dim["vendor_name"] = vendor_dim["VendorID"].map(vendor_mapping)
    
    rate_dim = df[['RatecodeID']].copy()
    rate_dim = rate_dim.drop_duplicates().reset_index(drop=True)
    rate_dim.insert(0, "rate_code_key", rate_dim.index + 1)
    rate_mapping = {
        1.0: "Standard Rate",
        2.0: "JFK",
        3.0: "Newark",
        4.0: "Nassau/Westchester",
        5.0: "Negotiated Fare",
        6.0: "Group Ride"
    }
    rate_dim["rate_name"] = rate_dim["RatecodeID"].map(rate_mapping)
    
    fact_table = df.copy()
    fact_table = fact_table.merge(vendor_dim, on="VendorID", how="left")
    fact_table = fact_table.merge(datetime_dim[["datetime_key", "tpep_pickup_datetime"]], on="tpep_pickup_datetime", how="left")
    fact_table = fact_table.merge(payment_dim, on="payment_type", how="left")
    
    fact_table = fact_table.merge(location_dim, left_on="PULocationID", right_on="location_id", how="left")
    fact_table.rename(columns={"location_key": "pickup_location_key"}, inplace=True)
    fact_table.drop(columns=["location_id"], inplace=True)
    
    fact_table = fact_table.merge(location_dim, left_on="DOLocationID", right_on="location_id", how="left")
    fact_table.rename(columns={"location_key": "dropoff_location_key"}, inplace=True)
    fact_table.drop(columns=["location_id"], inplace=True)
    
    fact_table = fact_table[[
        "vendor_key",
        "datetime_key",
        "payment_key",
        "pickup_location_key",
        "dropoff_location_key",
        "passenger_count",
        "trip_distance",
        "fare_amount",
        "tip_amount",
        "total_amount"
    ]]
    
    return {
        "datetime_dim": datetime_dim,
        "payment_dim": payment_dim,
        "location_dim": location_dim,
        "vendor_dim": vendor_dim,
        "rate_dim": rate_dim,
        "fact_table": fact_table
    }

@test
def test_output(output, *args) -> None:
    assert output is not None, 'The output is undefined'
    assert 'fact_table' in output, 'Fact table is missing from output'
