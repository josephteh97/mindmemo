import json
import google.generativeai as genai
from profile_manager import load_profile, save_profile
from prompts import PROFILE_UPDATE_PROMPT
from datetime import datetime

def update_profile_from_session(new_diary_text: str, conversation_history: list):
    existing_profile = load_profile()

    conversation_text = "\n".join([
        f"{msg['role'].upper()}: {msg['content']}"
        for msg in conversation_history
    ])

    prompt = PROFILE_UPDATE_PROMPT.format(
        existing_profile=json.dumps(existing_profile, indent=2),
        new_diary_entries=new_diary_text or "No new diary entries this session.",
        new_conversations=conversation_text or "No conversation this session."
    )

    model = genai.GenerativeModel("gemini-1.5-pro")
    response = model.generate_content(prompt)

    try:
        raw = response.text.strip()
        # Strip markdown code fences if present
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        updated_profile = json.loads(raw.strip())
        updated_profile["last_updated"] = datetime.now().isoformat()
        save_profile(updated_profile)
        print(f"[Solace] Profile updated at {updated_profile['last_updated']}")
    except json.JSONDecodeError as e:
        print(f"[Solace] Warning: Could not parse profile update — {e}")
