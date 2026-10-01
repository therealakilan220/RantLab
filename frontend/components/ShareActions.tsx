"use client";

import Link from "next/link";
import { useState, type RefObject } from "react";
import { toPng } from "html-to-image";
import { toDataURL } from "qrcode";
import { useToast } from "./Toast";

type Props = {
  targetRef: RefObject<HTMLDivElement | null>;
  cardId: string;
  problem: string;
};

const iconProps = {
  viewBox: "0 0 24 24",
  className: "h-4 w-4",
  fill: "none",
  stroke: "currentColor",
  strokeWidth: 2.2,
  strokeLinecap: "round" as const,
  strokeLinejoin: "round" as const,
  "aria-hidden": true,
};

export default function ShareActions({ targetRef, cardId, problem }: Props) {
  const toast = useToast();
  const [saving, setSaving] = useState(false);
  const [qr, setQr] = useState<string | null>(null);
  const [qrOpen, setQrOpen] = useState(false);

  function getShareUrl(): string {
    const customBase = process.env.NEXT_PUBLIC_APP_URL?.replace(/\/$/, "");
    if (customBase) {
      return `${customBase}/card/${cardId}`;
    }
    if (typeof window !== "undefined") {
      return window.location.href;
    }
    return `/card/${cardId}`;
  }

  async function share() {
    const url = getShareUrl();
    const text = `${problem} Here's a plan to fix it:`;
    if (typeof navigator.share === "function") {
      try {
        await navigator.share({ title: "RantLab action plan", text, url });
      } catch {
        /* user closed the share sheet */
      }
      return;
    }
    window.open(`https://wa.me/?text=${encodeURIComponent(`${text} ${url}`)}`, "_blank", "noopener");
  }

  async function copyLink() {
    try {
      await navigator.clipboard.writeText(getShareUrl());
      toast("Link copied");
    } catch {
      toast("Couldn't copy. Select the address bar and copy it instead.", "error");
    }
  }

  async function downloadPng() {
    if (!targetRef.current) return;
    setSaving(true);
    try {
      const background = getComputedStyle(document.body).backgroundColor;
      const dataUrl = await toPng(targetRef.current, { pixelRatio: 2, backgroundColor: background, cacheBust: true });
      const a = document.createElement("a");
      a.href = dataUrl;
      a.download = `rantlab-${cardId}.png`;
      a.click();
      toast("Image downloaded");
    } catch {
      toast("Couldn't create the image. Take a screenshot instead.", "error");
    } finally {
      setSaving(false);
    }
  }

  async function toggleQr() {
    if (qrOpen) {
      setQrOpen(false);
      return;
    }
    if (!qr) {
      try {
        const url = getShareUrl();
        setQr(await toDataURL(url, { margin: 1, width: 360, color: { dark: "#16213e", light: "#ffffff" } }));
      } catch {
        toast("Couldn't create the QR code.", "error");
        return;
      }
    }
    setQrOpen(true);
  }

  const secondary =
    "inline-flex items-center justify-center gap-2 rounded-full border border-line bg-surface px-5 py-3 text-sm font-semibold text-ink transition-colors hover:border-ink disabled:opacity-60";

  return (
    <div className="space-y-4">
      <div className="flex flex-col gap-3 sm:flex-row sm:flex-wrap sm:items-center">
        <button
          onClick={share}
          className="inline-flex items-center justify-center gap-2 rounded-full bg-brand px-6 py-3 text-sm font-semibold text-white transition-colors hover:bg-brand/90"
        >
          <svg {...iconProps}>
            <circle cx="18" cy="5" r="3" />
            <circle cx="6" cy="12" r="3" />
            <circle cx="18" cy="19" r="3" />
            <path d="M8.6 13.5l6.8 4M15.4 6.5l-6.8 4" />
          </svg>
          Share
        </button>
        <button onClick={copyLink} className={secondary}>
          <svg {...iconProps}>
            <path d="M10 13a5 5 0 0 0 7.5.5l3-3a5 5 0 0 0-7-7l-1.7 1.7" />
            <path d="M14 11a5 5 0 0 0-7.5-.5l-3 3a5 5 0 0 0 7 7l1.7-1.7" />
          </svg>
          Copy link
        </button>
        <button onClick={downloadPng} disabled={saving} className={secondary}>
          <svg {...iconProps}>
            <path d="M12 4v11" />
            <path d="M7 10l5 5 5-5" />
            <path d="M5 20h14" />
          </svg>
          {saving ? "Saving image" : "Download image"}
        </button>
        <button onClick={toggleQr} aria-expanded={qrOpen} className={secondary}>
          <svg {...iconProps}>
            <rect x="3" y="3" width="7" height="7" rx="1" />
            <rect x="14" y="3" width="7" height="7" rx="1" />
            <rect x="3" y="14" width="7" height="7" rx="1" />
            <path d="M14 14h3v3h-3zM20 14v.01M14 20h.01M17 17h3v3" />
          </svg>
          {qrOpen ? "Hide QR code" : "QR code"}
        </button>
        <Link href="/" className="px-2 py-3 text-center text-sm font-semibold text-ink-soft transition-colors hover:text-ink sm:ml-auto">
          Start another rant
        </Link>
      </div>

      {qrOpen && qr && (
        <div className="rise flex flex-col items-center gap-5 rounded-[24px] border border-line bg-surface p-6 text-center sm:flex-row sm:text-left">
          {/* eslint-disable-next-line @next/next/no-img-element */}
          <img src={qr} alt="QR code that opens this plan" className="h-40 w-40 shrink-0 rounded-xl bg-white p-2 shadow-sm" />
          <div className="flex-1 overflow-hidden">
            <p className="font-display text-xl font-bold text-ink">Scan to open on a phone</p>
            <p className="mt-1 text-sm leading-relaxed text-ink-soft">
              Point any phone camera at the code to open this plan and forward it to whoever can fix the problem.
            </p>
            <div className="mt-3 flex items-center gap-2 rounded-xl border border-line bg-mist px-3 py-2 text-xs text-ink-soft">
              <span className="truncate font-mono">{getShareUrl()}</span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}