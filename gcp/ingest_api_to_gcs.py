# Cria em: ~/person_projects/data-platform/gcp/ingest_api_to_gcs.py
import os, json, pathlib, datetime, requests
from google.cloud import storage

PROJECT_ID  = os.environ["GOOGLE_CLOUD_PROJECT"]
BUCKET_NAME = f"{PROJECT_ID}-datalake"
BASE_URL    = "https://api.openbrewerydb.org/v1/breweries"


def fetch_api() -> list[dict]:
    """Busca todos os registros da API com paginação."""
    todos = []
    for page in range(1, 6):  # 5 páginas × 50 = 250 cervejarias
        resp = requests.get(BASE_URL, params={"per_page": 50, "page": page})
        resp.raise_for_status()
        lote = resp.json()
        if not lote:
            break
        todos.extend(lote)
        print(f"Página {page}: {len(lote)} registros")
    return todos


def save_to_tmp(data: list[dict]) -> pathlib.Path:
    """Salva NDJSON em /tmp com nome baseado na data (um objeto por linha)."""
    hoje = datetime.date.today().isoformat()
    path = pathlib.Path(f"/tmp/breweries_{hoje}.json")
    path.write_text("\n".join(json.dumps(r) for r in data))
    print(f"Salvo em {path} ({len(data)} registros)")
    return path


def upload_to_gcs(local_path: pathlib.Path) -> str:
    """Sobe o arquivo para Cloud Storage em raw/breweries/YYYY-MM-DD.json"""
    client  = storage.Client()
    bucket  = client.bucket(BUCKET_NAME)
    dest    = f"raw/breweries/{local_path.name}"
    blob    = bucket.blob(dest)
    blob.upload_from_filename(str(local_path))
    gcs_uri = f"gs://{BUCKET_NAME}/{dest}"
    print(f"Upload OK → {gcs_uri}")
    return gcs_uri


def run() -> str:
    """Função principal — será chamada pelo Airflow."""
    data    = fetch_api()
    path    = save_to_tmp(data)
    gcs_uri = upload_to_gcs(path)
    return gcs_uri    # Airflow guarda isso via XCom


if __name__ == "__main__":
    run()