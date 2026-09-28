# Hindsight Memory Layer — Member 3 Handoff

## What is already completed

The Hindsight memory layer is fully set up and tested.

- Hindsight Cloud connected successfully
- Memory bank: `procurement-agent`
- 15 vendor records uploaded
- Recall tests: 3/3 passed

## Main file

Use:

`hindsight_memory.py`

This file handles the Hindsight connection and memory operations.

## How to recall vendor history

Import:

```python
from hindsight_memory import recall_vendor_history

memories = recall_vendor_history(
    query="What happened with this vendor in previous negotiations?",
    vendor_name="Nexus Components"
)

from hindsight_memory import format_memories_for_prompt

memory_text = format_memories_for_prompt(memories)

## Complete Example

```python
from hindsight_memory import (
    recall_vendor_history,
    format_memories_for_prompt
)

memories = recall_vendor_history(
    query="What happened in previous negotiations and what tactics worked?",
    vendor_name="Nexus Components"
)

memory_text = format_memories_for_prompt(memories)

prompt = f"""
You are an AI procurement negotiation assistant.

Relevant vendor history:
{memory_text}

Based on this history, provide useful negotiation guidance.
"""

```

## Important

Do NOT create another Hindsight connection.

Do NOT create another memory bank.

Reuse the existing `hindsight_memory.py` functions.

The Hindsight API key is stored in `.env` and must remain private.