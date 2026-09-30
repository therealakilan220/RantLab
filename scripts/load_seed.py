"""Post every complaint in data/seed.json to a running backend, then print the board.

Usage:  python scripts/load_seed.py [http://localhost:8000]
Needs:  pip install httpx   (already in backend/requirements.txt)
"""
import json
import sys
from pathlib import Path

import httpx

base = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8000"
seed = json.loads((Path(__file__).resolve().parents[1] / "data" / "seed.json").read_text(encoding="utf-8"))

for i, item in enumerate(seed, 1):
    r = httpx.post(f"{base}/api/rant", json={"text": item["text"]}, timeout=180)
    print(f"{i:>2}/{len(seed)}  {r.status_code}  [{item['group']}]  {item['text'][:60]}")

board = httpx.get(f"{base}/api/board", timeout=30).json()
print("\nBoard:")
for c in board["clusters"]:
    print(f"  {c['count']:>2} x {c['label']}")
