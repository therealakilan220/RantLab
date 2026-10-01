"""
d6 — API-level QA script (Priyan)
Runs all testable scenarios from bug_log.md that don't need a browser.
Prints PASS / FAIL for each. Saves summary to data/qa_results.json.
"""
import io, json, sys, time
from pathlib import Path
import httpx

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

BASE = "http://localhost:8000"
OUT  = Path(__file__).resolve().parents[1] / "data" / "qa_results.json"
SEP  = "-" * 68
results = []

def check(name, passed, detail=""):
    status = "PASS" if passed else "FAIL"
    mark   = "[PASS]" if passed else "[FAIL]"
    print(f"  {mark}  {name}")
    if detail and not passed:
        print(f"         >> {detail}")
    results.append({"test": name, "status": status, "detail": detail})
    return passed

def run():
    print(SEP)
    print("  RantLab d6 -- API QA Pass")
    print(SEP)

    # ── Health ────────────────────────────────────────────────────────────
    print("\n[Health]")
    try:
        r = httpx.get(f"{BASE}/api/health", timeout=5)
        h = r.json()
        check("GET /api/health returns 200",          r.status_code == 200)
        check("status == ok",                          h.get("status") == "ok")
        check("stub_mode field present",               "stub_mode" in h)
        check("ollama field present",                  "ollama" in h)
        check("whisper field present",                 "whisper" in h)
    except Exception as e:
        check("Backend reachable", False, str(e))
        print("\n  Backend is down -- aborting QA.\n")
        return

    # ── Text input ────────────────────────────────────────────────────────
    print("\n[Text input]")
    r = httpx.post(f"{BASE}/api/rant", json={"text": "The library Wi-Fi drops every afternoon."}, timeout=60)
    check("Normal text rant -> 200",          r.status_code == 200, r.text[:80])
    card = r.json() if r.status_code == 200 else {}
    check("Card has id",                      "id" in card)
    check("Card has problem",                 "problem" in card and bool(card.get("problem")))
    check("Card has pattern",                 "pattern" in card)
    check("Card has affected",                "affected" in card)
    check("Card has exactly 3 fixes",         len(card.get("fixes", [])) == 3)
    check("input_type == text",               card.get("input_type") == "text")
    for i, fix in enumerate(card.get("fixes", []), 1):
        check(f"Fix {i} cost valid",          fix.get("cost") in ("free","cheap","budget"), fix.get("cost"))
        check(f"Fix {i} timeframe valid",     fix.get("timeframe") in ("today","this_week","this_semester"), fix.get("timeframe"))
        check(f"Fix {i} has owner",           bool(fix.get("owner")))
        check(f"Fix {i} has title",           bool(fix.get("title")))

    # Blank text
    r = httpx.post(f"{BASE}/api/rant", json={"text": "   "}, timeout=10)
    check("Blank text -> error empty_text",   r.json().get("error",{}).get("code") == "empty_text", r.text[:60])

    # Empty JSON
    r = httpx.post(f"{BASE}/api/rant", json={}, timeout=10)
    check("Empty JSON -> error bad_input",    r.json().get("error",{}).get("code") == "bad_input", r.text[:60])

    # Too long text (2001 chars)
    r = httpx.post(f"{BASE}/api/rant", json={"text": "x" * 2001}, timeout=10)
    check("2001-char text -> 413",            r.status_code == 413, str(r.status_code))

    # Exactly 2000 chars (boundary - should pass)
    r = httpx.post(f"{BASE}/api/rant", json={"text": "x" * 1999 + "."}, timeout=60)
    check("2000-char text -> 200",            r.status_code == 200, str(r.status_code))

    # ── Voice input ───────────────────────────────────────────────────────
    print("\n[Voice input]")
    r = httpx.post(f"{BASE}/api/rant", files={"audio": ("rant.webm", b"x" * 5000, "audio/webm")}, timeout=60)
    check("Stub voice (5 KB) -> 200",         r.status_code == 200, r.text[:60])
    check("input_type == voice",              r.json().get("input_type") == "voice" if r.status_code == 200 else False)

    # Too small audio
    r = httpx.post(f"{BASE}/api/rant", files={"audio": ("r.webm", b"x", "audio/webm")}, timeout=10)
    check("1-byte audio -> empty_audio",      r.json().get("error",{}).get("code") == "empty_audio", r.text[:60])

    # Both audio and text
    r = httpx.post(f"{BASE}/api/rant",
                   data={"text": "hello"},
                   files={"audio": ("r.webm", b"x" * 5000, "audio/webm")},
                   timeout=10)
    check("Both audio+text -> bad_input",     r.json().get("error",{}).get("code") == "bad_input", r.text[:60])

    # ── Card retrieval ────────────────────────────────────────────────────
    print("\n[Card share page]")
    # Use the card id we got earlier
    if card.get("id"):
        r = httpx.get(f"{BASE}/api/cards/{card['id']}", timeout=10)
        check(f"GET /api/cards/{card['id']} -> 200",  r.status_code == 200, r.text[:60])
        check("Returned card id matches",              r.json().get("id") == card["id"] if r.status_code == 200 else False)

    r = httpx.get(f"{BASE}/api/cards/c_nope", timeout=10)
    check("GET /api/cards/c_nope -> 404",     r.status_code == 404, str(r.status_code))

    # ── Board ─────────────────────────────────────────────────────────────
    print("\n[Board]")
    r = httpx.get(f"{BASE}/api/board", timeout=30)
    check("GET /api/board -> 200",            r.status_code == 200, r.text[:60])
    board = r.json() if r.status_code == 200 else {}
    check("Board has generated_at",           "generated_at" in board)
    check("Board has clusters list",          isinstance(board.get("clusters"), list))
    clusters = board.get("clusters", [])
    if clusters:
        counts = [c["count"] for c in clusters]
        check("Board sorted by count desc",   counts == sorted(counts, reverse=True))
        check("Each cluster has id",          all("id" in c for c in clusters))
        check("Each cluster has label",       all("label" in c for c in clusters))
        check("Each cluster has complaints",  all("complaints" in c for c in clusters))

    # ── Privacy ───────────────────────────────────────────────────────────
    print("\n[Privacy / data checks]")
    import sqlite3
    db = Path(__file__).resolve().parents[1] / "data" / "rantlab.db"
    if db.exists():
        con = sqlite3.connect(str(db))
        schema = con.execute("SELECT sql FROM sqlite_master WHERE name='cards'").fetchone()[0]
        pii_cols = ["name", "email", "phone", "student_id", "roll"]
        for col in pii_cols:
            check(f"DB has no '{col}' column", col not in schema.lower())
        con.close()
    else:
        check("DB file exists", False, "rantlab.db not found")

    # ── Summary ───────────────────────────────────────────────────────────
    passed = sum(1 for r in results if r["status"] == "PASS")
    failed = sum(1 for r in results if r["status"] == "FAIL")
    print(f"\n{SEP}")
    print(f"  TOTAL: {passed} passed, {failed} failed out of {len(results)} tests")
    print(SEP)

    OUT.write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(f"  Results saved -> {OUT}")
    if failed:
        print(f"\n  [FAILED TESTS - send to Akilan/Jayasree]")
        for r in results:
            if r["status"] == "FAIL":
                print(f"    - {r['test']}: {r['detail']}")

if __name__ == "__main__":
    run()
