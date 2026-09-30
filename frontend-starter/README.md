# Frontend setup (Jayasree, do this once)

This folder holds the files we already agreed on (API client, types, mocks, proxy config).
The Next.js app itself is generated with one command, then these files are copied in.

Run from the **repo root**:

```bash
# 1. Generate the app (choose the defaults if asked: TypeScript, Tailwind, App Router, no src/ dir)
npx create-next-app@latest frontend --ts --tailwind --eslint --app --no-src-dir --import-alias "@/*" --use-npm

# 2. Copy our files in (overwrites next.config)
cp -r frontend-starter/. frontend/
rm -f frontend/README.md            # keep the generated one
rm -f frontend/next.config.mjs frontend/next.config.js   # only if the generator made one of these

# 3. Local env
cp frontend/.env.local.example frontend/.env.local

# 4. Run
cd frontend && npm run dev          # http://localhost:3000
```

Windows PowerShell: use `xcopy frontend-starter frontend /E /Y` instead of `cp -r`, and `del` instead of `rm -f`.

After it works, commit `frontend/` and delete `frontend-starter/` in the same commit so nobody copies it twice.

## How to build against the API

- `NEXT_PUBLIC_USE_MOCK=1` returns `mocks/card.json` and `mocks/board.json` after a short delay, so you can build every screen with no backend.
- Set it to `0` (and restart `npm run dev`) once the backend is running in stub mode. Stub mode returns real-shaped cards.
- Use `lib/api.ts` for every call. Do not call `fetch("/api/...")` from components directly.
- `lib/types.ts` has `TIMEFRAME_LABEL` and `COST_LABEL` for display text.

## Screens to build (in order)

1. `/` record or type, loading stages, then the card
2. `/card/[id]` public share page, mobile first
3. `/board` recurring issues (stretch)

## Microphone note

Browsers only allow the mic on `localhost` or HTTPS. To test on a phone, run a free tunnel to port 3000
(`cloudflared tunnel --url http://localhost:3000` or `ngrok http 3000`) and open the HTTPS link it prints.
