"use client";

import { useEffect, useState } from "react";

const VOICE = ["Transcribing your rant", "Finding the real problem", "Drafting three fixes"];
const TEXT = ["Finding the real problem", "Drafting three fixes"];
const STEP_AT_MS = [0, 4000, 10000];

export default function LoadingStages({ inputType }: { inputType: "voice" | "text" }) {
  const stages = inputType === "voice" ? VOICE : TEXT;
  const [active, setActive] = useState(0);
  const [elapsed, setElapsed] = useState(0);

  useEffect(() => {
    const timers = stages
      .slice(1)
      .map((_, i) => window.setTimeout(() => setActive(i + 1), STEP_AT_MS[i + 1]));
    return () => timers.forEach((t) => window.clearTimeout(t));
  }, [stages]);

  useEffect(() => {
    const startedAt = Date.now();
    const id = window.setInterval(() => setElapsed(Math.floor((Date.now() - startedAt) / 1000)), 1000);
    return () => window.clearInterval(id);
  }, []);

  return (
    <div className="rounded-[28px] border border-line bg-surface p-6 shadow-card sm:p-8" aria-live="polite">
      <div className="flex items-start justify-between gap-4">
        <div>
          <p className="font-display text-2xl font-bold text-ink">Working on your plan</p>
          <p className="mt-1 text-sm text-ink-soft">This runs on a local AI model, so it takes 5 to 25 seconds.</p>
        </div>
        <span className="shrink-0 rounded-full bg-mist px-3 py-1 font-display text-sm font-semibold tabular-nums text-ink">
          {elapsed}s
        </span>
      </div>
      <ol className="mt-6 space-y-1">
        {stages.map((label, i) => (
          <li
            key={label}
            className={`flex items-center gap-4 rounded-2xl px-4 py-3 transition-colors ${i === active ? "bg-mist" : ""}`}
          >
            {i < active ? (
              <span className="flex h-7 w-7 items-center justify-center rounded-full bg-plan text-on-accent">
                <svg viewBox="0 0 24 24" className="h-4 w-4" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
                  <path d="M5 12.5l4.5 4.5L19 7.5" />
                </svg>
              </span>
            ) : i === active ? (
              <span className="h-7 w-7 animate-spin rounded-full border-[3px] border-heat border-t-transparent" />
            ) : (
              <span className="h-7 w-7 rounded-full border-2 border-line" />
            )}
            <span className={i <= active ? "font-medium text-ink" : "text-ink-soft"}>{label}</span>
          </li>
        ))}
      </ol>
      {elapsed >= 30 && (
        <p className="mt-4 text-sm text-ink-soft">Taking longer than usual. The model may be warming up; hang on a few more seconds.</p>
      )}
    </div>
  );
}