"use client";

import Link from "next/link";
import { clearHistory, useHistory } from "@/lib/history";
import { SAMPLE_CARDS } from "@/lib/samples";
import { timeAgo } from "@/lib/format";

export default function RecentPlans() {
  const items = useHistory();
  const rows = [
    ...items.map((i) => ({ id: i.id, problem: i.problem, created_at: i.created_at, sample: false })),
    ...SAMPLE_CARDS.map((c) => ({ id: c.id, problem: c.problem, created_at: c.created_at, sample: true })),
  ];

  return (
    <section className="rounded-[28px] border border-line bg-surface p-6 sm:p-8">
      <div className="flex items-baseline justify-between gap-4">
        <h2 className="font-display text-xl font-bold text-ink">Recent plans</h2>
        {items.length > 0 && (
          <button onClick={clearHistory} className="text-sm font-medium text-ink-soft transition-colors hover:text-ink">
            Clear mine
          </button>
        )}
      </div>
      <p className="mt-1 text-sm text-ink-soft">Your own plans are saved only in this browser.</p>
      <ul className="mt-4 divide-y divide-line">
        {rows.map((row) => (
          <li key={row.id}>
            <Link href={`/card/${row.id}`} className="flex items-center justify-between gap-4 py-3 text-ink transition-colors hover:text-heat">
              <span className="min-w-0 truncate font-medium">{row.problem}</span>
              {row.sample ? (
                <span className="shrink-0 rounded-full bg-mist px-2.5 py-0.5 text-xs font-medium text-ink-soft">Example</span>
              ) : (
                <span className="shrink-0 text-xs text-ink-soft">{timeAgo(row.created_at)}</span>
              )}
            </Link>
          </li>
        ))}
      </ul>
    </section>
  );
}