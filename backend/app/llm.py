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
    first = transcript.strip().split(".")[0][:90] or "Stub problem"
    return {
        "problem": first,
        "pattern": "Stub mode: this is a canned pattern. Set STUB_MODE=0 for real output.",
        "affected": "Stub mode: other students who use the same place.",
        "fixes": [
            {"title": "Post a fault-reporting QR code", "detail": "Link it to a simple form so staff see when and where it happens.",
             "owner": "Facilities desk", "cost": "free", "timeframe": "today"},
            {"title": "Survey the affected area", "detail": "Check when the problem is worst and how many people it hits.",
             "owner": "Facilities team", "cost": "cheap", "timeframe": "this_week"},
            {"title": "Fund a permanent fix", "detail": "Use the survey data to justify a small budget request.",
             "owner": "Administration", "cost": "budget", "timeframe": "this_semester"},
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
