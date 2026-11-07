import json
from pathlib import Path
run=Path(__file__).resolve().parent
for name in ["pipeline_status.json","from_35/status.json"]:
 f=run/name
 if f.exists():print(name,json.dumps(json.loads(f.read_text()),ensure_ascii=False,indent=2))
for k in range(5):
 f=run/"folds"/str(k)
 for name in ["status.json","evidence_progress.json"]:
  p=f/name
  if p.exists():print("fold",k,name,p.read_text())
