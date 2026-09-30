import type { Metadata, Viewport } from "next";
import { Bricolage_Grotesque, Instrument_Sans } from "next/font/google";
import Header from "@/components/Header";
import StatusPill from "@/components/StatusPill";
import { ToastProvider } from "@/components/Toast";
import "./globals.css";

const heading = Bricolage_Grotesque({ subsets: ["latin"], variable: "--font-heading", display: "swap" });
const body = Instrument_Sans({ subsets: ["latin"], variable: "--font-body", display: "swap" });

export const metadata: Metadata = {
  title: { default: "RantLab: turn complaints into action plans", template: "%s | RantLab" },
  description: "Rant for 30 seconds about a campus problem. RantLab finds the real issue and drafts three fixes with owners, costs and timeframes.",
  openGraph: {
    title: "RantLab",
    description: "Don't just complain about the problem. Turn it into a plan.",
    type: "website",
  },
};

export const viewport: Viewport = {
  themeColor: [
    { media: "(prefers-color-scheme: light)", color: "#f6f8fb" },
    { media: "(prefers-color-scheme: dark)", color: "#0b111e" },
  ],
};

const THEME_SCRIPT = `(function(){try{var t=localStorage.getItem('rantlab-theme');if(t!=='light'&&t!=='dark'){t=window.matchMedia('(prefers-color-scheme: dark)').matches?'dark':'light'}document.documentElement.dataset.theme=t}catch(e){}})();`;

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en" className={`${heading.variable} ${body.variable}`} suppressHydrationWarning>
      <head>
        <script dangerouslySetInnerHTML={{ __html: THEME_SCRIPT }} />
      </head>
      <body className="min-h-screen font-sans antialiased">
        <ToastProvider>
          <Header />
          <main className="mx-auto max-w-3xl px-5 pb-16 pt-6 sm:pt-10">{children}</main>
          <footer className="mx-auto flex max-w-5xl flex-col items-start justify-between gap-3 border-t border-line px-5 py-8 text-sm text-ink-soft sm:flex-row sm:items-center">
            <span>RantLab, built by Team Fantastic 4. No paid APIs.</span>
            <StatusPill />
          </footer>
        </ToastProvider>
      </body>
    </html>
  );
}