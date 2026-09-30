"""Run every seed complaint through the API and write data/eval_output.md for scoring.

Member 4: fill in the Score columns by hand (relevant? specific? sensible owner?, 1-5).
Usage:  python scripts/eval_dump.py [http://localhost:8000]
"""
import json
import sys
import time
from pathlib import Path

import httpx

root = Path(__file__).resolve().parents[1]
base = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8000"
seed = json.loads((root / "data" / "seed.json").read_text(encoding="utf-8"))

lines = ["# Output review", "", "| # | Seconds | Complaint | Problem | Fix 1 | Fix 2 | Fix 3 | Relevant | Specific | Owner |", "|---|---|---|---|---|---|---|---|---|---|"]
times = []
for i, item in enumerate(seed, 1):
    start = time.time()
    r = httpx.post(f"{base}/api/rant", json={"text": item["text"]}, timeout=180)
    secs = time.time() - start
    if r.status_code != 200:
        lines.append(f"| {i} | {secs:.1f} | {item['text']} | ERROR {r.status_code}: {r.text[:80]} | | | | | | |")
        continue
    times.append(secs)
    card = r.json()
    fix = [f"{f['title']} ({f['owner']}, {f['cost']}, {f['timeframe']})" for f in card["fixes"]]
    lines.append(f"| {i} | {secs:.1f} | {item['text']} | {card['problem']} | {fix[0]} | {fix[1]} | {fix[2]} | | | |")
    print(f"{i}/{len(seed)} done in {secs:.1f}s")

if times:
    lines += ["", f"Average time to card: {sum(times) / len(times):.1f}s over {len(times)} complaints (text input, no upload or transcription)."]
(root / "data" / "eval_output.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
print("Wrote data/eval_output.md")
