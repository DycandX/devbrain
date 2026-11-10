"""Usage command reporting token consumption of Claude Code sessions per project."""

import json
from typing import Optional

from rich.table import Table
import typer

from devbrain.cli.ui.console import console, print_info
from devbrain.harvester.usage_stats import UsageRow, collect_claude_usage


def _row_dict(row: UsageRow) -> dict:
    return {
        "project": row.name,
        "sessions": row.sessions,
        "prompts": row.prompts,
        "tool_calls": row.tool_calls,
        "central_brain_calls": row.brain_calls,
        "context_tokens": row.context_tokens,
        "cache_hit_ratio": round(row.cache_hit_ratio, 3),
        **row.usage,
    }


def _compact(n: int) -> str:
    """Format a token count as 12.3K / 4.5M / 1.2B."""
    for limit, suffix in ((1_000_000_000, "B"), (1_000_000, "M"), (1_000, "K")):
        if n >= limit:
            return f"{n / limit:.1f}{suffix}"
    return str(n)


def usage_command(
    days: Optional[int] = typer.Option(
        30, "--days", "-d", help="Only count sessions from the last N days (0 for all time)"
    ),
    top: int = typer.Option(15, "--top", "-n", help="Number of projects to list"),
    json_output: bool = typer.Option(False, "--json", help="Output raw JSON"),
):
    """Report Claude Code token usage per project, read from local session transcripts."""
    rows = collect_claude_usage(days=days or None)

    total = UsageRow(name="TOTAL")
    for row in rows:
        total.add(row)

    if json_output:
        console.print_json(json.dumps({"total": _row_dict(total), "projects": [_row_dict(r) for r in rows]}))
        return

    if not rows:
        print_info("No Claude Code sessions found for this period.")
        return

    period = f"last {days} days" if days else "all time"
    table = Table(title=f"Claude Code token usage ({period})", header_style="bold cyan")
    # Number columns keep their width; the project name gives way on narrow terminals
    table.add_column("Project", no_wrap=True, overflow="ellipsis", min_width=10, max_width=20)
    for column in ("Sess", "Prompts", "Tools", "Brain", "Context", "Cache", "Output"):
        table.add_column(column, justify="right", no_wrap=True, min_width=len(column))

    for row in [*rows[:top], total]:
        table.add_row(
            row.name,
            f"{row.sessions:,}",
            f"{row.prompts:,}",
            f"{row.tool_calls:,}",
            f"{row.brain_calls:,}",
            _compact(row.context_tokens),
            f"{row.cache_hit_ratio:.0%}",
            _compact(row.usage["output_tokens"]),
            style="bold" if row is total else None,
            end_section=row is not total and row is rows[:top][-1],
        )

    console.print(table)
    console.print(
        "[dim]Context = input + cache read + cache write tokens. "
        "Brain = calls to central-brain MCP tools. Cache reads are billed at a fraction of fresh input.[/dim]"
    )
