from pathlib import Path
import json,shutil,hashlib,sys,os
ROOT=Path(__file__).resolve().parent;PROJECT=Path("/ai/sjq/AffectGPT-sjq");SOURCE=ROOT/"source/cue_student";TARGET=PROJECT/"cue_student"
assert json.loads((ROOT/"stop_status.json").read_text())["complete"]
assert (ROOT/"unit_tests.log").read_text().rstrip().endswith("OK")
report=json.loads((ROOT/"integration_report.json").read_text());assert report["passed"]
sys.path.insert(0,str(ROOT/"source"))
from cue_student.common import code_hash,atomic_json
assert code_hash()==report["code_hash"]
for f in SOURCE.glob("*.py"):shutil.copy2(f,TARGET/f.name)
for f in (SOURCE/"tests").glob("*.py"):shutil.copy2(f,TARGET/"tests"/f.name)
for f in (ROOT/"configs").glob("*.json"):shutil.copy2(f,TARGET/"configs"/f.name)
for folder in (TARGET/"__pycache__",TARGET/"tests/__pycache__"):
 if folder.exists():shutil.rmtree(folder)
for src,dest in ((SOURCE/"splits/holdout300",TARGET/"splits/holdout300"),(SOURCE/"artifacts/smoke_release_v1",TARGET/"artifacts/smoke_release_v1")):
 if dest.exists():shutil.rmtree(dest)
 shutil.copytree(src,dest)
shutil.copy2(ROOT/"README.md",TARGET/"README.md")
assert {p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in SOURCE.glob("*.py")}=={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in TARGET.glob("*.py")}
atomic_json(ROOT/"deployment.json",dict(code_hash=report["code_hash"],canonical_source=str(TARGET),holdout=json.loads((TARGET/"splits/holdout300/manifest.json").read_text())["holdout_id"],complete=True))
plan=PROJECT/"方案.md";text=plan.read_text();heading="## 当前生效训练版本：严格排除任意模态失败样本（2026-10-20）"
if heading not in text:
 plan.write_text(heading+"\n\n当前任务为 strict_all_modalities_20261020_163131。78条失败模态任务对应72个样本，已在任何数据划分前整条排除；train=27679、validation=3076、人工holdout=300、diagnostic=200。人工集保留299条，失败的samplenew3_00094241替换为从旧诊断独立保留集抽取的samplenew3_00039200。五组均从预训练权重重新开始，沿用既有加载速率优化。先前训练结果作废并清理；以下历史章节若有旧运行路径或旧样本数，以本节及cue_student/README.md和当前status.json为准。\n\n"+text)
print("DEPLOYED",report["code_hash"],flush=True)
