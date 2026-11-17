import pytest
from generation_service.bootstrap import Settings


@pytest.fixture(autouse=True)
def isolate_settings(monkeypatch, tmp_path):
    monkeypatch.setitem(Settings.model_config, "env_file", tmp_path / "missing.env")
