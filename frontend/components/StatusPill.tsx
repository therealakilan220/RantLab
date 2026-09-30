"use client";

import { useEffect, useState } from "react";
import { getHealth } from "@/lib/api";

type State = "checking" | "live" | "stub" | "degraded" | "offline";

const LABEL: Record<State, string> = {
  checking: "Checking backend",
  live: "AI online, running locally",
  stub: "Backend in stub mode, AI off",
  degraded: "AI model not ready",
  offline: "Backend offline",
};

const DOT: Record<State, string> = {
  checking: "bg-line",
  live: "bg-plan",
  stub: "bg-warn",
  degraded: "bg-warn",
  offline: "bg-heat",
};

export default function StatusPill() {
  const [state, setState] = useState<State>("checking");

  useEffect(() => {
    let cancelled = false;
    const check = () =>
      getHealth()
        .then((h) => {
          if (cancelled) return;
          if (h.stub_mode) setState("stub");
          else setState(h.ollama && h.whisper ? "live" : "degraded");
        })
        .catch(() => {
          if (!cancelled) setState("offline");
        });
    check();
    const id = window.setInterval(check, 30000);
    return () => {
      cancelled = true;
      window.clearInterval(id);
    };
  }, []);

  return (
    <span className="inline-flex items-center gap-2 rounded-full border border-line bg-surface px-3 py-1.5 text-xs font-medium text-ink-soft">
      <span className="relative flex h-2 w-2">
        {state === "live" && <span className="absolute inset-0 animate-ping rounded-full bg-plan/60" />}
        <span className={`relative h-2 w-2 rounded-full ${DOT[state]}`} />
      </span>
      {LABEL[state]}
    </span>
  );
}