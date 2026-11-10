"""Core constants for devbrain matching docs/brainstorming/07 taxonomy."""


# File & Directory Names
CONFIG_FILENAME = ".brainrc.json"
BRAIN_DATA_DIR = ".brain_data"
BRAIN_IGNORE_FILENAME = ".brainignore"

# Standard Vault Hierarchy (07_Taksonomi_Vault)
DIR_SYSTEM = "00_System"
DIR_SYSTEM_RULES = "00_System/rules"
DIR_SYSTEM_PERSONAS = "00_System/personas"
DIR_AGENT_SKILLS = "00_System/Agent_Skills"
DIR_MEMORIES = "00_System/Memories"

DIR_PROJECTS = "10_Projects"

DIR_KNOWLEDGE = "20_Knowledge"
DIR_KNOWLEDGE_ARCH = "20_Knowledge/Architecture_Patterns"
DIR_KNOWLEDGE_BUGS = "20_Knowledge/Bug_Solutions"
DIR_KNOWLEDGE_TOOLS = "20_Knowledge/Frameworks_Tools"
DIR_KNOWLEDGE_SECURITY = "20_Knowledge/Security_Checklists"

DIR_DECISIONS = "30_Decisions"

DIR_INBOX = "90_Agent_Inbox"
DIR_INBOX_ANTIGRAVITY = "90_Agent_Inbox/antigravity"
DIR_INBOX_CLAUDE = "90_Agent_Inbox/claude-code"
DIR_INBOX_HERMES = "90_Agent_Inbox/hermes"
DIR_INBOX_MANUAL = "90_Agent_Inbox/manual_review"

DIR_DAILY = "99_Daily"

STANDARD_DIRS = [
    DIR_SYSTEM,
    DIR_SYSTEM_RULES,
    DIR_SYSTEM_PERSONAS,
    DIR_AGENT_SKILLS,
    DIR_MEMORIES,
    DIR_PROJECTS,
    DIR_KNOWLEDGE,
    DIR_KNOWLEDGE_ARCH,
    DIR_KNOWLEDGE_BUGS,
    DIR_KNOWLEDGE_TOOLS,
    DIR_KNOWLEDGE_SECURITY,
    DIR_DECISIONS,
    DIR_INBOX,
    DIR_INBOX_ANTIGRAVITY,
    DIR_INBOX_CLAUDE,
    DIR_INBOX_HERMES,
    DIR_INBOX_MANUAL,
    DIR_DAILY,
]

# Default Embedding Models
DEFAULT_EMBEDDING_PROVIDER = "fastembed"
# Multilingual (about 50 languages, 384 dimensions) so Indonesian and English notes
# and queries land in the same vector space.
DEFAULT_EMBEDDING_MODEL = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"

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

# Minimum cosine similarity for a chunk to count as a semantic match, per embedding
# model. Measured with benchmarks/eval_retrieval.py; models not listed get no floor.
EMBEDDING_MODEL_MIN_SIMILARITY = {
    "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2": 0.38,
}
