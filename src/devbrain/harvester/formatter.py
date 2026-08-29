"""Obsidian Markdown Formatter and Frontmatter Enricher."""

from datetime import datetime
import json
from pathlib import Path
from typing import Optional, Tuple

from devbrain.harvester.entity_linker import generate_graph_links_block
from devbrain.harvester.extractor import ExtractedSessionPayload, sanitize_frontmatter_string


def format_session_note(
    payload: ExtractedSessionPayload,
    device_name: str,
    matched_project: Optional[Tuple[str, str]] = None,
) -> Tuple[str, str]:
    """Format extracted session payload into an Obsidian Markdown note with graph connections.

    Returns:
        (filename, formatted_markdown_content)
    """
    timestamp_str = payload.created_time.strftime("%Y%m%d_%H%M%S")
    clean_session_id = payload.session_id.replace(" ", "-")[:12]
    clean_device = device_name.replace(" ", "-").lower()

    filename = f"{timestamp_str}_{clean_device}_{payload.source_name}_{clean_session_id}.md"

    tags_json = json.dumps(payload.tags)
    clean_title = sanitize_frontmatter_string(payload.title, max_length=120)
    clean_summary = sanitize_frontmatter_string(payload.summary, max_length=250)

    graph_block = generate_graph_links_block(
        created_time=payload.created_time,
        matched_project=matched_project,
        device_name=device_name,
    )

    note_content = f"""---
id: "INGEST-{timestamp_str}-{clean_session_id}"
title: "{clean_title}"
type: "agent-session-log"
source: "{payload.source_name}"
device: "{device_name}"
created: "{payload.created_time.isoformat()}"
redactions_applied: {payload.num_redactions}
tags: {tags_json}
---

# 📝 {clean_title}

> **Source Agent:** `{payload.source_name}` | **Device:** `{device_name}` | **Session ID:** `{payload.session_id}`

{graph_block}

---

## 🔍 Ingestion Overview:
{clean_summary}

---

{payload.body_markdown}

---
*Ingested into Central AI Brain Hub on {payload.created_time.strftime('%Y-%m-%d %H:%M:%S UTC')}*
"""

    return filename, note_content
