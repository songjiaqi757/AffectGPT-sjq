import collections,copy,torch
from amg_finetune_nogc.dataset import GraphContinueDataset as Original
from amg_finetune_nogc.prompts import make_tokens
from amg_runtime.common import read,canonical,require
def graph_enabled(sample_id,visit,variant):
 return variant=="C" or int(canonical([42,sample_id,visit])[:13],16)/float(16**13)<0.5
class GraphContinueDataset(Original):
 def __init__(self,run,model_cfg,subset_ids=None):
  super().__init__(run,model_cfg,subset_ids);self.variant=self.plan["active_variant"];self.visits=collections.Counter()
  rows=read(self.run/"polarity_labels.json");self.polarity={x["sample_id"]:x for x in rows}
  require(set(self.polarity)=={x["sample_id"] for x in read(self.run/"train_records.json")},"Polarity label membership mismatch")
 def text_example(self,index,label_type):
  sample=self.annotation[index];sid=sample["sample_id"];self.visits[sid]+=1
  keep=graph_enabled(sid,self.visits[sid],self.variant);ev=super().evidence(sample)
  if not keep:
   ev=copy.deepcopy(ev);ev["fallback"]["required"]=True
  prompt,target,text,info=make_tokens(self,sample,ev,label_type,self.limits)
  info.update(variant=self.variant,graph_requested=keep,graph_dropout=not keep,sample_visit=self.visits[sid])
  return prompt,target,text,info
 def __getitem__(self,index):
  item=super().__getitem__(index);row=self.polarity[item["sample_id"]]
  item["polarity_label"]=row["polarity_id"] if row["valid_for_polarity_loss"] else -100
  return item
 def collater(self,instances):
  batch=super().collater(instances);batch["polarity_labels"]=torch.tensor([x["polarity_label"] for x in instances],dtype=torch.long)
  return batch
