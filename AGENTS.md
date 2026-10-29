# AGENTS.md — Protocol for AI Pair Programmers (Antigravity & Codex)

This project is actively maintained and developed by two AI systems: **Antigravity** and **Codex**.  
All AI agents reading or modifying this repository must follow the protocol below.

---

## 🚨 MANDATORY ENTRY POINT FOR ANY AI STARTING WORK
When you start a session or pick up a task in this project, **you must read `HANDOFF.md` first**:
1. Open and read `HANDOFF.md` to get the current goal, architecture map, completed features, pending tasks, and test commands.
2. Read the latest entries of `WORKLOG.md` to see recent changes and context.
3. Run `git status` and check actual code files to verify the current state against `HANDOFF.md`. If discrepancies exist, report them and update the documentation to match reality.

---

## The 7 Co-working Rules:
1. **`HANDOFF.md` is the Single Source of Current Truth**: Keep it updated with current goals, completed & verified items, unverified items, backlog, blockers, next steps, and Git commit hash.
2. **`WORKLOG.md` is Append-Only**: Append chronological change logs with timestamp, agent name (Antigravity/Codex), modified files, reasoning, and test proof.
3. **Verify Before Coding**: Cross-check `HANDOFF.md` with Git status and real code on disk before making any changes.
4. **Update Continuously**: Update docs after every subtask, before switching focus, and before yielding turns. Do not delay until quota runs out.
5. **Strict Three-Tier Categorization**:
   - `Completed & Verified`: Must be backed by real test execution.
   - `Completed but Unverified`: Implemented but not yet tested.
   - `Proposed / Backlog`: Planned or suggested, not yet implemented.
6. **Detailed Handoff Points**: Explicitly state stopping point, resumption steps, and exact terminal commands. Never log secrets or tokens.
7. **Single Active Modifier**: One AI modifies code at a time to prevent conflicts.

## Mandatory completion reminder — applies to every AI
Before reporting work finished or handing it to another AI, update **both `HANDOFF.md` and `WORKLOG.md`**. This is an explicit user requirement, including small UI/text changes. Record what changed, actual verification results, remaining work and how to resume. Keep WORKLOG append-only; never claim an unrun test passed. Updating only one file is incomplete. Do not wait for the user to remind you.

---

## Quality & Performance Constraints:
- **Zero Arbitrary Additions**: Never add unrequested sound effects, unprompted UI animations, or arbitrary workflows. Mirror `broadcast playroom dev` behavior 100%.
- **Zero GPU Lockup**: No full-screen `backdrop-filter: blur(...)`. Use CSS containment `contain: layout style paint; isolation: isolate;`. Settle to 0% GPU idle when viewing.
- **Standby Transparency**: All overlays (Ask, Giveaway, Randomizer, Replie) must be 100% transparent and cleanly dismissed when not actively in use.
- **Tone**: Polite, friendly Thai ending with "ครับ". Never use the "ใบเตย" persona.
- **No Parenthetical Explanations / Multilingual Descriptions**: Never append parenthetical descriptions or explanations after option/button/theme names (e.g. omit `(...)`, keep clean concise names only without appending Thai/multilingual descriptions in parentheses).
