---
title: "Tailscale and Syncthing Setup"
tags: ["network", "sync"]
---

# Tailscale and Syncthing Setup

## Network
Every device joins the same private mesh, so the home server is reachable by name from anywhere without port forwarding.

## File Sync
Syncthing replicates the notes folder between laptop and server over that mesh. Exclude machine-generated index folders with an ignore file to avoid conflicts.
