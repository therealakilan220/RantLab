"""Turn a transcript into problem + pattern + 3 fixes with Ollama (Akilan).

Supports English, Tanglish (Tamil + English), Hinglish, and campus code-mixing.
Flow: ask for JSON -> normalise labels -> validate with pydantic -> on failure retry once
with the error message -> otherwise raise llm_failed.
"""
import json
import re

import httpx
from pydantic import ValidationError

from . import config
from .errors import ApiError
from .models import LLMOutput

SYSTEM_PROMPT = """You turn a spoken complaint from a college campus into a short, practical action plan.
Complaints may be in Tamil, Tanglish, Hindi-English mix, or campus slang. The model should still output the same JSON fields, always in clear professional English so the card is easy to share.

Return ONLY one JSON object with exactly these keys:
{
  "problem": "one sentence naming the underlying problem",
  "pattern": "one sentence on the likely recurring cause or pattern",
  "affected": "one sentence on who else is probably affected",
  "fixes": [
    {"title": "short action, max 80 characters", "detail": "one or two sentences",
     "owner": "role or department", "cost": "free", "timeframe": "today"}
  ]
}
Rules:
- Give exactly 3 fixes, ordered from most feasible to least feasible.
- "cost" must be one of: free, cheap, budget.
- "timeframe" must be one of: today, this_week, this_semester.
- "owner" is a role or department such as "Hostel warden", "Canteen manager", or "IT / Network team". Never a person's name.
- Every fix must be specific to this complaint. No generic advice like "improve communication" or restricting student access.
- The first fix should be a free action that can start today (reset equipment, staff a desk, post a notice).
- Do not invent numbers or facts that were not in the complaint.
- Never include personal information."""

EXAMPLE_IN = "The canteen queue is insane at lunch, I wait 25 minutes and only two counters are open."
EXAMPLE_OUT = {
    "problem": "Canteen lunch queues are long because too few counters are open at peak time.",
    "pattern": "Demand peaks between classes while staffing stays the same all day.",
    "affected": "Every student and staff member who eats at the canteen between 12 and 2 pm.",
    "fixes": [
        {"title": "Open all counters from 12 to 2 pm", "detail": "Ask canteen staff to shift break times so every counter is staffed at the lunch peak.",
         "owner": "Canteen manager", "cost": "free", "timeframe": "today"},
        {"title": "Add a pre-order sheet for popular items", "detail": "Let students order before class using a shared form so food is ready on arrival.",
         "owner": "Canteen manager and student council", "cost": "cheap", "timeframe": "this_week"},
        {"title": "Add a second serving line", "detail": "Set up an extra line for quick items such as tea and snacks to split the queue.",
         "owner": "Administration", "cost": "budget", "timeframe": "this_semester"},
    ],
}

EXAMPLE_TAMIL_IN = "என்னுடைய பள்ளி நூலகத்தில் வைஃபை மிகவும் மெதுவாக இருக்கிறது, அசைன்மென்ட் சமர்ப்பிக்க ஒரு மணி நேரம் ஆகிறது."
EXAMPLE_TAMIL_OUT = {
    "problem": "School library Wi-Fi is too slow to submit assignments on time.",
    "pattern": "Network capacity stays the same while assignment deadlines drive a traffic spike.",
    "affected": "Students in the library who need the academic portal before a deadline.",
    "fixes": [
        {"title": "Reset and load-balance library access points", "detail": "Ask IT to reboot saturated routers and give academic sites priority during peak hours.",
         "owner": "IT / Network team", "cost": "free", "timeframe": "today"},
        {"title": "Map library Wi-Fi dead zones", "detail": "Walk the floors with a signal app and note rooms where uploads stall.",
         "owner": "IT / Network team", "cost": "cheap", "timeframe": "this_week"},
        {"title": "Upgrade library access points", "detail": "Install higher-capacity access points so the library can handle deadline traffic.",
         "owner": "Administration", "cost": "budget", "timeframe": "this_semester"},
    ],
}

EXAMPLE_TANGLISH_IN = "Library-la Wi-Fi semma slow-ah irukku, assignment submit panna 40 mins aagudhu."
EXAMPLE_TANGLISH_OUT = {
    "problem": "Library Wi-Fi connection is extremely slow during assignment submission deadlines.",
    "pattern": "Overloaded network bandwidth and congested access points during peak assignment hours.",
    "affected": "Students studying in the library trying to submit online assignments.",
    "fixes": [
        {"title": "Restart and balance library Wi-Fi routers", "detail": "Request IT staff to reset saturated access points and optimize bandwidth priority for academic portals.",
         "owner": "IT / Network team", "cost": "free", "timeframe": "today"},
        {"title": "Conduct Wi-Fi signal coverage audit", "detail": "Map out dead zones in the library block to identify where extra routers are needed.",
         "owner": "IT / Network team", "cost": "cheap", "timeframe": "this_week"},
        {"title": "Upgrade library access points", "detail": "Install high-capacity Wi-Fi 6 access points across all library floors.",
         "owner": "Administration", "cost": "budget", "timeframe": "this_semester"},
    ],
}


def _stub_fields(transcript: str) -> dict:
    t_lower = transcript.lower()
    
    if any(k in t_lower for k in ("lift", "elevator")):
        return {
            "problem": "Campus elevator is out of service, causing mobility bottlenecks for upper floors.",
            "pattern": "Mechanical wear and lack of scheduled preventive maintenance during peak building hours.",
            "affected": "Disabled students, staff, and students with classes on upper floors.",
            "fixes": [
                {
                    "title": "Post out-of-service notices and redirect traffic",
                    "detail": "Estate office to place clear 'Out of Service' signage and redirect foot traffic to the service lift or stairs.",
                    "owner": "Facilities desk",
                    "cost": "free",
                    "timeframe": "today",
                },
                {
                    "title": "Emergency elevator technician inspection",
                    "detail": "Schedule emergency elevator technician inspection to diagnose motor/cable failure.",
                    "owner": "Maintenance team",
                    "cost": "cheap",
                    "timeframe": "this_week",
                },
                {
                    "title": "Establish vendor AMC maintenance contract",
                    "detail": "Establish a recurring quarterly AMC contract with the elevator vendor to ensure reliable uptime.",
                    "owner": "Campus Administration",
                    "cost": "budget",
                    "timeframe": "this_semester",
                },
            ],
        }

    if any(k in t_lower for k in ("wifi", "wi-fi", "internet", "network", "வைஃபை")):
        return {
            "problem": "Campus Wi-Fi connectivity drops frequently during peak study hours.",
            "pattern": "Access point saturation and bandwidth congestion during high-demand periods.",
            "affected": "Students and researchers needing internet for coursework and assignment submissions.",
            "fixes": [
                {
                    "title": "Reboot and load-balance saturated routers",
                    "detail": "Restart high-load access points and prioritize academic traffic bandwidth during study hours.",
                    "owner": "IT / Network team",
                    "cost": "free",
                    "timeframe": "today",
                },
                {
                    "title": "Conduct Wi-Fi dead-zone audit",
                    "detail": "Map signal coverage across floors to identify areas requiring signal repeaters.",
                    "owner": "IT / Network team",
                    "cost": "cheap",
                    "timeframe": "this_week",
                },
                {
                    "title": "Deploy high-capacity enterprise access points",
                    "detail": "Install high-density Wi-Fi 6 access points in high-traffic study areas.",
                    "owner": "Administration",
                    "cost": "budget",
                    "timeframe": "this_semester",
                },
            ],
        }

    if any(k in t_lower for k in ("canteen", "food", "lunch", "cafeteria")):
        return {
            "problem": "Canteen lunch queues are excessively long due to insufficient billing counters.",
            "pattern": "High demand surge between lectures while staffing levels remain static.",
            "affected": "Students and faculty with short 30-40 minute lunch intervals.",
            "fixes": [
                {
                    "title": "Staff all billing counters during lunch hours",
                    "detail": "Shift staff break timings so all billing counters remain fully operational from 12 to 2 PM.",
                    "owner": "Canteen manager",
                    "cost": "free",
                    "timeframe": "today",
                },
                {
                    "title": "Introduce quick pre-order kiosk or token line",
                    "detail": "Set up a separate line for pre-packed meals and quick beverage pickups.",
                    "owner": "Canteen manager and student council",
                    "cost": "cheap",
                    "timeframe": "this_week",
                },
                {
                    "title": "Expand dining area and add automated POS terminals",
                    "detail": "Install self-checkout kiosks and add additional modular seating.",
                    "owner": "Administration",
                    "cost": "budget",
                    "timeframe": "this_semester",
                },
            ],
        }

    if any(k in t_lower for k in ("hostel", "water", "bathroom", "washroom", "heater")):
        return {
            "problem": "Hostel facilities suffer from inconsistent basic amenities during morning rush hours.",
            "pattern": "High simultaneous morning usage exceeding local supply line capacity.",
            "affected": "Hostel residents getting ready for early morning lectures.",
            "fixes": [
                {
                    "title": "Inspect valves and adjust booster pump schedule",
                    "detail": "Adjust maintenance pump timings to activate 30 minutes prior to peak morning usage.",
                    "owner": "Hostel warden",
                    "cost": "free",
                    "timeframe": "today",
                },
                {
                    "title": "Repair faulty fixtures and replace heating coils",
                    "detail": "Deploy plumbing crew to repair leaking valves and service hot water boilers.",
                    "owner": "Estate Maintenance",
                    "cost": "cheap",
                    "timeframe": "this_week",
                },
                {
                    "title": "Upgrade water storage and solar heater capacity",
                    "detail": "Install high-capacity auxiliary overhead tanks and solar heating backup.",
                    "owner": "Campus Administration",
                    "cost": "budget",
                    "timeframe": "this_semester",
                },
            ],
        }

    if any(k in t_lower for k in ("bus", "transport", "route")):
        return {
            "problem": "College bus service is frequently delayed, causing students to miss morning lectures.",
            "pattern": "Fixed route schedules do not account for morning traffic bottlenecks and lack live tracking.",
            "affected": "Day-scholar students and faculty commuting from outer campus routes.",
            "fixes": [
                {
                    "title": "Adjust morning departure times earlier by 15 minutes",
                    "detail": "Shift origin depot departure time earlier to create a traffic buffer for morning peak hours.",
                    "owner": "Transport officer",
                    "cost": "free",
                    "timeframe": "today",
                },
                {
                    "title": "Enable GPS live bus tracking for students",
                    "detail": "Activate driver smartphone GPS sharing so students can monitor real-time bus arrivals.",
                    "owner": "Transport coordinator",
                    "cost": "cheap",
                    "timeframe": "this_week",
                },
                {
                    "title": "Deploy additional bus on high-density routes",
                    "detail": "Contract an auxiliary bus for congested morning and evening lab return routes.",
                    "owner": "Campus Administration",
                    "cost": "budget",
                    "timeframe": "this_semester",
                },
            ],
        }

    if any(k in t_lower for k in ("library", "book", "reading room", "study")):
        return {
            "problem": "Library operating hours and seating capacity are insufficient during exam periods.",
            "pattern": "Study facility demand surges sharply during exam weeks while operating hours remain fixed.",
            "affected": "Students preparing for semester exams needing quiet study spaces in the evening.",
            "fixes": [
                {
                    "title": "Extend library reading room hours to 9 PM during exam weeks",
                    "detail": "Roster student volunteers or security staff to keep ground-floor reading halls open late.",
                    "owner": "Chief Librarian",
                    "cost": "free",
                    "timeframe": "today",
                },
                {
                    "title": "Convert vacant seminar rooms into temporary quiet study halls",
                    "detail": "Open unused department seminar halls after 5 PM for self-study.",
                    "owner": "Academic Dean",
                    "cost": "free",
                    "timeframe": "this_week",
                },
                {
                    "title": "Expand 24/7 digital reading room capacity",
                    "detail": "Equip additional hall with power outlets, LED study lamps, and ergonomic seating.",
                    "owner": "Campus Administration",
                    "cost": "budget",
                    "timeframe": "this_semester",
                },
            ],
        }

    # Clean default fallback for any other complaint
    first = transcript.strip().split(".")[0][:90] or "Campus facility issue"
    return {
        "problem": f"{first} needs immediate maintenance attention.",
        "pattern": "Recurring breakdown due to continuous usage without scheduled inspection.",
        "affected": "Students, faculty, and campus staff using this facility daily.",
        "fixes": [
            {
                "title": "Deploy immediate inspection and temporary signage",
                "detail": "Send on-duty maintenance staff to inspect the issue and place status notifications.",
                "owner": "Facilities desk",
                "cost": "free",
                "timeframe": "today",
            },
            {
                "title": "Conduct detailed root-cause diagnosis",
                "detail": "Evaluate repair requirements and procure necessary replacement parts.",
                "owner": "Maintenance team",
                "cost": "cheap",
                "timeframe": "this_week",
            },
            {
                "title": "Implement permanent preventive maintenance protocol",
                "detail": "Establish periodic inspection cycles to prevent similar recurring failures.",
                "owner": "Campus Administration",
                "cost": "budget",
                "timeframe": "this_semester",
            },
        ],
    }


def _norm(value) -> str:
    cleaned = str(value).strip().lower().replace(" ", "_").replace("-", "_")
    # Cost aliases
    if cleaned in ("free", "no_cost", "free_of_cost", "zero", "0"):
        return "free"
    if cleaned in ("cheap", "low_cost", "minor", "small_cost"):
        return "cheap"
    if cleaned in ("budget", "high_cost", "capital", "expensive"):
        return "budget"
    # Timeframe aliases
    if cleaned in ("today", "immediately", "1_day", "now", "24h"):
        return "today"
    if cleaned in ("this_week", "thisweek", "weekly", "few_days", "7_days"):
        return "this_week"
    if cleaned in ("this_semester", "thissemester", "long_term", "semester", "months"):
        return "this_semester"
    return cleaned


def _extract_json(raw: str) -> dict:
    """Extract and parse JSON from raw text, removing markdown codeblocks or extra prose."""
    text = raw.strip()
    # Strip markdown fences if present
    match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", text, re.IGNORECASE)
    if match:
        text = match.group(1).strip()
    
    # If not surrounded by fences, search for the outermost JSON object braces
    if not (text.startswith("{") and text.endswith("}")):
        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end != -1 and end > start:
            text = text[start : end + 1]

    return json.loads(text)


def _clean(data: dict) -> dict:
    fixes = data.get("fixes")
    if isinstance(fixes, list):
        for fix in fixes:
            if isinstance(fix, dict):
                fix["cost"] = _norm(fix.get("cost", ""))
                fix["timeframe"] = _norm(fix.get("timeframe", ""))
        data["fixes"] = fixes[:3]
    return data


def _call_ollama(messages: list[dict]) -> str:
    resp = httpx.post(
        f"{config.OLLAMA_URL}/api/chat",
        json={"model": config.OLLAMA_MODEL, "messages": messages, "format": "json",
              "stream": False, "options": {"temperature": 0.3}},
        timeout=180,
    )
    resp.raise_for_status()
    return resp.json()["message"]["content"]


def _call_cloud(messages: list[dict]) -> str:
    headers = {"Authorization": f"Bearer {config.CLOUD_API_KEY}"} if config.CLOUD_API_KEY else {}
    resp = httpx.post(
        f"{config.CLOUD_API_URL}/chat/completions",
        headers=headers,
        json={
            "model": config.CLOUD_API_MODEL,
            "messages": messages,
            "temperature": 0.3,
            "response_format": {"type": "json_object"},
        },
        timeout=180,
    )
    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]["content"]


def _call_model(messages: list[dict]) -> str:
    return _call_cloud(messages) if config.USE_CLOUD_API else _call_ollama(messages)


def is_up() -> bool:
    if config.STUB_MODE:
        return True
    if config.USE_CLOUD_API:
        return bool(config.CLOUD_API_URL and config.CLOUD_API_KEY)
    try:
        return httpx.get(f"{config.OLLAMA_URL}/api/tags", timeout=2).status_code == 200
    except httpx.HTTPError:
        return False


def generate_card_fields(transcript: str) -> dict:
    """Return problem, pattern, affected, fixes[3]. Supports English, Tamil, Tanglish and Hinglish."""
    if config.STUB_MODE:
        return _stub_fields(transcript)

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": EXAMPLE_IN},
        {"role": "assistant", "content": json.dumps(EXAMPLE_OUT)},
        {"role": "user", "content": EXAMPLE_TAMIL_IN},
        {"role": "assistant", "content": json.dumps(EXAMPLE_TAMIL_OUT)},
        {"role": "user", "content": EXAMPLE_TANGLISH_IN},
        {"role": "assistant", "content": json.dumps(EXAMPLE_TANGLISH_OUT)},
        {"role": "user", "content": transcript},
    ]
    hint = "Set USE_CLOUD_API=1 with a key, or start Ollama and try again." if config.USE_CLOUD_API else "Start Ollama and try again."
    for _attempt in range(2):
        try:
            raw = _call_model(messages)
        except (httpx.ConnectError, httpx.TimeoutException, httpx.HTTPStatusError) as exc:
            raise ApiError(503, "model_unavailable",
                           f"The AI model isn't running. {hint}") from exc
        try:
            parsed = _extract_json(raw)
            return LLMOutput.model_validate(_clean(parsed)).model_dump()
        except (ValidationError, ValueError, AttributeError) as exc:
            messages += [
                {"role": "assistant", "content": raw},
                {"role": "user", "content": f"That JSON was invalid: {exc}. Return only the corrected JSON object with keys problem, pattern, affected, and fixes (exactly 3 items)."},
            ]
    raise ApiError(502, "llm_failed", "We couldn't turn that into an action plan. Please try again.")
