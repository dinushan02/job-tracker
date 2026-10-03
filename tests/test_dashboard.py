from datetime import date, timedelta


def make(client, **overrides):
    data = {"company": "Acme", "role": "Python Developer"}
    data.update(overrides)
    return client.post("/applications", json=data)


def test_stats_empty(client):
    r = client.get("/dashboard/stats")
    assert r.status_code == 200
    body = r.json()
    assert body["total"] == 0
    assert body["response_rate"] == 0.0
    assert len(body["per_week"]) == 8


def test_stats_counts_and_response_rate(client):
    make(client)
    make(client, company="B", status="interview")
    make(client, company="C", status="rejected")
    make(client, company="D", status="offer")
    body = client.get("/dashboard/stats").json()
    assert body["total"] == 4
    assert body["by_status"]["applied"] == 1
    assert body["by_status"]["interview"] == 1
    assert body["response_rate"] == 0.75


def test_stats_per_week(client):
    make(client)
    old = str(date.today() - timedelta(weeks=3))
    make(client, company="Old", applied_date=old)
    counts = [w["count"] for w in client.get("/dashboard/stats").json()["per_week"]]
    assert counts[-1] == 1
    assert counts[-4] == 1
    assert sum(counts) == 2


def test_stats_require_token(anon_client):
    assert anon_client.get("/dashboard/stats").status_code == 401