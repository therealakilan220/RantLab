"use client";

import Link from "next/link";

export default function ErrorPage({ reset }: { error: Error & { digest?: string }; reset: () => void }) {
  return (
    <div className="py-16 text-center">
      <p className="font-display text-3xl font-bold text-ink">Something broke on this page</p>
      <p className="mt-2 text-ink-soft">Try again. If it keeps happening, go back to the home page.</p>
      <div className="mt-8 flex justify-center gap-3">
        <button onClick={reset} className="rounded-full bg-brand px-6 py-3 text-sm font-semibold text-white">
          Try again
        </button>
        <Link href="/" className="rounded-full border border-line bg-surface px-6 py-3 text-sm font-semibold text-ink">
          Home page
        </Link>
      </div>
    </div>
  );
}