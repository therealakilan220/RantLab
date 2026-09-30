"""FastAPI app and the rant pipeline (Akilan). Endpoints follow docs/api-contract.md."""
import logging
import os
import tempfile
import uuid
from contextlib import asynccontextmanager
from datetime import datetime, timezone

from fastapi import FastAPI, Request
from fastapi.concurrency import run_in_threadpool
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.datastructures import UploadFile

from . import cluster, config, db, embed, llm, stt
from .errors import ApiError
from .models import Card

log = logging.getLogger("rantlab")


def _warm_up() -> None:
    for step in (embed.warm_up, stt.warm_up):
        try:
            step()
        except Exception:  # a missing model should not stop the server from starting
            log.exception("warm-up step failed: %s", step.__module__)


@asynccontextmanager
async def lifespan(_app: FastAPI):
    db.init_db()
    await run_in_threadpool(_warm_up)
    yield


app = FastAPI(title="RantLab API", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])


@app.exception_handler(ApiError)
async def api_error_handler(_request: Request, exc: ApiError):
    return JSONResponse(status_code=exc.status, content={"error": {"code": exc.code, "message": exc.message}})


@app.get("/api/health")
def health():
    return {"status": "ok", "stub_mode": config.STUB_MODE, "ollama": llm.is_up(), "whisper": stt.is_ready()}


def _transcribe(path: str) -> str:
    try:
        return stt.transcribe(path)
    except ValueError as exc:
        if str(exc) == "empty_audio":
            raise ApiError(400, "empty_audio", "We couldn't hear anything. Try again closer to the mic.") from exc
        raise
    except Exception as exc:
        log.exception("transcription failed")
        raise ApiError(415, "unsupported_audio", "We couldn't read that recording. Please try again.") from exc


def _build_card(transcript: str, input_type: str) -> dict:
    fields = llm.generate_card_fields(transcript)
    card = Card(
        id="c_" + uuid.uuid4().hex[:6],
        created_at=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        input_type=input_type,
        transcript=transcript,
        **fields,
    ).model_dump()
    db.save_card(card, embed.embed(transcript))
    return card


@app.post("/api/rant")
async def create_rant(request: Request):
    content_type = request.headers.get("content-type", "")
    audio, text = None, None
    if content_type.startswith("multipart/form-data"):
        form = await request.form()
        audio, text = form.get("audio"), form.get("text")
    elif content_type.startswith("application/json"):
        try:
            body = await request.json()
        except ValueError as exc:
            raise ApiError(400, "bad_input", 'Send JSON like {"text": "..."}.') from exc
        text = body.get("text") if isinstance(body, dict) else None
    else:
        raise ApiError(400, "bad_input", "Send either an audio file or a text field.")

    has_audio = isinstance(audio, UploadFile)
    if has_audio == (text is not None):
        raise ApiError(400, "bad_input", "Send exactly one of audio or text.")

    if has_audio:
        data = await audio.read()
        if len(data) < config.MIN_AUDIO_BYTES:
            raise ApiError(400, "empty_audio", "We couldn't hear anything. Try again closer to the mic.")
        if len(data) > config.MAX_AUDIO_BYTES:
            raise ApiError(413, "too_long", "That recording is too long. Keep it under 60 seconds.")
        suffix = os.path.splitext(audio.filename or "")[1] or ".webm"
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(data)
        try:
            transcript = await run_in_threadpool(_transcribe, tmp.name)
        finally:
            os.remove(tmp.name)
        input_type = "voice"
    else:
        transcript = str(text).strip()
        if not transcript:
            raise ApiError(400, "empty_text", "Type or say what's bothering you first.")
        if len(transcript) > config.MAX_TEXT_CHARS:
            raise ApiError(413, "too_long", "That's a bit long. Keep it under 2000 characters.")
        input_type = "text"

    return await run_in_threadpool(_build_card, transcript, input_type)


@app.get("/api/cards/{card_id}")
def get_card(card_id: str):
    card = db.get_card(card_id)
    if card is None:
        raise ApiError(404, "not_found", "We couldn't find that card.")
    return card


@app.get("/api/board")
def board():
    rows = db.all_cards_with_embeddings()
    items = [(c["id"], e) for c, e in rows]
    mapping = cluster.cluster(items, config.CLUSTER_THRESHOLD)
    db.set_cluster_ids(mapping)

    cards = {c["id"]: c for c, _ in rows}
    groups: dict[str, list[str]] = {}
    for card_id in cards:
        groups.setdefault(mapping.get(card_id, "k_" + card_id.removeprefix("c_")), []).append(card_id)

    clusters = []
    for cluster_id, members in groups.items():
        central = cards[cluster.most_central(items, members)]
        members.sort(key=lambda m: cards[m]["created_at"], reverse=True)
        clusters.append({
            "id": cluster_id,
            "label": central["problem"],
            "count": len(members),
            "latest_at": cards[members[0]]["created_at"],
            "complaints": [{"card_id": m, "transcript": cards[m]["transcript"]} for m in members],
        })
    clusters.sort(key=lambda k: (k["count"], k["latest_at"]), reverse=True)
    return {"generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"), "clusters": clusters}
