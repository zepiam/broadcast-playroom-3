"""Build a review inventory from the application UI and explicit behaviour checks."""
import hashlib, json, re
from pathlib import Path
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
OUT = Path(__file__).resolve().parent
soup = BeautifulSoup((ROOT / 'src/index.html').read_text(encoding='utf-8'), 'html.parser')

def clean(value):
    return re.sub(r'\s+', ' ', value or '').strip()

nav = {node.get('data-sec'): clean(node.get_text(' ', strip=True)) for node in soup.select('.settings-nav-item[data-sec]')}
windows = {'giveaway':'Giveaway', 'ask':'ASK', 'replie':'Replie', 'randomizer':'Randomizer',
           'playroom':'Playroom', 'settings':'ตั้งค่า', 'chat-settings':'ตั้งค่า Live Chat',
           'author-profile':'โปรไฟล์ผู้ชม', 'user-manager':'User Manager',
           'voice-settings':'ตั้งค่าโมเดลเสียง', 'composer':'Composer Studio'}
groups = {}
seen = set()

def add(group, label, ref='', hint='', edition='both', paused=False):
    label = clean(label)
    if not label: return
    key = (group, label, ref)
    if key in seen: return
    seen.add(key)
    ident = hashlib.sha256(('v1|' + '|'.join(key)).encode()).hexdigest()[:16]
    groups.setdefault(group, []).append({'id': ident, 'label':label, 'ref':ref, 'hint':hint, 'edition':edition, 'paused':paused})

def label_for(node):
    title = clean(node.get('title'))
    if node.name == 'button':
        text = clean(node.get_text(' ', strip=True))
        return title or text
    ident = node.get('id')
    label = soup.find('label', attrs={'for':ident}) if ident else None
    if not label:
        parent = node.find_parent(['label', 'div', 'section'])
        label = parent.find('label', recursive=False) if parent else None
    sibling = node.find_previous_sibling(['label', 'div', 'span'])
    sibling_text = clean(sibling.get_text(' ', strip=True)) if sibling else ''
    return title or (clean(label.get_text(' ', strip=True)) if label else '') or clean(node.get('placeholder')) or clean(node.get('aria-label')) or (sibling_text[:120] if sibling_text else '') or ('ตั้งค่า ' + ident if ident else '')

for node in soup.select('button, input, select, textarea'):
    if node.get('type') == 'hidden' or node.has_attr('hidden') or node.find_parent(id='win-chat-widget'): continue
    if node.find_parent(attrs={'data-item-id':'clip-marker'}): continue
    pane = node.find_parent(class_='settings-section-pane')
    win = node.find_parent(class_='floating-window')
    if pane:
        sec = pane.get('id', '').removeprefix('sec-')
        group = 'ตั้งค่า › ' + nav.get(sec, sec)
    elif win:
        wid = win.get('id', '').removeprefix('win-')
        if wid not in windows: continue
        group = windows[wid]
    else:
        group = 'หน้าแรก › แถบบน' if node.find_parent(class_='topbar') else 'หน้าแรก › Live Chat และเครื่องมือ'
    label = label_for(node)
    if not label or label in ('✕','×','—','−','🗖','📥','ปิด','ย่อหน้าต่าง','ปิดหน้าต่าง'): continue
    if len(label) > 180: label = label[:177] + '…'
    ref = ('#' + node['id']) if node.get('id') else ('data-widget-type=' + node['data-widget-type'] if node.get('data-widget-type') else '')
    kind = {'button':'ปุ่ม', 'input':'ช่อง/ตัวเลือก', 'select':'รายการเลือก', 'textarea':'ช่องข้อความ'}.get(node.name, '')
    add(group, kind + ': ' + label, ref, edition='full' if node.find_parent(attrs={'data-feature':'rvc'}) else 'both')

manual = {
 'เริ่มต้นและการใช้งานทั่วไป': [
  'เปิดและปิดโปรแกรม / เปิดซ้ำ / บันทึกค่าคงอยู่', 'โหมดฟอนต์ใหญ่และการจัดวางทุกหน้าต่าง',
  'เมนูคลิกขวาในโปรแกรมและกู้ปุ่มแถบบนที่ซ่อน', 'หน้าต่างเครื่องมือแยกและอยู่เหนือหน้าหลัก',
  'คีย์บอร์ดเลื่อนตัวเลือก dropdown และการใช้โปรแกรมเมื่อไม่มี Chrome'],
 'หน้าแรก › แชทสด': [
  'เชื่อมและตัดการเชื่อมต่อ Twitch, YouTube, Kick, SOOP, TikTok และ MyLive ทีละแพลตฟอร์ม',
  'ชื่อช่อง / URL ถูกต้องและผิด แสดงสถานะและข้อผิดพลาด', 'เชื่อมต่อใหม่หลังเน็ตหลุด และหยุดเชื่อมต่อด้วยตนเอง',
  'ข้อความสด ชื่อผู้ชม ไอคอนแพลตฟอร์ม รูปโปรไฟล์ และ emote', 'ข้อความของตัวเองและข้อความที่ส่งจากโปรแกรมปรากฏครั้งเดียว',
  'ช่องส่งข้อความ Twitch Chat Bot เปิดเฉพาะเมื่อพร้อม และส่งถึงแพลตฟอร์มจริง',
  'อ่านข้อความย้อนหลังโดยไม่เด้งลงล่าง / ปุ่มกลับไปล่าสุด', 'ประวัติบนหน้าจอสูงสุด 200 บรรทัด และไฟล์ log อายุ 7 วัน',
  'Demo สุ่มแชท: ข้อความในหน้าหลัก Composer และ OBS ตรงกัน / ปรับช่วงเวลา / หยุด',
  'ป้ายสถานะ TTS เวลาสร้างเสียง และข้อความที่มีแต่ emote'],
 'TTS และเสียง': [
  'เปิด/ปิดอ่านแชท ปรับระดับเสียงและทดสอบเสียงหญิง/ชาย', 'ข้อความเข้าคิวตามลำดับ และหยุดอ่านแล้วล้างคิวเดิม',
  'ข้อความคำสั่งเข้าร่วม / secret code ไม่ถูกอ่าน', 'คำแทนที่แบบ 55@ และคำยาวตรงตามที่ตั้ง',
  'กดทดสอบเสียงซ้ำระหว่างกำลังเล่นไม่ได้ / เล่นจบกดใหม่ได้', 'เสียงสำรองและข้อความแจ้งเตือนเมื่อ TTS มีปัญหา',
  'Server Status ตรวจตอนเริ่ม / ตรวจทุกนาที / กดตรวจเอง / สถานะช้าและล้มเหลว',
  'ระยะเวลารอคิวสูงสุด: เปลี่ยนค่า บันทึก เปิดใหม่ และตรวจผลจริง'],
 'RVC › Full เท่านั้น': [
  'รุ่น Full แสดงตัวเลือก RVC และสถานะอุปกรณ์', 'ค้นหา/นำเข้า/เลือก/เปลี่ยน/ปิดโมเดล',
  'ดาวน์โหลดโมเดล ความคืบหน้า ยกเลิก และกรณีดาวน์โหลดล้มเหลว', 'ใช้โมเดลแปลงเสียง TTS จริงและตรวจเสียงออกลำโพง',
  'เมื่อ RVC ผิดพลาด แสดงสถานะและใช้เสียงสำรองตามที่กำหนด'],
 'Lite / Full และไฟล์โปรแกรม': [
  'Lite ไม่มีปุ่ม RVC, โหลดโมเดล หรือไฟล์ CUDA / Full มี RVC', 'ติดตั้งและเปิดรุ่นทดลองในเครื่องอื่น',
  'ข้อมูลบัญชี การตั้งค่า ประวัติ สื่อและโมเดลไม่ติดไปกับชุดแจก', 'ปิดโปรแกรมแล้ว Overlay ใน OBS หาย / เปิดกลับมาแสดงใหม่',
  'ลิงก์ OBS เวอร์ชั่นเดิมยังใช้ได้ และพอร์ตไม่เปลี่ยนเอง'],
 'Composer › หน้าจอและเลเยอร์': [
  'สร้าง เปลี่ยนชื่อ เลือก ทำสำเนา ลบหน้า และเลือกหน้าสำหรับ OBS',
  'เพิ่ม ย้าย ปรับขนาด ล็อก ซ่อน ลบ และเปลี่ยนลำดับเลเยอร์', 'กรอบบางบอกตำแหน่ง widget โปร่งใสแสดงเฉพาะ Composer',
  'ซูม แพน พรีวิว นำเข้า/ส่งออก บันทึก และเปิดใหม่', 'แก้ widget หนึ่งแล้วไม่รีเฟรช กระพริบ หรือลบข้อมูลของ widget อื่น',
  'เมนูคลิกขวา canvas และการเลือก widget ซ้อนกัน', 'ขนาดฟอนต์ใหญ่: ชื่อเลเยอร์และปุ่มจัดเรียงไม่ล้น'],
 'Composer › Chat Default และ Theme': [
  'เพิ่ม Chat และเลือก Appearance ก่อนเพิ่ม', 'Default ↔ Theme สลับกลับได้ / เปลี่ยนทันทีใน Composer และ OBS',
  'ชื่อธีม การแบ่งหน้า theme และตำแหน่ง dropdown ไม่ล้น', 'ปรับฟอนต์ ขนาด สี ระยะ กล่อง ทิศทาง และจำนวนข้อความ',
  'รูปโปรไฟล์ ไอคอนแพลตฟอร์ม ชื่อ เวลา emote และข้อความใน OBS',
  'Demo และแชทจริงตรงกันใน Composer กับ OBS / ปรับ theme โดยข้อความเดิมไม่หาย'],
 'Composer › Chat รูปแบบอื่น': [
  'Danmaku: ทิศทาง ความเร็ว ขนาด สี ระยะ และ Demo/ข้อความจริง',
  'Balloon: รูปแบบ ฟอนต์ สี ระยะ และ Demo/ข้อความจริง',
  'Character Talk: ตัวละคร ฟอนต์ ชื่อ ข้อความ ภาพ และ Demo/ข้อความจริง',
  'ทุกแบบแสดงตรงกันระหว่าง Composer กับ OBS และเปลี่ยนตั้งค่าได้ทันที'],
 'Composer › Clock': [
  'เพิ่ม Clock / สลับ Theme ↔ Style ไปมา', 'รูปแบบเวลา วันที่ ฟอนต์ สี ขนาด และกรอบ',
  'Style Dot และตัวกระพริบ pixel ตามเวอร์ชั่นเดิม', 'Composer กับ OBS แสดงตรงกันและไม่มีกรอบซ้ำ'],
 'Composer › Viewer': [
  'ยอดผู้ชมตามแพลตฟอร์มที่เชื่อมต่อ รวมไอคอน MyLive', 'Demo ยอดผู้ชม / กลับสู่ยอดจริงเมื่อเริ่มไลฟ์',
  'แนวตั้ง / แนวนอน และจัดชิดซ้าย กลาง ขวา', 'ธีม ฟอนต์ สี ขนาด และการแสดงผล Composer/OBS'],
 'Composer › ข้อความ ภาพ วิดีโอ และ URL': [
  'Text: ข้อความ ฟอนต์ สี ขนาด พื้นหลัง และ marquee วิ่งจนพ้นกรอบก่อนวน',
  'Image: เลือกภาพ ตำแหน่ง ขนาด ครอบ/พอดี และความโปร่งใส', 'Video: เลือกวิดีโอ เล่น/วน เสียง และขนาด',
  'Browser URL / Alert: URL ถูกต้อง แสดงผลและการปรับขนาด', 'Webcam / กรอบกล้อง: ขนาด สี และการจัดวาง'],
 'Composer › Now Playing, Avatar และ Donate': [
  'Now Playing: ชื่อเพลง ปก เลื่อนชื่อยาว แถบความคืบหน้า ธีมและแหล่งเพลง',
  'PNG Avatar: ภาพพูด/หยุด ปรับขนาด และการตอบสนองต่อไมโครโฟน',
  'Donation Goal: เป้าหมาย ยอดปัจจุบัน แถบ สี ข้อความ และการบันทึก'],
 'Composer › เครื่องมือและเอฟเฟกต์': [
  'Replie: ข้อความ / ภาพ / Combo คำสั่ง bot เต็มจอ และซ่อนเมื่อจบ',
  'ASK: แสดงคำถาม ตัวเลือก คะแนน ผล และซ่อน standby', 'Giveaway: รับโค้ด เก็บชื่อ สุ่มรายชื่อ และผลใน Overlay',
  'Randomizer: รายการ ตัวเลือกแต่ละรูปแบบ ผลสุ่ม และการซ่อน standby',
  'Playroom: คำสั่ง คลิป ภาพ/เสียง และการแสดงผล', 'Emote Party: ทิศทาง ปริมาณ ขนาด ความเร็ว และการจบเอฟเฟกต์'],
 'OBS และ Dock': [
  'เชื่อม OBS WebSocket / ผิดรหัส / ตัดและเชื่อมใหม่', 'ลิงก์ Browser Source ทั้งหน้าเริ่มต้น หน้าเฉพาะ และลิงก์เก่า',
  'เปลี่ยนฉาก OBS และฉากซ้อนแล้ว Dock แสดง widget ของฉากปัจจุบัน',
  'Live Chat สองบรรทัด ไอคอน emote และปุ่มเครื่องมือใน OBS Dock', 'ล้างคิว TTS และควบคุม ASK/Giveaway/Replie/Randomizer จาก Dock'],
 'ผู้ชม / Blacklist': [
  'เปิดโปรไฟล์ แก้ชื่อ รูป โน้ต และบันทึก', 'ประวัติแชทเก็บรหัส emote และลบเมื่อเกิน 7 วัน',
  'User Manager ค้นหา กรอง เปิดโปรไฟล์ และส่งออก CSV', 'Blacklist เลือกบล็อก Replie / Overlay / TTS / ทุกส่วนแยกได้',
  'ผู้ชมที่ถูกบล็อกถูกจำกัดตามตัวเลือก และปลดบล็อกกลับมาได้'],
 'Chat Bot และตัวกรอง': [
  'Twitch เชื่อม/สลับ/ออกบัญชี และส่งข้อความจริง', 'เพิ่ม แก้ ลบ เปิด/ปิดคำสั่งและ cooldown',
  'เพิ่ม แก้ ลบ Timer และตรวจเงื่อนไขส่ง', 'ASK ส่งผลแชทเฉพาะเมื่อเปิดตัวเลือก',
  'คำหยาบ คำแทนที่/ปุ่มฟัง คำสั่งเงียบ และเสียง secret code', 'เช็คการบันทึกและปิดหน้าต่างหลังบันทึก'],
 'พักไว้ตามที่ตกลง': ['Clip Marker และปุ่มลัด: พัก ไม่ต้องทดสอบในรอบนี้', 'KICK Chat Bot: พัก ไม่ต้องทดสอบในรอบนี้', 'EasyDonate: ซ่อนไว้ รอแผนภายหลัง']
}
manual.update({
 'Composer › Chat ปรับแต่งรายตัว': ['เลือกชนิด Default / Theme และเลือกชุดธีม', 'สีพื้นหลัง สีกรอบ ความทึบ และมุมโค้ง', 'ขนาดฟอนต์ ชนิดฟอนต์ สีข้อความ และเงาข้อความ', 'สี/ขนาดชื่อผู้ชม และตำแหน่งชื่อ', 'การแสดงภาพโปรไฟล์ ขนาด และรูปทรง', 'ป้ายแพลตฟอร์ม ไอคอน ชื่อ และเวลา', 'รูปแบบกล่อง ระยะห่าง padding และการจัดแนว', 'จำนวนข้อความ ระยะเวลา และทิศทางข้อความใหม่', 'ภาพ emote และข้อความหลายบรรทัด', 'ปรับค่าแล้วเก็บข้อความเดิม / บันทึกแล้วเปิดใหม่'],
 'Composer › Danmaku ปรับแต่งรายตัว': ['ความเร็วและทิศทางการเคลื่อนที่', 'ขนาดและฟอนต์ข้อความ', 'สีข้อความ เส้นขอบ เงา และความโปร่งใส', 'รูปโปรไฟล์ ชื่อ ไอคอนแพลตฟอร์ม และ emote', 'ระยะห่าง ความหนาแน่น และจำนวนข้อความ', 'ทดลองข้อความจริงและ Demo บน Composer / OBS'],
 'Composer › Balloon ปรับแต่งรายตัว': ['รูปแบบบอลลูน พื้นหลัง กรอบ และมุม', 'ฟอนต์ ขนาด สี และระยะห่าง', 'ตำแหน่ง ทิศทางการลอย ความเร็ว และระยะเวลา', 'แสดงชื่อ รูปผู้ชม ไอคอนแพลตฟอร์ม และ emote', 'ทดลองข้อความจริงและ Demo บน Composer / OBS'],
 'Composer › Character Talk ปรับแต่งรายตัว': ['เลือกภาพตัวละครและตำแหน่ง', 'ชื่อผู้พูด กล่องข้อความ ฟอนต์ ขนาด และสี', 'เวลาค้าง ข้อความยาว และเอฟเฟกต์', 'ทดลองข้อความจริงและ Demo บน Composer / OBS'],
 'Composer › Clock ปรับแต่งรายตัว': ['เลือก Theme / Style และย้อนกลับได้', 'รูปแบบ 12/24 ชั่วโมงและวินาที', 'วันที่ ภาษา และการแสดง/ซ่อน', 'ฟอนต์ ขนาด สี เงา พื้นหลัง และกรอบ', 'Dot pixel และแอนิเมชันกระพริบ', 'เปลี่ยนค่าและแสดงตรงกันใน Composer / OBS'],
 'Composer › Viewer ปรับแต่งรายตัว': ['รูปแบบธีมและพื้นหลัง', 'แสดงยอดรวมและรายแพลตฟอร์มที่เชื่อม', 'ฟอนต์ สี ขนาด ไอคอน และระยะห่าง', 'จัดแนวซ้าย/กลาง/ขวาในแนวตั้งและแนวนอน', 'เปิด Demo ปรับยอด แล้วกลับยอดจริง', 'บันทึก เปิดใหม่ และดูใน OBS'],
 'Composer › Now Playing ปรับแต่งรายตัว': ['แหล่งข้อมูลเพลงและการเชื่อมต่อ', 'รูปแบบชื่อเพลง ศิลปิน และปกอัลบั้ม', 'แสดง/ซ่อนปก ภาพสำรอง และขนาด', 'ตัวหนังสือยาวเลื่อนและไม่ถูกตัดผิด', 'แสดง/ซ่อนแถบความคืบหน้าและเวลา', 'สี ฟอนต์ ขนาด พื้นหลัง และธีม', 'หยุดเพลง / เปลี่ยนเพลง / แสดงตรงกันใน OBS'],
 'Composer › ภาพ วิดีโอ ข้อความ ปรับแต่งรายตัว': ['Text: พิมพ์ข้อความ ฟอนต์ ขนาด สี เงา และพื้นหลัง', 'Text: จัดแนว ความทึบ ความเร็วและทิศทาง marquee', 'Text: ข้อความวิ่งผ่านขอบครบทั้งประโยคก่อนวน', 'Image: นำเข้า เปลี่ยนรูป ครอบ/พอดี ขนาด และความทึบ', 'Video: นำเข้า เล่น วน หยุด ปรับเสียง และขนาด', 'URL: กรอก/เปลี่ยนลิงก์และทดสอบใน OBS'],
 'Composer › Avatar / Donate ปรับแต่งรายตัว': ['PNG Avatar: เลือกภาพ idle / พูด / กะพริบ', 'PNG Avatar: เลือกแหล่งไมค์ ตรวจพูดและหยุดพูด', 'PNG Avatar: ขนาด ตำแหน่ง ความโปร่งใส และแสดงผล OBS', 'เป้าหมายโดเนต: ชื่อ ยอดเริ่มต้น ยอดปัจจุบัน และเป้าหมาย', 'เป้าหมายโดเนต: สีแถบ ตัวเลข ฟอนต์ และธีม', 'เปลี่ยนยอด บันทึก แล้วเปิดใหม่'],
 'Composer › กิจกรรม ปรับแต่งรายตัว': ['Replie: เพิ่ม/แก้/ลบคำสั่ง เลือกข้อความ ภาพ หรือ Combo', 'Replie: เวลาปรากฏ แสดงเต็มจอ และปิดเมื่อหมดเวลา', 'ASK: สร้างคำถาม ตัวเลือก เริ่ม/หยุด ดูผล', 'Giveaway: กำหนดโค้ด เริ่มรับชื่อ ล้างชื่อ สุ่มและแสดงผล', 'Randomizer: แก้รายการ เลือกแต่ละรูปแบบสุ่ม และแสดงผล', 'Playroom: เพิ่ม/แก้/ลบคำสั่ง กำหนดสื่อและทดสอบ', 'Emote Party: จำนวน ความเร็ว ทิศทาง ขนาดและเวลาสิ้นสุด', 'ทุกกิจกรรม: พักแล้ว Overlay โปร่งใส / Composer และ OBS ตรงกัน'],
 'ตั้งค่า › การบันทึกและรีสตาร์ต': ['ทุกหมวด: เปลี่ยนค่า บันทึก ปิดหน้าต่าง เปิดใหม่', 'ทุกหมวด: ยกเลิกแล้วค่าไม่เปลี่ยน', 'ตั้งค่าเสียง / ภาษา / ลักษณะหน้าจอคงอยู่เมื่อเปิดโปรแกรมใหม่', 'OBS / แพลตฟอร์ม / การเชื่อมต่ออัตโนมัติคงอยู่ตามที่ตั้ง', 'เปลี่ยนขนาดตัวอักษรใหญ่สุดแล้วข้อความ ปุ่ม และช่องกรอกไม่ล้น'],
})
for group, entries in manual.items():
    for label in entries:
        add(group, label, hint='ทดสอบการใช้งานจริงและการแสดงผลที่เกี่ยวข้อง', edition='full' if group.startswith('RVC') else 'both', paused=group=='พักไว้ตามที่ตกลง')

payload = {'schema':'bp3-feature-catalog-v1', 'generated_from':'src/index.html และรายการพฤติกรรมจาก HANDOFF/ข้อกำหนด',
           'groups':[{'name':name, 'items':items} for name, items in groups.items()]}
(OUT / 'catalog.json').write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding='utf-8')
embedded = json.dumps(payload, ensure_ascii=False, separators=(',', ':')).replace('<', '\\u003c')
(OUT / 'index.html').write_text((OUT / 'template.html').read_text(encoding='utf-8').replace('__CATALOG__', embedded), encoding='utf-8')
print('Groups:', len(groups), 'Items:', sum(map(len, groups.values())))
