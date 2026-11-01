# Update AGENTS.md with Mandatory Production Artifact Pre-Flight Gate
with open("AGENTS.md", "r", encoding="utf-8") as f:
    agents_md = f.read()

rule_text = """
### Mandatory Production Artifact Pre-Flight Gate (Zero User Burden)
- **Never rely on Dev Mode (`src/`) to declare a release ready:** Dev servers serve loose source files dynamically. Production runs strictly from compiled bundles (`dist/` and `_internal/dist/`). Testing dev does NOT prove production works.
- **Mandatory 3-Step Production Pre-Flight Verification before any Release:**
  1. **Build Gate:** `npm run build` must run `copy_dist_assets.py` with the Safety Audit Gate passing (verifying all CSS links, bundle sizes > 50 kB, and inline image/layout constraints).
  2. **Headless E2E on `dist/`:** Automated Playwright tests must load `dist/index.html` directly, asserting zero FOUC, correct titlebar icon bounding box (16x16 px), correct background colors, and no duplicated controls.
  3. **Self-Healing Fallback:** The backend `launch_dev.py` MUST maintain runtime self-healing so that even if corrupted assets are somehow extracted on a client machine, the app automatically repairs its HTML before display.
- **Strict Quality Rule:** The user must NEVER have to debug, inspect, or catch basic build discrepancies. The AI agent bears 100% autonomous responsibility for production readiness and verification.
"""

if "Mandatory Production Artifact Pre-Flight Gate" not in agents_md:
    agents_md = agents_md.replace("When the user requests a version update/release", rule_text + "\nWhen the user requests a version update/release")
    with open("AGENTS.md", "w", encoding="utf-8") as f:
        f.write(agents_md)
    print("AGENTS.md updated successfully!")
else:
    print("AGENTS.md already contains rule")

# Update WORKLOG.md
worklog_entry = """## [2026-11-01 12:58] – Antigravity (Codified Mandatory Production Artifact Pre-Flight Gate)

- **ผู้ดำเนินการ:** Antigravity (Google DeepMind)
- **สถานะ:** เพิ่มกฎเหล็กและข้อกำหนดอย่างเป็นทางการลงใน `AGENTS.md`, `HANDOFF.md` และ `WORKLOG.md`
- **สรุปสาระสำคัญ:**
  - กำหนดให้ AI ทุกตัว (ทั้ง Antigravity และ Codex) ต้องทดสอบเฉพาะไฟล์ Production จริง (`dist/index.html` และ Executable) ก่อนปล่อยอัปเดตทุกครั้ง ห้ามใช้ผลการรันใน Dev มาอ้างอิงความถูกต้องเด็ดขาด
  - การันตีระบบตรวจสอบอัตโนมัติ (Build Gate, Playwright E2E on dist, Backend Self-Healing) เพื่อไม่ให้ภาระการตรวจสอบตกเป็นของผู้ใช้
  - บันทึกเป็นมาตรฐานการทำงานถาวรของโปรเจกต์

---

"""

with open("WORKLOG.md", "r", encoding="utf-8") as f:
    old_worklog = f.read()

with open("WORKLOG.md", "w", encoding="utf-8") as f:
    f.write(worklog_entry + old_worklog)

print("WORKLOG.md updated successfully!")

# Update HANDOFF.md
with open("HANDOFF.md", "r", encoding="utf-8") as f:
    handoff = f.read()

if "Mandatory Production Pre-Flight Gate" not in handoff:
    handoff += "\n## Permanent Quality Standard: Mandatory Production Pre-Flight Gate\n- All future releases MUST be verified against `dist/` and compiled artifacts via Playwright before publishing. Zero user burden.\n"
    with open("HANDOFF.md", "w", encoding="utf-8") as f:
        f.write(handoff)
    print("HANDOFF.md updated successfully!")
