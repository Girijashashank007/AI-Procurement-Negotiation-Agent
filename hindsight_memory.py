import os
from datetime import datetime

from dotenv import load_dotenv
from hindsight_client import Hindsight


# Load values from .env
load_dotenv()

API_KEY = os.getenv("HINDSIGHT_API_KEY")
BANK_ID = os.getenv("HINDSIGHT_BANK_ID")

CLOUD_URL = "https://api.hindsight.vectorize.io"


if not API_KEY:
    raise ValueError("HINDSIGHT_API_KEY is missing in .env")

if not BANK_ID:
    raise ValueError("HINDSIGHT_BANK_ID is missing in .env")


# Create Hindsight client
def get_client():
    return Hindsight(base_url=CLOUD_URL, api_key=API_KEY)


def ensure_bank():
    """Create the procurement memory bank if it does not already exist."""
    try:
        get_client().create_bank(
            bank_id=BANK_ID,
            name="Procurement Negotiation Memory"
        )
        print(f"Memory bank '{BANK_ID}' created.")
    except Exception as e:
        if "already exists" in str(e).lower() or "409" in str(e):
            print(f"Memory bank '{BANK_ID}' already exists.")
        else:
            raise


def verify_connection():
    """Check whether the Hindsight connection is working."""
    ensure_bank()

    result = get_client().recall(bank_id=BANK_ID, query="connection test")
    print("Hindsight connection successful.")
    return result


def store_vendor_history(
    vendor_name,
    content,
    context="vendor negotiation history",
    timestamp=None
):
    """Store one vendor record in Hindsight memory."""

    if timestamp:
        timestamp = datetime.fromisoformat(
            timestamp.replace("Z", "+00:00")
        )

    result = get_client().retain(
        bank_id=BANK_ID,
        content=f"Vendor: {vendor_name}\n{content}",
        context=context,
        timestamp=timestamp
    )

    return result


def recall_vendor_history(query, vendor_name=None):
    """Recall relevant vendor history from Hindsight."""

    if vendor_name:
        query = f"Vendor: {vendor_name}. {query}"

    result = get_client().recall(bank_id=BANK_ID, query=query)

    return [memory.text for memory in result.results]


def format_memories_for_prompt(memories):
    """Convert recalled memories into text for an AI prompt."""

    if not memories:
        return "No relevant vendor history found."

    return "\n".join(
        f"- {memory}"
        for memory in memories
    )

def close_client():
    pass