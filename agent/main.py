import os
import json
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import google.generativeai as genai
from dotenv import load_dotenv

from conversation import chat
from diary_reader import get_unprocessed_entries, mark_as_processed
from memory_updater import update_profile_from_session

load_dotenv()
genai.configure(api_key=os.environ["GOOGLE_API_KEY"])

app = Flask(__name__, static_folder="/app/web")
CORS(app)

# In-memory session store (single user app)
session_store = {
    "history": [],
    "processed_this_session": []
}

@app.route("/")
def index():
    return send_from_directory("/app/web", "index.html")

@app.route("/chat", methods=["POST"])
def handle_chat():
    data = request.json
    user_message = data.get("message", "").strip()

    if not user_message:
        return jsonify({"error": "Empty message"}), 400

    # Process any new diary entries before responding
    new_entries = get_unprocessed_entries()
    if new_entries:
        new_diary_text = "\n\n---\n\n".join([e["content"] for e in new_entries])
        mark_as_processed([e["filename"] for e in new_entries])
        session_store["processed_this_session"].extend([e["filename"] for e in new_entries])
    else:
        new_diary_text = ""

    reply, updated_history = chat(user_message, session_store["history"])
    session_store["history"] = updated_history

    return jsonify({"reply": reply})

@app.route("/end-session", methods=["POST"])
def end_session():
    """Call this when the user ends a session to trigger self-learning."""
    new_diary_text = "\n".join(session_store.get("processed_this_session", []))
    update_profile_from_session(new_diary_text, session_store["history"])
    session_store["history"] = []
    session_store["processed_this_session"] = []
    return jsonify({"status": "Session ended. Profile updated."})

@app.route("/diary", methods=["POST"])
def write_diary():
    data = request.json
    content = data.get("content", "").strip()

    if not content:
        return jsonify({"error": "Empty diary entry"}), 400

    from datetime import datetime
    filename = datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + ".txt"
    path = os.path.join("/app/diary", filename)
    os.makedirs("/app/diary", exist_ok=True)

    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

    return jsonify({"status": "saved", "filename": filename}), 201

@app.route("/profile", methods=["GET"])
def get_profile():
    from profile_manager import load_profile
    return jsonify(load_profile())

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
