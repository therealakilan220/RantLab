# Data (Member 4 owns this folder)

- `seed.json` starter complaints. Each has a `group` label that says which cluster it should land in, so we can check clustering. Grow this to 40 with deliberate near-duplicates.
- `audio/` voice samples for testing Whisper and as demo backups. Keep each clip small (under 1 MB) or share large ones through a Drive folder instead. GitHub rejects files over 100 MB.
- `rantlab.db` is created automatically by the backend and is git-ignored. Delete it to start fresh.
- `eval_output.md` is written by `scripts/eval_dump.py` for scoring outputs (git-ignored).

No real names, phone numbers, room numbers or other personal details in any test data.
