"use client";

import { useEffect } from "react";

const KEY = "rantlab-theme";

function apply(theme: "light" | "dark") {
  document.documentElement.dataset.theme = theme;
}

export default function ThemeToggle() {
  useEffect(() => {
    const mq = window.matchMedia("(prefers-color-scheme: dark)");
    const onChange = (e: MediaQueryListEvent) => {
      try {
        if (window.localStorage.getItem(KEY)) return;
      } catch {
        /* storage unavailable */
      }
      apply(e.matches ? "dark" : "light");
    };
    mq.addEventListener("change", onChange);
    return () => mq.removeEventListener("change", onChange);
  }, []);

  function toggle() {
    const next = document.documentElement.dataset.theme === "dark" ? "light" : "dark";
    apply(next);
    try {
      window.localStorage.setItem(KEY, next);
    } catch {
      /* storage unavailable */
    }
  }

  return (
    <button
      onClick={toggle}
      aria-label="Switch between light and dark mode"
      title="Switch theme"
      className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full border border-line bg-mist text-ink-soft transition-colors hover:text-ink"
    >
      <svg viewBox="0 0 24 24" className="h-5 w-5 dark:hidden" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
        <path d="M21 12.8A9 9 0 1 1 11.2 3a7 7 0 0 0 9.8 9.8z" />
      </svg>
      <svg viewBox="0 0 24 24" className="hidden h-5 w-5 dark:block" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
        <circle cx="12" cy="12" r="4" />
        <path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4" />
      </svg>
    </button>
  );
}