---
title: "ADR-001: SQLite over Qdrant for local storage"
tags: ["adr", "storage"]
---

# ADR-001: SQLite over Qdrant for local storage

## Context
The tool must run on a laptop with no background services. A dedicated vector server adds a container and a port to manage.

## Decision
Store vectors and metadata in an embedded SQLite file. Brute-force similarity is fast enough below one hundred thousand chunks.

## Consequences
Zero setup for new users. Revisit if the corpus grows by two orders of magnitude.
