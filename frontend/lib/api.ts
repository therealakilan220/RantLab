import type { ApiError, Card, Cluster } from "./types";
import { getSampleCard } from "./samples";

export interface Board {
  generated_at: string;
  clusters: Cluster[];
}

export interface Health {
  status: string;
  stub_mode: boolean;
  ollama: boolean;
  whisper: boolean;
}

export class ApiRequestError extends Error {
  code: string;
  constructor(code: string, message: string) {
    super(message);
    this.code = code;
  }
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  let res: Response;
  try {
    res = await fetch(path, init);
  } catch {
    throw new ApiRequestError("network", "Can't reach the RantLab server. Is the backend running?");
  }
  if (res.ok) return (await res.json()) as T;

  let body: Partial<ApiError> | null = null;
  try {
    body = await res.json();
  } catch {
    body = null;
  }
  throw new ApiRequestError(
    body?.error?.code ?? `http_${res.status}`,
    body?.error?.message ?? "Something went wrong. Please try again."
  );
}

export function submitText(text: string): Promise<Card> {
  return request<Card>("/api/rant", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ text }),
  });
}

export function submitAudio(audio: Blob, filename: string): Promise<Card> {
  const form = new FormData();
  form.append("audio", audio, filename);
  return request<Card>("/api/rant", { method: "POST", body: form });
}

export function getCard(id: string): Promise<Card> {
  const sample = getSampleCard(id);
  if (sample) return Promise.resolve(sample);
  return request<Card>(`/api/cards/${encodeURIComponent(id)}`, { cache: "no-store" });
}

export function getBoard(): Promise<Board> {
  return request<Board>("/api/board", { cache: "no-store" });
}

export function getHealth(): Promise<Health> {
  return request<Health>("/api/health", { cache: "no-store" });
}