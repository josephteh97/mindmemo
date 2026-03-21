import google.generativeai as genai
from profile_manager import load_profile, profile_to_summary
from diary_reader import get_recent_entries
from prompts import SYSTEM_PROMPT_TEMPLATE

def build_system_prompt() -> str:
    profile = load_profile()
    return SYSTEM_PROMPT_TEMPLATE.format(
        profile_summary=profile_to_summary(profile),
        diary_context=get_recent_entries(n=5)
    )

CRISIS_KEYWORDS = [
    "suicide", "kill myself", "end my life", "don't want to live",
    "self harm", "hurt myself", "can't go on"
]

def contains_crisis_signal(text: str) -> bool:
    return any(kw in text.lower() for kw in CRISIS_KEYWORDS)

def chat(user_message: str, history: list) -> tuple[str, list]:
    if contains_crisis_signal(user_message):
        crisis_msg = (
            "I hear you, and I'm so glad you're talking to me. "
            "What you're feeling matters deeply. Please reach out to a crisis line right now — "
            "you deserve real human support. In Singapore: Samaritans of Singapore (SOS): 1-767. "
            "I'm still here with you."
        )
        history.append({"role": "user", "content": user_message})
        history.append({"role": "assistant", "content": crisis_msg})
        return crisis_msg, history

    system_prompt = build_system_prompt()

    model = genai.GenerativeModel(
        model_name="gemini-2.0-flash",
        system_instruction=system_prompt
    )

    # Build Gemini chat history format
    gemini_history = []
    for msg in history:
        role = "user" if msg["role"] == "user" else "model"
        gemini_history.append({"role": role, "parts": [msg["content"]]})

    chat_session = model.start_chat(history=gemini_history)
    response = chat_session.send_message(user_message)

    reply = response.text

    history.append({"role": "user", "content": user_message})
    history.append({"role": "assistant", "content": reply})

    return reply, history
