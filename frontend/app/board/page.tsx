"use client";

import Link from "next/link";
import { useCallback, useEffect, useMemo, useState } from "react";
import { ApiRequestError, getBoard, type Board } from "@/lib/api";
import { timeAgo } from "@/lib/format";

const REFRESH_MS = 20000;

export default function BoardPage() {
  const [board, setBoard] = useState<Board | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [showSingles, setShowSingles] = useState(false);
  const [query, setQuery] = useState("");
  const [refreshing, setRefreshing] = useState(false);

  const load = useCallback(
    () =>
      getBoard()
        .then((b) => {
          setBoard(b);
          setError(null);
        })
        .catch((e) => setError(e instanceof ApiRequestError ? e.message : "Couldn't load the board.")),
    []
  );

  useEffect(() => {
    load();
    const id = window.setInterval(load, REFRESH_MS);
    return () => window.clearInterval(id);
  }, [load]);

  async function refresh() {
    setRefreshing(true);
    await load();
    setRefreshing(false);
  }

  const clusters = useMemo(() => board?.clusters ?? [], [board]);
  const q = query.trim().toLowerCase();
  const matches = q
    ? clusters.filter(
        (c) => c.label.toLowerCase().includes(q) || c.complaints.some((x) => x.transcript.toLowerCase().includes(q))
      )
    : clusters;
  const visible = showSingles || q ? matches : matches.filter((c) => c.count > 1);
  const hiddenCount = matches.length - visible.length;
  const total = clusters.reduce((sum, c) => sum + c.count, 0);
  const max = Math.max(1, ...clusters.map((c) => c.count));

  return (
    <div className="space-y-8">
      <section>
        <h1 className="font-display text-5xl font-extrabold leading-[1.02] tracking-tight text-ink">What keeps going wrong</h1>
        <p className="mt-4 max-w-xl text-lg leading-relaxed text-ink-soft">
          Similar rants are grouped automatically. The longer the bar, the more people reported it.
        </p>
      </section>

      {board && total > 0 && (
        <div className="flex flex-col gap-3 sm:flex-row sm:items-center">
          <div className="relative flex-1">
            <svg viewBox="0 0 24 24" className="pointer-events-none absolute left-4 top-1/2 h-4 w-4 -translate-y-1/2 text-ink-soft" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" aria-hidden="true">
              <circle cx="11" cy="11" r="7" />
              <path d="M20 20l-3.5-3.5" />
            </svg>
            <input
              type="search"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Search problems, e.g. wifi or canteen"
              aria-label="Search problems"
              className="w-full rounded-full border border-line bg-surface py-3 pl-11 pr-4 text-sm text-ink outline-none transition-colors placeholder:text-ink-soft/70 focus:border-ink"
            />
          </div>
          <div className="flex items-center justify-between gap-3 sm:justify-end">
            <span className="text-sm text-ink-soft">
              <span className="font-semibold text-ink">{total}</span> reports in{" "}
              <span className="font-semibold text-ink">{clusters.length}</span> {clusters.length === 1 ? "group" : "groups"}
            </span>
            <button
              onClick={refresh}
              aria-label="Refresh the board"
              title="Refreshes automatically every 20 seconds"
              className="flex h-10 w-10 items-center justify-center rounded-full border border-line bg-surface text-ink-soft transition-colors hover:text-ink"
            >
              <svg viewBox="0 0 24 24" className={`h-4 w-4 ${refreshing ? "animate-spin" : ""}`} fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
                <path d="M20 11a8 8 0 1 0-2.3 5.7" />
                <path d="M20 4v7h-7" />
              </svg>
            </button>
          </div>
        </div>
      )}

      {error && <p className="rounded-2xl border border-heat/20 bg-heat-soft px-5 py-4 text-sm text-heat">{error}</p>}

      {!board && !error && (
        <div className="space-y-3">
          {[0, 1, 2].map((i) => (
            <div key={i} className="h-28 animate-pulse rounded-[24px] bg-surface" />
          ))}
        </div>
      )}

      {board && clusters.length === 0 && (
        <div className="rounded-[28px] border border-dashed border-line bg-surface p-10 text-center">
          <p className="font-display text-2xl font-bold text-ink">Nothing reported yet</p>
          <p className="mt-2 text-ink-soft">Once people start ranting, recurring problems show up here.</p>
          <Link href="/" className="mt-6 inline-block rounded-full bg-brand px-6 py-3 text-sm font-semibold text-white">
            Report the first problem
          </Link>
        </div>
      )}

      {board && q && matches.length === 0 && (
        <p className="rounded-2xl border border-dashed border-line bg-surface px-5 py-8 text-center text-ink-soft">
          No problems match &ldquo;{query}&rdquo;. Try a shorter word.
        </p>
      )}

      <ul className="space-y-3">
        {visible.map((c) => (
          <li key={c.id} className="overflow-hidden rounded-[24px] border border-line bg-surface">
            <details className="group">
              <summary className="flex cursor-pointer list-none items-center gap-5 p-5 sm:p-6 [&::-webkit-details-marker]:hidden">
                <span className="w-12 shrink-0 text-right font-display text-4xl font-bold tabular-nums text-ink">{c.count}</span>
                <div className="min-w-0 flex-1">
                  <p className="font-semibold text-ink">{c.label}</p>
                  <div className="mt-2.5 h-2 overflow-hidden rounded-full bg-mist">
                    <div className="h-full rounded-full bg-heat transition-[width] duration-500" style={{ width: `${(c.count / max) * 100}%` }} />
                  </div>
                  <p className="mt-2 text-xs text-ink-soft">Last reported {timeAgo(c.latest_at)}</p>
                </div>
                <svg viewBox="0 0 24 24" className="h-5 w-5 shrink-0 text-ink-soft transition-transform group-open:rotate-180" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
                  <path d="M6 9l6 6 6-6" />
                </svg>
              </summary>
              <ul className="space-y-1 border-t border-line bg-mist/50 px-4 py-3 sm:px-5">
                {c.complaints.map((x, i) => (
                  <li key={`${x.card_id}-${i}`}>
                    <Link href={`/card/${x.card_id}`} className="block rounded-xl px-3 py-2.5 text-sm leading-relaxed text-ink transition-colors hover:bg-surface">
                      &ldquo;{x.transcript}&rdquo;
                    </Link>
                  </li>
                ))}
              </ul>
            </details>
          </li>
        ))}
      </ul>

      {hiddenCount > 0 && (
        <button onClick={() => setShowSingles(true)} className="text-sm font-semibold text-ink-soft underline-offset-4 hover:text-ink hover:underline">
          Show {hiddenCount} one-off {hiddenCount === 1 ? "report" : "reports"}
        </button>
      )}

      {board && total > 0 && <p className="text-xs text-ink-soft">The board refreshes automatically every 20 seconds.</p>}
    </div>
  );
}