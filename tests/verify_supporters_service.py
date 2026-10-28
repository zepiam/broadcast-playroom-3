import base64,sys
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]));sys.dont_write_bytecode=True
import supporters_service as service
with patch.object(service.supporters_api,'redeem_truemoney_voucher',return_value={'ok':True,'tx_id':'fixture','amount':50}) as redeem:
 assert not service.action({'action':'redeem','voucher':'https://example.com/?v=no'})['ok']
 assert service.action({'action':'redeem','voucher':'ข้อความ https://gift.truemoney.com/campaign/?v=abc123 ส่งให้แล้ว'})['ok']
 assert redeem.call_args.args[0]=='https://gift.truemoney.com/campaign/?v=abc123' and redeem.call_args.kwargs['source']=='Broadcast Playroom'
with patch.object(service.supporters_api,'complete_truemoney_supporter',return_value={'ok':True}) as complete:
 assert service.action({'action':'complete','tx_id':'fixture','name':'Tester','platform':'twitch'})['ok'];assert complete.call_args.kwargs['source']=='Broadcast Playroom'
with patch('machine_id.get_machine_id',return_value='fixture-machine'),patch.object(service.supporters_api,'submit_supporter',return_value={'ok':True}) as submit:
 assert service.action({'action':'submit','method':'manual','name':'Tester','amount':20,'bank':'Bank','transfer_date':'2026-10-27','transfer_time':'10:30'})['ok'];assert submit.call_args.kwargs['source']=='Broadcast Playroom'
 payload=base64.b64encode(b'fixture image').decode('ascii');assert service.action({'action':'submit','method':'slip','name':'Tester','amount':20,'slip':'data:image/png;base64,'+payload})['ok'];path=Path(submit.call_args.kwargs['slip_path']);assert not path.exists()
 assert not service.action({'action':'submit','method':'slip','name':'Tester','amount':20,'slip':'data:text/html;base64,'+payload})['ok']
print('PASS mocked redeem/complete/manual/slip, source and input validation, temporary cleanup')
