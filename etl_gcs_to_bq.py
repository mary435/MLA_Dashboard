from pathlib import Path
import pandas as pd
from prefect import flow, task
from prefect_gcp.cloud_storage import GcsBucket
from prefect_gcp import GcpCredentials

@task(retries=3)
def extract_from_gcs(file: str) -> Path:
    """Download file data from GCS"""
    gcs_path = f"data/{file}.parquet"
    gcs_block = GcsBucket.load("mla-bucket")
    gcs_block.get_directory(from_path=gcs_path, local_path=f".")
    return Path(f"{gcs_path}")

@task(retries=3)
def transform(path: Path) -> pd.DataFrame:
    """Data cleaning example"""
    df = pd.read_parquet(path) 
    #print(f"rows processed: {df['id'].count()}")
    return df

@task()
def write_bq(df: pd.DataFrame, file:str) -> None:
    """Write DataFrame to BiqQuery"""

    gcp_credentials_block = GcpCredentials.load("mla-bucket-creds")

    table = f'mla_bq_zoom.{file}'

    df.to_gbq(
        destination_table=table,
        project_id="mla-dashboard-zoom",
        credentials=gcp_credentials_block.get_credentials_from_service_account(),
        chunksize=500_000,
        #if_exists="append",
        if_exists="replace",
    )


@flow()
def etl_gcs_to_bq(file: str):
    """Main ETL flow to load data into Big Query"""

    path = extract_from_gcs(file)
    df = transform(path)
    write_bq(df, file)
    return len(df)


@flow()
def etl_parent_flow( files: list[str]):
    rows = 0
    for file in files:
        rows += etl_gcs_to_bq(file)
    print(f"Total rows processed: {rows}")


if __name__ == "__main__":
    files = ['categories', 'best_sellers', 'trends', 'items', 'products', 'subcategories', 'hist_trends']
    etl_parent_flow(files)
    print(f"Total files processed: {files}")