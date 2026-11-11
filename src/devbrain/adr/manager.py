"""Architecture Decision Records (ADR) Manager for DevBrain (30_Decisions/)."""

from datetime import datetime, timezone
import json
from pathlib import Path
import re
from typing import Any, Optional

import yaml

from devbrain.core.constants import DIR_DECISIONS, DIR_PROJECTS
from devbrain.core.fsutil import atomic_write_text
from devbrain.core.sqlite_db import BrainSQLiteStorage


class ADRManager:
    """Manages creation, parsing, listing, and cross-linking of Architecture Decision Records."""

    def __init__(self, vault_path: Path, sqlite_storage: Optional[BrainSQLiteStorage] = None):
        self.vault_path = Path(vault_path).resolve()
        self.decisions_dir = self.vault_path / DIR_DECISIONS
        self.decisions_dir.mkdir(parents=True, exist_ok=True)
        self.sqlite = sqlite_storage or BrainSQLiteStorage(self.vault_path)

    def _slugify(self, text: str) -> str:
        """Convert a title to a clean URL/filename slug."""
        text = text.lower().strip()
        text = re.sub(r"[^\w\s-]", "", text)
        return re.sub(r"[-\s]+", "-", text)

    def _get_next_adr_id(self) -> str:
        """Calculate the next sequential ADR number (e.g. ADR-001, ADR-002)."""
        existing_files = list(self.decisions_dir.glob("ADR-*.md"))
        max_num = 0
        for f in existing_files:
            match = re.match(r"ADR-(\d+)", f.name, re.IGNORECASE)
            if match:
                num = int(match.group(1))
                if num > max_num:
                    max_num = num
        return f"ADR-{max_num + 1:03d}"

    def create_decision(
        self,
        title: str,
        project: Optional[str] = None,
        context: str = "",
        decision: str = "",
        consequences: str = "",
        alternatives: str = "",
        status: str = "accepted",
        date_str: Optional[str] = None,
    ) -> dict[str, Any]:
        """Create a new ADR markdown file and index it in SQLite."""
        adr_id = self._get_next_adr_id()
        slug = self._slugify(title)
        filename = f"{adr_id}-{slug}.md"
        file_path = self.decisions_dir / filename
        date_val = date_str or datetime.now(timezone.utc).strftime("%Y-%m-%d")

        frontmatter = {
            "type": "adr",
            "id": adr_id,
            "title": title,
            "project": project or "Global",
            "status": status.lower(),
            "date": date_val,
            "created": datetime.now(timezone.utc).isoformat(),
            "tags": ["adr", "architecture-decision", self._slugify(project or "global")],
        }

        content = f"""---
{yaml.dump(frontmatter, sort_keys=False).strip()}
---

# {adr_id}: {title}

| Metadata | Value |
| :--- | :--- |
| **Status** | `{status.lower()}` |
| **Project** | {f'[[{project}]]' if project else 'Global'} |
| **Date** | {date_val} |

---

## 1. Context & Problem Statement
{context.strip() if context else 'Belum ada konteks tambahan yang dicatat.'}

---

## 2. Decision Outcome
{decision.strip() if decision else 'Keputusan arsitektur belum dideskripsikan secara spesifik.'}

---

## 3. Alternatives Considered
{alternatives.strip() if alternatives else '- Tidak ada alternatif lain yang dievaluasi.'}

---

## 4. Consequences & Trade-offs
### Positif
- Solusi terstandarisasi dan menjaga konsistensi arsitektur.

### Negatif / Trade-offs
{consequences.strip() if consequences else '- Tidak ada trade-off signifikan yang dicatat.'}
"""
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)

        summary = f"{title}. Context: {context[:100]}... Decision: {decision[:100]}..." if context or decision else title
        self.sqlite.upsert_decision(
            id=adr_id,
            title=title,
            project=project,
            status=status.lower(),
            file_path=str(file_path),
            date=date_val,
            summary=summary,
        )

        if project:
            self.link_to_project_card(adr_id, project)

        return {
            "id": adr_id,
            "title": title,
            "project": project,
            "status": status.lower(),
            "file_path": str(file_path),
            "date": date_val,
        }

    def list_decisions(
        self,
        project: Optional[str] = None,
        status: Optional[str] = "accepted",
    ) -> list[dict[str, Any]]:
        """List decisions from SQLite cache, falling back to disk scanning if needed."""
        db_results = self.sqlite.get_decisions(project=project, status=status)
        if db_results:
            return db_results

        # Fallback to scanning disk directly
        results = []
        for file in sorted(self.decisions_dir.glob("ADR-*.md")):
            parsed = self.parse_adr_file(file)
            if parsed:
                if project and parsed.get("project") and parsed["project"].lower() != project.lower():
                    continue
                if status and parsed.get("status") and parsed["status"].lower() != status.lower():
                    continue
                results.append(parsed)
        return results

    def find_decision_file(self, adr_id: str) -> Optional[Path]:
        """Locate an ADR note by its id (e.g. ADR-001), ignoring case."""
        matches = sorted(self.decisions_dir.glob(f"{adr_id.upper()}-*.md")) or sorted(
            self.decisions_dir.glob(f"{adr_id.upper()}.md")
        )
        return matches[0] if matches else None

    def supersede_decision(self, old_id: str, new_id: str) -> dict[str, Any]:
        """Mark one ADR as replaced by another and link the two notes.

        The old note keeps its content; only its status changes, so the history
        of why the earlier choice was made stays readable.
        """
        old_id, new_id = old_id.upper(), new_id.upper()
        if old_id == new_id:
            raise ValueError("An ADR cannot supersede itself.")
        old_file, new_file = self.find_decision_file(old_id), self.find_decision_file(new_id)
        if old_file is None or new_file is None:
            missing = old_id if old_file is None else new_id
            raise FileNotFoundError(f"No ADR note found for {missing} in {DIR_DECISIONS}/.")

        self._set_frontmatter(old_file, {"status": "superseded", "superseded_by": new_id})
        self._append_note_line(old_file, f"> **Superseded by** [[{new_file.stem}|{new_id}]].")
        self._set_frontmatter(new_file, {"supersedes": old_id})
        self._append_note_line(new_file, f"> **Supersedes** [[{old_file.stem}|{old_id}]].")

        for adr_file, status, superseded_by in ((old_file, "superseded", new_id), (new_file, None, None)):
            parsed = self.parse_adr_file(adr_file) or {}
            self.sqlite.upsert_decision(
                id=str(parsed.get("id") or re.match(r"(ADR-\d+)", adr_file.stem, re.IGNORECASE).group(1).upper()),
                title=str(parsed.get("title") or adr_file.stem),
                file_path=str(adr_file),
                date=str(parsed.get("date") or parsed.get("created") or ""),
                project=None if parsed.get("project") in (None, "Global") else parsed.get("project"),
                status=status or str(parsed.get("status") or "accepted"),
                superseded_by=superseded_by,
            )
        return {"old": old_id, "new": new_id, "old_file": str(old_file), "new_file": str(new_file)}

    def _set_frontmatter(self, file_path: Path, values: dict[str, Any]) -> None:
        """Set frontmatter keys in an ADR note, leaving its other lines untouched."""
        raw = file_path.read_text(encoding="utf-8")
        parts = raw.split("---", 2)
        if not raw.startswith("---") or len(parts) < 3:
            raise ValueError(f"{file_path.name} has no frontmatter.")
        lines = parts[1].strip("\n").split("\n")
        for key, value in values.items():
            line = f"{key}: {json.dumps(value, ensure_ascii=False)}"
            index = next((i for i, l in enumerate(lines) if re.match(rf"^{key}:", l)), None)
            if index is None:
                lines.append(line)
            else:
                lines[index] = line
        atomic_write_text(file_path, "---\n" + "\n".join(lines) + "\n---" + parts[2])

    def _append_note_line(self, file_path: Path, line: str) -> None:
        """Add a line under the title, once."""
        raw = file_path.read_text(encoding="utf-8")
        if line in raw:
            return
        heading = re.search(r"^# .*$", raw, re.MULTILINE)
        if heading:
            raw = raw[: heading.end()] + f"\n\n{line}" + raw[heading.end():]
        else:
            raw = raw.rstrip() + f"\n\n{line}\n"
        atomic_write_text(file_path, raw)

    def parse_adr_file(self, file_path: Path) -> Optional[dict[str, Any]]:
        """Parse frontmatter and content from an ADR file."""
        if not file_path.is_file():
            return None
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                raw = f.read()

            if not raw.startswith("---"):
                return None

            parts = raw.split("---", 2)
            if len(parts) < 3:
                return None

            data = yaml.safe_load(parts[1]) or {}
            data["file_path"] = str(file_path)
            data["body"] = parts[2].strip()
            return data
        except Exception:
            return None

    def link_to_project_card(self, adr_id: str, project_name: str) -> bool:
        """Inject ADR wikilink into project note in 10_Projects/."""
        project_dir = self.vault_path / DIR_PROJECTS / project_name
        project_card = project_dir / "README.md"
        if not project_card.is_file():
            # Try finding by name directly in 10_Projects/
            project_card = self.vault_path / DIR_PROJECTS / f"{project_name}.md"

        if not project_card.is_file():
            return False

        try:
            with open(project_card, "r", encoding="utf-8") as f:
                content = f.read()

            adr_link = f"- [[{adr_id}]]"
            if adr_id in content:
                return True  # Already linked

            if "## Decisions (ADR)" in content:
                content = content.replace("## Decisions (ADR)", f"## Decisions (ADR)\n{adr_link}")
            elif "## 5. Architectural Decisions" in content:
                content = content.replace("## 5. Architectural Decisions", f"## 5. Architectural Decisions\n{adr_link}")
            else:
                content += f"\n\n## Decisions (ADR)\n{adr_link}\n"

            with open(project_card, "w", encoding="utf-8") as f:
                f.write(content)
            return True
        except Exception:
            return False
