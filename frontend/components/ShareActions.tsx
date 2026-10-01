"use client";

import Link from "next/link";
import { useEffect, useState, type RefObject } from "react";
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

const STORAGE_KEY = "rantlab_public_url";

export default function ShareActions({ targetRef, cardId, problem }: Props) {
  const toast = useToast();
  const [saving, setSaving] = useState(false);
  const [qr, setQr] = useState<string | null>(null);
  const [qrOpen, setQrOpen] = useState(false);
  const [customOrigin, setCustomOrigin] = useState<string>("");
  const [inputUrl, setInputUrl] = useState<string>("");
  const [showConfig, setShowConfig] = useState(false);
  const [isLocalhost, setIsLocalhost] = useState(false);

  useEffect(() => {
    if (typeof window === "undefined") return;
    const isLocal = window.location.hostname === "localhost" || window.location.hostname === "127.0.0.1";
    setIsLocalhost(isLocal);

    const saved = localStorage.getItem(STORAGE_KEY) || process.env.NEXT_PUBLIC_APP_URL || "";
    if (saved) {
      setCustomOrigin(saved);
      setInputUrl(saved);
    } else if (isLocal) {
      setShowConfig(true);
    }
  }, []);

  const getEffectiveUrl = (): string => {
    if (customOrigin) {
      return `${customOrigin.replace(/\/+$/, "")}/card/${encodeURIComponent(cardId)}`;
    }
    const customBase = process.env.NEXT_PUBLIC_APP_URL?.replace(/\/+$/, "");
    if (customBase) {
      return `${customBase}/card/${encodeURIComponent(cardId)}`;
    }
    if (typeof window !== "undefined") {
      return `${window.location.origin}/card/${encodeURIComponent(cardId)}`;
    }
    return `/card/${cardId}`;
  };

  const effectiveUrl = getEffectiveUrl();

  useEffect(() => {
    if (!qrOpen) return;
    toDataURL(effectiveUrl, {
      margin: 1,
      width: 360,
      color: { dark: "#16213e", light: "#ffffff" },
    })
      .then((data) => setQr(data))
      .catch(() => toast("Couldn't create the QR code.", "error"));
  }, [qrOpen, effectiveUrl, toast]);

  function saveCustomUrl() {
    let clean = inputUrl.trim();
    if (!clean) {
      localStorage.removeItem(STORAGE_KEY);
      setCustomOrigin("");
      toast("Reset to default address");
      return;
    }
    if (!clean.startsWith("http://") && !clean.startsWith("https://")) {
      clean = `https://${clean}`;
    }
    clean = clean.replace(/\/+$/, "");
    try {
      new URL(clean);
      localStorage.setItem(STORAGE_KEY, clean);
      setCustomOrigin(clean);
      setInputUrl(clean);
      toast("Public share URL saved!");
    } catch {
      toast("Please enter a valid URL (e.g. https://xyz.trycloudflare.com)", "error");
    }
  }

  function resetUrl() {
    localStorage.removeItem(STORAGE_KEY);
    setCustomOrigin("");
    setInputUrl("");
    toast("Reset to current origin");
  }

  async function share() {
    const url = effectiveUrl;
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
      await navigator.clipboard.writeText(effectiveUrl);
      toast(customOrigin ? "Public link copied" : "Link copied");
    } catch {
      toast("Couldn't copy link to clipboard.", "error");
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

  function toggleQr() {
    setQrOpen((prev) => !prev);
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

      {qrOpen && (
        <div className="rise space-y-4 rounded-[24px] border border-line bg-surface p-6">
          <div className="flex flex-col items-center gap-5 text-center sm:flex-row sm:text-left">
            {qr ? (
              // eslint-disable-next-line @next/next/no-img-element
              <img src={qr} alt="QR code that opens this plan" className="h-44 w-44 shrink-0 rounded-xl bg-white p-2 shadow-sm" />
            ) : (
              <div className="flex h-44 w-44 shrink-0 items-center justify-center rounded-xl bg-mist text-xs text-ink-soft">
                Generating QR...
              </div>
            )}
            <div className="min-w-0 flex-1">
              <p className="font-display text-xl font-bold text-ink">Scan to open on a phone</p>
              <p className="mt-1 text-sm leading-relaxed text-ink-soft">
                Point any phone camera at the code to open this plan and forward it to whoever can fix the problem.
              </p>
              <p className="mt-2.5 truncate rounded-lg bg-mist/70 px-3 py-1.5 font-mono text-xs text-ink-soft">
                {effectiveUrl}
              </p>
            </div>
          </div>

          {/* Localhost / Public URL configuration helper */}
          <div className="border-t border-line pt-4">
            <div className="flex items-center justify-between gap-2">
              <span className="text-xs font-semibold uppercase tracking-wider text-ink-soft">
                {isLocalhost && !customOrigin ? "⚠️ Localhost Notice & Public Tunnel" : "Public Share Address"}
              </span>
              <button
                type="button"
                onClick={() => setShowConfig((prev) => !prev)}
                className="text-xs font-medium text-brand hover:underline"
              >
                {showConfig ? "Hide settings" : "Configure public/tunnel URL"}
              </button>
            </div>

            {showConfig && (
              <div className="mt-3 rounded-xl bg-mist/60 p-4 text-xs">
                {isLocalhost && !customOrigin && (
                  <p className="mb-2 text-heat font-medium">
                    Other devices (like mobile phones) cannot open &ldquo;localhost&rdquo; links.
                    Run a tunnel (e.g. <code className="rounded bg-surface px-1 py-0.5 text-ink">cloudflared tunnel --url http://localhost:3000</code> or ngrok) or use your LAN IP, and paste the URL below:
                  </p>
                )}
                <div className="flex flex-col gap-2 sm:flex-row sm:items-center">
                  <input
                    type="text"
                    value={inputUrl}
                    onChange={(e) => setInputUrl(e.target.value)}
                    placeholder="https://your-tunnel.trycloudflare.com or http://192.168.1.X:3000"
                    className="flex-1 rounded-lg border border-line bg-surface px-3 py-2 text-xs font-mono text-ink outline-none focus:border-ink"
                  />
                  <div className="flex gap-2">
                    <button
                      type="button"
                      onClick={saveCustomUrl}
                      className="rounded-lg bg-brand px-3 py-2 font-semibold text-white transition-colors hover:bg-brand/90"
                    >
                      Apply
                    </button>
                    {customOrigin && (
                      <button
                        type="button"
                        onClick={resetUrl}
                        className="rounded-lg border border-line bg-surface px-3 py-2 font-medium text-ink hover:border-ink"
                      >
                        Reset
                      </button>
                    )}
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}