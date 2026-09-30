import type { Card } from "./types";

export const SAMPLE_CARDS: Card[] = [
  {
    id: "sample-hostel-water",
    created_at: "2026-09-30T07:40:00Z",
    input_type: "voice",
    transcript: "Every morning in hostel block C there's no hot water after 7 am. Around fifty of us have 8 am classes, so everyone fights over the two geysers that still work, and half of us end up taking cold showers or getting late.",
    problem: "Hot water runs out in the hostel block every morning after 7 am.",
    pattern: "Too few working geysers for the rush before 8 am classes.",
    affected: "Hostel residents with early classes.",
    fixes: [
      { title: "Publish a staggered morning bathroom schedule", detail: "Split floors into 15-minute slots so the working geysers aren't overloaded.", owner: "Hostel warden", cost: "free", timeframe: "today" },
      { title: "Repair the broken geysers in the block", detail: "Log a maintenance ticket and get the faulty units inspected and fixed.", owner: "Hostel maintenance team", cost: "cheap", timeframe: "this_week" },
      { title: "Install a solar or central hot-water system", detail: "A shared tank sized for the block removes the morning bottleneck.", owner: "Estate / Facilities office", cost: "budget", timeframe: "this_semester" },
    ],
    cluster_id: null,
  },
  {
    id: "sample-college-bus",
    created_at: "2026-09-29T09:10:00Z",
    input_type: "text",
    transcript: "The college bus from Tambaram is late almost every day by 20 minutes, so our first-hour attendance gets marked absent and there's no way to track where the bus is.",
    problem: "The college bus arrives about 20 minutes late most days.",
    pattern: "Route timing doesn't match current traffic, and there's no live tracking.",
    affected: "Day scholars on that route who lose first-hour attendance.",
    fixes: [
      { title: "Excuse first-hour attendance for delayed buses", detail: "The transport office shares a daily delay list with faculty.", owner: "Transport office and class coordinators", cost: "free", timeframe: "today" },
      { title: "Start the route 20 minutes earlier", detail: "Re-time pickups using this month's actual arrival times.", owner: "Transport office", cost: "free", timeframe: "this_week" },
      { title: "Add live GPS tracking for college buses", detail: "Share bus locations so students aren't left waiting at the stop.", owner: "Transport office and IT team", cost: "budget", timeframe: "this_semester" },
    ],
    cluster_id: null,
  },
  {
    id: "sample-computer-lab",
    created_at: "2026-09-28T14:25:00Z",
    input_type: "voice",
    transcript: "Half the computers in the second floor lab don't boot and the keyboards are broken, so three of us share one PC during lab exams.",
    problem: "Many systems in the computer lab don't work.",
    pattern: "Hardware faults aren't reported or repaired between lab sessions.",
    affected: "Students with lab sessions and lab exams in that room.",
    fixes: [
      { title: "Tag and log every broken system", detail: "Put an out-of-order label on each faulty PC and record the fault in one sheet.", owner: "Lab assistant", cost: "free", timeframe: "today" },
      { title: "Replace broken keyboards and mice", detail: "Spare peripherals are cheap and fix most of the unusable seats.", owner: "Lab in-charge", cost: "cheap", timeframe: "this_week" },
      { title: "Run a full hardware audit before lab exams", detail: "Service or replace failing machines so every student has a working system.", owner: "Department and IT support", cost: "budget", timeframe: "this_semester" },
    ],
    cluster_id: null,
  },
];

export function isSampleId(id: string): boolean {
  return id.startsWith("sample-");
}

export function getSampleCard(id: string): Card | null {
  return SAMPLE_CARDS.find((c) => c.id === id) ?? null;
}