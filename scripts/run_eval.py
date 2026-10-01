"""
d4 -- Model evaluation script (Priyan)

Sends the 10 test complaints to the running backend, times each one,
and prints a score sheet you can copy into data/eval_rubric.md.

Usage (with backend running in STUB_MODE=0):
    cd <repo root>
    python scripts/run_eval.py

Output: prints results + saves to data/eval_output.json
"""
import io
import json
import sys
import time
from pathlib import Path

# Force UTF-8 output on Windows so the script doesn't crash on special chars
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

import httpx

BASE = "http://localhost:8000"
OUT  = Path(__file__).resolve().parents[1] / "data" / "eval_output.json"

COMPLAINTS = [
    {"id": 1,  "group": "wifi",      "text": "The Wi-Fi in the library keeps dropping every afternoon and nobody seems to fix it."},
    {"id": 2,  "group": "canteen",   "text": "The canteen queue at lunch is insane, I waited 25 minutes and only two counters were open."},
    {"id": 3,  "group": "hostel",    "text": "There is no hot water in the hostel bathrooms in the morning, it has been like this for two weeks."},
    {"id": 4,  "group": "bus",       "text": "The college bus arrives twenty minutes late almost every day and we miss the first lecture."},
    {"id": 5,  "group": "library",   "text": "The library closes at 6 pm but exam season is when we need it most, why can it not stay open until 9?"},
    {"id": 6,  "group": "ac",        "text": "The AC in classroom C102 has not worked for a month, it is 35 degrees outside and we cannot concentrate."},
    {"id": 7,  "group": "washroom",  "text": "There is no soap or hand wash in any of the washrooms on the second floor, it has been missing for days."},
    {"id": 8,  "group": "classroom", "text": "The projector in D201 keeps flickering and the faculty has complained multiple times but nothing has been fixed."},
    {"id": 9,  "group": "medical",   "text": "The campus medical room is only open until 2 pm which is useless if you feel sick during an evening lab."},
    {"id": 10, "group": "wifi",      "text": "The Wi-Fi password was changed without telling anyone and the IT desk was unreachable for two days."},
]

SEP = "-" * 72

def check_health():
    try:
        r = httpx.get(f"{BASE}/api/health", timeout=5)
        h = r.json()
        stub = h.get("stub_mode", True)
        ollama = h.get("ollama", False)
        whisper = h.get("whisper", False)
        print(f"Backend: OK  |  stub_mode={stub}  |  ollama={ollama}  |  whisper={whisper}")
        if stub:
            print("\n[WARNING] STUB_MODE=1 -- results will be canned, not real AI output.")
            print("   Set STUB_MODE=0 in .env and restart the backend for real evaluation.\n")
        return True
    except Exception as e:
        print(f"[ERROR] Backend not reachable at {BASE}: {e}")
        print("   Start it with: uvicorn app.main:app --reload --port 8000")
        return False

def flag_issues(card: dict) -> list[str]:
    """Heuristically flag common LLM failure modes."""
    issues = []
    generic_phrases = [
        "raise awareness", "improve communication", "talk to admin",
        "create a committee", "send an email", "raise the issue",
    ]
    for i, fix in enumerate(card.get("fixes", []), 1):
        title = fix.get("title", "").lower()
        owner = fix.get("owner", "")
        # Generic fix check
        if any(p in title for p in generic_phrases):
            issues.append(f"Fix {i}: generic advice — '{fix['title']}'")
        # Owner looks like a person's name (two capitalised words, no slash or dept keyword)
        dept_keywords = ["/", "team", "staff", "manager", "desk", "admin",
                         "council", "warden", "office", "department", "head"]
        if owner and not any(k in owner.lower() for k in dept_keywords):
            words = owner.split()
            if len(words) == 2 and all(w[0].isupper() for w in words if w):
                issues.append(f"Fix {i}: owner looks like a person's name — '{owner}'")
        # Cost / timeframe
        if fix.get("cost") not in ("free", "cheap", "budget"):
            issues.append(f"Fix {i}: bad cost value — '{fix.get('cost')}'")
        if fix.get("timeframe") not in ("today", "this_week", "this_semester"):
            issues.append(f"Fix {i}: bad timeframe value — '{fix.get('timeframe')}'")
    # Problem just repeats transcript
    prob = card.get("problem", "").lower()
    trans = card.get("transcript", "").lower()
    overlap = len(set(prob.split()) & set(trans.split())) / max(len(prob.split()), 1)
    if overlap > 0.8:
        issues.append("problem field looks like a copy of the transcript")
    return issues

def run():
    print(SEP)
    print("  RantLab — d4 Model Evaluation")
    print(SEP)
    if not check_health():
        return

    results = []
    print(f"\n{'#':>2}  {'Group':<10}  {'Time':>6}   Card ID      Issues")
    print(SEP)

    for c in COMPLAINTS:
        t0 = time.perf_counter()
        try:
            r = httpx.post(
                f"{BASE}/api/rant",
                json={"text": c["text"]},
                timeout=120,
            )
            elapsed = time.perf_counter() - t0
            if r.status_code != 200:
                print(f"{c['id']:>2}  {c['group']:<10}  {'ERR':>6}   HTTP {r.status_code}: {r.text[:60]}")
                results.append({**c, "error": r.text, "elapsed_s": round(elapsed, 2)})
                continue
            card = r.json()
            issues = flag_issues(card)
            flag = " [FLAGGED]" if issues else " [OK]"
            print(f"{c['id']:>2}  {c['group']:<10}  {elapsed:>5.1f}s  {card['id']}{flag}")
            for iss in issues:
                print(f"       >> {iss}")
            results.append({**c, "card": card, "elapsed_s": round(elapsed, 2), "auto_flags": issues})
        except Exception as e:
            elapsed = time.perf_counter() - t0
            print(f"{c['id']:>2}  {c['group']:<10}  {'ERR':>6}   {e}")
            results.append({**c, "error": str(e), "elapsed_s": round(elapsed, 2)})

    # Summary
    times = [r["elapsed_s"] for r in results if "card" in r]
    flagged = sum(1 for r in results if r.get("auto_flags"))
    print(SEP)
    if times:
        print(f"  Avg time : {sum(times)/len(times):.1f}s")
        print(f"  Min / Max: {min(times):.1f}s / {max(times):.1f}s")
    print(f"  Auto-flagged cards: {flagged} / {len(COMPLAINTS)}")
    print(SEP)

    OUT.write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\n  Full results saved -> {OUT}\n")
    print("  Open data/eval_rubric.md and fill in your manual scores.")
    print("  Paste any [FLAGGED] card's JSON in the team chat for Akilan to fix.")


if __name__ == "__main__":
    run()
