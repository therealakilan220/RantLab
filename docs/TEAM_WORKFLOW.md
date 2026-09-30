# Team workflow

Goal: four people push all day without breaking each other. Keep it boring.

## Who owns what

| Area | Owner | Files |
|---|---|---|
| Pipeline, LLM prompt, integration | Akilan | `backend/app/main.py`, `llm.py`, `models.py`, `config.py`, `docs/api-contract.md` |
| Speech, database, embeddings, clustering | Arvind | `backend/app/stt.py`, `db.py`, `embed.py`, `cluster.py` |
| Frontend (Demo Lead) | Jayasree | `frontend/` |
| Test data, QA, demo, deck | Priyan | `data/`, `scripts/`, `backend/tests/`, `README.md` |

Do not edit a file you do not own. Message the owner, or open a small PR and tag them.

## Git rules

1. `main` always runs. If you break it, fix it before anything else.
2. Work on a branch named `feat/<yourname>-<thing>`, for example `feat/m2-clustering`.
3. Small commits, pushed at least every hour. A commit message is one plain line: "Add transcribe() with vad filter".
4. Before you push: `git pull --rebase origin main`, then run the tests if you touched the backend.
5. Merge to `main` as soon as a piece works, not at the checkpoints. Anyone may merge their own PR; a second pair of eyes is nice but never a blocker in a 24-hour build.
6. Never commit `.env`, `data/rantlab.db`, model files, or audio over 1 MB.

## Changing the API contract

1. Edit `docs/api-contract.md` and the matching `models.py` and `frontend/lib/types.ts` in the **same PR**.
2. Add a line to the change log at the bottom of the contract.
3. Post in the team chat: "Contract changed: <what>". Then the frontend and backend update together.

## Stub mode vs real mode

- `STUB_MODE=1` (default): everything runs with no AI models. Use it for frontend work and wiring.
- `STUB_MODE=0`: real Whisper, Ollama, MiniLM. Needs `pip install -r backend/requirements-ai.txt` and `ollama pull qwen2.5:3b`.
- Switching modes changes the embedding size, so delete `data/rantlab.db` when you switch.

## Sync points

| Hour | Who | Check |
|---|---|---|
| H1 | Everyone | Repo cloned, `pytest` passes, frontend runs on mocks |
| H6 | Akilan | `POST /api/rant` with text returns a real card |
| H12 | All | Voice in the browser produces a card |
| H16 | All | Feature freeze, tag `v1-mvp`, only bug fixes after this |
| H20 | All | Stop building, rehearse |

## When something conflicts

If `git pull --rebase` shows a conflict, stop and ask the file's owner. Do not pick "theirs" or "mine" blindly for JSON, lock files or the contract.
