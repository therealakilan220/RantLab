export type Cost = "free" | "cheap" | "budget";
export type Timeframe = "today" | "this_week" | "this_semester";

export interface Fix { title: string; detail: string; owner: string; cost: Cost; timeframe: Timeframe; }

export interface Card {
  id: string; created_at: string; input_type: "voice" | "text";
  transcript: string; problem: string; pattern: string; affected: string;
  fixes: [Fix, Fix, Fix]; cluster_id: string | null;
}

export interface Cluster {
  id: string; label: string; count: number; latest_at: string;
  complaints: { card_id: string; transcript: string }[];
}

export interface ApiError { error: { code: string; message: string } }