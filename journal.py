"""Journal analysis with the Claude API, plus a local safety net."""
import json
import re

import anthropic
import streamlit as st

# Fast and cheap for a live demo. Switch to "claude-sonnet-5-5" for higher quality.
MODEL = "claude-haiku-5-5"

SYSTEM = """You analyze a short student journal entry for signs of academic burnout.
You are not a clinician and must not diagnose.
Respond with ONLY a JSON object, no other text:
{"burnout_language_score": <number 0-10>,
 "themes": [<up to 4 short strings, e.g. "exhaustion", "loss of motivation">],
 "protective_factors": [<up to 3 short strings, e.g. "supportive friends">],
 "crisis_flag": <true if the text mentions self-harm, suicide, or feeling unsafe, else false>,
 "summary": "<one neutral sentence>"}"""

# Local backup check, so a crisis is caught even if the API call fails.
CRISIS_WORDS = [
    "kill myself", "suicide", "suicidal", "end my life", "end it all",
    "self harm", "self-harm", "hurt myself", "want to die", "don't want to live",
    "dont want to live", "not safe",
]


def keyword_crisis(text: str) -> bool:
    t = text.lower()
    return any(w in t for w in CRISIS_WORDS)


@st.cache_resource
def _client():
    return anthropic.Anthropic(api_key=st.secrets["ANTHROPIC_API_KEY"])


def _parse(raw: str) -> dict:
    match = re.search(r"\{.*\}", raw, re.S)  # tolerate stray text or code fences
    data = json.loads(match.group(0))
    score = min(max(float(data.get("burnout_language_score", 0)), 0.0), 10.0)
    return {
        "burnout_language_score": score,
        "themes": [str(x) for x in data.get("themes", [])][:4],
        "protective_factors": [str(x) for x in data.get("protective_factors", [])][:3],
        "crisis_flag": bool(data.get("crisis_flag", False)),
        "summary": str(data.get("summary", "")),
    }


def analyze_journal(text: str):
    """Return (result_dict, error_message). One of them is None."""
    try:
        msg = _client().messages.create(
            model=MODEL,
            max_tokens=500,
            system=SYSTEM,
            messages=[{"role": "user", "content": text}],
        )
        raw = "".join(b.text for b in msg.content if b.type == "text")
        result = _parse(raw)
    except Exception as e:  # network, key, or JSON problems: never crash the demo
        return None, str(e)
    result["crisis_flag"] = result["crisis_flag"] or keyword_crisis(text)
    return result, None
