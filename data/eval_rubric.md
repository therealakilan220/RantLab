# RantLab — Evaluation Rubric (d3)

**Owner: Priyan** | Run this after Akilan's prompt lands (~H4). Send weak results back to Akilan with the row number.

---

## How to run

```bash
# With the backend running in STUB_MODE=0:
python scripts/eval_dump.py          # dumps all stored cards as JSON
# Or test manually one by one using the curl below and fill in the table
curl -s -X POST localhost:8000/api/rant \
  -H "Content-Type: application/json" \
  -d '{"text": "<paste complaint here>"}' | python -m json.tool
```

---

## Scoring scale (per fix, 0–2)

| Criterion | 0 | 1 | 2 |
|---|---|---|---|
| **Relevant** | Fix has nothing to do with the complaint | Fix is loosely related | Fix directly addresses the root cause |
| **Specific** | Generic advice ("improve communication") | Partially specific | Clearly actionable for this exact complaint |
| **Owner** | A person's name, or blank | A vague group ("someone") | A real role/department ("IT / Network team") |
| **Cost label** | Wrong or missing | ✓ one of: free / cheap / budget | — |
| **Timeframe label** | Wrong or missing | ✓ one of: today / this_week / this_semester | — |

**Card-level fields** (0–2 each): `problem`, `pattern`, `affected`

Max score per card = 3 fixes × (2+2+2) + 3 card fields × 2 = **24 points**

---

## Test complaints (10 for model evaluation)

Use these exact texts. Pick a mix of groups.

| # | Group | Text |
|---|---|---|
| 1 | wifi | The Wi-Fi in the library keeps dropping every afternoon and nobody seems to fix it. |
| 2 | canteen | The canteen queue at lunch is insane, I waited 25 minutes and only two counters were open. |
| 3 | hostel | There is no hot water in the hostel bathrooms in the morning, it has been like this for two weeks. |
| 4 | bus | The college bus arrives twenty minutes late almost every day and we miss the first lecture. |
| 5 | library | The library closes at 6 pm but exam season is when we need it most, why can it not stay open until 9? |
| 6 | ac | The AC in classroom C102 has not worked for a month, it is 35 degrees outside and we cannot concentrate. |
| 7 | washroom | There is no soap or hand wash in any of the washrooms on the second floor, it has been missing for days. |
| 8 | classroom | The projector in D201 keeps flickering and the faculty has complained multiple times but nothing has been fixed. |
| 9 | medical | The campus medical room is only open until 2 pm which is useless if you feel sick during an evening lab. |
| 10 | wifi | The Wi-Fi password was changed without telling anyone and the IT desk was unreachable for two days. |

---

## Score sheet

Fill one row per complaint. Time = seconds from tap/submit to card appearing.

| # | Time (s) | problem /2 | pattern /2 | affected /2 | Fix1 R/S/O | Fix2 R/S/O | Fix3 R/S/O | Total /24 | Notes |
|---|---|---|---|---|---|---|---|---|---|
| 1 | | | | | / / | / / | / / | | |
| 2 | | | | | / / | / / | / / | | |
| 3 | | | | | / / | / / | / / | | |
| 4 | | | | | / / | / / | / / | | |
| 5 | | | | | / / | / / | / / | | |
| 6 | | | | | / / | / / | / / | | |
| 7 | | | | | / / | / / | / / | | |
| 8 | | | | | / / | / / | / / | | |
| 9 | | | | | / / | / / | / / | | |
| 10 | | | | | / / | / / | / / | | |
| **Avg** | | | | | | | | | |

> R = Relevant, S = Specific, O = Owner (each scored 0–2)

---

## What to send back to Akilan

If any card scores < 16/24 **or** any fix scores 0 on Relevant or Specific, paste that card's full JSON in the team chat with a one-line note on what was wrong.

Common failure modes to watch for:
- Fix owner is a person's name (should be a role)
- Fix is generic: "raise awareness", "improve communication", "talk to admin"
- `cost` or `timeframe` enum is wrong or mixed-case
- `problem` field just repeats the transcript word for word
- All 3 fixes have the same timeframe (should escalate from today → semester)

---

## Timing benchmarks (fill after d6 QA pass)

| Metric | Target | Measured |
|---|---|---|
| Text rant → card (stub mode) | < 1 s | |
| Text rant → card (real LLM) | < 25 s | |
| Voice upload → transcription | < 10 s for 30 s clip | |
| Transcription → card (real LLM) | < 25 s | |
| End-to-end voice → card | < 35 s | |
| `/api/board` cold | < 2 s | |
