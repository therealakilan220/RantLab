export default function Logo({ className = "h-9 w-9", onDark = false }: { className?: string; onDark?: boolean }) {
  return (
    <svg viewBox="0 0 32 32" className={className} aria-hidden="true">
      <rect width="32" height="32" rx="9" className={onDark ? "fill-white/15" : "fill-brand"} />
      <path
        d="M9 9.5h14a2.5 2.5 0 0 1 2.5 2.5v7a2.5 2.5 0 0 1-2.5 2.5h-7l-4.5 3.8V21.5H9A2.5 2.5 0 0 1 6.5 19v-7A2.5 2.5 0 0 1 9 9.5z"
        className="fill-heat"
      />
      <path d="M12.3 15.6l2.6 2.6 4.8-5.2" stroke="#fff" strokeWidth="2.2" fill="none" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  );
}