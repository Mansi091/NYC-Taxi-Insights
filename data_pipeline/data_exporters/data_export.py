import os
from mage_ai.data_preparation.decorators import data_exporter

if 'data_exporter' not in globals():
    from mage_ai.data_preparation.decorators import data_exporter

@data_exporter
def export_data_to_big_query(data, **kwargs) -> None:
    project_id = os.getenv("GOOGLE_CLOUD_PROJECT", "your-gcp-project-id")
    dataset_id = "uber_dataset"

    if project_id == "your-gcp-project-id":
        print("WARNING: Default project ID used. Please set GOOGLE_CLOUD_PROJECT env var.")

    for table_name, df in data.items():
        table_id = f"{project_id}.{dataset_id}.{table_name}"
        print(f"Exporting data to BigQuery table: {table_id} (Rows: {len(df)})")
        
        try:
            df.to_gbq(
                destination_table=table_id,
                project_id=project_id,
                if_exists='replace',
            )
            print(f"Successfully exported {table_name}")
        except Exception as e:
            print(f"Failed to export {table_name} to BigQuery: {e}")
            raise e
