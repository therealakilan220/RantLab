# RantLab — Speaker 4 Q&A Sheet (d10)
**Owner: Priyan** | Prepared for the pitch panel. Memorise the one-line answers.

---

## Slide 7 — Real numbers (fill exact values before going on stage)

| Metric | Measured | Notes |
|---|---|---|
| Text rant → card (stub mode) | ~0.0s | Instant (canned response) |
| Text rant → card (real LLM, Qwen2.5:3b) | ~2.3s | Measured in d4 eval |
| Voice upload → transcription (30s clip) | < 10s | faster-whisper base on CPU |
| End-to-end voice → card | < 15s | transcription + LLM |
| Seed load: 40 complaints | < 2 min | load_seed.py |
| Board cluster response | < 1s | from SQLite, no LLM needed |
| LLM output quality (10 complaints) | 10/10 valid JSON | Qwen2.5:3b with 1 retry |

---

## Questions the panel will likely ask — and your answers

### On the AI / tech

**Q: Why Qwen2.5 3B and not a bigger model like Llama 3?**
> A: 3B runs comfortably on a laptop CPU under 15 seconds per card. Bigger models are slower without a GPU. We tested it and the output quality is good enough for campus complaints — short, structured JSON with clear constraints.

**Q: What if the LLM returns bad JSON?**
> A: The `llm.py` module validates the output with Pydantic and retries once with the error message appended to the prompt. If it fails twice, the API returns a friendly 502 error and asks the user to try again. We never show a raw stack trace.

**Q: Why faster-whisper instead of the OpenAI Whisper API?**
> A: Everything runs locally — no internet needed after setup, no data leaves the device, and it's free. faster-whisper runs the same model weights but 2–4× faster than the original Python package.

**Q: How does the clustering work?**
> A: We embed each complaint using MiniLM-L6-v2 (a 22 MB local model) which gives a 384-dimension vector. We then compute cosine similarity between all pairs. Any two complaints with similarity ≥ 0.6 are linked into the same cluster using union-find. It's fast, explainable, and easy to tune.

**Q: What if two unrelated complaints end up in the same cluster?**
> A: Raise the `CLUSTER_THRESHOLD` in `.env` — default is 0.6. At 0.8 only near-identical complaints group. At 0.4 (stub mode) everything groups loosely. We tested on our 40-complaint seed set and Wi-Fi complaints group together while canteen complaints stay separate.

### On privacy

**Q: Are student complaints stored with names or IDs?**
> A: No. The database has no name, email, student ID or phone number columns — by design. The only identifier is a random 6-character hex string (`c_ab12cd`). We verified this by inspecting the schema.

**Q: Is the complaint text sent to any cloud AI?**
> A: No. Whisper, Qwen2.5 and MiniLM all run locally via Ollama and faster-whisper. No data leaves the machine. We grepped the entire backend and confirmed there are no calls to OpenAI, Groq, Anthropic or any external API.

**Q: What if someone types personal information into the rant?**
> A: We show a one-line notice before recording: "Your rant is processed locally and stored anonymously. No names or contact details are recorded." We also advise users in the UI not to include personal details. We cannot prevent it, but we don't ask for it and don't display it to others on the board.

### On the product

**Q: Who would actually use this?**
> A: Students to surface real problems anonymously. Student councils and admin to see which issues are recurring — not just one complaint but a cluster of 7. The board page ranks by count so the most common problem is always at the top.

**Q: What stops people spamming fake complaints?**
> A: Right now nothing — this is an MVP for a 24-hour hack. In production you'd add rate limiting per IP or a one-time login. The clustering already dilutes spam because one person can't move a cluster count much.

**Q: Why a card and not just a form?**
> A: A form captures symptoms. A card captures the problem, the pattern, and three specific fixes with owners and timelines. It's ready to hand to someone who can actually act on it.

**Q: Can this work for things other than campuses?**
> A: Yes — change the system prompt in `llm.py`. The same pipeline works for any community: office buildings, housing societies, hospitals. The stack is generic; only the prompt is domain-specific.

### On the build

**Q: How long did this take?**
> A: 24 hours, 4 people. Backend and AI pipeline in the first 12 hours, frontend wired up by hour 16, QA and polish in the final 8.

**Q: What would you cut if you had to demo in 5 minutes with no internet?**
> A: We have a 90-second pre-recorded backup video showing the full flow: voice rant → card → board. We also have the app running fully offline on the demo machine.

**Q: What's the biggest risk to the live demo?**
> A: The first LLM request after a cold start takes about 30 seconds. We warm it up by running one dummy request before going on stage. We also have a phone hotspot ready if venue Wi-Fi fails.

---

## Your speaker slot (Slide 7 — Results + Privacy)

**Your 90-second script:**

> "Let's talk numbers. Every text rant produces a card in about 2 seconds on a laptop CPU. Voice takes under 15 seconds end to end — record, transcribe, generate three fixes. We tested 10 different complaint types and got valid, structured JSON every time.
>
> On privacy: nothing leaves this machine. Whisper transcribes locally. Qwen2.5 runs through Ollama on localhost. MiniLM embeds locally. We checked the database schema — no names, no emails, no IDs. Just an anonymous random string per card.
>
> We showed a one-line notice on the record screen. Users know what's stored. And because everything runs locally, even if you unplugged the internet right now, RantLab would still work."

---

## One-page quick reference (print this for the demo table)

| If asked about... | Say... |
|---|---|
| Speed | "2 seconds for text, under 15 for voice" |
| Privacy | "100% local — Ollama, Whisper, MiniLM, all on-device" |
| Clustering | "Cosine similarity with MiniLM, threshold 0.6" |
| Bad JSON | "Pydantic validation, one retry, then friendly error" |
| Scale | "This is an MVP — rate limiting and auth in v2" |
| Other domains | "Just change the system prompt in llm.py" |
| Backup | "Pre-recorded 90s video ready on the demo machine" |
