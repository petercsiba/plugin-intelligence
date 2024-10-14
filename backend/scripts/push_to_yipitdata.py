import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
import boto3
from datetime import datetime
import os

from dotenv import load_dotenv
from playhouse.shortcuts import model_to_dict
from supawee.client import connect_to_postgres

from supabase.models.base import BaseGoogleWorkspace

# AWS S3 configuration
S3_BUCKET = 'plugin-intelligence-yipit-data'
S3_FEED_NAME = 'test-feed'
# rest of credentials in ~/.aws/credentials
AWS_PROFILE = 'PowerUserAccess-831154875375'

# LOGIC
MODEL = BaseGoogleWorkspace
P_DATE = '2024-10-14'


load_dotenv()
YES_I_AM_CONNECTING_TO_PROD_DATABASE_URL = os.environ.get(
    "YES_I_AM_CONNECTING_TO_PROD_DATABASE_URL"
)


def peewee_to_parquet(model, parquet_file_path, p_date_str: str):
    """Convert Peewee model data to Parquet format.

    NOTE: The entire select query result is loaded into memory (with all the python and pandas overhead ofc).
    """

    with connect_to_postgres(YES_I_AM_CONNECTING_TO_PROD_DATABASE_URL):
        print(f"Fetching data for {model._meta.table_name} for p_date: {p_date_str}")
        query = model.select().where(model.p_date == p_date_str)

        # Convert to a list of dictionaries
        data = [model_to_dict(row) for row in query]

    # Convert to pandas DataFrame
    df = pd.DataFrame(data)

    # Convert DataFrame to PyArrow Table
    table = pa.Table.from_pandas(df)

    print(f"Writing data to {parquet_file_path}")
    pq.write_table(table, parquet_file_path, compression='snappy')


def upload_to_s3(file_path, s3_key):
    """Upload file to S3 bucket."""
    session = boto3.Session(profile_name=AWS_PROFILE)
    s3 = session.client('s3')
    file_size_in_mb = round(os.path.getsize(file_path) / (1024 * 1024), 1)
    print(f"Uploading file with size {file_size_in_mb}MB to s3://{S3_BUCKET}/{s3_key}")
    s3.upload_file(file_path, S3_BUCKET, s3_key)


def main():
    parquet_file_path = f'{MODEL._meta.table_name}.parquet'

    # Convert Peewee model data to Parquet
    peewee_to_parquet(MODEL, parquet_file_path, p_date_str=P_DATE)

    # Prepare S3 key
    current_date = datetime.now().strftime('%Y-%m-%d')
    s3_key = f'feeds/{S3_FEED_NAME}/v1/dt={current_date}/{os.path.basename(parquet_file_path)}'

    # Upload to S3
    upload_to_s3(parquet_file_path, s3_key)

    print(f"File uploaded successfully to s3://{S3_BUCKET}/{s3_key}")

    os.remove(parquet_file_path)


if __name__ == "__main__":
    main()
