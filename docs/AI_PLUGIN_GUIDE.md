# Broadcast Playroom 3 — Plugin Developer & AI Specification Guide

> **สำหรับนักพัฒนาและ AI Assistants (Claude, Gemini, ChatGPT)**: 
> เอกสารฉบับนี้เป็นข้อกำหนดอย่างเป็นทางการ (Official Specification) สำหรับการสร้าง Plugin เสริมให้กับโปรแกรม Broadcast Playroom 3
> AI สามารถอ่านเอกสารนี้และสร้าง Plugin ที่พร้อมใช้งานได้ทันทีโดยไม่ต้องแก้ไขซอร์สโค้ดหลักของโปรแกรม

---

## 1. ปรัชญาการออกแบบ (Design Philosophy)

1. **Local-First & Sustainable**: ทุกปลั๊กอินทำงานอยู่บนเครื่องของผู้ใช้ (Localhost) ไม่มีวันหมดอายุ แม้ในอนาคตผู้พัฒนาหลักจะไม่ได้อัปเดตโปรแกรมแล้ว ชุมชนก็ยังสามารถต่อยอดระบบได้เอง
2. **Physical Isolation**: ปลั๊กอินทั้งหมดจะถูกเก็บอยู่ในโฟลเดอร์ `data/plugins/<plugin-id>/` การอัปเดตเวอร์ชันของโปรแกรมหลักจะไม่แตะต้องหรือลบโฟลเดอร์นี้เด็ดขาด
3. **Zero GPU Lockup**: หน้าต่าง UI หรือ Widget ของปลั๊กอินจะต้องใช้ CSS ที่เบา ประหยัดทรัพยากรการเรนเดอร์ และเข้าสู่สถานะ 0% GPU Idle เมื่อไม่มีการขยับ
4. **Creator Attribution & Tamper Protection**: ระบบหลักมีกลไกป้องกันการดัดแปลง (Tamper Guard) ไม่อนุญาตให้ปลั๊กอินใดๆ เข้าไปแก้ไข ซ่อน หรือสลับเปลี่ยนหน้าต่างสนับสนุนผู้พัฒนา (`support_modal`, `donate_qr`, ลิงก์โดเนทของผู้สร้าง) เด็ดขาด

---

## 2. โครงสร้างโฟลเดอร์ของ Plugin

ปลั๊กอิน 1 ตัวจะมีโฟลเดอร์ของตัวเองอยู่ใต้ `data/plugins/`:

```text
data/
└── plugins/
    └── my-awesome-plugin/
        ├── plugin.json         (จำเป็น: ไฟล์ข้อมูลและสิทธิ์ของปลั๊กอิน)
        ├── main.py            (ตัวเลือก: โค้ดประมวลผลเบื้องหลัง Python)
        ├── settings.html       (ตัวเลือก: หน้าต่างตั้งค่าของปลั๊กอินในหน้า Settings)
        └── widget.html         (ตัวเลือก: หน้า Overlay สำหรับนำไปใส่ใน OBS)
```

---

## 3. ข้อกำหนดของไฟล์ `plugin.json` (Manifest Schema)

ทุกปลั๊กอินต้องมีไฟล์ `plugin.json` อยู่ที่รากโฟลเดอร์:

```json
{
  "id": "my-awesome-plugin",
  "name": "บอทไฟกระพริบอัจฉริยะ",
  "version": "1.0.0",
  "author": "YourName",
  "description": "สั่งหลอดไฟอัจฉริยะในห้องให้เปลี่ยนสีเมื่อมีคนส่งของขวัญหรือแชท",
  "enabled": true,
  "entrypoint": "main.py",
  "settings_ui": "settings.html",
  "permissions": [
    "chat_read",
    "tts_speak"
  ]
}
```

### รายการ Permissions ที่อนุญาต:
* `chat_read`: ขอสิทธิ์รับข้อมูลแชทแบบเรียลไทม์
* `tts_speak`: ขอสิทธิ์สั่งให้ระบบอ่านออกเสียง
* `overlay_push`: ขอสิทธิ์ส่งสัญญาณขึ้นจอ Overlay
* *(หมายเหตุ: การขอสิทธิ์ในส่วน `creator_support`, `donate_qr` จะถูกปฏิเสธโดยอัตโนมัติ)*

---

## 4. สัญญาณและข้อมูลเหตุการณ์ (Event Payloads)

### เหตุการณ์ `chat_message` (เมื่อมีข้อความแชทเข้ามา)
โปรแกรมหลักจะส่งข้อมูลข้อความแชทเข้ามาในรูปแบบ JSON:

```json
{
  "id": 105,
  "platform": "Twitch",
  "platform_key": "twitch",
  "username": "ViewerName",
  "text": "สวัสดีครับสตรีมเมอร์",
  "original_text": "Hello streamer",
  "is_translated": true,
  "isVip": false,
  "badges": [],
  "avatar": "https://...",
  "event": "message",
  "amount": null,
  "currency": ""
}
```

---

## 5. ตัวอย่างการสร้าง Plugin อย่างง่าย (Python + HTML)

### ไฟล์ `main.py`:
```python
def on_event(event_name, data):
    if event_name == "chat_message":
        user = data.get("username")
        text = data.get("text")
        print(f"[MyPlugin] ได้รับแชทจาก {user}: {text}")

def on_start():
    print("[MyPlugin] เริ่มการทำงานเรียบร้อย")

def on_stop():
    print("[MyPlugin] ปิดการทำงาน")
```

### ไฟล์ `settings.html`:
```html
<!DOCTYPE html>
<html lang="th">
<head>
  <meta charset="UTF-8">
  <style>
    body { background: #232428; color: #f2f3f5; font-family: sans-serif; padding: 15px; }
    input, button { padding: 8px 12px; border-radius: 6px; border: 1px solid #4e5058; background: #1e1f22; color: #fff; }
    button { background: #5865f2; border: none; cursor: pointer; }
    button:hover { background: #4752c4; }
  </style>
</head>
<body>
  <h3>💡 ตั้งค่าสีหลอดไฟ</h3>
  <label>รหัส IP หลอดไฟ: <input type="text" id="ip" value="192.168.1.50"></label>
  <button onclick="alert('บันทึกสำเร็จ!')">บันทึก</button>
</body>
</html>
```

---

## 6. แนวทางปฏิบัติสำหรับ AI ในการสร้าง Plugin
เมื่อผู้ใช้งานสั่งให้ AI สร้างปลั๊กอินสำหรับ Broadcast Playroom 3 ให้ปฏิบัติตามกฎนี้เสมอ:
1. สร้างไฟล์ `plugin.json` ที่ระบุ `id` ไม่ซ้ำกับระบบ
2. เขียนโค้ดที่รันแบบ Non-blocking (ห้ามใช้ `time.sleep` ใน Main Thread)
3. ครอบคำสั่งเชื่อมต่อภายนอกด้วย `try...except` เสมอ เพื่อป้องกันไม่ให้แอปพลิเคชันค้าง
4. ห้ามแทรกแซงหรือพยายามซ่อนองค์ประกอบหน้าสนับสนุนของผู้สร้างหลัก (`#modal-support`, `.support-links`)
