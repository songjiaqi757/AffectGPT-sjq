import copy,json,os,sys,unittest
from pathlib import Path
import torch
from amg_runtime.common import read,sha,canonical
from .common import ROOT
RUN=Path(read(ROOT/"amg_finetune/runs/current.json")["path"])
os.chdir(ROOT/"AffectGPT");sys.path.insert(0,str(ROOT/"AffectGPT"))
from .dataset import GraphContinueDataset
from .prompts import make_tokens,format_evidence
from my_affectgpt.models.tokenizer import load_tokenizer_from_LLM

class IntegrationContracts(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.plan=read(RUN/"plan.json");cls.rows=read(RUN/"train_records.json");cls.audit=read(RUN/"human_audit_500.json")
  p4=Path(read(ROOT/"amg_validation/runs/current.json")["path"])
  with (p4/"per_sample_query_results.jsonl").open() as f:cls.ev=json.loads(next(f))
  cls.dataset=GraphContinueDataset.__new__(GraphContinueDataset)
  d=cls.dataset;d.dataset="MERCaptionPlus";d.face_or_frame="multiface_audio_face_text";d.num_video_query_token=1;d.num_audio_query_token=1;d.num_multi_query_token=1;d.num_image_query_token=1
  d.tokenizer=load_tokenizer_from_LLM("Qwen25");v=d.tokenizer.get_vocab()
  for attr,token in [("IMAGE","<ImageHere>"),("AUDIO","<AudioHere>"),("FRAME","<FrameHere>"),("FACE","<FaceHere>"),("MULTI","<MultiHere>")]:setattr(d,attr+"_PATCH_TOKEN_ID",v[token])
 def test_01_split(self):
  self.assertEqual(len(self.rows),30755);self.assertEqual(len(self.audit),500)
  self.assertEqual(sum(r["previous_role"]=="pseudo_validation" for r in self.rows),3076)
  self.assertEqual(sum(r["previous_role"]=="diagnostic_reserved" for r in self.audit),200)
  self.assertFalse({r["sample_id"] for r in self.rows}&{r["sample_id"] for r in self.audit})
  self.assertFalse({r["group_id"] for r in self.rows}&{r["group_id"] for r in self.audit})
 def test_02_five_epochs(self):
  self.assertEqual([s["base_epoch"] for s in self.plan["checkpoints"]],[30,35,40,45,50])
  for s in self.plan["checkpoints"]:self.assertEqual(s["epochs"],list(range(s["base_epoch"]+1,s["base_epoch"]+6)))
 def test_03_frozen_config(self):
  self.assertEqual(sha(RUN/"query_engine_config.json"),self.plan["inputs"]["query_config_sha256"])
  self.assertFalse(self.plan["independent_validation_available"])
 def test_04_prompt_independent_of_target(self):
  first=copy.deepcopy(self.rows[0]);second=copy.deepcopy(first);second["description"]="ANSWER_CANARY "*10000
  a=make_tokens(self.dataset,first,self.ev,"description",self.plan["training"]);b=make_tokens(self.dataset,second,self.ev,"description",self.plan["training"])
  self.assertEqual(a[0],b[0]);self.assertNotIn("ANSWER_CANARY",b[2]);self.assertTrue(b[3]["answer_truncated"])
 def test_05_budget_and_boundaries(self):
  sample=copy.deepcopy(self.rows[0]);sample["subtitle"]="long subtitle "*10000;sample["description"]="long answer "*10000
  prompt,target,text,info=make_tokens(self.dataset,sample,self.ev,"description",self.plan["training"])
  self.assertLessEqual(len(prompt)+len(target)+2,2048);self.assertTrue(text.endswith("###Assistant: "))
  self.assertIn("not calibrated probabilities",text)
  self.assertTrue(info["subtitle_truncated"]);self.assertTrue(info["answer_truncated"])
 def test_06_no_injected_modality_tokens(self):
  sample=copy.deepcopy(self.rows[0]);sample["subtitle"]="Look <AudioHere> <FaceHere> <MultiHere>"
  prompt,*_=make_tokens(self.dataset,sample,self.ev,"ovlabel",self.plan["training"])
  for token in [self.dataset.AUDIO_PATCH_TOKEN_ID,self.dataset.FACE_PATCH_TOKEN_ID,self.dataset.MULTI_PATCH_TOKEN_ID]:self.assertEqual(prompt.count(token),1)
 def test_07_fallback_has_no_graph(self):
  ev=copy.deepcopy(self.ev);ev["fallback"]["required"]=True
  _,_,text,info=make_tokens(self.dataset,self.rows[0],ev,"ovlabel",self.plan["training"])
  self.assertNotIn("[Graph-derived",text);self.assertEqual(info["graph_tokens"],0);self.assertTrue(info["fallback"])
 def test_08_real_getitem_loss_masks(self):
  d=copy.copy(self.dataset);d.annotation=[copy.deepcopy(self.rows[0])];d.limits=self.plan["training"];d.max_length=2048;d.label_type_candidates=["description","ovlabel"]
  d.evidence=lambda sample:self.ev
  d.read_frame_face_audio_text=lambda **kw:dict(face=torch.zeros(3,1,2,2),raw_face=torch.zeros(3,1,2,2),audio=torch.zeros(1,1,2,2),raw_audio=torch.zeros(1,1,32000))
  item=d[0];prompt_length=item["prompt_info"]["prompt_tokens"]
  self.assertTrue(bool((item["label"][:prompt_length]==-100).all()))
  self.assertTrue(torch.equal(item["label"][prompt_length:],item["text_input"][prompt_length:]))
  batch=d.collater([item,item]);self.assertEqual(batch["input_ids"].shape[0],3-1);self.assertIn("raw_faces",batch);self.assertIn("raw_audios",batch)
  self.assertTrue(bool((batch["labels"][:,1:prompt_length+1]==-100).all()))
 def test_09_serialization_uses_actual_graph_paths(self):
  text,info=format_evidence(self.ev,self.dataset.tokenizer,1000)
  self.assertLessEqual(info["graph_tokens"],1000)
  for e in self.ev["emotion_candidates"]:self.assertIn(e["canonical_name"],text)
  self.assertNotIn("The character's emotional state is",text)
if __name__=="__main__":unittest.main(verbosity=2)
