from graph_paths import resolve_path as _graph_resolve_path
from argparse import Namespace
from graph_paths import Path
from datetime import datetime
from zoneinfo import ZoneInfo
import gc,json
import torch
from cue_student.common import PROJECT,atomic_json,code_hash
from cue_student.train import run
base=PROJECT/"cue_student/artifacts"
out=base/("stochastic_resume_"+datetime.now(ZoneInfo("Asia/Shanghai")).strftime("%Y%m%d_%H%M%S"));out.mkdir()
cfg=json.loads((base/"integration_20261020_124254/text.config.json").read_text())
cfg["dropout"]=.2
config=out/"text_dropout.config.json";atomic_json(config,cfg)
release=base/"smoke_release_v1"
def execute(output,limit,resume=None):
    run(Namespace(config=str(config),release=str(release),output=str(output),device="cuda:0",
                  cpu_threads=8,resume=str(resume) if resume else None,init_from=None,max_steps=limit,
                  allow_smoke=True,allow_unverified_groups=False))
    gc.collect();torch.cuda.empty_cache()
execute(out/"resumed",1)
execute(out/"resumed",2,out/"resumed/last.pt")
execute(out/"uninterrupted",2)
a=torch.load(_graph_resolve_path(out / 'resumed/last.pt'), map_location='cpu', weights_only=False)
b=torch.load(_graph_resolve_path(out / 'uninterrupted/last.pt'), map_location='cpu', weights_only=False)
difference=max(float((a["model"][k]-b["model"][k]).abs().max()) for k in a["model"])
assert difference==0.,difference
report={"passed":True,"head_dropout":.2,"encoder_train":"frozen","optimizer_steps":2,
        "resumed_vs_uninterrupted_max_abs_difference":difference,"final_code_hash":code_hash(),
        "scope":"stochastic real-model smoke resume test, not formal training","output":str(out)}
atomic_json(out/"report.json",report)
summary_path=PROJECT/"cue_student/reports/implementation_test_report_20261020.json"
summary=json.loads(summary_path.read_text());summary["stochastic_resume"]={"passed":True,"head_dropout":.2,"max_abs_difference":difference,"report":str(out/"report.json")}
atomic_json(summary_path,summary)
doc=PROJECT/"cue_student/reports/implementation_test_report_20261020.md"
doc.write_text(doc.read_text()+"\n追加随机性恢复检查：将分类头dropout设为0.2，真实XLM-R冻结基线训练一步后恢复，与连续训练两步的参数最大差异仍为0，验证随机数状态恢复。证据："+str(out/"report.json")+"\n")
print("STOCHASTIC_RESUME_PASSED",str(out/"report.json"),flush=True)
