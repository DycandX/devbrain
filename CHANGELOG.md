# Changelog

All notable changes to the `devbrain` project are documented here and in [`docs/changelog/`](docs/changelog/_index.md).

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [0.1.0-alpha] - 2026-08-29

### 🚀 Added
- **Project Structure & Packaging:** Configured `pyproject.toml` (Hatchling build backend), package structure `src/devbrain/`, and `.gitignore`.
- **Configuration Manager (`.brainrc.json`):** Pydantic schema validation, auto-lookup via `find_config()`, and safe I/O handlers.
- **Full 07 Taxonomy Vault Scaffolder:** Non-destructive initialization generating `00_System/`, `10_Projects/`, `20_Knowledge/`, `30_Decisions/`, `90_Agent_Inbox/`, `99_Daily/`, and `.brainignore`.
- **CLI Commands (`Typer` & `Rich`):** Interactive `devbrain init` wizard and `devbrain status` health check table.
- **English Localization:** Translated all CLI outputs, interactive prompts, and starter Markdown notes to standard English.
- **Automated Tests:** 8 passing `pytest` unit & integration tests covering CLI, config, and scaffolding.

For complete release details, see [docs/changelog/v0.1.0-alpha.md](docs/changelog/v0.1.0-alpha.md).
