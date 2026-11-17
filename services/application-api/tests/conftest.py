import os

import pytest
from application_api import bootstrap
from application_api.config import FIELDS


@pytest.fixture(autouse=True)
def isolate_configuration(monkeypatch, tmp_path):
    for name in os.environ:
        if name.lower() in FIELDS:
            monkeypatch.delenv(name)
    original = bootstrap.load_config
    monkeypatch.setattr(bootstrap, "load_config", lambda: original(tmp_path / "missing.env"))
