import json, os, sys, tempfile, functools, threading
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from playwright.sync_api import sync_playwright

root = Path(__file__).resolve().parents[1]
with tempfile.TemporaryDirectory() as tmp, sync_playwright() as p:
    server = ThreadingHTTPServer(('127.0.0.1', 0), functools.partial(SimpleHTTPRequestHandler, directory=str(root / 'quality_checklist')))
    threading.Thread(target=server.serve_forever, daemon=True).start()
    browser = p.chromium.launch(downloads_path=tmp)
    context = browser.new_context(accept_downloads=True)
    page = context.new_page()
    page.goto((root / 'quality_checklist' / 'index.html').as_uri() if os.environ.get('BP3_TEST_FILE') == '1' else f'http://127.0.0.1:{server.server_port}/index.html')
    page.locator('#edition').select_option('full')
    page.locator('#environment').fill('Full + OBS test')
    page.locator('#summary').fill('แก้ข้อเสียก่อน แล้วทดสอบซ้ำ')
    page.locator('#customLabel').fill('รายการเพิ่มเติมจากผู้ตรวจ')
    page.locator('#addCustom').click()
    custom = page.locator('#groups details').filter(has_text='รายการเพิ่มเติมโดยผู้ตรวจ')
    assert custom.locator('.title').inner_text() == 'รายการเพิ่มเติมจากผู้ตรวจ'
    page.locator('#search').fill('ระยะเวลารอคิว')
    section = page.locator('#groups details').first
    section.locator('summary').click()
    card = section.locator('.item').first
    item_id = card.get_attribute('data-id')
    card.locator('input[value=fail]').check()
    card.locator('.note').fill('อาการทดสอบ\nบรรทัดที่สอง <ปลอดภัย>')
    actual = os.environ.get('BP3_TEST_DOWNLOAD') == '1'
    if not actual:
        page.evaluate("URL.createObjectURL = blob => { window.__savedBlob = blob; return 'data:text/plain,test'; }; URL.revokeObjectURL = () => {}")
    path = Path(tmp) / 'review.json'
    if actual:
        with page.expect_download() as pending: page.locator('#exportJson').click()
        pending.value.save_as(path)
    else:
        page.locator('#exportJson').click()
        path.write_text(page.evaluate('window.__savedBlob.text()'), encoding='utf-8')
    review = json.loads(path.read_text(encoding='utf-8'))
    selected = next(i for i in review['items'] if i['id'] == item_id)
    assert review['schema'] == 'bp3-review-v1' and review['edition'] == 'full'
    assert selected['status'] == 'fail' and selected['note'].endswith('<ปลอดภัย>')
    assert review['summary'] == 'แก้ข้อเสียก่อน แล้วทดสอบซ้ำ'
    assert any(i['label'] == 'รายการเพิ่มเติมจากผู้ตรวจ' for i in review['items'])
    md = Path(tmp) / 'review.md'
    if actual:
        with page.expect_download() as pending: page.locator('#exportMd').click()
        pending.value.save_as(md)
    else:
        page.locator('#exportMd').click()
        md.write_text(page.evaluate('window.__savedBlob.text()'), encoding='utf-8')
    assert 'ใช้ไม่ได้' in md.read_text(encoding='utf-8')
    page.reload()
    assert page.locator('#summary').input_value() == review['summary']
    page.locator('#search').fill('ระยะเวลารอคิว')
    page.locator('#groups details').first.locator('summary').click()
    assert page.locator(f'[data-id="{item_id}"] input[value=fail]').is_checked()
    page.locator('#summary').fill('เปลี่ยนชั่วคราว')
    page.on('dialog', lambda dialog: dialog.accept())
    page.locator('#importFile').set_input_files(path)
    assert page.locator('#summary').input_value() == review['summary']
    page.locator('#search').fill('รายการเพิ่มเติมจากผู้ตรวจ')
    assert page.locator('#groups .item').count() == 1
    page.locator('#search').fill('ระยะเวลารอคิว')
    page.locator('#filter').select_option('fail')
    assert page.locator(f'[data-id="{item_id}"]').count() == 1
    page.locator('#importFile').set_input_files({'name':'invalid.json', 'mimeType':'application/json', 'buffer':b'{bad'})
    assert page.locator('#summary').input_value() == review['summary']
    assert 'เปิดไฟล์ไม่สำเร็จ' in page.locator('#notice').inner_text()
    print('PASS checklist: edit, auto-save, JSON/Markdown, reload, import, filter, invalid file' + ('; actual downloads verified' if actual else '; browser download not verified'))
    browser.close()
    server.shutdown()
    server.server_close()
