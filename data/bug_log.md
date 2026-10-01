# RantLab — Bug Log (d6)

**Owner: Priyan** | Start filling this at H12. Send priority-1 bugs to Akilan immediately.

Priority: **P1** = blocks the demo | **P2** = bad UX, fix before H16 | **P3** = cosmetic, fix if time allows

---

## How to run the QA pass

Test every scenario below in order. Check the box when it passes. Log failures in the table.

### Scenario checklist

#### Text input
- [ ] Normal rant (20–50 words) → card returned, all 3 fixes present
- [ ] Very short text (1 word) → friendly error, not a crash
- [ ] Blank / whitespace only → `empty_text` error shown in UI
- [ ] 2000 characters exactly → card returned (boundary)
- [ ] 2001 characters → `too_long` error
- [ ] Special characters: `"<>&'` in the rant → card returned, no XSS

#### Voice input
- [ ] 25-second clean recording → transcribed and card returned
- [ ] Under 1 second of audio (near silence) → `empty_audio` error
- [ ] Noisy background recording (use `data/audio/noisy.webm`) → card or friendly error
- [ ] Full 30-second recording → card returned within 35 s
- [ ] Browser mic permission denied → UI shows a clear message

#### Board
- [ ] Load seed data (`python scripts/load_seed.py`) → board shows clusters
- [ ] Wi-Fi complaints in same cluster, canteen complaints separate
- [ ] Board sorted by count descending

#### Card share page
- [ ] Open `/card/c_mock01` (or a real ID) → card renders
- [ ] Open `/card/c_nope` → 404 page, not a crash
- [ ] Copy link button → clipboard has correct URL

#### Network / edge cases
- [ ] Backend down while submitting → frontend shows error, does not freeze
- [ ] Slow network (throttle in DevTools to Slow 3G) → loading states visible
- [ ] Reload page mid-loading → no broken state

#### Mobile (use tunnel URL from cloudflared / ngrok)
- [ ] Mic permission prompt appears on Chrome Android
- [ ] Card readable on a 375px-wide screen
- [ ] Share URL opens correctly on phone browser

---

## Bug table

| # | Priority | Area | Steps to reproduce | Expected | Actual | Assigned to | Fixed? |
|---|---|---|---|---|---|---|---|
| 1 | | | | | | | |
| 2 | | | | | | | |
| 3 | | | | | | | |
| 4 | | | | | | | |
| 5 | | | | | | | |
| 6 | | | | | | | |
| 7 | | | | | | | |
| 8 | | | | | | | |

*(add rows as needed)*

---

## Known risks to watch for

| Risk | What to check |
|---|---|
| Ollama returns bad JSON | Does the UI show a friendly error (not a stack trace)? |
| Whisper times out | Does the UI show "Try again" rather than spinning forever? |
| DB locked (two requests at once) | Submit two rants quickly — do both return cards? |
| Embedding size mismatch after DB wipe | Delete `data/rantlab.db` and restart; board should still work |
