# RantLab

**Don't just complain about the problem. Turn it into a plan.**

Record a 20 to 30 second voice rant. RantLab transcribes it, finds the underlying problem, proposes three fixes (each with an owner, a cost bracket and a timeframe), and gives you a shareable card. Similar complaints are grouped into a board of recurring issues.

Team Fantastic 4, Open Innovation track. Everything runs locally on free, open-source tools. No paid APIs.

## Stack

| Job | Tool |
|---|---|
| Speech to text | faster-whisper |
| Problem extraction and fixes | Ollama with Qwen2.5 3B |
| Grouping similar complaints | sentence-transformers all-MiniLM-L6-v2 |
| Backend | Python, FastAPI, SQLite |
| Frontend | Next.js, TypeScript, Tailwind CSS |

## Repo map

```
docs/            API contract, team workflow, task sheet
backend/app/     FastAPI app (main.py) and one module per job
backend/tests/   API tests (run in stub mode)
frontend-starter/  shared frontend files to copy in after create-next-app
data/            seed complaints, audio samples
scripts/         load_seed.py, eval_dump.py, dev.sh
```

## Quick start (about 5 minutes, no AI models needed)

You need Python 3.10+ and Node 18+.

```bash
git clone <repo-url> rantlab && cd rantlab
cp .env.example .env

# Backend
cd backend
python -m venv .venv
source .venv/bin/activate            # Windows: .venv\Scripts\activate
pip install -r requirements.txt
pytest                               # should pass
uvicorn app.main:app --reload --port 8000
```

Check it: open http://localhost:8000/api/health and http://localhost:8000/docs (interactive API page).

Try a rant:

```bash
curl -X POST localhost:8000/api/rant -H "Content-Type: application/json" \
  -d '{"text":"The library Wi-Fi keeps dropping every afternoon"}'
```

Frontend: follow `frontend-starter/README.md` once (Jayasree), then `cd frontend && npm run dev`.

Load sample data so the board has something to show:

```bash
python scripts/load_seed.py
```

## Switching to the real AI (STUB_MODE=0)

```bash
# 1. Ollama: install from ollama.com, then
ollama pull qwen2.5:3b
# 2. Heavy Python deps (large download)
pip install -r backend/requirements-ai.txt
# 3. In .env set STUB_MODE=0, then
rm data/rantlab.db                   # embedding sizes differ between modes
uvicorn app.main:app --reload --port 8000
```

First request is slow while models load. The server warms up Whisper and MiniLM at startup; run `ollama run qwen2.5:3b` once beforehand so the LLM is already in memory. If your laptop is too slow, use `qwen2.5:1.5b` and `WHISPER_MODEL=tiny`.

Optional fallback if Ollama is too slow: set `USE_CLOUD_API=1` plus `CLOUD_API_KEY` (Groq or any OpenAI-compatible chat API). Leave it off for the default local demo.

Real-mode smoke test (Tamil, after `STUB_MODE=0`):

```bash
curl -X POST localhost:8000/api/rant -H "Content-Type: application/json" \
  -d "{\"text\":\"என்னுடைய பள்ளி நூலகத்தில் வைஃபை மிகவும் மெதுவாக இருக்கிறது\"}"
```

The JSON card must still have `problem`, `pattern`, `affected`, and three `fixes` in English.

## Test on a phone

Browsers only allow the mic over HTTPS. Run a free tunnel to the frontend:

```bash
cloudflared tunnel --url http://localhost:3000     # or: ngrok http 3000
```

Open the HTTPS link on your phone. The frontend forwards `/api/*` to the backend, so one tunnel is enough.

The URL is generated each time you start the tunnel (it looks like `https://….trycloudflare.com` or `https://….ngrok-free.app`). Paste that live URL in the team chat; do not commit it. Confirm on a phone that a spoken complaint reaches the backend (`POST /api/rant` with audio).

## Read next

- `docs/api-contract.md` the agreed request and response shapes
- `docs/TEAM_WORKFLOW.md` who owns which files and the git rules
- `docs/rantlab-task-sheet.html` the 24-hour task board (open in a browser)

## Privacy

Reports are anonymous. The database has no name or email fields. With local AI, complaint text is not sent to an outside AI provider. Stored complaints still need to be handled responsibly, so do not put real personal details in test data.
