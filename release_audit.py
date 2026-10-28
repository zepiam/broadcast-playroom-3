"""Inspect a staged distribution for local user data before release.

This reads paths and metadata only. It does not modify or publish the package.
"""
import argparse,json,os
from pathlib import Path

PRIVATE_NAMES={
 'bot_accounts.dat','obs_connection.dat','dns_settings.json','clip_hotkey.json',
 'composer_layout.json','rvc_settings.json','log.txt','clip_markers.txt',
 'replace_words.json','.env','.env.local','.env.production',
}
PRIVATE_DIRS={'browser_profile','playroom_uploads','__pycache__'}
REVIEW_ASSETS={'men9ch-qr-500x500.png','promptpay_qr.png','sample_qr.png','truemoney_qr.png'}

def is_link_or_reparse(path):
 try:return path.is_symlink() or bool(getattr(path.lstat(),'st_file_attributes',0) & 0x400)
 except OSError:return True

def audit(root):
 root=Path(root).resolve(strict=True)
 if not root.is_dir():raise ValueError('Expected staged distribution directory')
 blocked=[];review=[];links=[]
 for folder,dirs,files in os.walk(root,followlinks=False):
  base=Path(folder)
  for name in dirs[:]:
   path=base/name;relative=path.relative_to(root).as_posix()
   if is_link_or_reparse(path):links.append(relative);dirs.remove(name)
   elif name.lower() in PRIVATE_DIRS:blocked.append(relative+'/');dirs.remove(name)
  for name in files:
   path=base/name;relative=path.relative_to(root).as_posix();lower=name.lower()
   if is_link_or_reparse(path):links.append(relative)
   elif lower in PRIVATE_NAMES or lower.endswith(('.pem','.pfx','.p12')) or (lower=='settings.json' and path.parent.name.lower()=='data'):blocked.append(relative)
   elif lower in REVIEW_ASSETS:review.append(relative)
 return {'blocked':sorted(blocked),'links':sorted(links),'review_assets':sorted(review),'passes_file_checks':not (blocked or links or review),'scope':'path names only; inspect credentials, contents and final package separately'}

def main():
 parser=argparse.ArgumentParser(description='Inspect a staged release for user-specific files and symlinks')
 parser.add_argument('directory');args=parser.parse_args()
 result=audit(args.directory);print(json.dumps(result,ensure_ascii=False,indent=2));return 0 if result['passes_file_checks'] else 1
if __name__=='__main__':raise SystemExit(main())
