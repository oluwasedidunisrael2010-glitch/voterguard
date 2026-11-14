import io

from fastapi.testclient import TestClient
from PIL import Image

from .conftest import make_image


def up(data, name="x.png", ctype="image/png"):
    return {"file": (name, data, ctype)}


def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200 and r.json()["status"] == "ok"


def test_analyze_valid_png(client):
    r = client.post("/analyze", files=up(make_image("a")))
    assert r.status_code == 200
    j = r.json()
    assert j["id"] >= 1 and len(j["sha256"]) == 64 and len(j["phash"]) == 16
    assert (j["width"], j["height"], j["image_format"]) == (400, 400, "PNG")
    assert j["findings"] and j["limitations"]


def test_analysis_saved_and_retrievable(client):
    j = client.post("/analyze", files=up(make_image("a"))).json()
    got = client.get(f"/analyses/{j['id']}").json()
    assert got["sha256"] == j["sha256"]
    assert any(a["id"] == j["id"] for a in client.get("/analyses").json())
    assert client.get("/analyses/9999").status_code == 404


def test_rejects_non_image(client):
    assert client.post("/analyze", files=up(b"hello world", "a.txt", "text/plain")).status_code == 400


def test_rejects_empty_file(client):
    assert client.post("/analyze", files=up(b"")).status_code == 400


def test_rejects_malformed_image(client):
    bad = b"\x89PNG\r\n\x1a\n" + b"garbage" * 50
    assert client.post("/analyze", files=up(bad)).status_code == 400


def test_rejects_truncated_image(client):
    good = make_image("a")
    assert client.post("/analyze", files=up(good[: len(good) // 2])).status_code == 400


def test_rejects_unsupported_format(client):
    gif = make_image("a", fmt="GIF")
    assert client.post("/analyze", files=up(gif, "a.gif", "image/gif")).status_code == 400


def test_rejects_oversized(client, monkeypatch):
    monkeypatch.setenv("MAX_UPLOAD_MB", "0.001")
    assert client.post("/analyze", files=up(make_image("a"))).status_code == 413


def test_persistence_after_restart(db_env):
    from app.main import app

    with TestClient(app) as c1:
        aid = c1.post("/analyze", files=up(make_image("a"))).json()["id"]
    with TestClient(app) as c2:  # simulated restart, same database file
        assert c2.get(f"/analyses/{aid}").status_code == 200


def test_duplicate_screening(client):
    base = make_image("a")
    assert client.post("/collection", data={"label": "synthetic-001"}, files=up(base)).status_code == 200

    # exact copy
    exact = client.post("/screen", files=up(base)).json()
    assert exact["candidates"] and exact["candidates"][0]["exact_match"] is True

    # resized + recompressed variant: similar, not exact
    img = Image.open(io.BytesIO(base)).resize((300, 300))
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=70)
    similar = client.post("/screen", files=up(buf.getvalue(), "v.jpg", "image/jpeg")).json()
    assert similar["candidates"], "similar image should be a candidate"
    assert similar["candidates"][0]["exact_match"] is False

    # clearly different image
    other = client.post("/screen", files=up(make_image("b"))).json()
    assert other["candidates"] == []


def test_review_flow_stats_and_audit(client):
    base = make_image("a")
    client.post("/collection", data={"label": "s1"}, files=up(base))
    mid = client.post("/screen", files=up(base)).json()["candidates"][0]["match_id"]

    bad = client.patch(f"/matches/{mid}/review", json={"disposition": "guilty", "reviewer": "r1"})
    assert bad.status_code == 422
    ok = client.patch(f"/matches/{mid}/review", json={"disposition": "not_duplicate", "reviewer": "r1", "note": "different person"})
    assert ok.status_code == 200 and ok.json()["disposition"] == "not_duplicate"
    assert client.patch("/matches/9999/review", json={"disposition": "not_duplicate", "reviewer": "r1"}).status_code == 404

    s = client.get("/stats").json()
    assert s["collection_images"] == 1 and s["match_candidates_by_disposition"] == {"not_duplicate": 1}
    actions = {e["action"] for e in client.get("/audit").json()}
    assert {"image_analyzed", "screening_run", "match_reviewed", "collection_image_added"} <= actions


def test_cors_allows_vercel_frontend(client):
    r = client.options("/analyze", headers={
        "Origin": "https://voterguard.vercel.app",
        "Access-Control-Request-Method": "POST",
    })
    assert r.headers.get("access-control-allow-origin") == "https://voterguard.vercel.app"
