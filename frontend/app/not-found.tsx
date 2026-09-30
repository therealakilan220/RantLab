import Link from "next/link";

export default function NotFound() {
  return (
    <div className="py-16 text-center">
      <p className="font-display text-8xl font-extrabold tracking-tight text-heat">404</p>
      <h1 className="mt-4 font-display text-3xl font-bold text-ink">This page doesn&apos;t exist</h1>
      <p className="mt-2 text-ink-soft">The link may be broken, or the page has moved.</p>
      <Link href="/" className="mt-8 inline-block rounded-full bg-brand px-6 py-3 text-sm font-semibold text-white">
        Go to the home page
      </Link>
    </div>
  );
}