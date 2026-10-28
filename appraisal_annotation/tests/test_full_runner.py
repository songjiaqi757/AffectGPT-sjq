import copy,json,sys,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import annotate_full as full
from annotate import DIMS,validate

def sample(sid='test'):
 return dict(sample_id=sid,text=dict(chinese='原文',english='Original'),audio_path='a',video_path='v',
  source_group_id=sid,source_video_id=None,source_status='unknown',data_role='pseudo_train',audio_duration=2.,visual_duration=2.)
def annotation():
 return dict(event_context='An observable event',dimensions=[dict(dimension_id=d,state=None,valid=False,
  evidence='',evidence_modalities=[],unknown_reason='insufficient_evidence') for d in DIMS])
class FullTests(unittest.TestCase):
 def setUp(self):
  full.HALT.clear();full.scheduler.HALT_REASON=''
  self.temp=tempfile.TemporaryDirectory();self.root=Path(self.temp.name)
  for d in ['annotations','teacher_raw','inputs','failed','media/audio','media/video','upload_cache']:(self.root/d).mkdir(parents=True)
 def tearDown(self):self.temp.cleanup();full.HALT.clear()
 def queue(self):
  q=full.JointQueue(self.root);q.initialize([sample('a'),sample('b')]);return q
 def test_one_joint_task_per_sample(self):
  q=self.queue();self.assertEqual(q.snapshot()['counts']['pending'],2)
  self.assertEqual(q.claim()['modality'],'joint')
 def test_restart_recovers_running(self):
  q=self.queue();q.claim();q.db.close();q=full.JointQueue(self.root);q.initialize([sample('a'),sample('b')])
  self.assertEqual(q.snapshot()['counts']['pending'],2)
 def test_success_persists_dimensions(self):
  q=self.queue();q.success('a',annotation());snap=q.snapshot()
  self.assertEqual((snap['successful_samples'],snap['valid_dimension_count'],snap['invalid_dimension_count']),(1,0,6))
  self.assertEqual(q.claim()['sid'],'b')
 def test_failed_never_counts_as_semantic_unknown(self):
  q=self.queue();q.mark('a','joint','failed','network',True);snap=q.snapshot()
  self.assertEqual((snap['counts']['failed'],snap['invalid_dimension_count']),(1,0))
 def test_retry_excludes_nonretryable_and_six_attempts(self):
  q=self.queue();q.mark('a','joint','failed','bad',False);q.mark('b','joint','failed','schema',True)
  self.assertEqual(q.recover_retries(),1)
  for _ in range(6):q.next_attempt('b','joint')
  q.mark('b','joint','failed','schema',True);self.assertEqual(q.recover_retries(),0)
 def test_attempt_usage_includes_failures(self):
  q=self.queue();q.attempt('a','joint',1,200,dict(prompt_tokens=10,completion_tokens=3,total_tokens=13),'invalid_output')
  self.assertEqual(q.snapshot()['usage_including_failed_generations']['total_tokens'],13)
 def test_export_keeps_failed_distinct(self):
  q=self.queue();q.mark('a','joint','failed','bad',True)
  full.export(self.root,[sample('a'),sample('b')],q)
  import csv
  with (self.root/'labels.csv').open(encoding='utf-8-sig') as f:rows=list(csv.DictReader(f))
  self.assertEqual(len(rows),12)
  self.assertTrue(all(r['state']=='' and r['valid']=='' and r['unknown_reason']=='' for r in rows))
  self.assertEqual(rows[0]['request_status'],'technical_failure')
 def test_joint_payload_and_private_transport(self):
  a=self.root/'media/audio/a.wav';v=self.root/'media/video/a.mp4';a.write_bytes(b'fullwav');v.write_bytes(b'x'*7_200_000)
  am=dict(duration_sec=2.,submitted_wav_sha256=full.media.sha(a.read_bytes()))
  vm=dict(submitted_video=dict(duration=2.,width=320,height=240),submitted_video_path=str(v),submitted_video_sha256=full.media.sha(v.read_bytes()))
  protocol=dict(prompt_sha256='frozen',generation=dict(temperature=0,modalities=['text']))
  uploads=[]
  def upload(path,key,cache):uploads.append(Path(path));return 'oss://private/test.mp4'
  with patch.object(full,'restore_inputs',return_value=(a,v,am,vm)):
   data,meta,private=full.build(sample(),protocol,'Exact prompt','credential',self.root,upload)
  body=json.loads(data);content=body['messages'][0]['content']
  self.assertEqual([x['type'] for x in content],['text','input_audio','video_url'])
  self.assertEqual(content[2]['video_url']['url'],'oss://private/test.mp4')
  self.assertEqual(uploads,[v]);self.assertTrue(private);self.assertFalse(meta['forbidden_inputs_included'])
  runtime=json.loads(content[0]['text'].split('\nRuntime input:\n')[1])
  self.assertEqual(set(runtime),{'sample_id','available_modalities','text','audio','video'})
 def test_success_cache_never_repeats_model(self):
  cfg=dict(workers=32,rpm=360,tpm=1600000,read_timeout_seconds=240)
  runner=full.Runner(self.root,[sample()],{},cfg,'prompt','credential')
  runner.queue.initialize([sample()])
  (self.root/'annotations/test.json').write_text(json.dumps(dict(annotation=annotation())))
  runner.transport=lambda *a,**k: (_ for _ in ()).throw(AssertionError('Unexpected model call'))
  runner.task(runner.queue.claim());self.assertEqual(runner.queue.snapshot()['successful_samples'],1)
 def test_http_policy(self):
  self.assertEqual(full.scheduler.classify_http(401,{}),('fatal',False))
  self.assertEqual(full.scheduler.classify_http(429,{'message':'Allocated quota exceeded'}),('rate_limit',True))
  self.assertEqual(full.scheduler.classify_http(400,{}),('request_rejected',False))
if __name__=='__main__':unittest.main()
