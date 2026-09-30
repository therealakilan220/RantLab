import type { Card } from "@/lib/types";
import { COST_LABEL, COST_STYLE, TIMEFRAME_LABEL, formatDate } from "@/lib/format";
import Logo from "./Logo";

function PersonIcon() {
  return (
    <svg viewBox="0 0 24 24" className="h-3.5 w-3.5" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
      <circle cx="12" cy="8" r="4" />
      <path d="M4 21a8 8 0 0 1 16 0" />
    </svg>
  );
}

function ClockIcon() {
  return (
    <svg viewBox="0 0 24 24" className="h-3.5 w-3.5" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
      <circle cx="12" cy="12" r="9" />
      <path d="M12 7v5l3 2" />
    </svg>
  );
}

export default function ConceptCard({ card }: { card: Card }) {
  return (
    <article className="overflow-hidden rounded-[28px] border border-line bg-surface shadow-card">
      <header className="bg-brand px-6 pb-9 pt-6 text-white sm:px-10 sm:pt-8">
        <div className="flex items-center justify-between gap-4 text-sm text-white/60">
          <span className="flex items-center gap-2">
            <Logo className="h-6 w-6" onDark />
            Action plan
          </span>
          <span>{formatDate(card.created_at)}</span>
        </div>
        <h2 className="mt-7 font-display text-3xl font-bold leading-tight tracking-tight sm:text-4xl">{card.problem}</h2>
      </header>

      <div className="px-6 py-8 sm:px-10">
        <figure className="relative pl-9">
          <span aria-hidden="true" className="absolute -top-2 left-0 font-display text-6xl leading-none text-heat">
            &ldquo;
          </span>
          <blockquote className="text-lg leading-relaxed text-ink">{card.transcript}</blockquote>
          <figcaption className="mt-2 text-sm text-ink-soft">
            {card.input_type === "voice" ? "Spoken" : "Typed"} anonymously
          </figcaption>
        </figure>

        <div className="mt-8 grid gap-6 border-t border-line pt-6 sm:grid-cols-2">
          <div>
            <h3 className="text-sm font-semibold text-ink">Why it keeps happening</h3>
            <p className="mt-1.5 leading-relaxed text-ink-soft">{card.pattern}</p>
          </div>
          <div>
            <h3 className="text-sm font-semibold text-ink">Who else it affects</h3>
            <p className="mt-1.5 leading-relaxed text-ink-soft">{card.affected}</p>
          </div>
        </div>
      </div>

      <section className="border-t border-line bg-mist/60 px-6 py-8 sm:px-10">
        <div className="flex items-baseline justify-between gap-4">
          <h3 className="font-display text-2xl font-bold text-ink">Three fixes</h3>
          <span className="text-sm text-ink-soft">Easiest first</span>
        </div>
        <ol className="mt-5 space-y-3">
          {card.fixes.map((fix, i) => (
            <li key={i} className="flex gap-4 rounded-2xl border border-line bg-surface p-5">
              <span className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-plan font-display font-bold text-on-accent">
                {i + 1}
              </span>
              <div className="min-w-0 flex-1">
                <p className="font-semibold leading-snug text-ink">{fix.title}</p>
                <p className="mt-1 text-sm leading-relaxed text-ink-soft">{fix.detail}</p>
                <div className="mt-4 flex flex-wrap items-center gap-2 text-xs font-medium">
                  <span className="inline-flex items-center gap-1.5 rounded-full bg-mist px-3 py-1 text-ink">
                    <PersonIcon />
                    {fix.owner}
                  </span>
                  <span className={`rounded-full px-3 py-1 ${COST_STYLE[fix.cost] ?? "bg-mist text-ink"}`}>
                    {COST_LABEL[fix.cost] ?? fix.cost}
                  </span>
                  <span className="inline-flex items-center gap-1.5 rounded-full bg-mist px-3 py-1 text-ink">
                    <ClockIcon />
                    {TIMEFRAME_LABEL[fix.timeframe] ?? fix.timeframe}
                  </span>
                </div>
              </div>
            </li>
          ))}
        </ol>
      </section>

      <footer className="flex flex-wrap items-center justify-between gap-2 border-t border-line px-6 py-4 text-sm text-ink-soft sm:px-10">
        <span className="font-display font-semibold text-ink">RantLab</span>
        <span>Don&apos;t just complain about the problem. Turn it into a plan.</span>
      </footer>
    </article>
  );
}