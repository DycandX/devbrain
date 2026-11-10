"""Parser for Claude Code session transcripts (~/.claude/projects/<project>/<session>.jsonl)."""

from dataclasses import dataclass, field
import json
from pathlib import Path
import re
from typing import Any, Dict, List, Optional

# Tools whose input names a file the session wrote to.
FILE_WRITING_TOOLS = {"Edit", "Write", "NotebookEdit", "MultiEdit"}
USAGE_FIELDS = (
    "input_tokens",
    "output_tokens",
    "cache_read_input_tokens",
    "cache_creation_input_tokens",
)
# User records that carry harness output rather than something the user typed.
_HARNESS_PREFIXES = ("<local-command", "<command-name>", "<command-message>", "<system-reminder>")
_TAG_BLOCK = re.compile(r"<(system-reminder|local-command-\w+|command-\w+)>[\s\S]*?</\1>", re.IGNORECASE)


@dataclass
class ClaudeSessionSummary:
    """What happened in one Claude Code session, reduced to what is worth remembering."""

    session_id: str
    cwd: Optional[str] = None
    git_branch: Optional[str] = None
    user_prompts: List[str] = field(default_factory=list)
    final_answer: str = ""
    files_changed: List[str] = field(default_factory=list)
    tool_calls: Dict[str, int] = field(default_factory=dict)
    usage: Dict[str, int] = field(default_factory=lambda: {k: 0 for k in USAGE_FIELDS})
    assistant_messages: int = 0

    @property
    def total_tool_calls(self) -> int:
        return sum(self.tool_calls.values())


def _clean_prompt(text: str) -> str:
    """Drop harness-injected tag blocks and collapse whitespace."""
    text = _TAG_BLOCK.sub(" ", text)
    return re.sub(r"\s+", " ", text).strip()


def _user_text(content: Any) -> str:
    """Text the user typed in a user record; empty for tool results."""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return " ".join(
            b.get("text", "") for b in content if isinstance(b, dict) and b.get("type") == "text"
        )
    return ""


def parse_claude_transcript(transcript: Path) -> Optional[ClaudeSessionSummary]:
    """Read one session transcript and summarize it.

    Returns None when the file holds no user prompt (empty or aborted session).
    """
    summary = ClaudeSessionSummary(session_id=transcript.stem)
    # A streamed assistant message is written as several records sharing one
    # message id, each repeating the usage block: count each message once.
    usage_by_message: Dict[str, Dict[str, int]] = {}
    files_seen: Dict[str, None] = {}

    try:
        with open(transcript, "r", encoding="utf-8", errors="replace") as f:
            for line in f:
                try:
                    record = json.loads(line)
                except ValueError:
                    continue
                if not isinstance(record, dict) or record.get("isSidechain"):
                    continue

                record_type = record.get("type")
                message = record.get("message")
                if record_type not in ("user", "assistant") or not isinstance(message, dict):
                    continue

                summary.cwd = summary.cwd or record.get("cwd")
                summary.git_branch = summary.git_branch or record.get("gitBranch")
                content = message.get("content")

                if record_type == "user":
                    if record.get("isMeta"):
                        continue
                    raw = _user_text(content).strip()
                    if not raw or raw.startswith(_HARNESS_PREFIXES):
                        continue
                    prompt = _clean_prompt(raw)
                    if prompt:
                        summary.user_prompts.append(prompt)
                    continue

                message_id = message.get("id") or record.get("uuid") or str(len(usage_by_message))
                usage = message.get("usage")
                if isinstance(usage, dict):
                    usage_by_message[message_id] = {
                        k: int(usage.get(k) or 0) for k in USAGE_FIELDS
                    }

                if not isinstance(content, list):
                    continue
                for block in content:
                    if not isinstance(block, dict):
                        continue
                    if block.get("type") == "text" and block.get("text", "").strip():
                        summary.final_answer = block["text"].strip()
                    elif block.get("type") == "tool_use":
                        name = block.get("name", "unknown")
                        summary.tool_calls[name] = summary.tool_calls.get(name, 0) + 1
                        tool_input = block.get("input") or {}
                        if name in FILE_WRITING_TOOLS and isinstance(tool_input.get("file_path"), str):
                            files_seen[tool_input["file_path"]] = None
    except OSError:
        return None

    if not summary.user_prompts:
        return None

    summary.files_changed = list(files_seen)
    summary.assistant_messages = len(usage_by_message)
    for usage in usage_by_message.values():
        for key in USAGE_FIELDS:
            summary.usage[key] += usage[key]
    return summary


def _truncate(text: str, limit: int) -> str:
    return text if len(text) <= limit else text[:limit].rstrip() + "..."


def render_claude_session(summary: ClaudeSessionSummary) -> str:
    """Render the summary as a compact Markdown body for the vault note."""
    max_prompts = 15
    max_files = 30

    lines = ["## 🎯 Goal", _truncate(summary.user_prompts[0], 600), ""]

    if len(summary.user_prompts) > 1:
        lines.append("## 💬 Follow-up Requests")
        for prompt in summary.user_prompts[1:max_prompts]:
            lines.append(f"- {_truncate(prompt, 200)}")
        if len(summary.user_prompts) > max_prompts:
            lines.append(f"- ... and {len(summary.user_prompts) - max_prompts} more")
        lines.append("")

    if summary.final_answer:
        lines += ["## ✅ Outcome", _truncate(summary.final_answer, 1500), ""]

    if summary.files_changed:
        lines.append("## 📝 Files Changed")
        for path in summary.files_changed[:max_files]:
            lines.append(f"- `{path}`")
        if len(summary.files_changed) > max_files:
            lines.append(f"- ... and {len(summary.files_changed) - max_files} more")
        lines.append("")

    usage = summary.usage
    top_tools = sorted(summary.tool_calls.items(), key=lambda kv: -kv[1])[:6]
    lines += [
        "## 📊 Session Stats",
        f"- **Workspace:** `{summary.cwd or 'unknown'}`"
        + (f" (branch `{summary.git_branch}`)" if summary.git_branch else ""),
        f"- **User prompts:** {len(summary.user_prompts)} | **Assistant messages:** {summary.assistant_messages}"
        f" | **Tool calls:** {summary.total_tool_calls}",
    ]
    if top_tools:
        lines.append("- **Top tools:** " + ", ".join(f"{name} ×{count}" for name, count in top_tools))
    lines.append(
        f"- **Tokens:** input {usage['input_tokens']:,} | output {usage['output_tokens']:,}"
        f" | cache read {usage['cache_read_input_tokens']:,}"
        f" | cache write {usage['cache_creation_input_tokens']:,}"
    )
    return "\n".join(lines)
