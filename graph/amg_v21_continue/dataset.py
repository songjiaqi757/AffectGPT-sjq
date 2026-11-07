import collections
from amg_runtime.common import read,canonical,require
from amg_finetune_nogc.dataset import GraphContinueDataset as Original
from .policy import make_tokens
class GraphContinueDataset(Original):
 def __init__(self,run,model_cfg,subset_ids=None):
  super().__init__(run,model_cfg,subset_ids);self.calls=collections.Counter();self.evidence_rows={}
  for k in range(5):
   with (self.run/"folds"/str(k)/"evidence.jsonl").open() as f:
    for line in f:
     import json
     x=json.loads(line);require(x["sample_id"] not in self.evidence_rows,"Duplicate OOF sample");self.evidence_rows[x["sample_id"]]=x
  require(len(self.evidence_rows)==self.plan["training_count"],"Incomplete OOF cache")
 def text_example(self,index,label_type):
  sample=self.annotation[index];sid=sample["sample_id"];self.calls[sid]+=1
  drop=int(canonical([42,sid,self.calls[sid]])[:13],16)/float(16**13)
  return make_tokens(self,sample,self.evidence_rows[sid],label_type,self.limits,drop)
