---
title: "Docker Multi-Stage Builds"
tags: ["docker", "devops"]
---

# Docker Multi-Stage Builds

## Why
The production image was 1.4 GB because it shipped compilers and dev dependencies.

## How
Use one stage to install dependencies and compile, then copy only the built artifacts into a slim runtime stage. Pin the base image by digest and run as a non-root user. The final image shrank to 180 MB and cold starts got faster.
