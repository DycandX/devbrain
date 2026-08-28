"""Core constants for devbrain."""

from pathlib import Path

# File & Directory Names
CONFIG_FILENAME = ".brainrc.json"
BRAIN_DATA_DIR = ".brain_data"
BRAIN_IGNORE_FILENAME = ".brainignore"

# Standard Vault Hierarchy (Hybrid PARA)
DIR_SYSTEM = "00_System"
DIR_AGENT_SKILLS = "00_System/Agent_Skills"
DIR_PROJECTS = "10_Projects"
DIR_KNOWLEDGE = "20_Knowledge"
DIR_INBOX = "90_Agent_Inbox"

STANDARD_DIRS = [
    DIR_SYSTEM,
    DIR_AGENT_SKILLS,
    DIR_PROJECTS,
    DIR_KNOWLEDGE,
    DIR_INBOX,
]

# Default Embedding Models
DEFAULT_EMBEDDING_PROVIDER = "fastembed"
DEFAULT_EMBEDDING_MODEL = "BAAI/bge-small-en-v1.5"

# Ignored Patterns by Default
DEFAULT_IGNORED_PATTERNS = [
    ".brain_data",
    ".obsidian",
    ".git",
    ".stversions",
    ".stfolder",
    "*.tmp",
    "*.temp",
    ".DS_Store",
    "Thumbs.db",
]
