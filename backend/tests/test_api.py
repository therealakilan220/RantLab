"""Contract tests in stub mode. Run:  cd backend && pytest"""


def rant(client, text):
    r = client.post("/api/rant", json={"text": text})
    assert r.status_code == 200, r.text
    return r.json()


def test_health(client):
    body = client.get("/api/health").json()
    assert body["status"] == "ok"


def test_text_rant_matches_contract(client):
    card = rant(client, "The library Wi-Fi keeps dropping every afternoon.")
    assert card["input_type"] == "text"
    assert len(card["fixes"]) == 3
    for fix in card["fixes"]:
        assert fix["cost"] in ("free", "cheap", "budget")
        assert fix["timeframe"] in ("today", "this_week", "this_semester")
    assert client.get(f"/api/cards/{card['id']}").json()["id"] == card["id"]


def test_voice_rant(client):
    r = client.post("/api/rant", files={"audio": ("rant.webm", b"x" * 5000, "audio/webm")})
    assert r.status_code == 200, r.text
    assert r.json()["input_type"] == "voice"


def test_errors(client):
    assert client.post("/api/rant", json={"text": "   "}).json()["error"]["code"] == "empty_text"
    assert client.post("/api/rant", json={}).json()["error"]["code"] == "bad_input"
    assert client.post("/api/rant", json={"text": "x" * 2001}).status_code == 413
    tiny = client.post("/api/rant", files={"audio": ("r.webm", b"x", "audio/webm")})
    assert tiny.json()["error"]["code"] == "empty_audio"
    assert client.get("/api/cards/c_nope").status_code == 404


def test_board_groups_similar_complaints(client):
    a = rant(client, "The library Wi-Fi keeps dropping every afternoon during study hours.")
    b = rant(client, "Library Wi-Fi keeps dropping every afternoon again, study hours are ruined.")
    c = rant(client, "Canteen food is always cold and overpriced at lunch.")
    clusters = client.get("/api/board").json()["clusters"]
    where = {m["card_id"]: k["id"] for k in clusters for m in k["complaints"]}
    assert where[a["id"]] == where[b["id"]]
    assert where[a["id"]] != where[c["id"]]
    counts = [k["count"] for k in clusters]
    assert counts == sorted(counts, reverse=True)
