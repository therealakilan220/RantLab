# RantLab

**Don't just complain about the problem. Turn it into a plan.**

Record a 20–30 second voice rant. RantLab transcribes it locally, finds the underlying problem, proposes three fixes (each with an owner, a cost bracket and a timeframe), and gives you a shareable card. Similar complaints are grouped into a board of recurring issues.

**Team Fantastic 4 · Open Innovation track · No paid APIs · Everything runs locally.**

---

## How it works

```
  Browser / Phone
       │
       │  audio (webm) or text
       ▼
  ┌─────────────────────────────────────────────────────┐
  │                  FastAPI  (port 8000)               │
  │                                                     │
  │  POST /api/rant                                     │
  │       │                                             │
  │       ├─[audio]─▶  faster-whisper (CPU, local)     │
  │       │              └─▶ transcript (text)          │
  │       │                                             │
  │       └─[text / transcript]                         │
  │               │                                     │
  │               ├─▶  Ollama · qwen2.5:3b (local)     │
  │               │      └─▶ problem, pattern,          │
  │               │           affected, 3 fixes         │
  │               │                                     │
  │               ├─▶  MiniLM-L6-v2 (local)            │
  │               │      └─▶ embedding vector           │
  │               │                                     │
  │               └─▶  SQLite  ──▶  Card saved          │
  │                                                     │
  │  GET /api/board                                     │
  │       └─▶  cosine-similarity clustering             │
  │              └─▶  clusters JSON                     │
  └─────────────────────────────────────────────────────┘
       │
       │  Card JSON
       ▼
  Next.js frontend (port 3000)
  ├─  /          record or type → loading stages → card
  ├─  /card/[id] public share page (mobile-first)
  └─  /board     recurring issues board
```

---

## Stack

| Job | Tool |
|---|---|
| Speech to text | faster-whisper (CPU, local) |
| Problem extraction + fixes | Ollama with Qwen2.5 3B |
| Grouping similar complaints | sentence-transformers all-MiniLM-L6-v2 |
| Backend | Python 3.10+, FastAPI, SQLite |
| Frontend | Next.js 14, TypeScript, Tailwind CSS |

---

## Quick start — no AI models needed (~5 minutes)

**You need:** Python 3.10+ and Node 18+.

### 1. Clone and configure

```powershell
git clone <repo-url> rantlab
cd rantlab
copy .env.example .env          # Windows
# Linux/Mac: cp .env.example .env
```

### 2. Backend

```powershell
cd backend
python -m venv .venv
.venv\Scripts\activate           # Linux/Mac: source .venv/bin/activate
pip install -r requirements.txt
pytest                           # contract tests — all should pass
uvicorn app.main:app --reload --port 8000
```

Check it's running:
- Health: http://localhost:8000/api/health
- Interactive docs: http://localhost:8000/docs

Quick test:
```powershell
curl -X POST localhost:8000/api/rant `
  -H "Content-Type: application/json" `
  -d '{"text":"The library Wi-Fi keeps dropping every afternoon"}'
```

### 3. Frontend

Follow `frontend-starter/README.md` (Jayasree's setup), then:
```powershell
cd frontend
npm run dev                      # http://localhost:3000
```

### 4. Load sample data

```powershell
python scripts/load_seed.py
```

This posts all 40 complaints in `data/seed.json` and prints the board clusters so you can verify grouping.

---

## Switching to real AI (STUB_MODE=0)

```powershell
# 1. Install Ollama from https://ollama.com, then pull the model
ollama pull qwen2.5:3b

# 2. Install heavy Python dependencies (large download, ~2 GB)
pip install -r backend/requirements-ai.txt

# 3. Edit .env — set STUB_MODE=0
# 4. Delete the old database (embedding dimensions differ between modes)
del data\rantlab.db             # Linux/Mac: rm data/rantlab.db

# 5. Restart the backend
uvicorn app.main:app --reload --port 8000
```

> **Tip:** First request is slow while models load. The server warms up Whisper and MiniLM at startup; run `ollama run qwen2.5:3b` once beforehand so the model is already in memory. If your laptop is slow, use `OLLAMA_MODEL=qwen2.5:1.5b` and `WHISPER_MODEL=tiny` in `.env`.

### Cloud API Fallback (Optional)
If Ollama is too slow on your hardware, set `USE_CLOUD_API=1` plus `CLOUD_API_KEY` (Groq or any OpenAI-compatible chat API) in `.env`. Leave it off for the default fully-offline local demo.

### Multilingual / Tamil Smoke Test
Real-mode smoke test (Tamil, after `STUB_MODE=0`):

```bash
curl -X POST localhost:8000/api/rant -H "Content-Type: application/json" \
  -d "{\"text\":\"என்னுடைய பள்ளி நூலகத்தில் வைஃபை மிகவும் மெதுவாக இருக்கிறது\"}"
```

The returned JSON card will have `problem`, `pattern`, `affected`, and three `fixes` structured in English.

---

## Test on a phone (HTTPS required for mic)

Browsers only allow microphone access over HTTPS. Use a free tunnel:

```powershell
cloudflared tunnel --url http://localhost:3000   # or: ngrok http 3000
```

Open the printed HTTPS URL on your phone. The frontend proxies `/api/*` to the backend, so one tunnel is enough.

> **Note:** The tunnel URL is generated fresh each time you start the tunnel (`https://....trycloudflare.com` or `https://....ngrok-free.app`). Share the live URL in team chat; do not commit it. Confirm on mobile that voice recording reaches `POST /api/rant`.

---

## Testing, Evaluation & QA

- **Automated Testing:** Run `pytest` under `backend/tests/` for contract and integration validation.
- **Evaluation Pipeline:** Use `scripts/run_eval.py` and `scripts/eval_dump.py` with `data/eval_rubric.md` to benchmark LLM output quality, scoring accuracy, and latency.
- **Audio Test Dataset:** `data/audio/` contains 6 audio test clips (`clip_01.wav` – `Clip_06.wav`) for local Whisper speech-to-text accuracy checks.
- **QA & Bug Tracking:** Verified test scenarios, browser compatibility checks, and bug logs are maintained in `data/bug_log.md` and `docs/qa_sheet.md`.

---

## Privacy & Security

- Reports are **anonymous by design** — the database contains no name, email, IP, or student ID columns.
- With `STUB_MODE=0`, complaint text is processed entirely by a **local Ollama instance** and never transmitted to external servers.
- Spoken audio is processed in a temporary file for transcription and **deleted immediately** — audio recordings are never stored on disk or database.
- See `data/privacy_checklist.md` for the full compliance checklist before demo.

---

## Admin Portal & Domain Routing

RantLab supports domain-based categorization (Hostel, Library, Mess, IT, Academics, General):
- **Domain-Scoped Clustering:** Groups complaints within relevant department boundaries.
- **Admin Dashboard & Mobile Alerts:** Specification and tasks for `/admin/[domain]` and push notifications are documented in [`docs/admin-portal-task-sheet.pdf`](docs/admin-portal-task-sheet.pdf).

---

## Repo map

```
backend/app/          FastAPI app + one Python module per job
  main.py             endpoints and rant pipeline
  llm.py              Ollama prompt + validation (retry once)
  stt.py              faster-whisper transcription
  embed.py            MiniLM sentence embedding
  cluster.py          cosine-similarity union-find grouping
  db.py               SQLite read/write (no PII columns)
  config.py           all settings, overridable via .env
  models.py           pydantic Card, Fix, LLMOutput
  errors.py           custom error handlers

backend/tests/        pytest contract tests (stub mode, no models needed)

frontend/             Next.js app (generated + starter files copied in)
  app/page.tsx        home — record or type → card
  app/card/[id]/      public share page (mobile-first)
  app/board/          recurring issues board
  app/about/          about page and system info
  components/         UI components (Recorder, ConceptCard, LoadingStages, etc.)
  lib/api.ts          all fetch calls, mock mode switch
  lib/types.ts        TypeScript types + display label maps

data/
  seed.json           40 realistic campus complaints (10 groups, near-duplicates)
  audio/              6 voice sample recordings for Whisper testing
  eval_rubric.md      scoring guide for LLM output quality (Priyan)
  eval_output.json    evaluation benchmarking results
  bug_log.md          QA checklist and bug table (Priyan)
  privacy_checklist.md  privacy sign-off before demo (Priyan)

docs/
  api-contract.md     agreed request/response shapes (read this first)
  TEAM_WORKFLOW.md    branch rules and who owns which files
  rantlab-task-sheet.html  24-hour task board (open in a browser)
  rantlab-task-sheet.pdf   printable task board PDF
  admin-portal-task-sheet.pdf  domain admin portal specifications
  qa_sheet.md         comprehensive QA checklist
  demo_video_script.md live demo walkthrough and presentation script

scripts/
  load_seed.py        post all seed complaints and print the board
  eval_dump.py        dump stored cards as JSON for evaluation
  run_eval.py         run LLM quality evaluation pipeline
  generate_task_sheet_pdf.py  build task sheet PDF
  generate_admin_portal_task_sheet_pdf.py  build admin portal task sheet PDF
  dev.sh              one-command dev startup (Linux/Mac)
```

---

## Team

| Person | Role |
|---|---|
| Akilan | Team lead: backend, LLM prompt, integration |
| Arvind | Speech-to-text, database, embeddings, clustering |
| Jayasree | Frontend: recorder, card, share page, board (Demo lead) |
| Priyan | Test data, evaluation, QA, privacy, README, demo deck |

---

## Docs to read next

- [`docs/api-contract.md`](docs/api-contract.md) — request/response shapes for all endpoints
- [`docs/TEAM_WORKFLOW.md`](docs/TEAM_WORKFLOW.md) — git branch rules and file ownership
- [`docs/rantlab-task-sheet.html`](docs/rantlab-task-sheet.html) — 24-hour task board (open in browser)
- [`docs/admin-portal-task-sheet.pdf`](docs/admin-portal-task-sheet.pdf) — Domain Admin Portal & mobile alert specifications
- [`data/eval_rubric.md`](data/eval_rubric.md) — how to score and time LLM outputs
- [`data/privacy_checklist.md`](data/privacy_checklist.md) — privacy compliance and data safety checklist
- [`docs/demo_video_script.md`](docs/demo_video_script.md) — live demo walkthrough script
