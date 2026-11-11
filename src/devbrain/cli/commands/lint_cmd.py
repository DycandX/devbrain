"""Lint command checking vault notes against the frontmatter schema and known defects."""

from pathlib import Path
from typing import Optional

from rich.table import Table
import typer

from devbrain.cli.ui.console import console, print_info, print_success, print_warning
from devbrain.core.config import find_config, load_config
from devbrain.maintenance.lint import lint_vault, summarize


def lint_command(
    fix: bool = typer.Option(False, "--fix", help="Repair the issues that can be fixed safely"),
    show: int = typer.Option(20, "--show", "-n", help="Number of notes to list"),
    vault: Optional[str] = typer.Option(None, "--vault", "-v", help="Path to Obsidian vault"),
):
    """Check notes for schema violations and known defects; report by default, repair with --fix."""
    if vault:
        vault_path = Path(vault).expanduser().resolve()
    else:
        cfg_file = find_config()
        if not cfg_file:
            print_warning("No .brainrc.json found. Pass --vault.")
            raise typer.Exit(code=1)
        vault_path = load_config(cfg_file).resolve_vault_path()

    reports = lint_vault(vault_path, fix=fix)
    if not reports:
        print_success("No issues found.")
        return

    counts = summarize(reports)
    table = Table(title="Issues by rule", header_style="bold cyan")
    table.add_column("Rule")
    table.add_column("Notes", justify="right")
    for rule, count in sorted(counts.items(), key=lambda kv: -kv[1]):
        table.add_row(rule, str(count))
    console.print(table)

    for report in reports[:show]:
        mark = "[green]fixed[/green]" if report.fixed else ""
        rules = ", ".join(i.rule for i in report.issues)
        console.print(f"  {report.rel_path} [dim]({rules})[/dim] {mark}")
    if len(reports) > show:
        console.print(f"  [dim]... and {len(reports) - show} more[/dim]")

    unfixable = sum(1 for r in reports for i in r.issues if not i.fixable)
    if fix:
        print_success(f"Repaired {sum(r.fixed for r in reports)} note(s).")
        if unfixable:
            print_warning(f"{unfixable} issue(s) need manual repair.")
        print_info("Run 'devbrain index' to refresh the search index.")
    else:
        print_info(f"{len(reports)} note(s) with issues. Run with --fix to repair them.")
