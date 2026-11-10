---
title: "JWT Refresh Token Rotation"
tags: ["auth", "security"]
---

# JWT Refresh Token Rotation

## Problem
Two browser tabs refreshed the access token at the same moment. Both sent the same refresh token, the second request was rejected as reuse, and the user was logged out.

## Fix
Wrap the rotation in a short Redis lock keyed by the token family. The losing request waits and receives the freshly issued pair instead of failing. Keep a 10 second grace window in which the previous refresh token is still accepted.
