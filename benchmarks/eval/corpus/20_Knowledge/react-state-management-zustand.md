---
title: "React State Management with Zustand"
tags: ["react", "frontend"]
---

# React State Management with Zustand

## Decision
Replaced a large context provider with a small store. Components subscribe to slices, so unrelated updates no longer re-render the whole tree.

## Notes
Keep server data in a query cache and only client-only state in the store. Persist the cart slice to local storage.
