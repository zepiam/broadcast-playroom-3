# คู่มือสร้าง Plugin — Broadcast Playroom 3 (Plugin API v1)

> เอกสารนี้เขียนให้ **AI อ่านแล้วสร้าง plugin ให้ผู้ใช้ได้เลย** (และคนอ่านเองก็ได้)
> ผู้ใช้: ส่งทั้งไฟล์นี้ให้ AI พร้อมบอกว่าอยากได้ plugin อะไร แล้ววางโฟลเดอร์ที่ AI สร้างลงในโฟลเดอร์ plugins ของโปรแกรม
> AI: ทำตามกติกาในเอกสารนี้อย่างเคร่งครัด อย่าเดา API ที่ไม่ได้เขียนไว้ที่นี่ — ถ้าไม่มีในเอกสาร แปลว่า **ยังทำไม่ได้**

API เวอร์ชัน 1 **ถูกล็อก** หลังจากนี้โปรแกรมจะไม่เปลี่ยนความหมายของสิ่งที่เขียนไว้ที่นี่ plugin ที่เขียนตามเอกสารนี้จะยังใช้ได้หลังอัปเดตโปรแกรม (ถ้าจะเพิ่มความสามารถ จะเพิ่มเป็น API เวอร์ชันใหม่ ไม่แก้ของเดิม)

---

## 1. Plugin ทำอะไรได้ / ทำอะไรไม่ได้

**ทำได้ (เฟสนี้ รองรับ JavaScript ล้วนเท่านั้น):**

1. **Widget** — หน้า HTML ที่แสดงผลบนจอสตรีม (ใส่ใน OBS เป็น Browser Source) โดยรับข้อมูลสดจากโปรแกรม (แชท, ASK/โหวต, ชิงโชค, สุ่ม) แบบอ่านอย่างเดียว
2. **เมาส์พิเศษ** — เปลี่ยนรูปเมาส์ (cursor) ในหน้าต่างโปรแกรมด้วยรูป PNG

**ทำไม่ได้ (อย่าพยายามเขียน):**

- เรียกอินเทอร์เน็ต/API ภายนอก (ถูกบล็อกโดย sandbox) — ยังไม่รองรับในเวอร์ชันนี้
- Python / ไฟล์ `main.py` / โค้ดที่รันนอก sandbox
- สั่งโปรแกรมทำอะไร (ส่งข้อความ, อ่านออกเสียง, ควบคุม overlay, เขียนไฟล์) — ทุกอย่างเป็น **อ่านอย่างเดียว**
- แก้ไข ซ่อน หรือลบ **เครดิตผู้พัฒนา** และ **ปุ่ม/เนื้อหา "สนับสนุนการพัฒนาโปรแกรม"** — plugin เข้าถึงหน้าหลักของโปรแกรมไม่ได้อยู่แล้ว และห้ามขอสิทธิ์เหล่านี้
- เข้าถึงหน้าหลักของโปรแกรม (DOM, localStorage, cookie) — plugin รันในกล่องแยก (sandbox)

---

## 2. ตำแหน่งและโครงสร้างโฟลเดอร์

Plugin 1 ตัว = 1 โฟลเดอร์ ใน `<โฟลเดอร์ข้อมูลโปรแกรม>/plugins/` (ผู้ใช้กดปุ่ม **"เปิดโฟลเดอร์ plugins"** ในหน้า ตั้งค่า > ปลั๊กอิน เพื่อเปิดโฟลเดอร์นี้) การอัปเดตโปรแกรมไม่แตะโฟลเดอร์นี้

```text
plugins/
└── my-plugin/            ← ชื่อโฟลเดอร์ = id (ดูกฎข้อ 3)
    ├── plugin.json       ← จำเป็น
    ├── widget.html       ← ถ้าเป็น widget (ไฟล์เดียวจบ ดูข้อ 5)
    └── cursor.png        ← ถ้าเป็นเมาส์พิเศษ
```

ชื่อโฟลเดอร์ที่ขึ้นต้นด้วย `_` หรือ `.` จะถูกข้าม

---

## 3. `plugin.json` (ต้องมี)

```json
{
  "id": "my-plugin",
  "name": "ชื่อที่แสดงในหน้าตั้งค่า",
  "version": "1.0.0",
  "author": "ชื่อผู้สร้าง",
  "description": "อธิบายสั้นๆ ว่าทำอะไร",
  "api_version": 1,
  "permissions": ["chat_read"],
  "widget": "widget.html"
}
```

| ฟิลด์ | กฎ |
|---|---|
| `id` | **ต้องเท่ากับชื่อโฟลเดอร์เป๊ะ** ใช้ได้เฉพาะ `a-z 0-9 _ -` ยาว 2–49 ตัว ขึ้นต้นด้วย a-z หรือ 0-9 |
| `api_version` | ต้องเป็นตัวเลข `1` (ไม่ใช่ข้อความ) ไม่งั้นโปรแกรมจะไม่รองรับ |
| `name`, `version`, `author`, `description` | ข้อความ แสดงในหน้าตั้งค่า (ไม่บังคับแต่ควรมี) |
| `permissions` | list ของสิทธิ์จากตารางข้อ 4 เท่านั้น ใส่สิทธิ์ที่ไม่รู้จัก = plugin ใช้งานไม่ได้ |
| `widget` | ชื่อไฟล์ `.html` ในโฟลเดอร์หลักของ plugin (ห้ามมี `/` `\` หรือ `..`) |
| `cursor` | ชื่อไฟล์ `.png` สำหรับเมาส์พิเศษ (ดูข้อ 6) |
| `cursor_hotspot` | `[x, y]` จุดที่ใช้คลิกบนรูปเมาส์ ค่าเริ่มต้น `[0, 0]` |

ต้องมี **อย่างน้อยหนึ่งอย่าง** ระหว่าง `widget` กับ `cursor`

## 4. สิทธิ์ (permissions) ที่มีในเวอร์ชัน 1

ผู้ใช้จะเห็นสิทธิ์ที่ plugin ขอ และต้องกดอนุมัติก่อนเปิด **ขอเท่าที่จำเป็นเท่านั้น** ถ้าแก้ `permissions` ทีหลัง ผู้ใช้ต้องอนุมัติใหม่

| สิทธิ์ | ให้อะไร |
|---|---|
| `chat_read` | รับ event `chat_message` (ข้อความแชทสด) |
| `events_read` | รับ event `chat_clear`, `chat_delete`, `ask_update`, `giveaway_update`, `randomizer_spin` |
| `ui_cursor` | ใช้ `cursor` เปลี่ยนรูปเมาส์ในหน้าต่างโปรแกรม (ใช้ได้แค่รูป PNG) |

ห้ามขอสิทธิ์อื่นเด็ดขาด โดยเฉพาะที่เกี่ยวกับ `creator_support`, `support_modal`, `donate_qr`, `promptpay_qr`, `footer_creator_links`, `about_author` — plugin ที่ขอจะถูกปฏิเสธ

---

## 5. Widget — เขียนอย่างไร

ผู้ใช้ก๊อปลิงก์ `http://127.0.0.1:<พอร์ต>/plugins/host/<id>` จากหน้าตั้งค่า ไปใส่เป็น **Browser Source** ใน OBS (ตั้งความกว้าง/สูงเองใน OBS) หน้า widget ต้องเปิดอยู่ได้ทั้งตอนใน OBS และเบราว์เซอร์

### กฎเหล็กของ widget (เพราะ sandbox)

1. **ไฟล์เดียวจบ** — HTML + CSS + JavaScript ต้องอยู่ในไฟล์ `widget.html` ไฟล์เดียว ใช้ `<style>` และ `<script>` แบบ **inline** เท่านั้น
   (ไฟล์ `.js` / `.css` แยก, `<script src>`, `<link rel=stylesheet>` จะถูกบล็อก)
2. **รูป/ฟอนต์/เสียง ต้องฝังเป็น `data:` URI** (เช่น `data:image/png;base64,...`) — โหลดจากอินเทอร์เน็ตหรือไฟล์ข้างๆ ไม่ได้ ใช้ SVG แบบ inline หรือ emoji/CSS ได้
3. **ห้ามเรียกเครือข่าย** — `fetch`, `XMLHttpRequest`, `WebSocket`, `<img src="http...">` ถูกบล็อกทั้งหมด
4. **พื้นหลังต้องโปร่งใส** — ใส่ `html,body{background:transparent;margin:0}` เพื่อให้ซ้อนบนภาพสตรีมได้
5. ห้ามใช้ `localStorage`/`sessionStorage`/cookie (ใช้ไม่ได้ใน sandbox) เก็บสถานะในตัวแปร JavaScript
6. ห้ามใช้ `alert`/`confirm`/`prompt`/`window.open`/`<form>` submit
7. ประหยัดทรัพยากร: อย่าทำ animation วนไม่หยุดที่หนัก GPU (หลีกเลี่ยง `backdrop-filter: blur`, ภาพเคลื่อนไหวต่อเนื่องที่ไม่จำเป็น) เมื่อไม่มีอะไรเปลี่ยนให้หยุดนิ่ง

### SDK — `BP3Plugin` (โปรแกรมฉีดให้เองในหน้า widget ไม่ต้อง import)

```js
BP3Plugin.apiVersion;          // 1
BP3Plugin.app;                 // ข้อมูลโปรแกรม เช่น { version: "3.61" } (มีค่าหลัง event 'init')
BP3Plugin.on(eventName, fn);   // ลงทะเบียนรับ event; fn(data)
```

ชื่อ event ที่รับได้ (สิทธิ์ที่ต้องมีอยู่ในวงเล็บ):

| event | ความหมาย | สิทธิ์ |
|---|---|---|
| `init` | widget เริ่มทำงาน ได้ `{ plugin:{id,permissions}, app:{version}, api_version }` | — |
| `chat_message` | มีข้อความแชทใหม่ | `chat_read` |
| `chat_clear` | ล้างแชท | `events_read` |
| `chat_delete` | ลบข้อความหนึ่งข้อความ (`data.id`) | `events_read` |
| `ask_update` | สถานะ ASK/โหวตเปลี่ยน | `events_read` |
| `giveaway_update` | สถานะชิงโชคเปลี่ยน | `events_read` |
| `randomizer_spin` | มีการสุ่ม | `events_read` |

### ข้อมูล (payload) ที่ส่งมา

- `chat_message` — ฟิลด์ที่ใช้ได้: `id` (ตัวเลข), `username` (ชื่อคนส่ง), `text` (ข้อความ; อาจมี `raw_text` เป็นข้อความดิบ), `platform` (ชื่อแพลตฟอร์ม เช่น twitch, youtube, kick, tiktok, mylive, soop) ฟิลด์อื่นอาจมีเพิ่มได้
- event อื่น ๆ — เป็นข้อมูลสถานะภายในของโปรแกรม โครงสร้างอาจมีฟิลด์เพิ่ม **ให้อ่านเฉพาะฟิลด์ที่ต้องใช้ และเผื่อกรณีเป็น `undefined` เสมอ** (ใช้ `d && d.field`) อย่าสมมติว่ามีฟิลด์ที่ไม่ได้ระบุ
- widget ได้รับเฉพาะ event ที่เกิดหลังจาก widget เปิดแล้ว (ไม่มีการย้อนส่งแชทเก่าให้) และแสดงข้อความจากผู้ชมที่ไม่น่าเชื่อถือ — **ห้ามใส่ข้อความแชทเข้า `innerHTML`** ให้ใช้ `textContent` เสมอ (กัน XSS)

### ตัวอย่าง widget ครบ — แสดงแชทล่าสุด 5 ข้อความ

`plugin.json`

```json
{
  "id": "recent-chat",
  "name": "แชทล่าสุด 5 ข้อความ",
  "version": "1.0.0",
  "author": "ตัวอย่าง",
  "description": "แสดงข้อความแชทล่าสุดบนจอสตรีม",
  "api_version": 1,
  "permissions": ["chat_read", "events_read"],
  "widget": "widget.html"
}
```

`widget.html`

```html
<!doctype html>
<html>
<head>
<meta charset="utf-8">
<style>
  html, body { margin: 0; background: transparent; }
  body { font: 600 26px system-ui, sans-serif; color: #fff; text-shadow: 0 2px 6px #000; padding: 12px; }
  .row { margin: 4px 0; }
  .who { color: #ffd54f; }
</style>
</head>
<body>
<div id="list"></div>
<script>
  var list = document.getElementById('list');
  function add(d) {
    var row = document.createElement('div');
    row.className = 'row';
    var who = document.createElement('span');
    who.className = 'who';
    who.textContent = ((d && d.username) || 'ไม่ระบุชื่อ') + ': ';
    var msg = document.createElement('span');
    msg.textContent = (d && (d.text || d.raw_text)) || '';
    row.appendChild(who); row.appendChild(msg);
    list.appendChild(row);
    while (list.children.length > 5) list.removeChild(list.firstChild);
  }
  BP3Plugin.on('chat_message', add);
  BP3Plugin.on('chat_clear', function () { list.textContent = ''; });
</script>
</body>
</html>
```

---

## 6. เมาส์พิเศษ (cursor)

```json
{
  "id": "my-cursor",
  "name": "เมาส์ของฉัน",
  "version": "1.0.0",
  "author": "ชื่อผู้สร้าง",
  "description": "เปลี่ยนรูปเมาส์ในโปรแกรม",
  "api_version": 1,
  "permissions": ["ui_cursor"],
  "cursor": "cursor.png",
  "cursor_hotspot": [2, 1]
}
```

- ไฟล์ต้องเป็น **PNG จริง** ขนาด **ไม่เกิน 64×64 พิกเซล** และ **ไม่เกิน 32 KB** (แนะนำ 32×32) พื้นหลังโปร่งใส
- ถ้าไฟล์ไม่ผ่านเงื่อนไข plugin จะแสดงว่า "ใช้งานไม่ได้" พร้อมเหตุผล
- `cursor_hotspot` คือพิกัดจุดคลิกในรูป (ปลายลูกศร) นับจากมุมซ้ายบน
- ถ้าเปิดหลายตัวพร้อมกัน ใช้ตัวแรก (เรียงตามชื่อโฟลเดอร์) การเปลี่ยนมีผลหลังรีเฟรช/เปิดหน้าต่างใหม่ ปิด plugin แล้วกลับเป็นเมาส์ปกติ
- plugin เมาส์ไม่มีโค้ด — ส่งแค่รูป โปรแกรมเป็นคนเปลี่ยนให้เอง

---

## 7. สถานะและการจัดการ (ผู้ใช้เห็นในหน้า ตั้งค่า > ปลั๊กอิน)

- plugin ที่เพิ่งวางลงโฟลเดอร์จะ **ปิดอยู่เสมอ** จนกว่าผู้ใช้จะกดเปิดและอนุมัติสิทธิ์ (หลังวางต้องกด "โหลดใหม่")
- ถ้า widget เกิด error (`throw` ที่ไม่ได้จับ) ซ้ำ **5 ครั้ง** โปรแกรมจะปิด plugin นั้นให้อัตโนมัติ — จับ error ใน handler ของตัวเองด้วย `try/catch`
- **Safe Mode** ปิด plugin ทุกตัวชั่วคราว (ใช้ตอนสงสัยว่า plugin ทำให้มีปัญหา)
- ปิดหรือลบ plugin แล้วโปรแกรมทำงานเหมือนเดิม 100%

## 8. Checklist ก่อนส่งงานให้ผู้ใช้ (AI ตรวจเองทุกข้อ)

- [ ] `id` ใน plugin.json = ชื่อโฟลเดอร์ ใช้เฉพาะ `a-z 0-9 _ -`
- [ ] `api_version` เป็นตัวเลข `1`
- [ ] `permissions` มีเฉพาะ `chat_read`, `events_read`, `ui_cursor` และขอเท่าที่ใช้จริง
- [ ] `widget` เป็นชื่อไฟล์ .html ในโฟลเดอร์หลัก และไฟล์มีอยู่จริง (หรือมี `cursor` ที่เป็น PNG ถูกเงื่อนไข)
- [ ] widget เป็นไฟล์เดียว ไม่มี `<script src>` / `<link>` / `fetch` / รูปจากภายนอก
- [ ] พื้นหลังโปร่งใส ไม่มีการใช้ localStorage / alert
- [ ] ข้อความจากแชทใส่ผ่าน `textContent` เท่านั้น
- [ ] อ่านฟิลด์ของ event แบบเผื่อ `undefined`
- [ ] ไม่แตะ/ไม่อ้างถึงเครดิตผู้พัฒนาหรือปุ่มสนับสนุนการพัฒนาโปรแกรม

## 9. ข้อความสำหรับผู้ใช้ส่งให้ AI (ก๊อปไปใช้ได้เลย)

> ฉันอยากได้ plugin สำหรับ Broadcast Playroom 3: **[อธิบายสิ่งที่อยากได้]**
> ให้อ่านคู่มือที่แนบมาแล้วสร้างโฟลเดอร์ plugin ให้ครบ (plugin.json + ไฟล์ที่จำเป็น) ตามกติกาในคู่มือ
> ใช้ได้เฉพาะ API ที่คู่มือเขียนไว้ ถ้าสิ่งที่ฉันขอทำไม่ได้ในเวอร์ชันนี้ ให้บอกตรงๆ และเสนอสิ่งที่ใกล้เคียงที่ทำได้
> พอเสร็จ ให้ตรวจตาม Checklist ท้ายคู่มือ แล้วบอกวิธีวางโฟลเดอร์และวิธีทดสอบ
