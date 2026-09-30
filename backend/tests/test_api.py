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


def test_tamil_text_rant_matches_contract(client):
    card = rant(client, "என்னுடைய பள்ளி நூலகத்தில் வைஃபை மிகவும் மெதுவாக இருக்கிறது")
    assert card["input_type"] == "text"
    assert len(card["fixes"]) == 3
    assert all(k in card for k in ("problem", "pattern", "affected"))


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


def test_llm_json_extraction():
    from app.llm import _extract_json, _norm, _clean

    # Code fenced JSON
    fenced = '```json\n{"problem": "Test", "pattern": "P", "affected": "A", "fixes": []}\n```'
    parsed = _extract_json(fenced)
    assert parsed["problem"] == "Test"

    # JSON with surrounding prose
    prose = 'Here is the result: {"problem": "Prose", "pattern": "P", "affected": "A", "fixes": []} Hope it helps!'
    parsed_prose = _extract_json(prose)
    assert parsed_prose["problem"] == "Prose"

    # Alias normalization
    assert _norm("free_of_cost") == "free"
    assert _norm("0") == "free"
    assert _norm("low_cost") == "cheap"
    assert _norm("capital") == "budget"
    assert _norm("immediately") == "today"
    assert _norm("thisweek") == "this_week"
    assert _norm("long_term") == "this_semester"

    # Clean data
    sample = {
        "problem": "P",
        "pattern": "Pat",
        "affected": "Aff",
        "fixes": [
            {"title": "T1", "detail": "D1", "owner": "IT", "cost": "free_of_cost", "timeframe": "now"},
            {"title": "T2", "detail": "D2", "owner": "Warden", "cost": "minor", "timeframe": "7_days"},
            {"title": "T3", "detail": "D3", "owner": "Admin", "cost": "capital", "timeframe": "months"},
            {"title": "T4", "detail": "D4", "owner": "Admin", "cost": "capital", "timeframe": "months"},
        ]
    }
    cleaned = _clean(sample)
    assert len(cleaned["fixes"]) == 3
    assert cleaned["fixes"][0]["cost"] == "free"
    assert cleaned["fixes"][0]["timeframe"] == "today"
    assert cleaned["fixes"][1]["cost"] == "cheap"
    assert cleaned["fixes"][1]["timeframe"] == "this_week"
    assert cleaned["fixes"][2]["cost"] == "budget"
    assert cleaned["fixes"][2]["timeframe"] == "this_semester"

