"""
server.py - tiny web server for the Procurement Negotiation Agent UI.
Reuses hindsight_memory.py (no new Hindsight connection or bank).
Run:  python server.py   then open http://127.0.0.1:5000
"""
import asyncio
import json
import os
from pathlib import Path

from dotenv import load_dotenv
from flask import Flask, jsonify, request, send_from_directory
from groq import Groq

from hindsight_memory import (
    recall_vendor_history,
    format_memories_for_prompt,
    store_vendor_history
)

load_dotenv()
BASE = Path(__file__).parent
app = Flask(__name__, static_folder=str(BASE / "static"))

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
groq_client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None

# vendor_data.json is only used to list vendors in the sidebar.
VENDORS = json.loads((BASE / "vendor_data.json").read_text(encoding="utf-8"))

PROMPT = """
You are an AI procurement negotiation assistant.

Vendor: {vendor}

Relevant vendor history from Hindsight:
{memory}

Use ONLY the vendor history provided above.
Do not invent or assume any dates, prices, discounts, negotiations, vendor actions, outcomes, delivery events or quality events.
If the history does not contain enough information, clearly say the information is not available.

Organize your response into exactly these sections, each starting with a line "## <title>":

## PAST HISTORY
Most important facts: prices, discounts, delays, quality issues, outcomes.

## WHAT WORKED WITH THIS VENDOR
Tactics that actually produced a result. If none is recorded, say:
"No successful negotiation tactic is recorded for this vendor."

## LESSONS FROM OTHER VENDORS
Clearly identify these as lessons from other vendors, not proven for this vendor.

## NEXT NEGOTIATION CONSIDERATIONS
Practical suggestions, clearly labelled as suggestions. Never claim a tactic will definitely work.

Keep it concise. Use short bullet points starting with "- ". Separate facts from suggestions.
"""


@app.get("/")
def home():
    # Look for index.html in static/ first, then next to server.py
    for folder in (BASE / "static", BASE):
        if (folder / "index.html").exists():
            return send_from_directory(str(folder), "index.html")
    return "index.html not found. Put it in a folder named 'static' next to server.py.", 404


@app.get("/api/vendors")
def vendors():
    return jsonify(
        [{"name": v["vendor_name"], "context": v["context"], "timestamp": v["timestamp"]} for v in VENDORS]
    )

@app.post("/api/vendors")
def add_vendor():
    data = request.get_json(silent=True) or {}

    name = data.get("name", "").strip()
    context = data.get("context", "").strip()
    history = data.get("history", "").strip()

    if not name or not context or not history:
        return jsonify(error="Name, context and history are required."), 400

    # Prevent duplicate vendors
    if any(v["vendor_name"].lower() == name.lower() for v in VENDORS):
        return jsonify(error="Vendor already exists."), 400

    from datetime import datetime, timezone

    timestamp = datetime.now(timezone.utc).isoformat()

    # Save vendor history into Hindsight
    store_vendor_history(
        vendor_name=name,
        content=history,
        context=context,
        timestamp=timestamp
    )

    # Create vendor record
    new_vendor = {
        "vendor_name": name,
        "context": context,
        "content": history,
        "timestamp": timestamp
    }

    # Add to current server memory
    VENDORS.append(new_vendor)

    # Save permanently to vendor_data.json
    (BASE / "vendor_data.json").write_text(
        json.dumps(VENDORS, indent=2),
        encoding="utf-8"
    )

    return jsonify(
        message="Vendor added successfully.",
        vendor={
            "name": name,
            "context": context,
            "timestamp": timestamp
        }
    ), 201

@app.post("/api/brief")
async def brief():
    vendor = (request.get_json(silent=True) or {}).get("vendor", "").strip()
    if not vendor:
        return jsonify(error="Choose a vendor first."), 400
    if not groq_client:
        return jsonify(error="GROQ_API_KEY is missing in .env"), 500
    try:
        memories = await asyncio.to_thread(
    recall_vendor_history,
    "What happened in previous negotiations and what tactics worked?",
    vendor_name=vendor
)
        resp = groq_client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=[{"role": "user", "content": PROMPT.format(
                vendor=vendor, memory=format_memories_for_prompt(memories))}],
        )
        return jsonify(briefing=resp.choices[0].message.content, memories=memories)
    except Exception as e:  # show a readable message in the UI
        return jsonify(error=str(e)), 500


if __name__ == "__main__":
    print("\n  Recall UI is starting...")
    print("  Open this in your browser:  http://127.0.0.1:5000")
    if not GROQ_API_KEY:
        print("  WARNING: GROQ_API_KEY is missing in .env (briefings will fail)")
    print()
    app.run(host="127.0.0.1", port=5000, debug=False)
