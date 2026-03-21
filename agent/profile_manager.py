import json
import os
from datetime import datetime
from typing import Any, Dict


PROFILE_PATH = "/app/memory/user_profile.json"

DEFAULT_PROFILE: Dict[str, Any] = {
    "name": None,
    "age_estimate": None,
    "core_values": [],
    "recurring_emotions": [],
    "known_triggers": [],
    "coping_patterns": [],
    "support_network": [],
    "trauma_themes": [],
    "strengths": [],
    "communication_style": "unknown",
    "current_focus": "unknown",
    "progress_notes": "",
    "last_updated": datetime.now().isoformat(),
}

def load_profile() -> Dict[str, Any]:
    if not os.path.exists(PROFILE_PATH):
        save_profile(DEFAULT_PROFILE)
        return dict(DEFAULT_PROFILE)
    with open(PROFILE_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, dict):
        save_profile(DEFAULT_PROFILE)
        return dict(DEFAULT_PROFILE)
    merged = dict(DEFAULT_PROFILE)
    merged.update(data)
    return merged


def save_profile(profile: dict) -> None:
    os.makedirs(os.path.dirname(PROFILE_PATH), exist_ok=True)
    with open(PROFILE_PATH, "w", encoding="utf-8") as f:
        json.dump(profile, f, indent=2, ensure_ascii=False)


def profile_to_summary(profile: dict) -> str:
    if not profile or profile == DEFAULT_PROFILE:
        return "This is the first interaction. You know nothing about this person yet. Be warm and open."

    lines = []
    if profile.get("name"):
        lines.append(f"Name: {profile['name']}")
    if profile.get("core_values"):
        lines.append(f"Core values: {', '.join(profile['core_values'])}")
    if profile.get("recurring_emotions"):
        lines.append(f"Recurring emotions: {', '.join(profile['recurring_emotions'])}")
    if profile.get("known_triggers"):
        lines.append(f"Known triggers: {', '.join(profile['known_triggers'])}")
    if profile.get("trauma_themes"):
        lines.append(f"Past pain themes: {', '.join(profile['trauma_themes'])}")
    if profile.get("strengths"):
        lines.append(f"Strengths: {', '.join(profile['strengths'])}")
    if profile.get("current_focus"):
        lines.append(f"Currently focused on: {profile['current_focus']}")
    if profile.get("progress_notes"):
        lines.append(f"Growth observed: {profile['progress_notes']}")
    return "\n".join(lines)


def profile_summary(profile: dict) -> str:
    return profile_to_summary(profile)


def merge_profile(existing: Dict[str, Any], updates: Dict[str, Any]) -> Dict[str, Any]:
    merged: Dict[str, Any] = dict(DEFAULT_PROFILE)
    if isinstance(existing, dict):
        merged.update(existing)

    def merge_list(key: str) -> None:
        cur = merged.get(key, [])
        nxt = updates.get(key, [])
        if not isinstance(cur, list):
            cur = []
        if not isinstance(nxt, list):
            nxt = []
        seen = set()
        out = []
        for item in cur + nxt:
            s = str(item).strip()
            if not s:
                continue
            k = s.lower()
            if k in seen:
                continue
            seen.add(k)
            out.append(s)
        merged[key] = out

    for k in [
        "core_values",
        "recurring_emotions",
        "known_triggers",
        "coping_patterns",
        "support_network",
        "trauma_themes",
        "strengths",
    ]:
        merge_list(k)

    for k in ["name", "age_estimate", "communication_style", "current_focus", "progress_notes"]:
        v = updates.get(k, None)
        if v is not None and str(v).strip() != "":
            merged[k] = str(v).strip()

    last_updated = updates.get("last_updated")
    if isinstance(last_updated, str) and last_updated.strip():
        merged["last_updated"] = last_updated.strip()
    else:
        merged["last_updated"] = datetime.now().isoformat()

    return merged
