"""Nine-dataset reports: retain checkpoint and reused-result provenance."""
from graph_paths import hash_matches as _graph_hash_matches
from graph_paths import resolve_path as _graph_resolve_path
import csv,io,math
from .common import *
DISCRETE={'MER2023','MER2024','MELD','IEMOCAPFour'}
DIMENSION={'CMUMOSI','CMUMOSEI','SIMS','SIMSv2'}
def primary(d):return 'HIT' if d in DISCRETE else 'WAF' if d in DIMENSION else 'F_s'
def write_csv(path,rows,fields):
 out=io.StringIO();writer=csv.DictWriter(out,fieldnames=fields,extrasaction='ignore');writer.writeheader();writer.writerows(rows);tmp=path.with_suffix('.csv.tmp');tmp.write_text(out.getvalue());tmp.replace(path)
def summarize(run,p):
 rows=[read(f) for f in (run/'scores').glob('*.json')];fields=['variant','base_epoch','epoch','dataset','samples','main_metric','main_score','HIT','WAF','ACC','F_s','P_s','R_s','reused','completed_at_beijing']
 write_csv(run/'metrics_all.csv',[dict(r,**r['metrics']) for r in sorted(rows,key=lambda r:(r['base_epoch'],r['epoch'],r['dataset']))],fields)
 summary=[]
 for v in p['variants']:
  for e in p['variant_epochs'][v]:
   part=[r for r in rows if r['variant']==v and r['epoch']==e];three=[r for r in part if r['dataset'] in ['MER2023','SIMS','OVMERDPlus']]
   r=dict(variant=v,base_epoch=p['variant_bases'][v],epoch=e,datasets_completed=len(part),dataset_wise_mean=sum(x['main_score'] for x in part)/9 if len(part)==9 else None,three_dataset_mean=sum(x['main_score'] for x in three)/3 if len(three)==3 else None)
   for x in part:
    for k,value in x['metrics'].items():r[x['dataset']+'_'+k]=value
   summary.append(r)
 atomic_json(run/'per_checkpoint_summary.json',summary);fields=['variant','base_epoch','epoch','datasets_completed','dataset_wise_mean','three_dataset_mean']
 for d in p['datasets']:fields += [d+'_'+k for k in (['HIT'] if d in DISCRETE else ['WAF','ACC'] if d in DIMENSION else ['F_s','P_s','R_s'])]
 write_csv(run/'per_checkpoint_summary.csv',summary,fields)
 if len(rows)==450:
  best=[max([r for r in rows if r['dataset']==d],key=lambda r:r['main_score']) for d in p['datasets']];atomic_json(run/'best_original_reporting.json',best)
  single=max(summary,key=lambda r:r['dataset_wise_mean']);atomic_json(run/'best_single_checkpoint.json',single)
  lines=['# 原图＋本轮D：五个原始起点各续训十轮，九数据集结果','','40个新权重＋35组10个已有权重。新增420项推理测评，复用30项，合计450项。HIT用于四个离散数据集，WAF用于四个极性数据集，F_s用于OVMERDPlus；九集均值为九个主指标等权平均。','','|原始起点|Epoch|'+'|'.join(p['datasets'])+'|九集均值|','|---:|---:|'+'---:|'*10]
  for r in summary:lines.append('|'+str(r['base_epoch'])+'|'+str(r['epoch'])+'|'+'|'.join(f'{100*r[d+"_"+primary(d)]:.2f}' for d in p['datasets'])+f'|{100*r["dataset_wise_mean"]:.2f}|')
  lines+=['','## 各数据集独立最佳','','|数据集|主指标|最好结果|原始起点|Epoch|','|---|---|---:|---:|---:|']
  for r in best:lines.append(f'|{r["dataset"]}|{r["main_metric"]}|{100*r["main_score"]:.2f}|{r["base_epoch"]}|{r["epoch"]}|')
  lines += ['',f'最佳单权重：原始{single["base_epoch"]}起点，epoch{single["epoch"]}，九集均值{100*single["dataset_wise_mean"]:.4f}%。各数据集独立最优可能来自不同权重，不能当作同一权重的表现。','35组为既有5+5轮训练，41轮重建过数据加载器；另外四组为连续10轮。训练源、图、门控、极性系数、主任务、学习率、步数等固定。结果是指定目标测试集的探索性比较，未据此调整本轮设置。']
  (run/'RESULTS.md').write_text('\n'.join(lines)+'\n')
 return len(rows)
def verify_final(run,p):
 import numpy as np
 require(complete_count(run)==450,'Incomplete inference');rows=[read(f) for f in (run/'scores').glob('*.json')];require(len(rows)==450,'Incomplete scores');weights={}
 for v in p['variants']:
  ck=read(run/v/'checkpoints.json');require(len(ck)==10,'Wrong checkpoint count')
  for x in ck:weights[(v,x['epoch'])]=x
 require(len(weights)==50,'Wrong merged weight count');count=0
 for job in jobs(run):
  score=read(run/'scores'/(job['job_id']+'.json'));require(score['checkpoint']['sha256']==weights[(job['variant'],job['epoch'])]['sha256'],'Wrong scored weight')
  require(score['main_metric']==primary(job['dataset']) and math.isfinite(score['main_score']),'Wrong primary metric')
  raw=Path(score['raw_path']);require(_graph_hash_matches(raw, score['raw_sha256'], sha(raw)),'Scored raw changed');values=np.load(_graph_resolve_path(raw), allow_pickle=True)['name2reason'].item();require(len(values)==job['samples'],'Prediction count mismatch');count+=len(values)
 require(count==639950,'Wrong combined sample coverage')
 atomic_json(run/'final_verification.json',dict(passed=True,new_weights=40,reused_weights=10,new_jobs=420,reused_jobs=30,total_jobs=450,new_predictions=625950,reused_predictions=14000,total_predictions=count,primary_metrics_verified=True,checkpoint_lineage_verified=True,raw_hashes_verified=True,completed_at_beijing=now()))
 summarize(run,p)
