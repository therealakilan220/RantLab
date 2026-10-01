# RantLab — Backup Demo Video Script (d8)
**Owner: Priyan** | Record this with OBS or any screen recorder. Target: 90 seconds.

---

## Before you record

- [ ] Backend running: `uvicorn app.main:app --reload --port 8000`
- [ ] Frontend running: `cd frontend && npm run dev`
- [ ] Seed data loaded: `python scripts/load_seed.py`
- [ ] Browser open at `http://localhost:3000`
- [ ] OBS (or Windows Game Bar: Win+G) ready, mic on, resolution 1920×1080
- [ ] Silence your phone

---

## Shot-by-shot script (90 seconds)

### Shot 1 — Home screen (0:00–0:08)
Show the RantLab home page.

**Say:** *"RantLab — don't just complain about the problem. Turn it into a plan."*

Pan the camera / zoom slowly across the home screen. Make sure the tagline and record button are visible.

---

### Shot 2 — Text rant submission (0:08–0:25)
Click the **Text** tab. Type this complaint slowly so viewers can read it:

> *"The Wi-Fi in the library keeps dropping every afternoon and nobody seems to fix it."*

Hit submit. The loading stages appear: **Transcribing... → Finding the real problem... → Drafting fixes...**

**Say:** *"Type or record your complaint. RantLab transcribes it, finds the root cause, and drafts three fixes."*

---

### Shot 3 — Card result (0:25–0:50)
The card appears. Slowly scroll through it on screen.

**Say:** *"Here's the card. The problem — library Wi-Fi drops at peak hours. The pattern — overloaded access points. Three fixes: post a fault QR code today for free, survey the access points this week for free, add new hardware this semester with a budget. Each fix has an owner, a cost, and a timeframe. Ready to hand to someone who can actually act."*

Point out the **Share** button.

---

### Shot 4 — Share link (0:50–1:00)
Click the share / copy link button. Open a new tab and paste the `/card/[id]` URL.

**Say:** *"One click — a shareable link. Anyone with this URL sees the full card. No login needed."*

---

### Shot 5 — Board page (1:00–1:25)
Navigate to `/board`.

**Say:** *"Now the board. Every complaint is embedded and grouped by similarity. Library Wi-Fi — seven complaints. Canteen queue — five. Hostel water — four. The most reported problem is always at the top. Student councils can see what's really happening, not just a single angry message."*

Slowly scroll through the clusters.

---

### Shot 6 — Close (1:25–1:30)
Return to the home page. Logo visible.

**Say:** *"RantLab. Local AI, anonymous by design, running on free open-source tools. No paid APIs."*

---

## Recording tips

- Use **1080p 60fps** if your machine can handle it, otherwise 1080p 30fps
- Keep the **browser window maximised**, no other apps visible
- Export as **MP4 H.264** — most projectors and Google Drive handle it
- Final file name: `rantlab_demo_backup.mp4`
- Upload to the team Google Drive folder immediately after recording

## OBS quick setup

1. Open OBS → Add Source → Display Capture
2. Add Source → Audio Input Capture (select your mic)
3. Settings → Output → Recording Path → Desktop
4. Hit **Start Recording**, do the script, hit **Stop Recording**
5. Find the `.mkv` file on your Desktop, rename and upload

---

## If you cannot record with OBS

Use **Windows Game Bar**: `Win + G` → click the record button (circle).
The video saves to `C:\Users\<you>\Videos\Captures\`.
