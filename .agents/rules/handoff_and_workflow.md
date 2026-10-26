---
trigger: always_on
description: Mandatory rules for handoff and dual-AI collaboration between Antigravity and Codex
---

# Dual-AI Collaboration & Handoff Rules

1. Before starting any task in `broadcast playroom 3`, always read `HANDOFF.md` first, followed by the latest entries in `WORKLOG.md`.
2. Cross-check documentation against actual Git status and codebase. If discrepancies exist, update the docs immediately.
3. Keep `HANDOFF.md` updated as the current snapshot of truth.
4. Keep `WORKLOG.md` append-only with timestamp, agent name, changed files, reasons, and verification results.
5. Update docs after each subtask, before task switches, and before stopping. Do not wait for quota exhaustion.
6. Clearly distinguish between "Completed & Verified" (tested with proof), "Completed but Unverified", and "Proposed / Backlog".
7. When pausing or handing off, document the exact stopping point, exact steps to resume, and required commands without secrets.
8. Only one agent modifies code at a time.
9. Always follow Zero GPU Lockup guidelines and polite Thai tone ending with "ครับ".
