"""Check private upload isolation and expiry with fake HTTP only."""
import json,tempfile,time,unittest
from pathlib import Path
from unittest.mock import patch
import media_upload as upload

class Response:
    def __init__(self,body=None,status=200):self.body=body;self.status_code=status
    def json(self):return self.body

class Tests(unittest.TestCase):
    def test_private_upload_and_cache_never_store_credentials(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);video=root/'complete.mp4';video.write_bytes(b'complete file')
            policy=dict(upload_host='https://test.oss-cn-beijing.aliyuncs.com',upload_dir='private/temp',
                max_file_size_mb=1024,x_oss_object_acl='private',x_oss_forbid_overwrite='true',
                oss_access_key_id='TEMP_ACCESS_SECRET',signature='TEMP_SIGNATURE_SECRET',policy='TEMP_POLICY_SECRET')
            calls=[]
            def post(host,**kwargs):
                self.assertNotIn('headers',kwargs) # Never forward model API key to object storage.
                self.assertEqual(kwargs['data']['x-oss-object-acl'],'private')
                self.assertEqual(kwargs['files']['file'][1].read(),b'complete file')
                calls.append(host);return Response()
            with patch.object(upload.requests,'get',return_value=Response({'data':policy})),patch.object(upload.requests,'post',side_effect=post):
                first=upload.temporary_url(video,'MODEL_API_SECRET',root/'cache')
                self.assertEqual(first,upload.temporary_url(video,'MODEL_API_SECRET',root/'cache'))
            self.assertEqual(len(calls),1);self.assertTrue(first.startswith('oss://private/temp/'))
            saved=next((root/'cache').glob('*.json')).read_text()
            for secret in ('MODEL_API_SECRET','TEMP_ACCESS_SECRET','TEMP_SIGNATURE_SECRET','TEMP_POLICY_SECRET'):
                self.assertNotIn(secret,saved)
            self.assertLess(json.loads(saved)['expires_unix'],time.time()+48*3600)
    def test_public_upload_policy_is_rejected_before_sending_media(self):
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/'video.mp4';path.write_bytes(b'file')
            with patch.object(upload.requests,'get',return_value=Response({'data':{
                'upload_host':'https://test.oss-cn-beijing.aliyuncs.com','x_oss_object_acl':'public-read'}})),patch.object(upload.requests,'post') as post:
                with self.assertRaisesRegex(AssertionError,'private'):upload.temporary_url(path,'SECRET',Path(d)/'cache')
                post.assert_not_called()

if __name__=='__main__':unittest.main()
