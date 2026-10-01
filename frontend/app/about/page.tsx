import type { Metadata } from "next";
import Link from "next/link";

export const metadata: Metadata = { title: "How it works" };

const PIPELINE = [
  { title: "You rant", body: "Record up to 30 seconds in the browser, or type it out. No account, no name." },
  { title: "Speech becomes text", body: "faster-whisper transcribes the recording on our own machine. The audio never goes to a cloud service." },
  { title: "The real problem is found", body: "Qwen2.5 3B, running locally through Ollama, strips out the frustration and names the underlying issue, its pattern and who else it affects." },
  { title: "Three fixes are drafted", body: "Each fix names a responsible role, a cost (free, low cost or needs budget) and a timeframe (today, this week or this semester), easiest first." },
  { title: "Similar rants are grouped", body: "MiniLM sentence embeddings and cosine similarity cluster related complaints, so recurring problems rise to the top of the Board." },
];

const STACK = [
  ["Speech to text", "faster-whisper"],
  ["Problem and fixes", "Ollama with Qwen2.5 3B"],
  ["Grouping", "sentence-transformers all-MiniLM-L6-v2"],
  ["Backend", "Python, FastAPI, SQLite"],
  ["Frontend", "Next.js, TypeScript, Tailwind CSS"],
];

const TEAM = [
  ["Akilan Pon Ilango", "Team lead, pipeline and AI prompt"],
  ["Arvind", "Speech, database and clustering"],
  ["Jayasree", "Frontend and live demo"],
  ["Priyan", "Testing, data and pitch deck"],
];

export default function AboutPage() {
  return (
    <div className="space-y-14">
      <section>
        <h1 className="font-display text-5xl font-extrabold leading-[1.02] tracking-tight text-ink">How RantLab works</h1>
        <p className="mt-5 max-w-xl text-lg leading-relaxed text-ink-soft">
          People complain about broken things every day, but those complaints rarely reach anyone who can fix
          them. RantLab turns a 30-second vent into a structured, shareable action plan.
        </p>
      </section>

      <section>
        <h2 className="font-display text-2xl font-bold text-ink">From rant to plan</h2>
        <ol className="mt-6 space-y-0">
          {PIPELINE.map((step, i) => (
            <li key={step.title} className="relative flex gap-5 pb-8 last:pb-0">
              {i < PIPELINE.length - 1 && <span className="absolute left-[18px] top-10 h-[calc(100%-2.5rem)] w-px bg-line" aria-hidden="true" />}
              <span className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-brand font-display font-bold text-white">{i + 1}</span>
              <div className="pt-1">
                <p className="font-semibold text-ink">{step.title}</p>
                <p className="mt-1 leading-relaxed text-ink-soft">{step.body}</p>
              </div>
            </li>
          ))}
        </ol>
      </section>

      <section className="grid gap-6 sm:grid-cols-2">
        <div className="rounded-[24px] border border-line bg-surface p-6">
          <h2 className="font-display text-xl font-bold text-ink">Built on free, open tools</h2>
          <dl className="mt-4 space-y-3">
            {STACK.map(([job, tool]) => (
              <div key={job} className="flex justify-between gap-4 border-b border-line pb-3 text-sm last:border-0 last:pb-0">
                <dt className="text-ink-soft">{job}</dt>
                <dd className="text-right font-medium text-ink">{tool}</dd>
              </div>
            ))}
          </dl>
        </div>
        <div className="rounded-[24px] border border-line bg-surface p-6">
          <h2 className="font-display text-xl font-bold text-ink">Private by design</h2>
          <ul className="mt-4 space-y-3 text-sm leading-relaxed text-ink-soft">
            <li>No login, name or email is ever asked for.</li>
            <li>All AI runs on our own machine. No paid APIs, and complaints are not sent to AI companies.</li>
            <li>Plans store only the complaint and the generated fixes, with no personal identifiers.</li>
            <li>Your list of recent plans lives only in your own browser.</li>
          </ul>
        </div>
      </section>

      <section>
        <h2 className="font-display text-2xl font-bold text-ink">Team Fantastic 4</h2>
        <p className="mt-1 text-ink-soft">Open Innovation track</p>
        <ul className="mt-5 grid gap-3 sm:grid-cols-2">
          {TEAM.map(([name, role]) => (
            <li key={name} className="flex items-center gap-4 rounded-2xl border border-line bg-surface p-4">
              <span className="flex h-11 w-11 shrink-0 items-center justify-center rounded-full bg-mist font-display text-lg font-bold text-ink">
                {name.charAt(0)}
              </span>
              <div>
                <p className="font-semibold text-ink">{name}</p>
                <p className="text-sm text-ink-soft">{role}</p>
              </div>
            </li>
          ))}
        </ul>
      </section>

      <section className="rounded-[28px] bg-brand px-6 py-10 text-center text-white sm:px-10">
        <p className="font-display text-3xl font-bold">Got something bugging you?</p>
        <p className="mt-2 text-white/70">It takes 30 seconds.</p>
        <Link href="/" className="mt-6 inline-block rounded-full bg-heat px-6 py-3 text-sm font-semibold text-white transition-transform hover:scale-105">
          Start a rant
        </Link>
      </section>
    </div>
  );
}