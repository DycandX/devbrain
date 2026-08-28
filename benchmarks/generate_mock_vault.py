"""Synthetic Markdown Vault Generator for Benchmarking devbrain."""

import os
from pathlib import Path
import random

TOPICS = [
    ("Architecture", ["microservices", "clean-arch", "event-driven", "cqrs", "hexagonal"]),
    ("Databases", ["postgresql", "qdrant", "redis", "mongodb", "neo4j", "sqlite"]),
    ("AI_Engineering", ["fastmcp", "fastembed", "rag", "langchain", "embeddings", "agents"]),
    ("DevOps", ["docker", "tailscale", "syncthing", "github-actions", "kubernetes"]),
    ("Security", ["jwt-auth", "secret-redaction", "oauth2", "encryption", "tls"]),
]

TEMPLATES = [
    """---
title: "{title}"
category: "{category}"
tags: {tags}
created: "2026-08-29"
---

# {title}

## Overview
This document outlines the operational and technical principles regarding {topic} in the context of modern distributed systems.

## Key Implementation Patterns
When designing software with {topic}, developers must adhere to strict modularity:
- Always enforce single-responsibility boundaries.
- Utilize deterministic schema contracts.
- Cache high-frequency query results.

### Code Sample
```python
def process_{topic_slug}(payload: dict) -> bool:
    # Validate payload for {topic}
    if not payload.get("active"):
        return False
    return True
```

## Troubleshooting & Best Practices
1. Ensure connection pools are appropriately sized.
2. Monitor memory footprint under sustained loads.
3. Keep logs structured and free of sensitive credentials.
""",
]


def generate_mock_vault(target_dir: Path, num_notes: int = 1000) -> int:
    """Generate num_notes synthetic Markdown files inside target_dir."""
    target_dir.mkdir(parents=True, exist_ok=True)

    print(f"Generating {num_notes} benchmark notes in: {target_dir} ...")
    count = 0

    for i in range(num_notes):
        category, topics = random.choice(TOPICS)
        topic = random.choice(topics)
        topic_slug = topic.replace("-", "_").lower()
        title = f"{topic.replace('-', ' ').title()} Technical Note #{i+1}"
        tags = random.sample(topics, min(3, len(topics)))
        tags_repr = "[" + ", ".join(f'"{t}"' for t in tags) + "]"

        folder_name = f"20_Knowledge/{category}"
        folder_path = target_dir / folder_name
        folder_path.mkdir(parents=True, exist_ok=True)

        filename = f"note_{i+1:04d}_{topic_slug}.md"
        file_path = folder_path / filename

        template = TEMPLATES[0]
        content = template.format(
            title=title,
            category=category,
            tags=tags_repr,
            topic=topic,
            topic_slug=topic_slug,
        )

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)

        count += 1

    print(f"Generated {count} notes successfully.")
    return count


if __name__ == "__main__":
    vault_path = Path("./mock_benchmark_vault").resolve()
    generate_mock_vault(vault_path, num_notes=1000)
