import type { Cost, Timeframe } from "./types";

export const COST_LABEL: Record<Cost, string> = {
  free: "Free",
  cheap: "Low cost",
  budget: "Needs budget",
};

export const COST_STYLE: Record<Cost, string> = {
  free: "bg-plan-soft text-plan",
  cheap: "bg-warn-soft text-warn",
  budget: "bg-heat-soft text-heat",
};

export const TIMEFRAME_LABEL: Record<Timeframe, string> = {
  today: "Today",
  this_week: "This week",
  this_semester: "This semester",
};

export function timeAgo(iso: string): string {
  const diff = (Date.now() - new Date(iso).getTime()) / 1000;
  if (!Number.isFinite(diff)) return "";
  if (diff < 60) return "just now";
  if (diff < 3600) return `${Math.floor(diff / 60)} min ago`;
  if (diff < 86400) return `${Math.floor(diff / 3600)} h ago`;
  return new Date(iso).toLocaleDateString(undefined, { day: "numeric", month: "short" });
}

export function formatDate(iso: string): string {
  const d = new Date(iso);
  if (Number.isNaN(d.getTime())) return "";
  return d.toLocaleDateString(undefined, { day: "numeric", month: "short", year: "numeric" });
}