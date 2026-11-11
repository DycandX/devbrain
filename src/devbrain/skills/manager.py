"""Agent skills shared through the vault: list, load, save, patch, approve.

A skill is a folder with a SKILL.md in the agentskills.io format (frontmatter
`name` and `description`, Markdown body, optional `references/` files). Active
skills live in 00_System/Agent_Skills/, which Hermes and other agents also read.

Agents may create skills and edit the ones agents created. Skills written by
hand, or added from elsewhere, are read-only to agents, and any skill can be
locked. Writes pass the content guard and are recorded in the skill ledger.
With write approval on, new and edited skills wait in .brain_data/pending_skills/
and only reach the shared folder once approved.
"""

import json
from pathlib import Path
import re
import shutil
from typing import Any, Dict, List, Optional

from devbrain.core.config import BrainConfig, SkillSettings, load_config
from devbrain.core.constants import BRAIN_DATA_DIR, CONFIG_FILENAME, DIR_AGENT_SKILLS
from devbrain.core.fsutil import atomic_write_text
from devbrain.core.sqlite_db import BrainSQLiteStorage
from devbrain.engine.parser import parse_frontmatter
from devbrain.memory.guard import check_skill_content

# agentskills.io: lowercase letters, digits, and hyphens; at most 64 characters.
# Enforced for skills agents create.
SKILL_NAME = re.compile(r"^[a-z0-9](?:[a-z0-9-]{0,62}[a-z0-9])?$")
# Any existing skill folder can be loaded, as long as the name is a plain folder name.
READABLE_SKILL_NAME = re.compile(r"^[a-z0-9][a-z0-9._-]*$")
MAX_DESCRIPTION_CHARS = 1024
MAX_SKILL_CHARS = 24_000
PENDING_DIR = Path(BRAIN_DATA_DIR) / "pending_skills"


class SkillRejected(ValueError):
    """A skill write refused by validation or the content guard."""


class SkillManager:
    def __init__(
        self,
        vault_path: Path,
        sqlite_storage: Optional[BrainSQLiteStorage] = None,
        config: Optional[BrainConfig] = None,
    ):
        self.vault_path = Path(vault_path).resolve()
        if config is None and (self.vault_path / CONFIG_FILENAME).is_file():
            config = load_config(self.vault_path)
        self.settings: SkillSettings = config.skills if config else SkillSettings()
        self.extra_roots = [Path(r).resolve() for r in (config.custom_skill_roots if config else [])]
        self.sqlite = sqlite_storage or BrainSQLiteStorage(self.vault_path)
        self.skills_dir = self.vault_path / DIR_AGENT_SKILLS
        self.pending_dir = self.vault_path / PENDING_DIR

    # --- Read --------------------------------------------------------------

    def _roots(self) -> List[Path]:
        roots = [self.skills_dir]
        for root in self.extra_roots:
            roots += [root, root / "skills"]
        return roots

    def find(self, name: str) -> Optional[Path]:
        """Folder of an active skill, searching the vault first."""
        if not READABLE_SKILL_NAME.match(name) or ".." in name:
            return None
        for root in self._roots():
            folder = root / name
            if (folder / "SKILL.md").is_file():
                return folder
        return None

    def catalog(self) -> List[Dict[str, str]]:
        """Every active skill with its description (the cheapest level of disclosure)."""
        seen: Dict[str, Dict[str, str]] = {}
        for root in self._roots():
            if not root.is_dir():
                continue
            for skill_file in sorted(root.glob("*/SKILL.md")):
                if skill_file.parent.name.startswith(".") or skill_file.parent.name in seen:
                    continue
                meta, _ = parse_frontmatter(skill_file.read_text(encoding="utf-8", errors="replace"))
                seen[skill_file.parent.name] = {
                    "name": skill_file.parent.name,
                    "description": " ".join(str(meta.get("description") or "").split()),
                    "files": ", ".join(
                        p.relative_to(skill_file.parent).as_posix()
                        for p in sorted(skill_file.parent.rglob("*"))
                        if p.is_file() and p.name != "SKILL.md"
                    ),
                }
        return list(seen.values())

    def load(self, name: str, path: Optional[str] = None) -> str:
        """SKILL.md of a skill, or one of its files. Raises KeyError when absent."""
        folder = self.find(name)
        if folder is None:
            raise KeyError(name)
        target = (folder / (path or "SKILL.md")).resolve()
        if not target.is_relative_to(folder.resolve()) or not target.is_file():
            raise KeyError(f"{name}/{path}")
        if path is None:
            self.sqlite.upsert_skill(name)
            self.sqlite.bump_skill_counter(name, "view_count")
        return target.read_text(encoding="utf-8", errors="replace")

    # --- Write -------------------------------------------------------------

    def save(self, name: str, description: str, body: str, source: Optional[str] = None) -> Dict[str, Any]:
        """Create a skill, or replace one that agents own. Returns {"name", "status", "warnings"}."""
        name = name.strip().lower()
        description = " ".join(description.split())
        if not SKILL_NAME.match(name):
            raise SkillRejected("Skill name must be lowercase letters, digits, and hyphens (at most 64 characters).")
        if not description or len(description) > MAX_DESCRIPTION_CHARS:
            raise SkillRejected(f"Description must be 1 to {MAX_DESCRIPTION_CHARS} characters; say what it does and when to use it.")
        if not body.strip():
            raise SkillRejected("Skill body is empty.")

        existing = self.find(name)
        if existing is not None:
            self._require_agent_owned(name)

        content = (
            f"---\nname: {json.dumps(name)}\ndescription: {json.dumps(description, ensure_ascii=False)}\n---\n\n"
            + body.strip() + "\n"
        )
        return self._write(name, content, "updated" if existing else "created", source)

    def patch(self, name: str, old_text: str, new_text: str, source: Optional[str] = None) -> Dict[str, Any]:
        """Replace one exact span of an agent-owned skill's SKILL.md."""
        folder = self.find(name)
        if folder is None:
            raise KeyError(name)
        self._require_agent_owned(name)
        current = (folder / "SKILL.md").read_text(encoding="utf-8")
        count = current.count(old_text) if old_text else 0
        if count != 1:
            raise SkillRejected(f"The text to replace must occur exactly once in SKILL.md; it occurs {count} time(s).")
        result = self._write(name, current.replace(old_text, new_text, 1), "patched", source)
        if result["status"] == "active":
            self.sqlite.bump_skill_counter(name, "patch_count")
        return result

    def _write(self, name: str, content: str, action: str, source: Optional[str]) -> Dict[str, Any]:
        if len(content) > MAX_SKILL_CHARS:
            raise SkillRejected(f"SKILL.md would be {len(content)} characters; keep it under {MAX_SKILL_CHARS} and move detail to references/.")
        refusals, warnings = check_skill_content(content)
        if refusals or (warnings and not self.settings.write_approval):
            reasons = refusals + [f"{w} (allowed only with skill write approval on)" for w in warnings if not refusals]
            self.sqlite.record_skill_event("blocked", name, source, "; ".join(reasons))
            raise SkillRejected("Refused: " + "; ".join(reasons))

        if self.settings.write_approval:
            atomic_write_text(self.pending_dir / name / "SKILL.md", content)
            fields: Dict[str, Any] = {"created_by": self._owner(name, source), "source": source}
            # An edit to an active skill waits beside it; the active version keeps serving
            if self.find(name) is None:
                fields["status"] = "pending"
            self.sqlite.upsert_skill(name, **fields)
            self.sqlite.record_skill_event(f"{action}-pending", name, source, "; ".join(warnings))
            return {"name": name, "status": "pending", "warnings": warnings}

        atomic_write_text(self.skills_dir / name / "SKILL.md", content)
        self.sqlite.upsert_skill(name, status="active", created_by=self._owner(name, source), source=source)
        self.sqlite.record_skill_event(action, name, source)
        return {"name": name, "status": "active", "warnings": warnings}

    def _owner(self, name: str, source: Optional[str]) -> str:
        row = self.sqlite.get_skill(name)
        return (row or {}).get("created_by") or source or "agent"

    def _require_agent_owned(self, name: str) -> None:
        row = self.sqlite.get_skill(name)
        if row and row.get("locked"):
            raise SkillRejected(f"Skill '{name}' is locked; agents cannot change it.")
        if not row or not row.get("created_by"):
            raise SkillRejected(f"Skill '{name}' was not created by an agent; agents cannot change it.")

    # --- Review ------------------------------------------------------------

    def pending(self) -> List[Dict[str, Any]]:
        items = []
        for skill_file in sorted(self.pending_dir.glob("*/SKILL.md")) if self.pending_dir.is_dir() else []:
            name = skill_file.parent.name
            text = skill_file.read_text(encoding="utf-8")
            _, warnings = check_skill_content(text)
            items.append({"name": name, "replaces_active": self.find(name) is not None, "warnings": warnings, "content": text})
        return items

    def approve(self, name: str) -> None:
        source = self.pending_dir / name / "SKILL.md"
        if not source.is_file():
            raise KeyError(f"No pending skill named {name}.")
        atomic_write_text(self.skills_dir / name / "SKILL.md", source.read_text(encoding="utf-8"))
        shutil.rmtree(source.parent)
        self.sqlite.upsert_skill(name, status="active")
        self.sqlite.record_skill_event("approved", name, "owner")

    def reject(self, name: str) -> None:
        folder = self.pending_dir / name
        if not folder.is_dir():
            raise KeyError(f"No pending skill named {name}.")
        shutil.rmtree(folder)
        if self.find(name) is None:
            self.sqlite.upsert_skill(name, status="rejected")
        self.sqlite.record_skill_event("rejected", name, "owner")

    def lock(self, name: str, locked: bool = True) -> None:
        if self.find(name) is None:
            raise KeyError(name)
        self.sqlite.upsert_skill(name, locked=int(locked))
        self.sqlite.record_skill_event("locked" if locked else "unlocked", name, "owner")

    def ledger(self, name: Optional[str] = None, limit: int = 50) -> List[Dict[str, Any]]:
        return self.sqlite.get_skill_ledger(name, limit)
