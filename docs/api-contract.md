# RantLab API Contract

Version 1.0. Owner: Akilan. Any change must be announced in the team chat before it is merged.

Base URL in development: `http://localhost:8000`. The Next.js app proxies `/api/*` to it, so the browser only calls relative `/api/...` paths and CORS is not an issue.

## Enums (exact strings, lowercase)

| Field | Allowed values |
|---|---|
| `cost` | `free`, `cheap`, `budget` |
| `timeframe` | `today`, `this_week`, `this_semester` |

The frontend maps these to display labels ("This week", "This semester").

## Types

### Fix
```json
{
  "title": "Check access-point coverage in the library block",
  "detail": "Walk the building with a phone Wi-Fi analyser and mark dead zones.",
  "owner": "IT / Network team",
  "cost": "free",
  "timeframe": "this_week"
}
```
`title` is one line (max about 80 characters). `detail` is one or two sentences. `owner` is a role or department, never a person's name.

### Card
```json
{
  "id": "c_8f3a2b",
  "created_at": "2026-09-30T11:05:12Z",
  "input_type": "voice",
  "transcript": "The Wi-Fi in the library keeps dropping every afternoon and nobody seems to fix it.",
  "problem": "Library Wi-Fi drops repeatedly in the afternoon.",
  "pattern": "Likely overloaded access points during peak study hours.",
  "affected": "Students who study in the library, especially before exams.",
  "fixes": [ "<Fix>", "<Fix>", "<Fix>" ],
  "cluster_id": null
}
```
Rules:
- `fixes` always has exactly 3 items, ordered from most to least feasible.
- `input_type` is `voice` or `text`.
- `cluster_id` is `null` until clustering has run, then a string such as `"k_2"`.
- No field holds a name, email or any personal identifier. Reports are anonymous.

### Cluster
```json
{
  "id": "k_2",
  "label": "Library Wi-Fi drops in the afternoon",
  "count": 7,
  "latest_at": "2026-09-30T11:05:12Z",
  "complaints": [
    { "card_id": "c_8f3a2b", "transcript": "The Wi-Fi in the library keeps dropping..." }
  ]
}
```
Clusters with `count` of 1 are still returned; the frontend decides whether to show them.

### Error
Every non-2xx response has this body:
```json
{ "error": { "code": "empty_audio", "message": "We couldn't hear anything. Try again closer to the mic." } }
```
`message` is safe to show to the user directly.

| HTTP | `code` | When |
|---|---|---|
| 400 | `empty_audio` | Silence or a clip under about 1 second |
| 400 | `empty_text` | Text is blank |
| 400 | `bad_input` | Missing both `audio` and `text`, or both present |
| 413 | `too_long` | Audio over 60 seconds or text over 2000 characters |
| 415 | `unsupported_audio` | File cannot be decoded by ffmpeg |
| 404 | `not_found` | Unknown card id |
| 502 | `llm_failed` | The model returned invalid JSON twice |
| 503 | `model_unavailable` | Ollama is not running |

## Endpoints

### `GET /api/health`
Returns `{ "status": "ok", "stub_mode": true, "ollama": true, "whisper": true }`. Use it to check the demo machine before going on stage.

### `POST /api/rant`
Creates a card from a voice recording or typed text. Send exactly one of the two.

Voice: `multipart/form-data` with a file field named `audio` (browser `webm` or `ogg`, up to 60 s).
Text: `application/json` with `{ "text": "..." }`.

Response `200`: a **Card**. Expect 5 to 25 seconds on a laptop CPU. The frontend should show stages while waiting ("Transcribing", "Finding the real problem", "Drafting fixes").

Side effects: the card and its transcript are saved to SQLite, and an embedding is stored for clustering.

### `GET /api/cards/{id}`
Response `200`: a **Card**. Used by the public share page at `/card/[id]`. `404` if unknown.

### `GET /api/board`
Response `200`:
```json
{ "generated_at": "2026-09-30T12:00:00Z", "clusters": [ "<Cluster>" ] }
```
Sorted by `count` descending, then `latest_at` descending.

### `GET /api/cards` (optional, low priority)
Response `200`: `{ "cards": [ "<Card>" ] }`, newest first, max 50. Build only if time allows.

## Python interfaces (backend modules)

Each module exposes exactly these functions so pieces can be swapped from stub to real.

```python
# stt.py (Member 2)
def transcribe(audio_path: str) -> str:
    """Return the transcript. Raise ValueError('empty_audio') if nothing was said."""

# llm.py (Akilan)
def generate_card_fields(transcript: str) -> dict:
    """Return problem, pattern, affected, fixes[3]. Validated with pydantic, one retry."""

# embed.py (Member 2)
def embed(text: str) -> list[float]:
    """MiniLM (all-MiniLM-L6-v2) embedding. Model loaded once at startup."""

# cluster.py (Member 2)
def cluster(items: list[tuple[str, list[float]]], threshold: float = 0.6) -> dict[str, str]:
    """items = (card_id, embedding). Returns {card_id: cluster_id}."""

# db.py (Member 2)
def save_card(card: dict, embedding: list[float]) -> None: ...
def get_card(card_id: str) -> dict | None: ...
def all_cards_with_embeddings() -> list[tuple[dict, list[float]]]: ...
```

## Pydantic models (backend/models.py)

```python
from typing import Literal
from pydantic import BaseModel, Field

Cost = Literal["free", "cheap", "budget"]
Timeframe = Literal["today", "this_week", "this_semester"]

class Fix(BaseModel):
    title: str
    detail: str
    owner: str
    cost: Cost
    timeframe: Timeframe

class LLMOutput(BaseModel):
    problem: str
    pattern: str
    affected: str
    fixes: list[Fix] = Field(min_length=3, max_length=3)

class Card(LLMOutput):
    id: str
    created_at: str
    input_type: Literal["voice", "text"]
    transcript: str
    cluster_id: str | None = None
```

## TypeScript types (frontend/lib/types.ts)

```ts
export type Cost = "free" | "cheap" | "budget";
export type Timeframe = "today" | "this_week" | "this_semester";

export interface Fix { title: string; detail: string; owner: string; cost: Cost; timeframe: Timeframe; }

export interface Card {
  id: string; created_at: string; input_type: "voice" | "text";
  transcript: string; problem: string; pattern: string; affected: string;
  fixes: [Fix, Fix, Fix]; cluster_id: string | null;
}

export interface Cluster {
  id: string; label: string; count: number; latest_at: string;
  complaints: { card_id: string; transcript: string }[];
}

export interface ApiError { error: { code: string; message: string } }
```

## Mock card for the frontend (save as frontend/mocks/card.json)

```json
{
  "id": "c_mock01",
  "created_at": "2026-09-30T11:05:12Z",
  "input_type": "voice",
  "transcript": "The Wi-Fi in the library keeps dropping every afternoon and nobody seems to fix it.",
  "problem": "Library Wi-Fi drops repeatedly in the afternoon.",
  "pattern": "Likely overloaded access points during peak study hours.",
  "affected": "Students who study in the library, especially before exams.",
  "fixes": [
    { "title": "Post a fault-reporting QR code in the library", "detail": "Link it to a simple form so IT sees exactly when and where drops happen.", "owner": "Library staff and IT desk", "cost": "free", "timeframe": "today" },
    { "title": "Survey access-point coverage and load", "detail": "Check which access points are saturated between 2 and 5 pm.", "owner": "IT / Network team", "cost": "free", "timeframe": "this_week" },
    { "title": "Add or upgrade access points in busy zones", "detail": "Use the survey data to place extra capacity where students actually sit.", "owner": "IT / Network team", "cost": "budget", "timeframe": "this_semester" }
  ],
  "cluster_id": null
}
```

## Prompt output requirement (for llm.py)

The model must return only a JSON object matching `LLMOutput`. Use Ollama's `format: "json"` option, temperature 0.3, validate with pydantic, retry once with the validation error appended, then raise `llm_failed`. Fixes must be specific to the complaint, ordered by feasibility, and the owner must be a role or department.

## Change log

- 1.0: first version.
