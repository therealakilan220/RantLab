"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Recorder from "@/components/Recorder";
import LoadingStages from "@/components/LoadingStages";
import RecentPlans from "@/components/RecentPlans";
import { ApiRequestError, submitAudio, submitText } from "@/lib/api";
import { addToHistory } from "@/lib/history";
import type { Card } from "@/lib/types";

const STEPS = ["Rant for up to 30 seconds", "We find the real problem", "Get three fixes with owners"];

export default function Home() {
  const router = useRouter();
  const [working, setWorking] = useState<"voice" | "text" | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function run(kind: "voice" | "text", task: () => Promise<Card>) {
    setError(null);
    setWorking(kind);
    try {
      const card = await task();
      addToHistory(card);
      router.push(`/card/${card.id}`);
    } catch (e) {
      setError(e instanceof ApiRequestError ? e.message : "Something went wrong. Please try again.");
      setWorking(null);
    }
  }

  return (
    <div className="space-y-10">
      <section>
        <h1 className="font-display text-5xl font-extrabold leading-[1.02] tracking-tight text-ink sm:text-6xl">
          Say what&apos;s broken.
          <br />
          Leave with a plan.
        </h1>
        <p className="mt-5 max-w-xl text-lg leading-relaxed text-ink-soft">
          Complain about anything on campus, the way you would to a friend. RantLab works out the real
          problem and drafts three fixes, each with an owner, a cost and a timeframe.
        </p>
        <ol className="mt-8 grid gap-3 sm:grid-cols-3">
          {STEPS.map((step, i) => (
            <li key={step} className="flex items-center gap-3 text-sm text-ink-soft">
              <span className="flex h-7 w-7 shrink-0 items-center justify-center rounded-full border border-line bg-surface font-display text-sm font-bold text-ink">
                {i + 1}
              </span>
              {step}
            </li>
          ))}
        </ol>
      </section>

      {working ? (
        <LoadingStages inputType={working} />
      ) : (
        <Recorder
          onAudio={(blob, filename) => run("voice", () => submitAudio(blob, filename))}
          onText={(text) => run("text", () => submitText(text))}
        />
      )}

      {error && (
        <p role="alert" className="rounded-2xl border border-heat/20 bg-heat-soft px-5 py-4 text-sm text-heat">
          {error}
        </p>
      )}

      <p className="flex items-center gap-2 text-sm text-ink-soft">
        <svg viewBox="0 0 24 24" className="h-4 w-4 shrink-0" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
          <rect x="5" y="11" width="14" height="10" rx="2" />
          <path d="M8 11V7a4 4 0 0 1 8 0v4" />
        </svg>
        No name, no email, no login. Every report is anonymous.
      </p>

      {!working && <RecentPlans />}
    </div>
  );
}