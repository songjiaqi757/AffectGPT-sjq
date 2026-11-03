"""Failure, restart and export tests using fake transport. No paid calls."""
import json,csv,tempfile,unittest,threading,time,copy
from pathlib import Path
from unittest.mock import patch
import annotate_full as full

class Response:
    def __init__(self,status,body,headers=None):self.status_code=status;self.text=json.dumps(body);self.headers=headers or {}

class Tests(unittest.TestCase):
    def setUp(self):
        full.HALT.clear();full.HALT_REASON=''
        self.temp=tempfile.TemporaryDirectory();self.root=Path(self.temp.name)
        for name in ('annotations','teacher_raw','inputs','failed'):(self.root/name).mkdir()
        self.s=[dict(sample_id='s',text={'chinese':'你好','english':'Hello'},audio_path='unused',video_path='unused')]
        self.protocol=json.loads((full.core.CONFIG/'protocol.json').read_text())
        self.cfg=dict(workers=12,rpm=240,tpm=1600000)
        self.ids=json.loads((full.core.CONFIG/'ontology.json').read_text())['cue_ids']
        q=full.Queue(self.root);q.initialize(self.s);q.db.close()
        self.build=patch.object(full.core,'build',side_effect=self.fake_build);self.build.start()
    def tearDown(self):self.build.stop();self.temp.cleanup();full.HALT.clear()
    def fake_build(self,s,m,p,media_url=None):
        return json.dumps({'modality':m}).encode(),dict(sample_id='s',modality=m,request_sha256='hash',duration_sec=2)
    def valid(self,m='text'):
        obj=dict(sample_id='s',modality=m,labels={cue:dict(state='negative',evidence_note='') for cue in self.ids[m]})
        return Response(200,dict(model=full.core.MODEL,choices=[dict(finish_reason='stop',message={'content':json.dumps(obj)})],usage={'prompt_tokens':20,'completion_tokens':10,'total_tokens':30}))
    def runner(self,transport):
        r=full.Runner(self.root,self.s,self.protocol,self.cfg,'SECRET',transport=transport,sleeper=lambda _:None)
        r.limiter.reserve=lambda _: [0,100];return r
    def test_generic_quota_rate_limit_is_not_fatal(self):
        self.assertEqual(full.classify_http(429,{'error':{'message':'Allocated quota exceeded'}}),('rate_limit',True))
        self.assertEqual(full.classify_http(429,{'error':{'code':'insufficient_quota'}}),('fatal',False))
    def test_429_then_success_and_exact_attempt_accounting(self):
        replies=iter([Response(429,{'error':'rate limit'},{'Retry-After':'2'}),self.valid()])
        r=self.runner(lambda *a,**k:next(replies));job=r.queue.claim();r.task(job)
        self.assertEqual(r.queue.snapshot()['counts']['succeeded'],1)
        self.assertEqual(r.queue.snapshot()['http_attempts'],2);self.assertEqual(r.limiter.rate_events,1)
        self.assertFalse(full.HALT.is_set())
    def test_invalid_output_retries_then_unlabeled_export(self):
        r=self.runner(lambda *a,**k:Response(200,{'model':full.core.MODEL,'choices':[{'finish_reason':'length','message':{'content':'{}'}}]}))
        job=r.queue.claim();r.task(job);self.assertEqual(r.queue.snapshot()['counts']['failed'],1)
        self.assertFalse((self.root/'annotations/s.text.json').exists())
        full.export(self.root,self.s,self.ids,r.queue)
        with (self.root/'labels.csv').open() as f:rows=list(csv.DictReader(f))
        self.assertEqual(len(rows),42);self.assertTrue(all(x['state']=='unlabeled' and x['mask']=='0' and not x['y'] for x in rows))
    def test_persistent_success_skips_new_paid_request(self):
        called=[]
        r=self.runner(lambda *a,**k:(called.append(1) or self.valid()));job=r.queue.claim();r.task(job)
        r.queue.mark('s','text','pending');r.task(r.queue.claim());self.assertEqual(len(called),1)
    def test_restart_recovers_only_running_tasks(self):
        q=full.Queue(self.root);job=q.claim();q.mark('s','audio','succeeded');q.initialize(self.s)
        counts=q.snapshot()['counts'];self.assertEqual(counts['succeeded'],1);self.assertEqual(counts['pending'],2)
    def test_permanent_400_is_not_retried(self):
        calls=[];r=self.runner(lambda *a,**k:(calls.append(1) or Response(400,{'error':'Invalid audio'})))
        r.task(r.queue.claim());self.assertEqual(len(calls),1);self.assertEqual(r.queue.recover_retries(),0)
    def test_bounded_six_attempts(self):
        r=self.runner(lambda *a,**k:Response(503,{'error':'temporary'}));r.task(r.queue.claim())
        r.queue.recover_retries()
        # Claim the same failed text task, rather than other pending modalities.
        r.queue.mark('s','audio','succeeded');r.queue.mark('s','visual','succeeded');r.task(r.queue.claim())
        self.assertEqual(r.queue.snapshot()['http_attempts'],6);self.assertEqual(r.queue.recover_retries(),0)
    def test_auth_error_halts_and_key_not_persisted(self):
        r=self.runner(lambda *a,**k:Response(401,{'error':'SECRET bad key'}));r.task(r.queue.claim())
        self.assertTrue(full.HALT.is_set())
        for p in self.root.rglob('*.json'):self.assertNotIn('SECRET',p.read_text())
    def test_limiter_paces_requests(self):
        limiter=full.RateLimiter(rpm=1200,tpm=10000)
        start=time.monotonic();limiter.reserve(10);limiter.reserve(10)
        self.assertGreaterEqual(time.monotonic()-start,.045)
    def test_dynamic_pool_completes_every_modality_once(self):
        calls=[]
        def transport(*a,**kwargs):
            m=json.loads(kwargs['data'])['modality'];calls.append(m);return self.valid(m)
        r=self.runner(transport)
        with patch.object(full.time,'sleep',lambda _:None):result=r.run()
        self.assertTrue(result['complete'])
        self.assertEqual(sorted(calls),['audio','text','visual'])
        self.assertEqual(r.queue.snapshot()['counts'],{'succeeded':3})
    def test_hot_limits_update_and_preserve_adaptive_backoff(self):
        r=self.runner(lambda *a,**k:self.valid())
        r.limiter.penalize(1)
        config={**self.cfg,'workers':32,'rpm':360}
        (self.root/'runtime_config.json').write_text(json.dumps(config))
        r.refresh_runtime()
        self.assertEqual(r.cfg['workers'],32)
        self.assertEqual(r.limiter.snapshot()['request_concurrency'],32)
        self.assertEqual(r.limiter.rpm,180)
        r.refresh_runtime();self.assertEqual(r.limiter.rpm,180)
    def test_hot_lowering_does_not_launch_disabled_worker(self):
        r=self.runner(lambda *a,**k:(_ for _ in ()).throw(AssertionError('Should not request')))
        r.cfg['workers']=1;r.worker(slot=2)
        self.assertEqual(r.queue.snapshot()['counts']['pending'],3)
    def test_invalid_hot_limits_leave_current_configuration(self):
        r=self.runner(lambda *a,**k:self.valid())
        (self.root/'runtime_config.json').write_text(json.dumps({**self.cfg,'workers':500}))
        r.refresh_runtime();self.assertEqual(r.cfg['workers'],12)
    def test_machine_tear_positive_uses_original_model_label(self):
        obj=json.loads(self.valid('visual').text)['choices'][0]['message']['content'];obj=json.loads(obj)
        obj['labels']['VIS_TEARING_PRESENT']={'state':'positive','evidence_note':'possible tear'}
        rec=full.reviewed_record(obj,{},self.protocol,{},1,1)
        self.assertEqual(rec['annotation']['labels']['VIS_TEARING_PRESENT'],obj['labels']['VIS_TEARING_PRESENT'])
        self.assertNotIn('quality_review',rec)
        self.assertNotIn('label_overrides',rec)
    def test_private_upload_header_and_successful_retry(self):
        received=[]
        (self.root/'transport_overrides.json').write_text(json.dumps({'s.visual':{'transport':'provider_private_temporary_oss','force_h264':True}}))
        def transport(*a,**kwargs):
            received.append(kwargs['headers']);return self.valid('visual')
        r=self.runner(transport);r.queue.mark('s','text','succeeded');r.queue.mark('s','audio','succeeded')
        with patch.object(full.core,'prepare_video',return_value={'submitted_video_path':'complete.mp4'}) as prepare,patch.object(full,'temporary_url',return_value='oss://private/file.mp4'):
            r.task(r.queue.claim())
        self.assertEqual(received[0]['X-DashScope-OssResourceResolve'],'enable')
        self.assertEqual(r.queue.snapshot()['counts'],{'succeeded':3})
        prepare.assert_called_once_with(self.s[0],force_h264=True,allow_large=True)
    def test_repair_excludes_moderation_and_short_video(self):
        from repair_failed import remedy
        self.assertIsNone(remedy('visual','data_inspection_failed provided URL does not appear to be valid'))
        self.assertIsNone(remedy('visual','The video file is too short.'))
        self.assertFalse(remedy('visual','Base64 budget')['force_h264'])
        self.assertTrue(remedy('visual','The provided URL does not appear to be valid')['force_h264'])
    def test_upload_network_failure_remains_retryable_without_model_attempt(self):
        (self.root/'transport_overrides.json').write_text(json.dumps({'s.visual':{'transport':'provider_private_temporary_oss'}}))
        calls=[];r=self.runner(lambda *a,**k:calls.append(1))
        r.queue.mark('s','text','succeeded');r.queue.mark('s','audio','succeeded')
        with patch.object(full.core,'prepare_video',return_value={'submitted_video_path':'complete.mp4'}),patch.object(full,'temporary_url',side_effect=full.requests.exceptions.ProxyError('upload timed out')):
            r.task(r.queue.claim())
        self.assertEqual(calls,[]);self.assertEqual(r.queue.snapshot()['http_attempts'],0)
        self.assertEqual(r.queue.recover_retries(),1)
    def test_explicit_single_request_retry_does_not_repeat_transient_error(self):
        calls=[]
        r=self.runner(lambda *a,**k:(calls.append(1) or Response(503,{'error':'temporary'})))
        r.task(r.queue.claim(),maximum_requests=1)
        self.assertEqual(len(calls),1)
        self.assertEqual(r.queue.snapshot()['http_attempts'],1)

if __name__=='__main__':unittest.main()
