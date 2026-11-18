import os
from pathlib import Path

from azure.storage.blob import BlobServiceClient
from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_FILE = PROJECT_ROOT / "data" / "all_stocks.csv"
CONTAINER_NAME = "raw-data"

load_dotenv(PROJECT_ROOT / ".env")


def upload_file() -> None:
    connection_string = os.getenv("AZURE_CONNECTION_STRING")
    if not connection_string:
        raise RuntimeError("AZURE_CONNECTION_STRING is missing. Set it in the project-root .env file.")
    if not DATA_FILE.is_file():
        raise FileNotFoundError(f"{DATA_FILE} does not exist. Run etl/extract_stock_data.py first.")

    service = BlobServiceClient.from_connection_string(connection_string)
    blob = service.get_blob_client(container=CONTAINER_NAME, blob=DATA_FILE.name)
    with DATA_FILE.open("rb") as data:
        blob.upload_blob(data, overwrite=True)
    print(f"Uploaded {DATA_FILE.name} to container {CONTAINER_NAME}.")


if __name__ == "__main__":
    upload_file()
