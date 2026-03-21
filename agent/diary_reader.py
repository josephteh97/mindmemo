import os
from datetime import datetime
import json


DIARY_DIR = "/app/diary"
PROCESSED_LOG = "/app/memory/processed_entries.json"


def get_unprocessed_entries() -> list[dict]:
    processed = _load_processed()
    entries = []

    if not os.path.isdir(DIARY_DIR):
        return []

    for filename in sorted(os.listdir(DIARY_DIR)):
        if filename.endswith((".txt", ".md")) and filename not in processed:
            path = os.path.join(DIARY_DIR, filename)
            with open(path, "r", encoding="utf-8") as f:
                content = f.read().strip()
            if content:
                entries.append(
                    {
                        "filename": filename,
                        "content": content,
                        "date": datetime.fromtimestamp(os.path.getmtime(path)).isoformat(),
                    }
                )
    return entries


def mark_as_processed(filenames: list[str]):
    processed = _load_processed()
    for f in filenames:
        processed[f] = datetime.now().isoformat()
    os.makedirs(os.path.dirname(PROCESSED_LOG), exist_ok=True)
    with open(PROCESSED_LOG, "w", encoding="utf-8") as file:
        json.dump(processed, file, indent=2, ensure_ascii=False)


def get_recent_entries(n=5) -> str:
    all_entries = []
    if not os.path.isdir(DIARY_DIR):
        return "No diary entries yet."
    for filename in sorted(os.listdir(DIARY_DIR))[-n:]:
        if filename.endswith((".txt", ".md")):
            path = os.path.join(DIARY_DIR, filename)
            with open(path, "r", encoding="utf-8") as f:
                content = f.read().strip()
            all_entries.append(f"[{filename}]\n{content}")
    return "\n\n---\n\n".join(all_entries) if all_entries else "No diary entries yet."

def _load_processed() -> dict:
    if not os.path.exists(PROCESSED_LOG):
        return {}
    with open(PROCESSED_LOG, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data if isinstance(data, dict) else {}
