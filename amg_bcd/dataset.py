import collections
from amg_runtime.common import canonical,require
from amg_finetune_nogc.dataset import GraphContinueDataset as Original
from .common import evidence_for
from .policy import make_tokens
class GraphContinueDataset(Original):
 def __init__(self,run,model_cfg,subset_ids=None):
  super().__init__(run,model_cfg,subset_ids);self.variant=self.plan["active_variant"];self.calls=collections.Counter()
 def evidence(self,sample):return evidence_for(self.run,self.variant,sample,training=True)
 def text_example(self,index,label_type):
  sample=self.annotation[index];drop=None
  if self.variant in ("C","D"):
   sid=sample["sample_id"];self.calls[sid]+=1;drop=int(canonical([42,sid,self.calls[sid]])[:13],16)/float(16**13)
  return make_tokens(self,sample,self.evidence(sample),label_type,self.limits,self.variant,drop)
