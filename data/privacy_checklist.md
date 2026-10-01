# RantLab — Privacy Checklist (d7)

**Owner: Priyan** | Complete this before H16 (MVP freeze). All items must pass before demo.

---

## Data minimisation

- [ ] Database has **no name, email, student ID, phone number or roll number columns** — verify by running:
  ```bash
  sqlite3 data/rantlab.db ".schema cards"
  ```
  Expected columns: `id, created_at, input_type, transcript, problem, pattern, affected, fixes_json, cluster_id, embedding_json`

- [ ] `id` field is a random hex string (`c_` + 6 random hex chars), not sequential or derived from user identity
- [ ] No IP address is logged by the backend (check `uvicorn` log output)
- [ ] Audio files are written to a temp file and **deleted immediately** after transcription (see `main.py` lines 103–108)

## AI processing

- [ ] In `STUB_MODE=0`, complaint text is sent only to **local Ollama** (verify `OLLAMA_URL` points to `localhost`)
- [ ] No complaint text is sent to any external API (no OpenAI, Groq, Google calls in the codebase — grep to confirm):
  ```bash
  grep -r "openai\|groq\|generativelanguage\|api.anthropic" backend/
  ```
  Expected: no results
- [ ] Whisper transcription runs **fully on-device** (faster-whisper, CPU, local model file)

## Frontend

- [ ] Record screen shows a **one-line privacy notice** visible before the user hits record:
  > "Your rant is processed locally and stored anonymously. No names or contact details are recorded."
- [ ] No analytics script (Google Analytics, Mixpanel, etc.) in the frontend — grep:
  ```bash
  grep -r "gtag\|analytics\|mixpanel\|hotjar" frontend/
  ```
  Expected: no results
- [ ] Share URL (`/card/[id]`) contains only the random card ID, no personal data

## Test data

- [ ] `data/seed.json` contains **no real names, real student IDs, real phone numbers** — confirm all 40 entries are fictional
- [ ] `data/audio/` voice samples contain **no real names spoken** — re-listen and confirm
- [ ] Git history has no accidentally committed personal data (check with `git log --all --full-diff -p -- data/`)

## At the demo

- [ ] Demo machine does not have anyone's real personal data in the database — wipe and reload seed before presenting:
  ```bash
  rm data/rantlab.db
  uvicorn app.main:app --reload --port 8000 &
  python scripts/load_seed.py
  ```
- [ ] Audience knows complaints are anonymous and local-only — cover this in slide/speaker notes

---

## Sign-off

| Item | Status | Notes |
|---|---|---|
| No PII columns in DB | ✅ Pass | Verified: id, created_at, input_type, transcript, problem, pattern, affected, fixes_json, cluster_id, embedding_json — no name/email/phone |
| No external AI calls | ✅ Pass | Grep confirmed: zero matches for openai, groq, generativelanguage, anthropic |
| Audio deleted after transcription | ✅ Pass | main.py lines 103-108: tempfile deleted in finally block |
| Privacy notice on record screen | ✅ Pass | Added to Recorder.tsx — "Your rant is processed locally and stored anonymously." |
| No analytics in frontend | ✅ Pass | Grep of frontend/app/*.tsx + components/*.tsx — zero matches for gtag, analytics, mixpanel, hotjar |
| Seed data is fictional | ✅ Pass | All 40 seed.json entries are invented campus scenarios, no real names |
| Demo DB wiped before presentation | ☐ Pending | Do this on the morning of the demo: `del data\rantlab.db` then restart + load_seed.py |

**All items must show Pass before going on stage.**
