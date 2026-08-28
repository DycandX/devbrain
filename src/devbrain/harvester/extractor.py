"""Cognitive Artifact Extractor for AI Agent Sessions."""

from dataclasses import dataclass
from datetime import datetime, timezone
import json
from pathlib import Path
from typing import List, Optional

from devbrain.harvester.discovery import HarvestableSession
from devbrain.harvester.sanitizer import sanitize_text


@dataclass
class ExtractedSessionPayload:
    """Standardized payload extracted from an AI session."""
    session_id: str
    source_name: str
    title: str
    summary: str
    body_markdown: str
    tags: List[str]
    created_time: datetime
    num_redactions: int


def extract_antigravity_session(session: HarvestableSession) -> Optional[ExtractedSessionPayload]:
    """Extract structured walkthrough and reasoning from an Antigravity IDE brain session."""
    walkthrough_file = session.root_path / "walkthrough.md"
    plan_file = session.root_path / "implementation_plan.md"
    transcript_file = session.root_path / ".system_generated" / "logs" / "transcript.jsonl"

    content_parts = []
    title = f"Antigravity Session {session.session_id[:8]}"
    summary = "Completed coding session in Google Antigravity IDE."
    tags = ["agent-inbox", "antigravity"]

    # 1. Prioritize Walkthrough
    if walkthrough_file.is_file():
        try:
            with open(walkthrough_file, "r", encoding="utf-8", errors="replace") as f:
                wt_text = f.read()
            # Extract first heading as title if present
            lines = [l.strip() for l in wt_text.splitlines() if l.strip()]
            if lines and lines[0].startswith("#"):
                title = lines[0].lstrip("#").strip()
            content_parts.append(wt_text)
            tags.append("walkthrough")
        except Exception:
            pass

    # 2. Append Implementation Plan if present
    if plan_file.is_file():
        try:
            with open(plan_file, "r", encoding="utf-8", errors="replace") as f:
                plan_text = f.read()
            content_parts.append("\n---\n## 📐 Implementation Architecture\n" + plan_text)
            tags.append("architecture")
        except Exception:
            pass

    # 3. Fallback to transcript.jsonl if no walkthrough
    if not content_parts and transcript_file.is_file():
        try:
            user_prompts = []
            with open(transcript_file, "r", encoding="utf-8", errors="replace") as f:
                for line in f:
                    if not line.strip():
                        continue
                    try:
                        record = json.loads(line)
                        if record.get("type") == "USER_INPUT" and record.get("content"):
                            user_prompts.append(record["content"])
                    except Exception:
                        continue

            if user_prompts:
                title = f"Task: {user_prompts[0][:60]}..."
                summary = user_prompts[0]
                content_parts.append(
                    f"## 🎯 Initial User Goal\n{user_prompts[0]}\n\n"
                    f"## 📋 Total User Interactions\n{len(user_prompts)} turns recorded."
                )
                tags.append("transcript")
        except Exception:
            pass

    if not content_parts:
        return None

    full_body = "\n\n".join(content_parts)
    sanitized_body, num_redactions = sanitize_text(full_body)

    created_dt = datetime.fromtimestamp(session.last_modified, timezone.utc)

    return ExtractedSessionPayload(
        session_id=session.session_id,
        source_name="antigravity",
        title=title,
        summary=summary,
        body_markdown=sanitized_body,
        tags=tags,
        created_time=created_dt,
        num_redactions=num_redactions,
    )


def extract_claude_session(session: HarvestableSession) -> Optional[ExtractedSessionPayload]:
    """Extract session logs from Claude Code projects."""
    content_parts = []
    title = f"Claude Code Project {session.session_id}"
    summary = f"Claude Code interaction in project {session.session_id}"
    tags = ["agent-inbox", "claude-code"]

    for file_path in session.artifact_files:
        if file_path.suffix in [".jsonl", ".json"]:
            try:
                with open(file_path, "r", encoding="utf-8", errors="replace") as f:
                    raw_text = f.read(50000)  # Read up to 50KB summary
                content_parts.append(f"### Log: `{file_path.name}`\n```json\n{raw_text[:2000]}\n```")
            except Exception:
                continue

    if not content_parts:
        return None

    full_body = f"# {title}\n\n" + "\n\n".join(content_parts)
    sanitized_body, num_redactions = sanitize_text(full_body)
    created_dt = datetime.fromtimestamp(session.last_modified, timezone.utc)

    return ExtractedSessionPayload(
        session_id=session.session_id,
        source_name="claude-code",
        title=title,
        summary=summary,
        body_markdown=sanitized_body,
        tags=tags,
        created_time=created_dt,
        num_redactions=num_redactions,
    )


def extract_session_payload(session: HarvestableSession) -> Optional[ExtractedSessionPayload]:
    """Generic dispatcher for extracting payload from any supported agent session."""
    if session.source_name == "antigravity":
        return extract_antigravity_session(session)
    elif session.source_name == "claude-code":
        return extract_claude_session(session)
    return None
