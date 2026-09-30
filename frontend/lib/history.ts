import { useMemo, useSyncExternalStore } from "react";
import type { Card } from "./types";

const KEY = "rantlab-history";
const EVENT = "rantlab-history-change";
const MAX_ITEMS = 5;

export interface HistoryItem {
  id: string;
  problem: string;
  created_at: string;
}

function read(): string | null {
  try {
    return window.localStorage.getItem(KEY);
  } catch {
    return null;
  }
}

function parse(raw: string | null): HistoryItem[] {
  if (!raw) return [];
  try {
    const value = JSON.parse(raw);
    return Array.isArray(value) ? (value as HistoryItem[]) : [];
  } catch {
    return [];
  }
}

function subscribe(onChange: () => void) {
  window.addEventListener("storage", onChange);
  window.addEventListener(EVENT, onChange);
  return () => {
    window.removeEventListener("storage", onChange);
    window.removeEventListener(EVENT, onChange);
  };
}

export function useHistory(): HistoryItem[] {
  const raw = useSyncExternalStore(subscribe, read, () => null);
  return useMemo(() => parse(raw), [raw]);
}

export function addToHistory(card: Card) {
  const item = { id: card.id, problem: card.problem, created_at: card.created_at };
  const next = [item, ...parse(read()).filter((h) => h.id !== card.id)].slice(0, MAX_ITEMS);
  try {
    window.localStorage.setItem(KEY, JSON.stringify(next));
    window.dispatchEvent(new Event(EVENT));
  } catch {
    /* storage unavailable, e.g. private mode */
  }
}

export function clearHistory() {
  try {
    window.localStorage.removeItem(KEY);
    window.dispatchEvent(new Event(EVENT));
  } catch {
    /* storage unavailable */
  }
}