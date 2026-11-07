import json
from amg_finetune_nogc.dataset import GraphContinueDataset as Original
from .common import *
class GraphContinueDataset(Original):
 def __init__(self,run,model_cfg,subset_ids=None):
  super().__init__(run,model_cfg,subset_ids);self.rows={}
  manifest=read(self.run/"cache_manifest.json")
  for entry in manifest["parts"]:
   require(sha(entry["path"])==entry["sha256"],"Training cache changed")
   with Path(entry["path"]).open() as f:
    for line in f:
     x=json.loads(line);require(x["sample_id"] not in self.rows,"Duplicate training ID");self.rows[x["sample_id"]]=x
  require(len(self.rows)==self.plan["training_count"],"Incomplete training prompts")
 def text_example(self,index,label_type):
  x=self.rows[self.annotation[index]["sample_id"]]["tasks"][label_type]
  return x["ids"],x["target"],"",x["info"]
