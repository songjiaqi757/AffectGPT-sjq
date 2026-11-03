from pathlib import Path
import json
run=Path(__file__).resolve().parent
def read(name):
 p=run/name
 return json.loads(p.read_text()) if p.exists() else None
print(json.dumps(dict(run=str(run),pipeline=read("status.json"),experiments={str(e):read("experiment_"+str(e)+"_status.json") for e in [30,35,40,45,50]}),ensure_ascii=False,indent=2))
