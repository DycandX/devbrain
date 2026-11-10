---
title: "Git Rebase Workflow"
tags: ["git"]
---

# Git Rebase Workflow

## Rule
Rebase a feature branch onto main before opening a pull request so history stays linear. Never rebase a branch that someone else has pulled.

## Recovering
If a rebase goes wrong, `git reflog` lists every previous position of HEAD. Reset to the entry before the rebase started.
