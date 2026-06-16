import os
from pathlib import Path
from google.cloud import storage

PROJECT_ID   = os.environ["GOOGLE_CLOUD_PROJECT"]
BUCKET_NAME  = f"{PROJECT_ID}-datalake"


def upload_file(local_path: str, destination_blob: str) -> None:
    client = storage.Client()
    bucket = client.bucket(BUCKET_NAME)
    blob   = bucket.blob(destination_blob)
    blob.upload_from_filename(local_path)
    print(f"Uploaded {local_path} → gs://{BUCKET_NAME}/{destination_blob}")


def list_blobs(prefix: str = "") -> None:
    client = storage.Client()
    blobs  = client.list_blobs(BUCKET_NAME, prefix=prefix)
    for blob in blobs:
        print(f"  {blob.name}  ({blob.size} bytes)")


if __name__ == "__main__":
    sample = Path("/tmp/sample_data.csv")
    sample.write_text("id,name,value\n1,Alice,100\n2,Bob,200\n")

    upload_file(str(sample), "raw/sample_data.csv")

    print("\nConteúdo em raw/:")
    list_blobs(prefix="raw/")