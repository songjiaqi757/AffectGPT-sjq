"""Reuse existing server primitives; bind this run to frozen checkpoints and prompt bundles."""
from amg_d_graph_compare.common import *
def checkpoint(run,variant,epoch):
 p=plan(run);spec=p["checkpoint_by_variant"][variant]
 require(spec["epoch"]==epoch,"Checkpoint epoch differs from frozen plan")
 return spec
def evidence_for(run,variant,row,**unused):
 p=plan(run);x=read(Path(run)/"prompt_cache"/(sid_key(row["sample_id"])+".json"))
 require(x["sample_id"]==row["sample_id"],"Wrong prompt cache sample")
 require(x["bundle_id"]==canonical({k:v for k,v in x.items() if k!="bundle_id"}),"Prompt bundle checksum changed")
 require(x["source_graph_release_id"]==p["graph_release_id"],"Wrong prompt-cache graph")
 return x
