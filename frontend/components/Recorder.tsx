"use client";

import { useEffect, useRef, useState } from "react";

const MAX_SECONDS = 30;
const MIN_SECONDS = 1.5;
const MAX_TEXT = 2000;
const BARS = 32;
const IDLE = Array.from({ length: BARS }, (_, i) => 0.1 + 0.12 * Math.abs(Math.sin(i * 0.55)));

const EXAMPLES = [
  { label: "Library Wi-Fi", text: "The library Wi-Fi keeps dropping every afternoon, right when everyone is trying to study, and nobody ever fixes it." },
  { label: "Canteen queue", text: "The canteen queue takes 25 minutes at lunch because only one billing counter is open, and our break is only 40 minutes." },
  { label: "Broken projector", text: "The projector in room 204 has been flickering for a week and every class in that room starts late because of it." },
];

const KBD = "rounded-md border border-line bg-mist px-1.5 py-0.5 font-sans text-[11px] font-semibold text-ink";

function pickFormat(): { mime: string; ext: string } {
  const options = [
    { mime: "audio/webm;codecs=opus", ext: "webm" },
    { mime: "audio/webm", ext: "webm" },
    { mime: "audio/ogg;codecs=opus", ext: "ogg" },
    { mime: "audio/mp4", ext: "mp4" },
  ];
  if (typeof MediaRecorder === "undefined") return { mime: "", ext: "webm" };
  return options.find((o) => MediaRecorder.isTypeSupported(o.mime)) ?? { mime: "", ext: "webm" };
}

const fmt = (s: number) => `0:${String(Math.min(s, MAX_SECONDS)).padStart(2, "0")}`;

type Props = {
  onAudio: (audio: Blob, filename: string) => void;
  onText: (text: string) => void;
};

export default function Recorder({ onAudio, onText }: Props) {
  const [mode, setMode] = useState<"voice" | "text">("voice");
  const [recording, setRecording] = useState(false);
  const [seconds, setSeconds] = useState(0);
  const [text, setText] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [levels, setLevels] = useState<number[]>(IDLE);

  const recorderRef = useRef<MediaRecorder | null>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const chunksRef = useRef<Blob[]>([]);
  const startedAtRef = useRef(0);
  const timerRef = useRef<number | null>(null);
  const audioCtxRef = useRef<AudioContext | null>(null);
  const rafRef = useRef<number | null>(null);
  const latestRef = useRef({ mode, recording, start: () => {}, stop: () => {} });

  function stopTimer() {
    if (timerRef.current !== null) window.clearInterval(timerRef.current);
    timerRef.current = null;
  }

  function stopMeter() {
    if (rafRef.current !== null) cancelAnimationFrame(rafRef.current);
    rafRef.current = null;
    audioCtxRef.current?.close().catch(() => undefined);
    audioCtxRef.current = null;
  }

  function releaseMic() {
    streamRef.current?.getTracks().forEach((t) => t.stop());
    streamRef.current = null;
  }

  useEffect(() => {
    return () => {
      stopTimer();
      stopMeter();
      const rec = recorderRef.current;
      if (rec && rec.state !== "inactive") {
        rec.onstop = null;
        rec.stop();
      }
      releaseMic();
    };
  }, []);

  useEffect(() => {
    latestRef.current = { mode, recording, start: () => void start(), stop };
  });

  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if (e.code !== "Space" || e.repeat) return;
      const target = e.target as HTMLElement | null;
      if (target && (["TEXTAREA", "INPUT", "BUTTON", "SELECT"].includes(target.tagName) || target.isContentEditable)) return;
      const { mode: m, recording: r, start: s, stop: st } = latestRef.current;
      if (m !== "voice") return;
      e.preventDefault();
      if (r) st();
      else s();
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, []);

  function startMeter(stream: MediaStream) {
    const Ctx =
      window.AudioContext ?? (window as unknown as { webkitAudioContext?: typeof AudioContext }).webkitAudioContext;
    if (!Ctx) return;
    const ctx = new Ctx();
    const analyser = ctx.createAnalyser();
    analyser.fftSize = 128;
    analyser.smoothingTimeConstant = 0.75;
    ctx.createMediaStreamSource(stream).connect(analyser);
    const data = new Uint8Array(analyser.frequencyBinCount);
    const usable = Math.floor(data.length * 0.7);
    audioCtxRef.current = ctx;

    const tick = () => {
      analyser.getByteFrequencyData(data);
      setLevels(
        Array.from({ length: BARS }, (_, i) => {
          const pos = Math.abs(i - (BARS - 1) / 2) / (BARS / 2);
          const v = data[Math.min(usable - 1, Math.floor(pos * usable))] / 255;
          return Math.max(0.08, Math.min(1, v * 1.3));
        })
      );
      rafRef.current = requestAnimationFrame(tick);
    };
    tick();
  }

  async function start() {
    setError(null);
    if (!navigator.mediaDevices?.getUserMedia || typeof MediaRecorder === "undefined") {
      setError("This browser can't record here. Open the site on https or localhost in Chrome, or type your rant instead.");
      return;
    }

    let stream: MediaStream;
    try {
      stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    } catch {
      setError("Microphone access is blocked. Allow the mic in your browser settings, or type your rant instead.");
      return;
    }

    const { mime, ext } = pickFormat();
    const rec = mime ? new MediaRecorder(stream, { mimeType: mime }) : new MediaRecorder(stream);
    streamRef.current = stream;
    recorderRef.current = rec;
    chunksRef.current = [];

    rec.ondataavailable = (e) => {
      if (e.data.size > 0) chunksRef.current.push(e.data);
    };

    rec.onstop = () => {
      const duration = (Date.now() - startedAtRef.current) / 1000;
      stopTimer();
      stopMeter();
      releaseMic();
      setLevels(IDLE);
      setRecording(false);
      const blob = new Blob(chunksRef.current, { type: rec.mimeType || mime || "audio/webm" });
      if (duration < MIN_SECONDS || blob.size === 0) {
        setError("That was too short. Take a few seconds and say what's bugging you.");
        return;
      }
      onAudio(blob, `rant.${ext}`);
    };

    rec.start();
    startedAtRef.current = Date.now();
    setSeconds(0);
    setRecording(true);
    try {
      startMeter(stream);
    } catch {
      /* waveform is decorative; recording still works */
    }

    timerRef.current = window.setInterval(() => {
      const s = Math.floor((Date.now() - startedAtRef.current) / 1000);
      setSeconds(s);
      if (s >= MAX_SECONDS) stop();
    }, 250);
  }

  function stop() {
    stopTimer();
    const rec = recorderRef.current;
    if (rec && rec.state !== "inactive") rec.stop();
  }

  function submitText() {
    const trimmed = text.trim();
    if (!trimmed) {
      setError("Write a sentence or two about what went wrong.");
      return;
    }
    setError(null);
    onText(trimmed);
  }

  const tab = (active: boolean) =>
    `rounded-full px-4 py-1.5 text-sm font-medium transition-colors ${
      active ? "bg-surface text-ink shadow-sm" : "text-ink-soft hover:text-ink"
    }`;

  return (
    <div className="overflow-hidden rounded-[28px] border border-line bg-surface shadow-card">
      <div className="flex items-center justify-between gap-4 border-b border-line px-5 py-3">
        <div role="tablist" aria-label="How do you want to rant?" className="flex rounded-full bg-mist p-1">
          <button role="tab" aria-selected={mode === "voice"} className={tab(mode === "voice")} onClick={() => setMode("voice")} disabled={recording}>
            Speak
          </button>
          <button role="tab" aria-selected={mode === "text"} className={tab(mode === "text")} onClick={() => setMode("text")} disabled={recording}>
            Type
          </button>
        </div>
        {mode === "voice" && (
          <span className={`font-display text-sm font-semibold tabular-nums ${recording ? "text-heat" : "text-ink-soft"}`}>
            {fmt(seconds)} / {fmt(MAX_SECONDS)}
          </span>
        )}
      </div>

      {mode === "voice" ? (
        <div className="px-5 pb-8 pt-8 sm:px-8">
          <div className="flex h-28 items-center justify-center gap-[3px]" aria-hidden="true">
            {levels.map((level, i) => (
              <span
                key={i}
                className={`w-1.5 rounded-full transition-[height] duration-75 sm:w-2 ${recording ? "bg-heat" : "bg-line"}`}
                style={{ height: `${Math.round(level * 100)}%` }}
              />
            ))}
          </div>
          <div className="mt-3 h-1 overflow-hidden rounded-full bg-mist">
            <div
              className="h-full rounded-full bg-heat transition-[width] duration-300"
              style={{ width: `${(Math.min(seconds, MAX_SECONDS) / MAX_SECONDS) * 100}%` }}
            />
          </div>

          <div className="mt-8 flex flex-col items-center gap-4 sm:flex-row sm:justify-center sm:gap-6">
            <button
              onClick={recording ? stop : start}
              aria-label={recording ? "Stop recording" : "Start recording"}
              className={`relative flex h-20 w-20 shrink-0 items-center justify-center rounded-full text-white transition-transform active:scale-95 ${
                recording ? "bg-heat" : "bg-brand hover:scale-105"
              }`}
            >
              {recording && <span className="absolute inset-0 animate-ping rounded-full bg-heat/30" />}
              {recording ? (
                <span className="relative h-6 w-6 rounded-md bg-white" />
              ) : (
                <svg viewBox="0 0 24 24" className="h-9 w-9" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
                  <rect x="9" y="2" width="6" height="12" rx="3" />
                  <path d="M5 10a7 7 0 0 0 14 0" />
                  <line x1="12" y1="17" x2="12" y2="22" />
                </svg>
              )}
            </button>
            <div className="text-center sm:text-left">
              <p className="font-display text-lg font-semibold text-ink">{recording ? "Listening" : "Tap to start ranting"}</p>
              <p className="text-sm text-ink-soft">
                {recording
                  ? "Tap again when you're done. Recording stops at 30 seconds."
                  : "Talk the way you'd complain to a friend. 20 to 30 seconds is plenty."}
              </p>
              <p className="mt-2 hidden text-xs text-ink-soft sm:block">
                Shortcut: press <kbd className={KBD}>Space</kbd> to {recording ? "stop" : "start"}
              </p>
            </div>
          </div>
        </div>
      ) : (
        <div className="p-5 sm:p-8">
          <label htmlFor="rant-text" className="font-display text-lg font-semibold text-ink">
            What went wrong?
          </label>
          <div className="mt-3 flex flex-wrap items-center gap-2">
            <span className="text-sm text-ink-soft">Try an example:</span>
            {EXAMPLES.map((ex) => (
              <button
                key={ex.label}
                onClick={() => {
                  setText(ex.text);
                  setError(null);
                }}
                className="rounded-full border border-line px-3 py-1.5 text-xs font-medium text-ink-soft transition-colors hover:border-ink hover:text-ink"
              >
                {ex.label}
              </button>
            ))}
          </div>
          <textarea
            id="rant-text"
            value={text}
            onChange={(e) => setText(e.target.value)}
            onKeyDown={(e) => {
              if ((e.ctrlKey || e.metaKey) && e.key === "Enter") {
                e.preventDefault();
                submitText();
              }
            }}
            maxLength={MAX_TEXT}
            rows={5}
            placeholder="The library Wi-Fi keeps dropping every afternoon and nobody fixes it."
            className="mt-4 w-full resize-none rounded-2xl border border-line bg-mist/50 p-4 text-base leading-relaxed text-ink outline-none transition-colors placeholder:text-ink-soft/60 focus:border-ink focus:bg-surface"
          />
          <div className="mt-4 flex items-center justify-between gap-4">
            <span className="text-sm tabular-nums text-ink-soft">
              {text.length} / {MAX_TEXT}
              <span className="ml-3 hidden text-xs sm:inline">
                <kbd className={KBD}>Ctrl</kbd> + <kbd className={KBD}>Enter</kbd> to send
              </span>
            </span>
            <button
              onClick={submitText}
              className="rounded-full bg-brand px-6 py-3 text-sm font-semibold text-white transition-colors hover:bg-brand/90"
            >
              Turn it into a plan
            </button>
          </div>
        </div>
      )}

      {error && (
        <p role="alert" className="border-t border-heat/20 bg-heat-soft px-5 py-4 text-sm text-heat sm:px-8">
          {error}
        </p>
      )}
    </div>
  );
}