"""Development-only diagnostics; does not read confirmation outcomes."""
import sys,json,runpy,collections
from pathlib import Path
import numpy as np
ROOT=Path('/ai/sjq/AffectGPT-sjq');sys.path.insert(0,str(ROOT))
from amg_d_graph_compare.common import read,atomic_json,canonical,now
run=Path(read(ROOT/'amg_method_decision/current_run.json')['run']);e=run/'evaluation/development'
h=runpy.run_path(str(ROOT/'analysis_reports/sample_audit_75_43_20261028/common.py'));ar=h['arrays'];ar.__globals__['refs']=read(e/'references.json');ar.__globals__['cache']={}
scores=read(e/'metrics.json');seeds=[42,2026,2027]
lookup={(x['checkpoint'],x['condition'],x['seed'],x['task']):x for x in scores}
rows=read(run/'data/development_records.json');byname={r['name']:r for r in rows};labels=read(run/'data/development_labels.json')
raw={ck:{r['name']:read(run/'predictions/development'/ck/(canonical(r['sample_id'])[:32]+'.json')) for r in rows} for ck in ['original_epoch40','fixed_graph45_to54']}
answers={(ck,n,a['condition'],a['seed']):a['response'] for ck,rr in raw.items() for n,x in rr.items() for a in x['answers']}
lengths=[]
for ck in raw:
 for c in ['A','B','C','S','P']:
  for task in ['MER_track1_discrete','MER_OV']:
   xx=[lookup[ck,c,s,task] for s in seeds];fam='MER_track1' if task.endswith('discrete') else 'MER_OV'
   texts=[answers[ck,r['name'],c,s] for r in rows if r['family']==fam for s in seeds]
   lengths.append(dict(checkpoint=ck,condition=c,task=task,mean_extracted_labels=float(np.mean([x['mean_extracted_labels'] for x in xx])),mean_response_words=float(np.mean([len(t.split()) for t in texts])),unique_raw_answers=len(set(texts))))
prompt_stats=collections.Counter();semantic=collections.Counter();bundles={}
for r in rows:
 b=read(run/'prompt_cache'/(canonical(r['sample_id'])[:32]+'.json'));bundles[r['name']]=b;semantic['semantic_changed']+=b['semantic_intervention'];semantic['appraisal_active']+=b['source_gate_level']>=2
 prompt_stats['identical_C_S_text']+=b['texts']['C']==b['texts']['S']
 if not b['semantic_intervention']:prompt_stats['same_sets_different_order_text']+=b['texts']['C']!=b['texts']['S']
case_sets=[]
for ck,c,ref,refck in [('original_epoch40','C','S','original_epoch40'),('fixed_graph45_to54','C','S','fixed_graph45_to54'),('fixed_graph45_to54','C','A','fixed_graph45_to54'),('fixed_graph45_to54','A','A','original_epoch40')]:
 task='MER_track1_discrete';aa=[ar(lookup[ck,c,s,task]['raw'],'MER2023') for s in seeds];bb=[ar(lookup[refck,ref,s,task]['raw'],'MER2023') for s in seeds];dif=[]
 for i,n in enumerate(aa[0]['names']):
  values=np.array([a['hit'][i]-b['hit'][i] for a,b in zip(aa,bb)]).reshape(-1);finite=values[np.isfinite(values)]
  if finite.size:dif.append((float(finite.mean()),n,i))
 chosen=[]
 for direction,ranked in [('harmed',sorted(dif)),('improved',sorted(dif,reverse=True))]:
  used=set()
  for delta,n,i in ranked:
   if (direction=='harmed' and delta>=-1e-12) or (direction=='improved' and delta<=1e-12):continue
   gt=labels[n]['MER_track1']['discrete']
   if gt in used:continue
   used.add(gt);r=byname[n];b=bundles[n]
   chosen.append(dict(direction=direction,name=n,ground_truth=labels[n],subtitle=r['subtitle'],chinese=r['text']['chinese'],delta_HIT_pp=100*delta,per_seed=[dict(seed=s,current=answers[ck,n,c,s],reference=answers[refck,n,ref,s]) for s in seeds],C_evidence=b['texts']['C'],S_evidence=b['texts']['S'],semantic_intervention=b['semantic_intervention']))
   if len(used)==3:break
 case_sets.append(dict(checkpoint=ck,condition=c,reference_checkpoint=refck,reference=ref,cases=chosen))
response_control=[]
for ck in raw:
 for changed in [True,False]:
  rr=[r for r in rows if bundles[r['name']]['semantic_intervention']==changed]
  response_control.append(dict(checkpoint=ck,semantic_state_set_changed=changed,samples=len(rr),logical_C_S_pairs=len(rr)*3,identical_raw_answers=sum(answers[ck,r['name'],'C',s]==answers[ck,r['name'],'S',s] for r in rr for s in seeds)))
out=dict(partition='development_only',semantic_counts=dict(semantic),prompt_counts=dict(prompt_stats),output_sizes=lengths,response_control=response_control,case_sets=case_sets,time_beijing=now())
atomic_json(e/'detailed_diagnostics.json',out)
lines=['# 开发集详细诊断（确认实验尚未完成）','','案例依据数据集标签、字幕与模型输出定位差异，未额外人工复核音视频，不据此推断具体图边的因果错误。','', '|权重|组|任务|平均抽取标签数|平均回答词数|','|---|---|---|---:|---:|']
for x in lengths:lines.append(f"|{x['checkpoint']}|{x['condition']}|{x['task']}|{x['mean_extracted_labels']:.3f}|{x['mean_response_words']:.2f}|")
for comp in case_sets:
 lines+=['',f"## {comp['checkpoint']} {comp['condition']} 对 {comp['reference_checkpoint']} {comp['reference']}"]
 for case in comp['cases']:
  lines+=['',f"### {case['name']} / {case['direction']} / 标签 {case['ground_truth']['MER_track1']['discrete']}",'',case['chinese'],case['subtitle'],f"三种子平均逐样本HIT差值：{case['delta_HIT_pp']:.3f}百分点。"]
  for x in case['per_seed']:lines.append(f"- seed {x['seed']}: 当前回答：{x['current']}；参照回答：{x['reference']}。")
  lines += ['',case['C_evidence'],'',case['S_evidence']]
(e/'DETAILED_CASES.md').write_text('\n'.join(lines)+'\n')
print('DIAGNOSTICS_SAVED',flush=True);print('PROMPT_COUNTS',dict(prompt_stats),'SEMANTIC',dict(semantic),flush=True)
print('OUTPUT_SIZES',json.dumps(lengths,ensure_ascii=False),flush=True);print('RESPONSE_CONTROL',json.dumps(response_control,ensure_ascii=False),flush=True)
for comp in case_sets:
 print('CASE_GROUP',{k:v for k,v in comp.items() if k!='cases'},flush=True)
 for c in comp['cases'][:3]:print('CASE',json.dumps({k:v for k,v in c.items() if k not in ['C_evidence','S_evidence']},ensure_ascii=False),flush=True)
