"""Vault lint: find notes that break the frontmatter schema or carry known defects, and fix them.

Fixes edit frontmatter line by line instead of re-serializing YAML, so key
order, comments, and formatting of untouched lines are preserved.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
import json
from pathlib import Path
import re
from typing import Callable, Dict, List, Optional, Tuple

import yaml

from devbrain.core.constants import BRAIN_DATA_DIR, DIR_DAILY
from devbrain.core.fsutil import atomic_write_text
from devbrain.core.schema import CREATED_FALLBACK_KEYS, REQUIRED_KEYS, infer_note_type, is_schema_exempt
from devbrain.harvester.extractor import HARNESS_NOTICE, clean_user_prompt, sanitize_frontmatter_string

_FRONTMATTER = re.compile(r"\A---[ \t]*\r?\n(.*?)\r?\n---[ \t]*(?:\r?\n|\Z)", re.DOTALL)
_TOP_LEVEL_KEY = re.compile(r"^([A-Za-z_][\w-]*):(.*)$")
_DAILY_LINK = re.compile(rf"\[\[{DIR_DAILY}/([^\]|]+)(?:\|([^\]]+))?\]\]")
_LEGACY_SUFFIX = " (Live Dataview):"


@dataclass
class Issue:
    rule: str
    message: str
    fixable: bool = True


@dataclass
class NoteReport:
    rel_path: str
    issues: List[Issue] = field(default_factory=list)
    fixed: bool = False


@dataclass
class _Note:
    """A note split into frontmatter lines and body, edited in place by fixes."""

    path: Path
    rel_path: str
    fm_lines: Optional[List[str]]
    body: str

    @classmethod
    def load(cls, path: Path, rel_path: str) -> "_Note":
        text = path.read_text(encoding="utf-8", errors="replace").replace("\r\n", "\n")
        match = _FRONTMATTER.match(text)
        if not match:
            return cls(path, rel_path, None, text)
        return cls(path, rel_path, match.group(1).split("\n"), text[match.end():])

    def render(self) -> str:
        if self.fm_lines is None:
            return self.body
        return "---\n" + "\n".join(self.fm_lines) + "\n---\n" + self.body

    def frontmatter(self) -> Optional[dict]:
        """Parsed frontmatter; None when absent or not valid YAML."""
        if self.fm_lines is None:
            return None
        try:
            data = yaml.safe_load("\n".join(self.fm_lines))
        except yaml.YAMLError:
            return None
        return data if isinstance(data, dict) else None

    def key_index(self, key: str) -> Optional[int]:
        for i, line in enumerate(self.fm_lines or []):
            m = _TOP_LEVEL_KEY.match(line)
            if m and m.group(1) == key:
                return i
        return None

    def set_key(self, key: str, value) -> None:
        """Set a scalar or list key, written as JSON (valid YAML for any value)."""
        line = f"{key}: {json.dumps(value, ensure_ascii=False)}"
        if self.fm_lines is None:
            self.fm_lines = []
        i = self.key_index(key)
        if i is None:
            self.fm_lines.append(line)
        else:
            self.fm_lines[i] = line

    def first_heading(self) -> Optional[str]:
        for line in self.body.splitlines():
            m = re.match(r"^#\s+(.+)$", line.strip())
            if m:
                return m.group(1).strip()
        return None


def _created_from_mtime(path: Path) -> str:
    return datetime.fromtimestamp(path.stat().st_mtime, timezone.utc).isoformat()


# --- Rules -----------------------------------------------------------------
# Each rule inspects a note, returns the issue it finds (or None), and fixes it
# in place when `fix` is true.

Rule = Callable[[_Note, bool, Path], Optional[Issue]]


def rule_invalid_yaml(note: _Note, fix: bool, vault: Path) -> Optional[Issue]:
    """Frontmatter that YAML cannot parse, usually an unescaped value."""
    if note.fm_lines is None or note.frontmatter() is not None:
        return None
    if fix:
        for i, line in enumerate(note.fm_lines):
            m = _TOP_LEVEL_KEY.match(line)
            if not m or not m.group(2).strip():
                continue
            try:
                yaml.safe_load(line)
            except yaml.YAMLError:
                raw = m.group(2).strip()
                if len(raw) >= 2 and raw[0] == raw[-1] and raw[0] in "\"'":
                    raw = raw[1:-1]
                note.fm_lines[i] = f"{m.group(1)}: {json.dumps(raw, ensure_ascii=False)}"
    fixable = note.frontmatter() is not None if fix else True
    return Issue("invalid-yaml", "Frontmatter is not valid YAML", fixable)


def rule_missing_frontmatter(note: _Note, fix: bool, vault: Path) -> Optional[Issue]:
    if note.fm_lines is not None:
        return None
    if fix:
        note.fm_lines = []
        note.set_key("type", infer_note_type(note.rel_path) or "note")
        note.set_key("title", note.first_heading() or note.path.stem)
        note.set_key("created", _created_from_mtime(note.path))
        note.set_key("tags", [])
        note.body = note.body if note.body.startswith("\n") else "\n" + note.body
    return Issue("missing-frontmatter", "Note has no frontmatter")


def rule_required_keys(note: _Note, fix: bool, vault: Path) -> Optional[Issue]:
    data = note.frontmatter()
    if data is None or is_schema_exempt(note.rel_path):
        return None
    missing = [k for k in REQUIRED_KEYS if data.get(k) in (None, "")]
    if not missing:
        return None
    if fix:
        for key in missing:
            if key == "created":
                fallback = next((data[k] for k in CREATED_FALLBACK_KEYS if data.get(k)), None)
                note.set_key("created", str(fallback) if fallback else _created_from_mtime(note.path))
            elif key == "title":
                note.set_key("title", data.get("name") or note.first_heading() or note.path.stem)
            elif key == "type":
                note.set_key("type", infer_note_type(note.rel_path) or "note")
            elif key == "tags":
                note.set_key("tags", [])
    return Issue("missing-keys", f"Missing required keys: {', '.join(missing)}")


def rule_project_aliases(note: _Note, fix: bool, vault: Path) -> Optional[Issue]:
    """Project cards are all named README.md; aliases let Obsidian find them by name."""
    data = note.frontmatter()
    if data is None or data.get("type") != "project" or data.get("aliases"):
        return None
    if fix:
        folder = Path(note.rel_path).parent.name
        names = [str(data.get("title") or ""), folder]
        note.set_key("aliases", list(dict.fromkeys(n for n in names if n and n != "README")))
    return Issue("project-aliases", "Project card has no aliases")


def rule_broken_daily_links(note: _Note, fix: bool, vault: Path) -> Optional[Issue]:
    broken = [m for m in _DAILY_LINK.finditer(note.body) if not (vault / DIR_DAILY / f"{m.group(1)}.md").is_file()]
    if not broken:
        return None
    if fix:
        lines = []
        for line in note.body.split("\n"):
            if line.lstrip().startswith("- **Timeline:**") and _DAILY_LINK.search(line):
                continue
            lines.append(line)
        note.body = "\n".join(lines)
        note.body = _DAILY_LINK.sub(
            lambda m: m.group(0) if (vault / DIR_DAILY / f"{m.group(1)}.md").is_file() else (m.group(2) or m.group(1)),
            note.body,
        )
    return Issue("broken-daily-link", f"{len(broken)} link(s) to missing daily notes")


def _session_title_from_body(body: str, fallback: str) -> str:
    """Rebuild a session title the way the extractor does, from the note's own goal text."""
    for heading in ("## 🎯 Initial User Goal", "## 🔍 Ingestion Overview:"):
        start = body.find(heading)
        if start == -1:
            continue
        rest = body[start + len(heading):].lstrip("\n")
        goal = rest.split("\n\n", 1)[0].split("\n## ", 1)[0]
        goal = HARNESS_NOTICE.sub("", clean_user_prompt(goal)).strip().rstrip(".").rstrip()
        if goal:
            prefix = "Task: " if fallback.startswith("Task:") else ""
            return sanitize_frontmatter_string(prefix + goal, max_length=100)
    return sanitize_frontmatter_string(HARNESS_NOTICE.sub("", fallback), max_length=100)


def rule_noisy_session_title(note: _Note, fix: bool, vault: Path) -> Optional[Issue]:
    """Session titles that still carry text injected by the agent harness."""
    data = note.frontmatter()
    if data is None or data.get("type") != "agent-session-log":
        return None
    title = str(data.get("title") or "")
    noisy_body = bool(HARNESS_NOTICE.search(note.body))
    # A notice cut off by the title length limit ("... The user changed se...")
    # no longer matches the pattern, so a noisy body marks the title as suspect too.
    noisy_title = bool(HARNESS_NOTICE.search(title) or re.search(r"<[A-Z_]{3,}>", title)) or (
        noisy_body and title.endswith("...")
    )
    if not noisy_title and not noisy_body:
        return None
    if fix:
        note.body = HARNESS_NOTICE.sub("", note.body)
    clean = _session_title_from_body(note.body, title) if noisy_title else title
    if fix and noisy_title and clean != title:
        note.set_key("title", clean)
        note.body = re.sub(
            r"^(#\s+(?:📝\s+)?)" + re.escape(title) + r"[ \t]*$",
            lambda m: m.group(1) + clean,
            note.body,
            count=1,
            flags=re.MULTILINE,
        )
    where = "title" if noisy_title else "body"
    return Issue("noisy-title", f"Session {where} carries harness text: {title[:60]}")


_NOISY_LINK_LABEL = re.compile(r"(\[\[[^\]|]+\|[^\]]*?)[ \t]*The user changed se[^\]]*(\]\])", re.IGNORECASE)


def rule_noisy_link_label(note: _Note, fix: bool, vault: Path) -> Optional[Issue]:
    """Session links on project cards that copied a noisy session title as their label."""
    count = len(_NOISY_LINK_LABEL.findall(note.body))
    if not count:
        return None
    if fix:
        note.body = _NOISY_LINK_LABEL.sub(r"\1\2", note.body)
    return Issue("noisy-link-label", f"{count} link label(s) carry harness text")


def rule_legacy_history_suffix(note: _Note, fix: bool, vault: Path) -> Optional[Issue]:
    if _LEGACY_SUFFIX not in note.body:
        return None
    if fix:
        note.body = note.body.replace(_LEGACY_SUFFIX, "")
        note.body = re.sub(r"(\]\])\n```dataview", r"\1\n\n```dataview", note.body)
    return Issue("legacy-suffix", "Stray '(Live Dataview):' text in session history")


RULES: Tuple[Rule, ...] = (
    rule_invalid_yaml,
    rule_missing_frontmatter,
    rule_required_keys,
    rule_project_aliases,
    rule_broken_daily_links,
    rule_noisy_session_title,
    rule_noisy_link_label,
    rule_legacy_history_suffix,
)


def _vault_notes(vault: Path) -> List[Path]:
    skipped = {".obsidian", BRAIN_DATA_DIR, ".git", ".trash"}
    return sorted(
        p for p in vault.rglob("*.md")
        if not any(part in skipped or part.startswith(".archive") for part in p.relative_to(vault).parts)
    )


def lint_vault(vault_path: Path, fix: bool = False) -> List[NoteReport]:
    """Check every note in the vault; with `fix`, rewrite notes whose issues can be repaired."""
    vault = Path(vault_path).resolve()
    reports: List[NoteReport] = []
    for path in _vault_notes(vault):
        rel = path.relative_to(vault).as_posix()
        note = _Note.load(path, rel)
        before = note.render()
        report = NoteReport(rel)
        for rule in RULES:
            issue = rule(note, fix, vault)
            if issue:
                report.issues.append(issue)
        if fix and report.issues and note.render() != before:
            atomic_write_text(path, note.render())
            report.fixed = True
        if report.issues:
            reports.append(report)
    return reports


def summarize(reports: List[NoteReport]) -> Dict[str, int]:
    counts: Dict[str, int] = {}
    for report in reports:
        for issue in report.issues:
            counts[issue.rule] = counts.get(issue.rule, 0) + 1
    return counts
