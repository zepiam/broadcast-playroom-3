"""Local adapter for the supplied supporters API; no payments are submitted without a user action."""
import base64
import binascii
import math
import os
import re
import tempfile
from urllib.parse import urlparse
import supporters_api

SOURCE='Broadcast Playroom'
def fetch():return supporters_api.fetch_supporters(timeout=8,retries=1)
def action(data):
    kind=data.get('action')
    if kind=='redeem':
        text=str(data.get('voucher','')).strip()
        match=re.search(r'https://gift\.truemoney\.com/campaign/\?v=[A-Za-z0-9_-]+',text,re.I)
        if not match:return {'ok':False,'error':'กรุณาตรวจสอบลิงก์ซอง TrueMoney'}
        return supporters_api.redeem_truemoney_voucher(match.group(0),source=SOURCE)
    if kind=='complete':
        tx=str(data.get('tx_id','')).strip();name=str(data.get('name','')).strip()
        if not tx or not name:return {'ok':False,'error':'กรุณากรอกชื่อผู้สนับสนุน'}
        return supporters_api.complete_truemoney_supporter(tx_id=tx,name=name,channel_url=str(data.get('channel_url','')).strip(),message=str(data.get('message','')).strip()[:200],platform=str(data.get('platform','')).strip(),source=SOURCE)
    if kind=='submit':
        name=str(data.get('name','')).strip();method=str(data.get('method',''));currency=str(data.get('currency','THB')).upper()
        try:amount=float(data.get('amount',0))
        except (ValueError,TypeError):amount=0
        if not name or not math.isfinite(amount) or amount<1 or amount>9999999 or method not in ('slip','manual') or currency not in ('THB','USD','JPY','EUR'):
            return {'ok':False,'error':'กรุณากรอกชื่อและยอดเงินให้ครบถ้วน'}
        params={'name':name,'amount':amount,'currency':currency,'message':str(data.get('message','')).strip()[:200], 'channel':'bank','method':method,'bank':str(data.get('bank','')).strip(), 'transfer_date':str(data.get('transfer_date','')).strip(),'transfer_time':str(data.get('transfer_time','')).strip(), 'platform':str(data.get('platform','')).strip(), 'channel_url':str(data.get('channel_url','')).strip(),'source':SOURCE}
        if method=='manual' and not all(params[x] for x in ('bank','transfer_date','transfer_time')):return {'ok':False,'error':'กรุณากรอกธนาคาร วันที่ และเวลา'}
        try:
            from machine_id import get_machine_id
            params['machine_id']=get_machine_id()
        except Exception:params['machine_id']=''
        if method=='slip':
            try:
                encoded=str(data.get('slip',''));mime,encoded=encoded.split(',',1)
                extensions={'data:image/png;base64':'.png','data:image/jpeg;base64':'.jpg','data:image/webp;base64':'.webp','data:image/gif;base64':'.gif'}
                if mime not in extensions:raise ValueError()
                image=base64.b64decode(encoded,validate=True)
                if not 0<len(image)<=5*1024*1024:raise ValueError()
            except (ValueError,binascii.Error):return {'ok':False,'error':'กรุณาเลือกรูปสลิป PNG, JPG, WebP หรือ GIF ขนาดไม่เกิน 5 MB'}
            path=None
            try:
                with tempfile.NamedTemporaryFile(suffix=extensions[mime],delete=False) as f:path=f.name;f.write(image)
                return supporters_api.submit_supporter(slip_path=path,**params)
            finally:
                if path:
                    try:os.unlink(path)
                    except OSError:pass
        return supporters_api.submit_supporter(**params)
    return {'ok':False,'error':'คำขอไม่ถูกต้อง'}
