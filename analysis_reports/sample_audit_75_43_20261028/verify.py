
from pathlib import Path
import os,json,hashlib,warnings
os.environ['CUDA_VISIBLE_DEVICES']='';warnings.filterwarnings('ignore',category=RuntimeWarning)
exec(compile((Path(__file__).parent/'common.py').read_text(),'common.py','exec'))
OUT=Path(__file__).parent
def sha(f):return hashlib.sha256(Path(f).read_bytes()).hexdigest()
stats=read(OUT/'statistics.json');cs=read(OUT/'selected_cases.json');checks=[]
for d in D:
 ss=[s for s in scores if s['dataset']==d];assert len(ss)==50
 w=max(ss,key=lambda s:s['main_score']);a=arrays(w['raw_path'],d)
 assert abs(float(metric(a,d))-w['main_score'])<1e-12
 assert sha(w['raw_path'])==w['raw_sha256']
 rows=[json.loads(l) for l in open(OUT/(d+'_all_samples.jsonl'))]
 assert len(rows)==stats[d]['n']
 assert all(len(x['quality50'])==50 for x in rows)
 checks.append(dict(dataset=d,winner=w['job_id'],score=w['main_score'],raw_sha256=w['raw_sha256'],raw_path=w['raw_path'],samples=len(rows),metric_match=True))
assert len(cs)==72
manifest=dict(schema='server_only_posthoc_sample_audit_v1',root=str(ROOT),run=str(R),selection='Within each dataset pick highest stored official main score among 50 weights; cases chosen by fixed SHA256 ordering within four strata and truth diversity; not random population estimate.',oracle_mean_percent=100*sum(x['score'] for x in checks)/9,nine_unique_dataset_samples=sum(s['n'] for s in stats.values()),sample_predictions_compared=50*sum(s['n'] for s in stats.values()),detailed_cases=72,media_frame_review_cases=16,media_review='Four sparse frame positions per clip on server; one final frame failed in first montage. No full audiovisual manual relabeling; no audio listening claimed.',checks=checks,notes=['All computations and file writes on server; no project or media files written to local filesystem.','No training/inference/scoring-model run started; existing caches only.','Categorical diagnostic quality is mean HIT over applicable wheels; OV diagnostic quality is mean per-sample harmonic P/R over applicable wheels, not official F_s.','For categorical tasks neutral GT is unscored under current wheels. OV one sample has no valid GT wheel; diagnostic denominators exclude it.','Binary tasks exclude GT=0 and treat nonpositive judge results as nonpositive, following existing implementation.','All50 errors refer to these correlated weights and current cached scoring; not proof of impossibility.','Between-experiment changes in weights and graph are descriptive; A-G within-weight comparisons are more controlled.'],gpu_imported=any(x in sys.modules for x in ['torch','vllm']))
(OUT/'verification.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2))
print(json.dumps({k:v for k,v in manifest.items() if k!='checks'},ensure_ascii=False,indent=2))
