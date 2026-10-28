import json,os,sys,tempfile,threading,urllib.request,urllib.error
from pathlib import Path
from unittest.mock import patch
os.environ['BP3_EDITION']='lite';sys.path.insert(0,str(Path(__file__).resolve().parents[1]));sys.dont_write_bytecode=True
from http.server import ThreadingHTTPServer
import launch_dev,supporters_service
with tempfile.TemporaryDirectory(prefix='support-e2e-') as folder:
 launch_dev.LAYOUT_FILE=str(Path(folder)/'layout.json');launch_dev._LAYOUT_CACHE=None;server=ThreadingHTTPServer(('127.0.0.1',0),launch_dev.QuietHandler);threading.Thread(target=server.serve_forever,daemon=True).start();base=f'http://127.0.0.1:{server.server_port}'
 try:
  with patch.object(supporters_service.supporters_api,'redeem_truemoney_voucher',return_value={'ok':True,'tx_id':'fixture','amount':50}) as mock:
   payload=json.dumps({'action':'redeem','voucher':'https://gift.truemoney.com/campaign/?v=test'}).encode();url=base+'/api/supporters/action'
   req=urllib.request.Request(url,data=payload,headers={'Content-Type':'application/json','Origin':base});result=json.load(urllib.request.urlopen(req));assert result['ok'] and mock.call_count==1
   req=urllib.request.Request(url,data=payload,headers={'Content-Type':'application/json','Origin':'https://untrusted.example'})
   try:urllib.request.urlopen(req);assert False
   except urllib.error.HTTPError as error:assert error.code==403
   assert mock.call_count==1
  print('PASS real local endpoint routes mock redeem and rejects cross-origin submission')
 finally:server.shutdown();server.server_close()
