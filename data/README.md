# data/ — Test data and evaluation files (Priyan)

| File | Purpose |
|---|---|
| `seed.json` | 40 realistic campus complaints across 10 groups, with deliberate near-duplicates for clustering. Run with `python scripts/load_seed.py`. |
| `audio/` | 6 voice recordings (20–30 s each) for Whisper testing and as demo fallback. See naming guide below. |
| `eval_rubric.md` | Scoring rubric for LLM output quality + timing benchmarks. Fill in after running 10 test complaints. |
| `bug_log.md` | QA checklist and bug table. Start at H12 (MVP freeze). |
| `privacy_checklist.md` | Privacy sign-off checklist. All items must pass before demo. |
| `rantlab.db` | Created automatically by the backend. **Git-ignored.** Delete to start fresh. |
| `eval_output.md` | Written by `scripts/eval_dump.py`. **Git-ignored.** |

---

## Audio file naming guide (d2)

Record 6 clips and save them here as `.webm` or `.ogg` (browser format):

| Filename | Description |
|---|---|
| `wifi_clean.webm` | Clear voice, Wi-Fi complaint, ~25 s |
| `canteen_clean.webm` | Clear voice, canteen complaint, ~25 s |
| `hostel_clean.webm` | Clear voice, hostel water complaint, ~25 s |
| `bus_clean.webm` | Clear voice, bus timing complaint, ~25 s |
| `library_clean.webm` | Clear voice, library closing time complaint, ~25 s |
| `noisy.webm` | Background noise (canteen or street), any complaint, ~25 s |

**Recording tips:**
- Use your phone browser (Chrome) → open the RantLab app → tap record
- Or use any voice recorder app and convert with `ffmpeg -i input.m4a output.webm`
- Keep files under 1 MB. Do not commit files over 10 MB (GitHub limit is 100 MB but keep it small).
- Do **not** say your real name in any recording.

---

## Rules

- No real names, phone numbers, room numbers or personal details in any file here.
- `rantlab.db` and `eval_output.md` are git-ignored — never force-add them.
