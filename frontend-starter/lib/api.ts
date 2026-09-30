import boardMock from "@/mocks/board.json";
import cardMock from "@/mocks/card.json";
import type { ApiError, BoardResponse, Card } from "./types";

// Set NEXT_PUBLIC_USE_MOCK=1 in .env.local to build the UI without the backend.
const USE_MOCK = process.env.NEXT_PUBLIC_USE_MOCK === "1";
const wait = (ms: number) => new Promise((r) => setTimeout(r, ms));

async function handle<T>(res: Response): Promise<T> {
  if (!res.ok) {
    let message = "Something went wrong. Please try again.";
    try {
      const body = (await res.json()) as ApiError;
      message = body.error.message;
    } catch {
      /* keep the default message */
    }
    throw new Error(message);
  }
  return res.json() as Promise<T>;
}

export async function submitText(text: string): Promise<Card> {
  if (USE_MOCK) {
    await wait(1200);
    return cardMock as Card;
  }
  const res = await fetch("/api/rant", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ text }),
  });
  return handle<Card>(res);
}

export async function submitAudio(blob: Blob): Promise<Card> {
  if (USE_MOCK) {
    await wait(1200);
    return cardMock as Card;
  }
  const form = new FormData();
  form.append("audio", blob, "rant.webm");
  const res = await fetch("/api/rant", { method: "POST", body: form });
  return handle<Card>(res);
}

export async function getCard(id: string): Promise<Card> {
  if (USE_MOCK) return cardMock as Card;
  return handle<Card>(await fetch(`/api/cards/${encodeURIComponent(id)}`));
}

export async function getBoard(): Promise<BoardResponse> {
  if (USE_MOCK) return boardMock as BoardResponse;
  return handle<BoardResponse>(await fetch("/api/board"));
}
