import json, pathlib, statistics, collections, math, hashlib
ROOT=pathlib.Path('/ai/sjq/AffectGPT-sjq')
R=ROOT/'amg_d_multistart10/runs/d_multistart10_20261025_160152'
def read(p):return json.loads(pathlib.Path(p).read_text())
p=read(R/'plan.json');D=list(p['datasets'])
rows=[read(f) for f in (R/'scores').glob('*.json')]
orig=[r for r in read(ROOT/'AffectGPT/output/evaluation_20261016_2140/per_checkpoint_summary.json') if r['variant']=='face']
base={r['epoch']:r for r in orig}
longrun=ROOT/'amg_inference/runs/graph_225_20261022_174537/evaluation_all_20261023_175630'
long=[read(f) for f in (longrun/'scores').glob('*.json')]
summ=read(R/'per_checkpoint_summary.json')
out={'run':str(R),'score_count':len(rows),'long_count':len(long),'datasets':{},'base_summaries':{},'training':{}}
for d in D:
 a=[r for r in rows if r['dataset']==d]
 b=[r for r in long if r['dataset']==d]
 dif=[100*(r['main_score']-base[r['base_epoch']]['scores'][d]) for r in a]
 early=[r for r in a if r['epoch']-r['base_epoch']<=5]
 late=[r for r in a if r['epoch']-r['base_epoch']>5]
 matched=[100*(r['main_score']-next(t['main_score'] for t in b if t['base_epoch']==r['base_epoch'] and t['epoch']==r['epoch'])) for r in early]
 out['datasets'][d]=dict(original_best=100*max(r['scores'][d] for r in orig),long_best=100*max(r['main_score'] for r in b),current_best=100*max(r['main_score'] for r in a),mean=100*statistics.mean(r['main_score'] for r in a),sd=100*statistics.stdev(r['main_score'] for r in a),paired_base_mean=statistics.mean(dif),improved=sum(v>0 for v in dif),total=len(a),early_mean=100*statistics.mean(r['main_score'] for r in early),late_mean=100*statistics.mean(r['main_score'] for r in late),matched_long_mean=statistics.mean(matched),matched_long_improved=sum(v>0 for v in matched))
for b in [30,35,40,45,50]:
 a=[r for r in summ if r['base_epoch']==b]
 out['base_summaries'][b]=dict(original_mean=100*base[b]['dataset_wise_mean'],mean=100*statistics.mean(r['dataset_wise_mean'] for r in a),best=100*max(r['dataset_wise_mean'] for r in a),best_epoch=max(a,key=lambda r:r['dataset_wise_mean'])['epoch'],epoch_means=[round(100*r['dataset_wise_mean'],4) for r in a])
out['overall']=dict(mean=100*statistics.mean(r['main_score'] for r in rows),paired_base_mean=statistics.mean(x['paired_base_mean'] for x in out['datasets'].values()),oracle=statistics.mean(x['current_best'] for x in out['datasets'].values()),best_single=read(R/'best_single_checkpoint.json'),long_best_single=max(read(longrun/'per_checkpoint_summary.json'),key=lambda r:r['dataset_wise_mean']))
labels=read(R/'polarity_labels.json')
out['polarity']=dict(counts=dict(collections.Counter(x['polarity'] for x in labels)),pseudo=sum(x['pseudo_label'] for x in labels),human_verified=sum(x['human_verified'] for x in labels))
for v in ['from_30','from_40','from_45','from_50']:
 stats=collections.defaultdict(lambda:collections.Counter());levels=collections.Counter();reasons=collections.Counter();tasks=collections.Counter();digest=hashlib.sha256();skips=0
 with (R/v/'steps.jsonl').open() as f:
  for line in f:
   x=json.loads(line);st=stats[x['epoch']];st['steps']+=1
   for k in ['loss','generation_loss','polarity_loss']:st[k]+=x[k]
   skips+=not x['optimizer_step_applied'];digest.update(json.dumps(x['sample_ids']).encode())
   for info in x['prompt_info']:
    levels[info['evidence_level']]+=1;tasks[info['label_type']]+=1;reasons.update(info['gate_reasons'])
    for k in ['answer_truncated','subtitle_truncated','omitted_evidence','graph_tokens','displayed_paths','appraisals_displayed','emotion_candidates_displayed']:
     st[k]+=info.get(k,0)
    st['samples']+=1
 out['training'][v]=dict(epochs={e:{k:val if k in ['steps','samples'] else val/st['steps'] if k.endswith('loss') else val for k,val in st.items()} for e,st in stats.items()},levels=dict(levels),reasons=dict(reasons),tasks=dict(tasks),skipped_steps=skips,sample_stream_sha256=digest.hexdigest())
(ROOT/'analysis_reports/reanalysis_20261027_stats.json').write_text(json.dumps(out,ensure_ascii=False,indent=2))
print(json.dumps({k:v for k,v in out.items() if k!='training'},ensure_ascii=False,indent=2))
print('TRAINING',json.dumps(out['training'],ensure_ascii=False))

