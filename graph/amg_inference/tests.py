"""Meaningful CPU checks for GPU gating, checkpoint publication and exclusive claims."""
import io,pickle,tempfile,unittest
from graph_paths import Path
from amg_runtime.common import atomic_json,read,canonical
from .common import gate,checkpoint,acquire_job,locked
from .prepare import NumpyOnly
class QueueTests(unittest.TestCase):
 def setUp(self):self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name)
 def tearDown(self):self.tmp.cleanup()
 def test_gpu_gates_need_the_whole_assigned_queue(self):
  for gpu,epochs in [(0,[30,40,50]),(1,[35,45])]:
   f=self.root/f"gpu_{gpu}_queue_status.json"
   atomic_json(f,dict(state="running",completed=epochs[:-1]));self.assertFalse(gate(self.root,gpu))
   atomic_json(f,dict(state="failed",completed=epochs));self.assertFalse(gate(self.root,gpu))
   atomic_json(f,dict(state="complete",completed=epochs[:-1]));self.assertFalse(gate(self.root,gpu))
   atomic_json(f,dict(state="complete",completed=epochs));self.assertTrue(gate(self.root,gpu))
 def test_job_waits_for_published_epoch_and_cannot_be_claimed_twice(self):
  (self.root/"jobs").mkdir();p=dict(training_run=str(self.root))
  f=self.root/"jobs"/"one.json";j=dict(state="pending",attempts=0,base_epoch=30,epoch=31)
  atomic_json(f,j);self.assertIsNone(acquire_job(self.root,p))
  weight=self.root/"checkpoint.pth";weight.write_text("test fixture")
  atomic_json(self.root/"from_30/checkpoints.json",[dict(path=str(weight),epoch=31,sha256="fixture")])
  first=acquire_job(self.root,p);self.assertIsNotNone(first);self.assertIsNone(acquire_job(self.root,p))
  first[1].close();j=read(f);j.update(state="complete");atomic_json(f,j);self.assertIsNone(acquire_job(self.root,p))
 def test_crash_is_reclaimed_but_failed_attempts_bounded(self):
  (self.root/"jobs").mkdir();weight=self.root/"checkpoint.pth";weight.write_text("fixture")
  atomic_json(self.root/"from_30/checkpoints.json",[dict(path=str(weight),epoch=31,sha256="fixture")])
  f=self.root/"jobs"/"one.json";j=dict(state="running",attempts=2,base_epoch=30,epoch=31);atomic_json(f,j)
  claim=acquire_job(self.root,dict(training_run=str(self.root)));self.assertEqual(claim[2]["attempts"],3);claim[1].close()
  self.assertIsNone(acquire_job(self.root,dict(training_run=str(self.root))));self.assertEqual(read(f)["state"],"failed")
 def test_training_lock_excludes_inference(self):
  first=locked(self.root/"gpu.lock");self.assertIsNotNone(first);self.assertIsNone(locked(self.root/"gpu.lock"))
  first.close();second=locked(self.root/"gpu.lock");self.assertIsNotNone(second);second.close()
 def test_unsafe_pickle_global_is_rejected(self):
  data=pickle.dumps(Path("/tmp/fixture"))
  with self.assertRaises(pickle.UnpicklingError):NumpyOnly(io.BytesIO(data)).load()
 def test_source_probe_requires_new_tokens_with_embedded_multimodal_input(self):
  import torch
  from types import SimpleNamespace
  from transformers import GenerationConfig
  from transformers.generation.utils import GenerationMixin
  from .model import probe_generation_settings
  model=SimpleNamespace(config=SimpleNamespace(is_encoder_decoder=False))
  inputs=torch.empty(1,1536,1)
  old=GenerationConfig(max_new_tokens=1200,min_length=1200)
  GenerationMixin._prepare_generated_length(model,old,True,False,"inputs_embeds",0,inputs)
  self.assertEqual(old.min_length,0)
  new=GenerationConfig(**probe_generation_settings(dict(max_new_tokens=1200,min_length=1200)))
  GenerationMixin._prepare_generated_length(model,new,True,True,"inputs_embeds",0,inputs)
  self.assertEqual(new.min_length,1200);self.assertEqual(new.max_length,1200)
 def test_priority_phase_filters_claims_and_can_resume_remaining_queue(self):
  (self.root/"jobs").mkdir();weight=self.root/"checkpoint.pth";weight.write_text("fixture")
  atomic_json(self.root/"from_30/checkpoints.json",[dict(path=str(weight),epoch=31,sha256="fixture")])
  p=dict(training_run=str(self.root),plan_id="fixture")
  for jid in ["chosen","other"]:
   atomic_json(self.root/"jobs"/(jid+".json"),dict(state="pending",attempts=0,base_epoch=30,epoch=31,job_id=jid))
  atomic_json(self.root/"job_dispatch.json",dict(enabled=True,plan_id="fixture",job_ids=["chosen"]))
  claim=acquire_job(self.root,p);self.assertEqual(claim[2]["job_id"],"chosen")
  j=claim[2];j["state"]="complete";atomic_json(claim[0],j);claim[1].close()
  self.assertIsNone(acquire_job(self.root,p))
  atomic_json(self.root/"job_dispatch.json",dict(enabled=False))
  claim=acquire_job(self.root,p);self.assertEqual(claim[2]["job_id"],"other");claim[1].close()
if __name__=="__main__":unittest.main()
