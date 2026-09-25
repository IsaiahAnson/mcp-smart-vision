"""Auth, rate-limit and IP-allowlist tests for http_server.

The real tools package needs Windows-only GUI libraries, so a stub `tools`
module is installed before http_server is imported. Run with:

    pip install fastapi httpx pytest
    pytest tests
"""
import importlib
import json
import sys
import types
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

GOOD_KEY = "k" * 32
PLACEHOLDER = "replace-with-your-generated-key"


@pytest.fixture
def server(monkeypatch, tmp_path):
    """Return a factory that imports http_server with the given config.json."""
    stub = types.ModuleType("tools")
    stub.ALL_TOOLS = [{
        "name": "echo",
        "description": "test tool",
        "parameters": {},
        "function": lambda **kw: {"success": True, "kw": kw},
    }]
    monkeypatch.setitem(sys.modules, "tools", stub)
    monkeypatch.chdir(tmp_path)  # keep the log file out of the repo

    config_path = ROOT / "config.json"
    backup = config_path.read_text() if config_path.exists() else None

    def load(config):
        if config is None:
            config_path.unlink(missing_ok=True)
        else:
            config_path.write_text(json.dumps(config))
        sys.modules.pop("http_server", None)
        return TestClient(importlib.import_module("http_server").app)

    yield load

    if backup is None:
        config_path.unlink(missing_ok=True)
    else:
        config_path.write_text(backup)
    sys.modules.pop("http_server", None)


def test_missing_config_refuses_placeholder_key(server):
    client = server(None)
    r = client.get("/api/v1/tools", headers={"X-API-Key": PLACEHOLDER})
    assert r.status_code == 503


def test_placeholder_key_in_config_is_refused(server):
    client = server({"api_key": PLACEHOLDER})
    assert client.get("/api/v1/tools", headers={"X-API-Key": PLACEHOLDER}).status_code == 503


def test_short_key_is_refused(server):
    client = server({"api_key": "short"})
    assert client.get("/api/v1/tools", headers={"X-API-Key": "short"}).status_code == 503


def test_valid_key_required(server):
    client = server({"api_key": GOOD_KEY})
    assert client.get("/api/v1/tools", headers={"X-API-Key": GOOD_KEY}).status_code == 200
    assert client.get("/api/v1/tools", headers={"X-API-Key": "wrong"}).status_code == 401
    assert client.get("/api/v1/tools").status_code == 401
    r = client.post("/api/v1/tools/echo", json={"parameters": {"a": 1}}, headers={"X-API-Key": GOOD_KEY})
    assert r.status_code == 200
    assert r.json()["result"]["kw"] == {"a": 1}


def test_rate_limit(server):
    client = server({"api_key": GOOD_KEY, "rate_limit": {"requests_per_minute": 3}})
    codes = [client.get("/health").status_code for _ in range(5)]
    assert codes == [200, 200, 200, 429, 429]


def test_ip_allowlist(server):
    # TestClient reports its host as "testclient".
    assert server({"api_key": GOOD_KEY, "allowed_ips": ["10.0.0.5"]}).get("/health").status_code == 403
    assert server({"api_key": GOOD_KEY, "allowed_ips": ["testclient"]}).get("/health").status_code == 200
