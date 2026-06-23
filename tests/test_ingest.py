# ~/person_projects/data-platform/tests/test_ingest.py
import json, sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent.parent / "gcp"))

from ingest_api_to_gcs import fetch_api, save_to_tmp


def test_fetch_api_retorna_lista():
    """API deve retornar uma lista com pelo menos 1 elemento."""
    resultado = fetch_api()
    assert isinstance(resultado, list)
    assert len(resultado) > 0


def test_fetch_api_campos_obrigatorios():
    """Cada registro deve ter id, name e brewery_type."""
    resultado = fetch_api()
    for item in resultado[:5]:   # checa os 5 primeiros
        assert "id" in item
        assert "name" in item
        assert "brewery_type" in item


def test_save_to_tmp_cria_arquivo(tmp_path, monkeypatch):
    """save_to_tmp deve criar um arquivo JSON válido em /tmp."""
    # monkeypatch: redireciona /tmp para pasta temporária do pytest
    import ingest_api_to_gcs as m
    monkeypatch.setattr(m.pathlib.Path, "__new__", lambda cls, *a, **k: tmp_path / a[0].split("/")[-1])

    data   = [{"id": "1", "name": "Test", "brewery_type": "micro"}]
    caminho = m.save_to_tmp(data)
    conteudo = json.loads(caminho.read_text())
    assert conteudo[0]["id"] == "1"
