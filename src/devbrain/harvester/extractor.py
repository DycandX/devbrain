"""Cognitive Artifact Extractor for AI Agent Sessions."""

from dataclasses import dataclass
from datetime import datetime, timezone
import json
from pathlib import Path
import re
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
    workspace_hint: Optional[str] = None


def clean_user_prompt(raw_text: str) -> str:
    """Extract clean user request text without XML tags or metadata blocks."""
    if not raw_text:
        return ""
    # Strip <ADDITIONAL_METADATA>...</ADDITIONAL_METADATA>
    text = re.sub(r"<ADDITIONAL_METADATA>[\s\S]*?</ADDITIONAL_METADATA>", "", raw_text, flags=re.IGNORECASE)
    # Strip <USER_REQUEST> tags
    text = re.sub(r"</?USER_REQUEST>", "", text, flags=re.IGNORECASE)
    # Strip any remaining XML/HTML tags
    text = re.sub(r"<[^>]+>", " ", text)
    return text.strip()


def sanitize_frontmatter_string(text: str, max_length: int = 120) -> str:
    """Sanitize title or summary to a safe single-line string for YAML frontmatter."""
    if not text:
        return "Untitled Session"
    # Remove XML tags and prompt wrappers
    cleaned = clean_user_prompt(text)
    # Remove markdown header markers if present
    cleaned = re.sub(r"^#+\s*", "", cleaned)
    # Collapse all whitespace and newlines into single spaces
    single_line = re.sub(r"\s+", " ", cleaned).strip()
    # Strip double quotes for YAML safety
    single_line = single_line.replace('"', "'").replace("\n", " ").replace("\r", " ")
    if len(single_line) > max_length:
        single_line = single_line[:max_length].rstrip() + "..."
    return single_line or "Untitled Session"


def extract_workspace_hint_from_transcript(transcript_path: Path) -> Optional[str]:
    """Scan transcript.jsonl for workspace directory or Cwd parameter."""
    if not transcript_path.is_file():
        return None
    try:
        with open(transcript_path, "r", encoding="utf-8", errors="replace") as f:
            for line in f:
                if not line.strip():
                    continue
                # Try JSON parse first
                try:
                    record = json.loads(line)
                    content = str(record.get("content", ""))
                    match = re.search(r"([A-Za-z]:[/\\][^\s\"'\r\n>]+)", content)
                    if match:
                        candidate = match.group(1).replace("\\", "/")
                        return candidate.split("/src/")[0]
                    for call in record.get("tool_calls", []):
                        args = call.get("args", {}) or call.get("parameters", {})
                        if "Cwd" in args and isinstance(args["Cwd"], str):
                            return args["Cwd"].replace("\\", "/")
                except Exception:
                    pass

                # Regex fallback on raw line for Cwd or file URIs
                cwd_match = re.search(r'["\']Cwd["\']\s*:\s*["\']([^"\']+)["\']', line, re.IGNORECASE)
                if cwd_match:
                    return cwd_match.group(1).replace("\\", "/")

                path_match = re.search(r'([A-Za-z]:[/\\][^\s"\'\r\n>]+)', line)
                if path_match:
                    candidate = path_match.group(1).replace("\\", "/")
                    if any(kw in candidate.lower() for kw in ["project", "workspace", "repo", "app"]):
                        return candidate.split("/src/")[0]
    except Exception:
        pass
    return None


def extract_antigravity_session(session: HarvestableSession) -> Optional[ExtractedSessionPayload]:
    """Extract structured walkthrough and reasoning from an Antigravity IDE brain session."""
    walkthrough_file = session.root_path / "walkthrough.md"
    plan_file = session.root_path / "implementation_plan.md"
    transcript_file = session.root_path / ".system_generated" / "logs" / "transcript.jsonl"

    content_parts = []
    title = f"Antigravity Session {session.session_id[:8]}"
    summary = "Completed coding session in Google Antigravity IDE."
    tags = ["agent-inbox", session.source_name]
    workspace_hint = extract_workspace_hint_from_transcript(transcript_file)

    # 1. Prioritize Walkthrough
    if walkthrough_file.is_file():
        try:
            with open(walkthrough_file, "r", encoding="utf-8", errors="replace") as f:
                wt_text = f.read()
            # Extract first heading as title if present
            lines = [l.strip() for l in wt_text.splitlines() if l.strip()]
            if lines and lines[0].startswith("#"):
                raw_heading = lines[0].lstrip("#").strip()
                title = sanitize_frontmatter_string(raw_heading, max_length=120)
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
                clean_initial_prompt = clean_user_prompt(user_prompts[0])
                title = sanitize_frontmatter_string(f"Task: {clean_initial_prompt}", max_length=100)
                summary = sanitize_frontmatter_string(clean_initial_prompt, max_length=200)
                content_parts.append(
                    f"## 🎯 Initial User Goal\n{clean_initial_prompt}\n\n"
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
        source_name=session.source_name,
        title=sanitize_frontmatter_string(title),
        summary=sanitize_frontmatter_string(summary),
        body_markdown=sanitized_body,
        tags=tags,
        created_time=created_dt,
        num_redactions=num_redactions,
        workspace_hint=workspace_hint,
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
                    raw_text = f.read(50000)
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
        title=sanitize_frontmatter_string(title),
        summary=sanitize_frontmatter_string(summary),
        body_markdown=sanitized_body,
        tags=tags,
        created_time=created_dt,
        num_redactions=num_redactions,
        workspace_hint=session.session_id,
    )


def extract_session_payload(session: HarvestableSession) -> Optional[ExtractedSessionPayload]:
    """Generic dispatcher for extracting payload from any supported agent session."""
    if session.source_name.startswith("antigravity"):
        return extract_antigravity_session(session)
    elif session.source_name == "claude-code":
        return extract_claude_session(session)
    return None
