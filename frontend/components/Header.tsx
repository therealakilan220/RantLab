"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import Logo from "./Logo";
import ThemeToggle from "./ThemeToggle";

export default function Header() {
  const path = usePathname() ?? "/";

  const link = (href: string, label: string) => {
    const active = href === "/" ? path === "/" : path.startsWith(href);
    return (
      <Link
        href={href}
        className={`rounded-full px-3 py-2 text-sm font-medium transition-colors sm:px-4 ${
          active ? "bg-brand text-white" : "text-ink-soft hover:bg-surface hover:text-ink"
        }`}
      >
        {label}
      </Link>
    );
  };

  return (
    <header className="mx-auto flex max-w-5xl items-center justify-between gap-3 px-5 py-5">
      <Link href="/" className="flex items-center gap-2.5" aria-label="RantLab home">
        <Logo />
        <span className="hidden font-display text-xl font-bold tracking-tight text-ink sm:inline">RantLab</span>
      </Link>
      <div className="flex items-center gap-2">
        <nav className="flex gap-1 rounded-full border border-line bg-mist p-1">
          {link("/", "New rant")}
          {link("/board", "Board")}
          {link("/about", "About")}
        </nav>
        <ThemeToggle />
      </div>
    </header>
  );
}