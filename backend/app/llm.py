"""Turn a transcript into problem + pattern + 3 fixes with Ollama (Akilan).

Flow: ask for JSON -> normalise labels -> validate with pydantic -> on failure retry once
with the error message -> otherwise raise llm_failed.
"""
import json

import httpx
from pydantic import ValidationError

from . import config
from .errors import ApiError
from .models import LLMOutput

SYSTEM_PROMPT = """You turn a spoken complaint from a college campus into a short, practical action plan.
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
- "owner" is a role or department such as "Hostel warden" or "IT / Network team". Never a person's name.
- Every fix must be specific to this complaint. No generic advice like "improve communication".
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
             "owner": "Facilities team", "cost": "free", "timeframe": "this_week"},
            {"title": "Fund a permanent fix", "detail": "Use the survey data to justify a small budget request.",
             "owner": "Administration", "cost": "budget", "timeframe": "this_semester"},
        ],
    }


def _norm(value) -> str:
    return str(value).strip().lower().replace(" ", "_").replace("-", "_")


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


def is_up() -> bool:
    if config.STUB_MODE:
        return True
    try:
        return httpx.get(f"{config.OLLAMA_URL}/api/tags", timeout=2).status_code == 200
    except httpx.HTTPError:
        return False


def generate_card_fields(transcript: str) -> dict:
    """Return problem, pattern, affected, fixes[3]."""
    if config.STUB_MODE:
        return _stub_fields(transcript)

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": EXAMPLE_IN},
        {"role": "assistant", "content": json.dumps(EXAMPLE_OUT)},
        {"role": "user", "content": transcript},
    ]
    for _attempt in range(2):
        try:
            raw = _call_ollama(messages)
        except (httpx.ConnectError, httpx.TimeoutException) as exc:
            raise ApiError(503, "model_unavailable",
                           "The AI model isn't running. Start Ollama and try again.") from exc
        try:
            return LLMOutput.model_validate(_clean(json.loads(raw))).model_dump()
        except (ValidationError, ValueError, AttributeError) as exc:
            messages += [
                {"role": "assistant", "content": raw},
                {"role": "user", "content": f"That JSON was invalid: {exc}. Return only the corrected JSON object."},
            ]
    raise ApiError(502, "llm_failed", "We couldn't turn that into an action plan. Please try again.")
