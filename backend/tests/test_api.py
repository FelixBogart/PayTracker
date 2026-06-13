import json
from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_create_shift_monkeypatch(monkeypatch):
    sample_payload = {
        "shift_date": "2026-06-01",
        "points": 100,
        "tipped_hours": 2.0,
        "untipped_hours": 1.0,
        "point_value": 0.007,
    }

    def fake_insert(payload):
        return [{"id": "fake-uuid", **payload}]

    monkeypatch.setattr("app.db.insert_shift", fake_insert)

    resp = client.post("/shifts/", json=sample_payload)
    assert resp.status_code == 200
    body = resp.json()
    assert "inserted" in body
    assert isinstance(body["inserted"], list)
    assert body["inserted"][0]["id"] == "fake-uuid"


def test_get_shifts_monkeypatch(monkeypatch):
    def fake_get(start, end):
        return [
            {
                "id": "r1",
                "shift_date": "2026-06-01",
                "points": 1200,
                "tipped_hours": 4.5,
                "untipped_hours": 3.0,
                "point_value": 0.007,
            }
        ]

    monkeypatch.setattr("app.db.get_shifts_between", fake_get)

    resp = client.get("/shifts/2026-06-01/2026-06-15")
    assert resp.status_code == 200
    body = resp.json()
    assert "rows" in body
    assert len(body["rows"]) == 1
    row = body["rows"][0]
    assert row["points"] == 1200
    assert "total_gross" in row


def test_summary_monkeypatch(monkeypatch):
    monkeypatch.setattr("app.db.summary_for_month", lambda ym: {"total_gross": 1000.0, "total_hours": 100.0, "avg_hourly": 10.0})

    resp = client.get("/summary/2026-06")
    assert resp.status_code == 200
    body = resp.json()
    assert body["avg_hourly"] == 10.0
