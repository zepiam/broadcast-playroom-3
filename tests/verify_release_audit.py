import sys,tempfile
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]));sys.dont_write_bytecode=True
from release_audit import audit
with tempfile.TemporaryDirectory() as tmp:
 root=Path(tmp);(root/'bin').mkdir();(root/'bin'/'app.exe').write_bytes(b'dummy');assert audit(root)['passes_file_checks']
 (root/'assets').mkdir();(root/'assets'/'sample_qr.png').write_bytes(b'dummy');assert audit(root)['review_assets']==['assets/sample_qr.png'] and not audit(root)['passes_file_checks']
 (root/'data').mkdir();(root/'data'/'settings.json').write_text('private');(root/'bot_accounts.dat').write_bytes(b'private')
 result=audit(root);assert not result['passes_file_checks'] and 'data/settings.json' in result['blocked'] and 'bot_accounts.dat' in result['blocked']
 assert (root/'data'/'settings.json').read_text()=='private'
 print('PASS read-only staged release audit catches user data and flags QR for review')
