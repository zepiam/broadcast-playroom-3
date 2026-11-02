# main.py — ตัวอย่างโค้ดเบื้องหลังสำหรับ Plugin ของ Broadcast Playroom 3

def on_event(event_name: str, data: dict):
    """ฟังก์ชันรับเหตุการณ์ต่างๆ จากโปรแกรมหลัก (เช่น แชทเข้า, ยอดโดเนท)"""
    if event_name == "chat_message":
        author = data.get("username", "นิรนาม")
        text = data.get("text", "")
        platform = data.get("platform", "Live")
        print(f"[{platform}] ได้รับแชทจาก {author}: {text}")

def on_start():
    """ทำงานเมื่อปลั๊กอินถูกโหลดขึ้นมาใช้งาน"""
    print("[Starter Template] เริ่มต้นการทำงานเรียบร้อย")

def on_stop():
    """ทำงานเมื่อปิดโปรแกรมหรือปิดปลั๊กอิน"""
    print("[Starter Template] หยุดการทำงาน")
