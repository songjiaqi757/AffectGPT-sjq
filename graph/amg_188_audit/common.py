
"""Server-only frozen 188-class graph intervention."""
from amg_d_graph_compare.common import *
PACKAGE="amg_188_audit"
CATEGORICAL={"MER2023","MER2024","MELD","IEMOCAPFour"}
POLARITY={"CMUMOSI","CMUMOSEI","SIMS","SIMSv2"}
CONDITIONS={"A":"No evidence","B":"Cue only","C":"Cue+Appraisal, no paths","D":"Cue+Emotion, no paths","E":"Cue+Appraisal+Emotion, no paths","P":"Exact original complete prompt, including retained paths"}
def checkpoint(run,variant,epoch):
 p=plan(run);s=p["checkpoint_by_variant"][variant];require(s["epoch"]==epoch,"Epoch drift");return s
def evidence_for(run,variant,row):
 x=read(Path(run)/"prompt_cache"/(sid_key(row["sample_id"])+".json"))
 require(x["bundle_id"]==canonical({k:v for k,v in x.items() if k!="bundle_id"}),"Prompt cache drift")
 return x
def launch_module(run,module,args,log,gpu=None):
 return launch(run,PACKAGE+"."+module,args,log,gpu)
