# RVC Flow — Broadcast Playroom 3 (FULL edition)

เอกสารอ้างอิงสำหรับไล่ปัญหา RVC (เขียนตอน v3.75, 2026-11-13). อ้างอิงจากโค้ดและเหตุการณ์จริงที่ debug มา
หมายเหตุ: Wayu TTS ถูกลบแล้วใน v3.75 — pipeline เสียงเหลือ **Edge-TTS → (RVC ถ้าเปิด)** เท่านั้น

## 1. ภาพรวม pipeline (อ่านแชท 1 ข้อความ)

```
แชท → หน้าเว็บ (index.html) คิวเสียง
   → GET /api/tts?text&gender&rate&pitch[&preview=1]          (launch_dev.py ~บรรทัด 11030+)
        1. preview=1 ? ข้ามคำแทนที่ : dict_manager.apply_replace(text)
        2. สร้าง cache_key = (text, gender, rate, pitch, volume, preview, rvc_enabled, rvc_model)
        3. มีในแคช (_TTS_AUDIO_CACHE) → ส่งเลย
        4. ไม่มี → tts_service.generate_audio_bytes()  = Edge-TTS (ต้องมีเน็ต)
        5. ถ้าไม่ใช่ preview → rvc_service.convert(audio)   ← จุดที่ RVC ทำงาน
              - ล้มเหลว: log + ส่งเสียง Edge เดิม + "ไม่เก็บแคช" (v3.75)
        6. เก็บแคช (LRU) → ส่ง audio/wav หรือ audio/mpeg กลับ
   → หน้าเว็บเล่นเสียง (ถ้า error หรือค้าง >14 วิ → "เสียงสำรอง" = speechSynthesis ของเบราว์เซอร์)
```

ข้อสำคัญ:
- **ปุ่ม "ทดลองฟัง" (preview=1) ไม่ผ่าน RVC โดยออกแบบ** — ฟังเป็น Edge ล้วน
- ถ้าแปลง RVC ล้มเหลว **ผู้ใช้จะได้ยินเสียง Edge ปกติ ไม่มี error บนหน้าจอ** (ออกแบบให้ fallback เงียบ) → ต้องดู `rvc_debug.log`
- RVC มีเฉพาะ FULL (`BP3_EDITION` มาจากชื่อ exe: มีคำว่า lite = lite). Lite: `rvc_service.convert` คืนเสียงเดิมทันที

## 2. ไฟล์ที่เกี่ยวข้อง

| ไฟล์ | หน้าที่ |
|---|---|
| `rvc_service.py` | บริการหลัก: หาโมเดล (`models()`), เลือก/โหลดแบบ async (`select()`), สถานะ (`status()`), แปลงเสียง (`convert()`), ดาวน์โหลดโมเดล, เก็บสถานะใน `rvc_settings.json`, เขียน `rvc_debug.log` |
| `rvc_engine.py` | ครอบ `rvc_python`: `RVCEngine.load()/convert_array()`, GPU check, resample |
| `rvc_runtime.py` | `create_inference()` เลือก device (cuda/cpu), half-precision, ตรวจไฟล์ `hubert_base.pt` + `rmvpe.pt` |
| `voice_downloader.py` | ดาวน์โหลดเสียงจาก Hugging Face (2 repo) → แตกลง `rvc_models/` |
| `package_numba_cache.py` | locator แคช numba สำหรับแอปที่แพ็ก (ดูหัวข้อ 6 — เคยขาดจนพัง) |
| `launch_dev.py` | endpoint `/api/tts`, `/api/rvc/*` และบล็อกบนสุด (จัด sys.path + fallback numba) |
| `src/rvc_controls.js`, `src/tool_controls.js` | UI เลือก/เปิด-ปิดโมเดล เรียก `/api/rvc/select` |

Endpoint: `/api/rvc/status` (GET), `/models`, `/catalog`, `/select` (POST `{id, enabled}`), `/download`, `/cancel`, `/import`, `/open-folder`

## 3. สถานะและไฟล์ตั้งค่า

- `rvc_settings.json` = `{"selected": "<id>", "enabled": true|false}` อยู่ใน data dir
- `id` = sha256 ของ path ไฟล์ `.pth` (ตัวพิมพ์เล็ก, resolve แล้ว) ตัดเหลือ 20 ตัว → **ถ้าย้าย/เปลี่ยนที่เก็บโมเดล id จะเปลี่ยน**
- ตอนเปิดแอป: `RVCService()` ถูกสร้างตอน import, ถ้า `enabled=true` และมี `selected` จะเรียก `select()` โหลดอัตโนมัติใน thread
- `select()` ตั้ง `enabled=False, state=loading` ระหว่างโหลด; สำเร็จ → `state=ready, enabled=true, loaded=true` + `_save()`; ล้มเหลว → `state=error, error=...`
- โหลดเสร็จแล้วมี **warmup** (แปลงเสียงเงียบ 0.5 วิ). ถ้า warmup ล้ม **โมเดลยังขึ้น ready** (!) แต่แปลงจริงจะล้มเหมือนกัน → ดู `last_convert_error`
- `convert()` รอโมเดลที่กำลังโหลดสูงสุด 30 วิ; ถ้า `enabled` และ `loaded` ไม่จริง → คืนเสียงเดิม

## 4. data dir อยู่ที่ไหน (ตัวการสับสนบ่อย)

`package_entry.py` ตัดสินใจ (ถ้ามี `<Root>/full` หรือ `lite` หรือ `<Root>/data` หรือ `.portable` → `<Root>/data`; ไม่งั้น `exe/data` หรือ `%LOCALAPPDATA%\BroadcastPlayroom3\data`) แล้วตั้ง env `BP3_DATA_DIR`

เครื่องของเจ้าของ (portable): `E:\DOCS\Documents\BroadcastPlayroom3\data\` (ไม่ใช่ AppData)

`rvc_service.models()` ค้นหา `.pth` (rglob) ในโฟลเดอร์ตามลำดับ: `BP3_DATA_DIR/rvc_models`, `ROOT/rvc_models`, `ROOT.parent/rvc_models`, `ROOT.parent/data/rvc_models`, `%LOCALAPPDATA%\BroadcastPlayroom3\data\rvc_models`, `...\rvc_models`, `.../broadcast playroom dev/rvc_models`, `~/.tts-for-livestream/voices`
→ โมเดลของเจ้าของจริงๆ อยู่ที่ AppData (`lumine-jp.pth` + `.index`) แต่ถูกเจอผ่านรายการนี้

## 5. ไฟล์ที่ต้องมีบน production (FULL)

- `full/_internal/rvc_python/base_model/hubert_base.pt` และ `rmvpe.pt` (ไม่มี → `ไฟล์ประกอบ RVC ของรุ่น FULL ไม่ครบ`)
- `_internal/` มี torch (cu128), numpy, scipy, librosa, numba, llvmlite, faiss, pyworld, resampy, soundfile (`_soundfile_data`)
- `.py` ของแอปอยู่ทั้ง `full/` และ `_internal/` → ดูหัวข้อ 6

## 6. เหตุการณ์ที่ผ่านมา (บทเรียน)

**(A) v3.71–v3.72: `_internal` มีสำเนา .py เก่าบังไฟล์ที่แพตช์ใหม่**
- `package_entry.py` (คอมไพล์ในตัว exe — แก้ไฟล์บนดิสก์ไม่มีผล) ใส่ `_internal` ไว้หน้าสุดของ `sys.path` → `_internal/tts_service.py` เก่าชนะ
- แก้ใน v3.73: บล็อกบนสุดของ `launch_dev.py` ย้ายโฟลเดอร์ exe ขึ้นหน้า `_internal` + แพตช์เขียน `.py` ลงทั้งสองที่
- เป็นปัญหาจริงแต่ **ไม่ใช่สาเหตุ RVC เงียบ** (RVC ยังเสียหลัง v3.73)

**(B) สาเหตุจริงของ RVC เงียบ: `package_numba_cache` หายไป (แก้ใน v3.75)**
- log: `RuntimeError: Failed to import 'package_numba_cache.FrozenDataCacheLocator' specified via NUMBA_CACHE_LOCATOR_CLASSES` (`ModuleNotFoundError: package_numba_cache`)
- exe รุ่น FULL ตั้ง env `NUMBA_CACHE_LOCATOR_CLASSES` ชี้ไปโมดูลนี้ → `librosa` import `numba` ตอน `rvc_python/lib/rmvpe.py` โหลด → พัง → ทุกการแปลงล้ม
- ไฟล์อยู่ใน dev แต่ไม่ถูกแพ็กลง production. แก้โดยใส่ใน CORE_FILES ของ publish + fallback ใน `launch_dev.py` (ถ้าหาโมดูลไม่เจอ ลบ env ทิ้ง)
- **ยังอธิบายไม่ได้ว่าทำไมรุ่นเก่าเคยใช้ได้** (ข้อสงสัยที่ยังเปิดอยู่)

**บทเรียนวิธี debug:** dev ใช้ได้ production พัง = ต้องสงสัย "ของที่อยู่ใน exe/_internal ไม่ตรงกับ dev" ไม่ใช่โค้ดตรรกะ. อย่าเดา — เพิ่ม log ให้เห็น error จริงก่อน (v3.74 ทำให้เจอใน 1 รอบ)

## 7. วิธีไล่ปัญหา (เรียงตามลำดับ)

1. เปิด `http://127.0.0.1:8801/api/rvc/status` (พอร์ตอาจต่าง)
   - `state=error` → อ่าน `error`
   - `state=ready, loaded=true` แต่เสียงไม่ใช่ RVC → ดู `last_convert_error`
   - `state=idle` ตอนเปิดแอป และไฟล์ตั้งค่า `enabled=true` → autoload ไม่ทำงาน ดู log บรรทัด `init:`
2. อ่าน `<data dir>/rvc_debug.log` (หมุนไฟล์ที่ 512 KB → `rvc_debug.old.log`). คำสำคัญ:
   - `init:` — path ไฟล์ตั้งค่า/โมเดล และสถานะที่อ่านได้
   - `load failed` / `warmup conversion failed` / `convert failed` — มี traceback
   - `convert skipped: enabled=... loaded=... state=...` — แปลงข้ามเพราะยังไม่เปิด/ยังไม่โหลด (log 5 ครั้งแรกต่อการรัน)
3. เทียบไฟล์ production กับ dev (md5): `launch_dev.py`, `tts_service.py`, `rvc_*.py`, `voice_downloader.py`, `package_numba_cache.py` ทั้งใน `full/` และ `full/_internal/`
4. ตรวจ `hubert_base.pt`, `rmvpe.pt`, โมเดล `.pth` มีจริง; `rvc_models` ใน data dir vs AppData
5. ถ้าเปลี่ยนไลบรารีใน `_internal` (torch/numpy/librosa/numba) ต้องทดสอบบน build จริง ไม่ใช่แค่ dev

## 8. ข้อควรระวังตอนแก้/ปล่อย

- ทดสอบใน dev ไม่พอสำหรับ RVC — ต้องอัปเดตบนเครื่อง production จริงแล้วลองอ่านแชทด้วย RVC
- โมดูล .py ใหม่ที่ถูก import ตอน runtime ต้องอยู่ใน CORE_FILES ของ `publish_release_vXXX.py` (ไม่งั้นผู้ใช้ที่อัปเดตด้วยแพตช์จะไม่ได้ไฟล์)
- เปลี่ยน signature ใน `tts_service.generate_audio_bytes` ต้องเช็กว่า `_internal` ไม่มีสำเนาเก่า
- error ของ RVC ถูกกลืนโดยตั้งใจ (ไม่ให้เสียงหาย) — อย่าลบ `rvc_debug.log`/`last_convert_error` ออก
