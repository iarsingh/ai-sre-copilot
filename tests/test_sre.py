from fastapi.testclient import TestClient
from sre.main import app

def test_memory_hypothesis_and_latest_refusal():
    client = TestClient(app)
    memory = client.post("/investigate", json={"reason": "OOMKilled", "memory_percent": 95, "image": "billing:1.4.2"}).json()
    assert memory["hypothesis"] == "memory-limit"
    assert memory["confirmed_root_cause"] is False
    assert memory["paged"] is False
    latest = client.post("/investigate", json={"reason": "OOMKilled", "memory_percent": 95, "image": "billing:latest"}).json()
    assert latest["refused"] is True
