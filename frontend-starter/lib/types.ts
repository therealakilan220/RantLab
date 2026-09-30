// Must match docs/api-contract.md and backend/app/models.py. Change the contract first.

export type Cost = "free" | "cheap" | "budget";
export type Timeframe = "today" | "this_week" | "this_semester";

export interface Fix {
  title: string;
  detail: string;
  owner: string;
  cost: Cost;
  timeframe: Timeframe;
}

export interface Card {
  id: string;
  created_at: string;
  input_type: "voice" | "text";
  transcript: string;
  problem: string;
  pattern: string;
  affected: string;
  fixes: [Fix, Fix, Fix];
  cluster_id: string | null;
}

export interface Cluster {
  id: string;
  label: string;
  count: number;
  latest_at: string;
  complaints: { card_id: string; transcript: string }[];
}

export interface BoardResponse {
  generated_at: string;
  clusters: Cluster[];
}

export interface ApiError {
  error: { code: string; message: string };
}

export const TIMEFRAME_LABEL: Record<Timeframe, string> = {
  today: "Today",
  this_week: "This week",
  this_semester: "This semester",
};

export const COST_LABEL: Record<Cost, string> = {
  free: "Free",
  cheap: "Cheap",
  budget: "Budget",
};
