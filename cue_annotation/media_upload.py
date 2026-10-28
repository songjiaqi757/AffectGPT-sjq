"""Private 48-hour provider upload; policy credentials remain in memory only."""
import json, os, time, threading
from pathlib import Path
from urllib.parse import urlparse
import requests
import annotate_api as core

POLICY_ENDPOINT='https://maas.qianwenaiapi.com/api/v1/uploads'
UPLOAD_SLOTS=threading.BoundedSemaphore(4)

def temporary_url(path,key,cache_dir):
    with UPLOAD_SLOTS:
        return _temporary_url(path,key,cache_dir)

def _temporary_url(path,key,cache_dir):
    path=Path(path);digest=core.sha(path.read_bytes())
    # Cache is scoped to account credential without persisting the credential.
    account=core.sha(key.encode())[:16]
    cache=Path(cache_dir)/f'{account}.{digest}.json'
    if cache.exists():
        saved=json.loads(cache.read_text())
        if saved['expires_unix']>time.time()+300 and saved['model']==core.MODEL:
            return saved['url']
    proxy=os.environ.get('QWEN_HTTPS_PROXY');proxies={'http':proxy,'https':proxy} if proxy else None
    for attempt in range(3):
        try:
            r=requests.get(POLICY_ENDPOINT,params={'action':'getPolicy','model':core.MODEL},
                headers={'Authorization':'Bearer '+key,'Content-Type':'application/json'},
                timeout=(20,60),proxies=proxies,allow_redirects=False)
            if r.status_code!=200:raise RuntimeError('Provider upload policy HTTP '+str(r.status_code))
            policy=r.json()['data'];host=policy['upload_host'];parsed=urlparse(host)
            assert parsed.scheme=='https' and parsed.hostname.endswith('.aliyuncs.com'), 'Unexpected provider upload host'
            assert policy['x_oss_object_acl']=='private', 'Upload must remain private'
            assert path.stat().st_size<=float(policy['max_file_size_mb'])*1024**2,'Provider upload file size exceeded'
            object_key=policy['upload_dir'].rstrip('/')+'/'+digest+path.suffix
            fields={'OSSAccessKeyId':policy['oss_access_key_id'],'policy':policy['policy'],
                'Signature':policy['signature'],'key':object_key,
                'x-oss-object-acl':'private','x-oss-forbid-overwrite':policy['x_oss_forbid_overwrite'],
                'success_action_status':'200'}
            uploaded_at=time.time()
            with path.open('rb') as f:
                result=requests.post(host,data=fields,files={'file':(path.name,f,'application/octet-stream')},
                    timeout=(120,300),proxies=proxies,allow_redirects=False)
            if result.status_code not in (200,204):raise RuntimeError('Provider file upload HTTP '+str(result.status_code))
            url='oss://'+object_key
            cache.parent.mkdir(parents=True,exist_ok=True)
            core.dump(cache,dict(url=url,model=core.MODEL,sha256=digest,bytes=path.stat().st_size,
                uploaded_unix=uploaded_at,expires_unix=uploaded_at+47*3600,access='private'))
            return url
        except (requests.RequestException,RuntimeError):
            if attempt==2:raise
            time.sleep(2**attempt)
