# Broadcast Playroom 3 (Tauri v2 + Vite)

โครงสร้างโปรเจกต์เวอร์ชันใหม่ของ Broadcast Playroom ออกแบบตามสถาปัตยกรรม **Tauri v2 + Vite** ด้วยดีไซน์มินิมอลแบบ **Discord Dark Theme**:

## สถาปัตยกรรม & โครงสร้างโฟลเดอร์
- `src/` - หน้าต่าง UI หลัก (HTML / CSS / JavaScript)
  - `index.html` - โครงหน้าต่างหลัก (ซีกซ้าย Sidebar + ด้านบน Top Bar + โครง Canvas)
  - `styles.css` - ธีมสี Dark Mode กึ่งสว่างแบบ Discord (ไร้กรอบซ้อนกรอบ)
  - `main.js` - สคริปต์ควบคุมการเปลี่ยนหมวดหมู่และฟังก์ชันหน้าบ้าน
- `src-tauri/` - การตั้งค่าและตัวเชื่อมต่อระบบ Tauri v2 (Rust Backend & Windows WebView2)
  - `tauri.conf.json` - ค่าคอนฟิกหน้าต่าง ขนาด 1280x820, พอร์ต 5173
- `vite.config.js` - ตัวจัดการ Bundler ความเร็วสูง

## การทดสอบและรันโปรแกรม
1. **เปิดดูหน้าตา UI ทันที:** ดับเบิ้ลคลิกไฟล์ `src/index.html` เพื่อดูในเบราว์เซอร์
2. **รัน Development Server:**
   ```bash
   npm run dev
   ```
   แล้วเปิดดูที่ `http://localhost:5173`
