"""Token usage aggregation over Claude Code session transcripts."""

from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Dict, List, Optional

from devbrain.harvester.claude_code import USAGE_FIELDS, parse_claude_transcript
from devbrain.harvester.discovery import get_default_agent_roots

MCP_TOOL_PREFIX = "mcp__central-brain__"


@dataclass
class UsageRow:
    """Usage totals for one group of sessions (a project, or everything)."""

    name: str
    sessions: int = 0
    prompts: int = 0
    tool_calls: int = 0
    brain_calls: int = 0
    usage: Dict[str, int] = field(default_factory=lambda: {k: 0 for k in USAGE_FIELDS})

    @property
    def context_tokens(self) -> int:
        """Tokens sent to the model: fresh input plus cache reads and cache writes."""
        u = self.usage
        return u["input_tokens"] + u["cache_read_input_tokens"] + u["cache_creation_input_tokens"]

    @property
    def cache_hit_ratio(self) -> float:
        """Share of context tokens served from the prompt cache."""
        total = self.context_tokens
        return self.usage["cache_read_input_tokens"] / total if total else 0.0

    def add(self, other: "UsageRow") -> None:
        self.sessions += other.sessions
        self.prompts += other.prompts
        self.tool_calls += other.tool_calls
        self.brain_calls += other.brain_calls
        for key in USAGE_FIELDS:
            self.usage[key] += other.usage[key]


def _project_label(cwd: Optional[str], fallback: str) -> str:
    if not cwd:
        return fallback
    return cwd.replace("\\", "/").rstrip("/").rsplit("/", 1)[-1] or fallback


def collect_claude_usage(
    days: Optional[int] = None,
    roots: Optional[List[Path]] = None,
) -> List[UsageRow]:
    """Aggregate Claude Code token usage per project, largest context first.

    Only sessions modified within the last `days` days are counted (all when None).
    """
    roots = roots if roots is not None else get_default_agent_roots()["claude-code"]
    cutoff = (datetime.now(timezone.utc) - timedelta(days=days)).timestamp() if days else None
    by_project: Dict[str, UsageRow] = {}

    for root in roots:
        if not root.is_dir():
            continue
        for project_dir in root.iterdir():
            if not project_dir.is_dir():
                continue
            for transcript in project_dir.glob("*.jsonl"):
                if cutoff and transcript.stat().st_mtime < cutoff:
                    continue
                summary = parse_claude_transcript(transcript)
                if summary is None:
                    continue

                label = _project_label(summary.cwd, project_dir.name)
                row = by_project.setdefault(label, UsageRow(name=label))
                row.sessions += 1
                row.prompts += len(summary.user_prompts)
                row.tool_calls += summary.total_tool_calls
                row.brain_calls += sum(
                    count for name, count in summary.tool_calls.items() if name.startswith(MCP_TOOL_PREFIX)
                )
                for key in USAGE_FIELDS:
                    row.usage[key] += summary.usage[key]

    return sorted(by_project.values(), key=lambda r: -r.context_tokens)
