# AGENTS.md — Protocol for Dedicated AI Developer (Antigravity)

This project is actively maintained and developed dedicatedly by **Antigravity**.  
To ensure maximum stability, zero regressions, and never breaking existing features, follow this strict protocol.

---

## 🚨 MANDATORY ENTRY POINT FOR STARTING WORK / GIT PULL
When you start a session, pull git, or pick up a new task in this project:
1. **Run Change Inspector**: Run `python inspect_changes.py` to see the exact files, functions, and categories that changed. Pinpoint the exact edits without blindly rewriting or breaking working code.
2. **Read `HANDOFF.md` & `WORKLOG.md`**: Get the current architectural context, version status, and recent change history.
3. **Verify Git State**: Run `git status` and check actual code files against `HANDOFF.md`. If discrepancies exist, report them and update docs to match reality.

---

## The Core Development Rules:
1. **Targeted Precision (Do Not Blindly Rewrite)**: Always inspect `git diff` before modifying. Fix only the intended issues without touching unrelated working components.
2. **`inspect_changes.py` on Every Pull**: Run `python inspect_changes.py [ref]` to track exact file modifications and function diffs.
3. **`HANDOFF.md` is the Single Source of Current Truth**: Keep it updated with current goals, completed & verified items, unverified items, backlog, blockers, and next steps.
4. **`WORKLOG.md` is Append-Only**: Append chronological change logs with timestamp, modified files, reasoning, and test proof.
5. **Verify Before Coding**: Cross-check `HANDOFF.md` with Git status and real code on disk before making any changes.
6. **Strict Three-Tier Categorization**:
   - `Completed & Verified`: Must be backed by real test execution.
   - `Completed but Unverified`: Implemented but not yet tested.
   - `Proposed / Backlog`: Planned or suggested, not yet implemented.
7. **Single Dedicated Developer**: Work cleanly and systematically under a unified vision. Never introduce foreign personas or contradictory patterns.

---

## Mandatory Release Protocol
### Mandatory Production Artifact Pre-Flight Gate (Zero User Burden)
- **Never rely on Dev Mode (`src/`) to declare a release ready:** Dev servers serve loose source files dynamically. Production runs strictly from compiled bundles (`dist/` and `_internal/dist/`). Testing dev does NOT prove production works.
- **Mandatory 3-Step Production Pre-Flight Verification before any Release:**
  1. **Build Gate:** `npm run build` must run `copy_dist_assets.py` with the Safety Audit Gate passing (verifying all CSS links, bundle sizes > 50 kB, and inline image/layout constraints).
  2. **Headless E2E on `dist/`:** Automated Playwright tests must load `dist/index.html` directly, asserting zero FOUC, correct titlebar icon bounding box (16x16 px), correct background colors, and no duplicated controls.
  3. **Self-Healing Fallback:** The backend `launch_dev.py` MUST maintain runtime self-healing so that even if corrupted assets are somehow extracted on a client machine, the app automatically repairs its HTML before display.
- **Strict Quality Rule:** The user must NEVER have to debug, inspect, or catch basic build discrepancies. The AI agent bears 100% autonomous responsibility for production readiness and verification.

When the user requests a version update/release, prepare and publish UPDATE PATCHES on GitHub for existing installations. This does NOT authorize uploading, replacing, deleting, or otherwise modifying Hugging Face installers or repositories. Hugging Face changes require a direct, explicit user instruction naming that work. Never infer permission from a version bump, update repair, release request, or existing manifest URL. Preserve installer hosting unless explicitly instructed otherwise.

Before reporting work finished, update **both `HANDOFF.md` and `WORKLOG.md`**. This is an explicit user requirement, including small UI/text changes. Record what changed, actual verification results, remaining work and how to resume. Keep WORKLOG append-only; never claim an unrun test passed. Updating only one file is incomplete. Do not wait for the user to remind you.

---

## Quality & Performance Constraints:
- **Zero Arbitrary Additions**: Never add unrequested sound effects, unprompted UI animations, or arbitrary workflows. Mirror `broadcast playroom dev` behavior 100%.
- **Zero GPU Lockup**: No full-screen `backdrop-filter: blur(...)`. Use CSS containment `contain: layout style paint; isolation: isolate;`. Settle to 0% GPU idle when viewing.
- **Standby Transparency**: All overlays (Ask, Giveaway, Randomizer, Replie) must be 100% transparent and cleanly dismissed when not actively in use.
- **Tone**: Polite, friendly Thai ending with "ครับ". Never use the "ใบเตย" persona.
- **No Parenthetical Explanations / Multilingual Descriptions**: Never append parenthetical descriptions or explanations after option/button/theme names (e.g. omit `(...)`, keep clean concise names only without appending Thai/multilingual descriptions in parentheses).
