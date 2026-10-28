import collections,copy,torch
from amg_finetune_nogc.dataset import GraphContinueDataset as Original
from .policy import make_tokens
from .common import evidence_for
from amg_runtime.common import read,canonical,require
def graph_enabled(sample_id,visit,variant):
 return variant=="C" or int(canonical([42,sample_id,visit])[:13],16)/float(16**13)<0.5
class GraphContinueDataset(Original):
 def __init__(self,run,model_cfg,subset_ids=None):
  super().__init__(run,model_cfg,subset_ids);self.variant=self.plan["active_variant"];self.visits=collections.Counter()
  self.oof_inventory=read(self.plan["oof_cache_inventory_path"])
  rows=read(self.run/"polarity_labels.json");self.polarity={x["sample_id"]:x for x in rows}
  require(set(self.polarity)=={x["sample_id"] for x in read(self.run/"train_records.json")},"Polarity label membership mismatch")
 def evidence(self,sample):return evidence_for(self.run,self.variant,sample,training=True,expected_cache_id=self.oof_inventory[sample["sample_id"]])
 def text_example(self,index,label_type):
  sample=self.annotation[index];sid=sample["sample_id"];self.visits[sid]+=1
  keep=graph_enabled(sid,self.visits[sid],self.variant);ev=self.evidence(sample)
  prompt,target,text,info=make_tokens(self,sample,ev,label_type,self.limits,self.variant,None if keep else 0.0)
  info.update(variant=self.variant,graph_requested=keep,graph_dropout=not keep,sample_visit=self.visits[sid])
  return prompt,target,text,info
 def __getitem__(self,index):
  item=super().__getitem__(index);row=self.polarity[item["sample_id"]]
  item["polarity_label"]=row["polarity_id"] if row["valid_for_polarity_loss"] else -100
  return item
 def collater(self,instances):
  batch=super().collater(instances);batch["polarity_labels"]=torch.tensor([x["polarity_label"] for x in instances],dtype=torch.long)
  return batch
