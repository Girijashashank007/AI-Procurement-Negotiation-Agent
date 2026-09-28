import os
from dotenv import load_dotenv
from groq import Groq
from hindsight_memory import (
    recall_vendor_history,
    format_memories_for_prompt,
    close_client
)

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY is missing in .env")

client = Groq(api_key=GROQ_API_KEY)

print("Groq connection setup successful.")

vendor_name = input("Enter vendor name: ").strip()

memories = recall_vendor_history(
    query="What happened in previous negotiations and what tactics worked?",
    vendor_name=vendor_name
)

memory_text = format_memories_for_prompt(memories)

prompt = f"""
You are an AI procurement negotiation assistant.

Vendor: {vendor_name}

Relevant vendor history from Hindsight:
{memory_text}

Use ONLY the vendor history provided above.

Do not invent or assume any:
- dates
- prices
- discounts
- negotiations
- vendor actions
- outcomes
- delivery events
- quality events

If the available history does not contain enough information to answer something, clearly say that the information is not available.

Based only on the available history, organize your response into these sections:

1. PAST HISTORY
   - List the most important facts about this vendor.
   - Include relevant prices, discounts, delays, quality issues, and previous negotiation outcomes when available.

2. WHAT WORKED WITH THIS VENDOR
   - State which negotiation tactics have actually produced a result with this vendor.
   - If no successful tactic is recorded for this vendor, clearly say:
     "No successful negotiation tactic is recorded for this vendor."

3. RELEVANT LESSONS FROM OTHER VENDORS
   - You may mention tactics that worked with other vendors in the provided history.
   - Clearly identify them as lessons from other vendors, not as proven tactics for the current vendor.

4. NEXT NEGOTIATION CONSIDERATIONS
   - Give practical suggestions based on the available history.
   - Clearly label these as suggestions, not facts or guaranteed outcomes.

Keep the response concise and easy for a procurement team to understand.

Clearly separate facts from suggestions.

Do not claim that any suggested tactic will definitely work, has a certain probability of success, or is proven unless that exact evidence exists in the Hindsight history.
Give practical and concise advice.
"""

response = client.chat.completions.create(
    model="openai/gpt-oss-120b",
    messages=[
        {
            "role": "user",
            "content": prompt
        }
    ]
)

print("\n===== PROCUREMENT NEGOTIATION ADVICE =====")
print(response.choices[0].message.content)

close_client()