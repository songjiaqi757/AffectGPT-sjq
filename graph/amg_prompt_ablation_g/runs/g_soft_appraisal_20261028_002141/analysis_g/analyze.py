"""Server-only analysis of completed G. Uses existing unified scoring artifacts unchanged."""
import os,sys,json,pathlib,ast,runpy,glob,re,types,collections,contextlib,io,hashlib,csv,math
os.environ['CUDA_VISIBLE_DEVICES']=''
os.environ.setdefault('OPENBLAS_NUM_THREADS','1')
import numpy as np,pandas as pd
ROOT=pathlib.Path('/ai/sjq/AffectGPT-sjq');A=ROOT/'AffectGPT'
sys.path.insert(0,str(ROOT))
from amg_runtime.common import canonical
def read(p):return json.loads(pathlib.Path(p).read_text())
def sha(p):
 h=hashlib.sha256()
 with pathlib.Path(p).open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
R=pathlib.Path(read(ROOT/'amg_prompt_ablation_g/current_run.json')['run']);plan=read(R/'plan.json')
OLD=pathlib.Path(plan['reference_run']);OUT=R/'analysis_g';OUT.mkdir(exist_ok=True)
assert read(R/'status.json')['phase']=='complete' and read(R/'final_verification.json')['passed']
for f,h in read(R/'code_manifest.json')['files'].items():assert sha(ROOT/f)==h
for f,h in read(R/'reference_input_hashes.json').items():assert sha(f)==h
source=read(OLD/'analysis_detailed/analysis_results.json')
records={}
with (OLD/'analysis_detailed/per_sample_diagnostics.jsonl').open() as f:
 for line in f:
  x=json.loads(line);records[(x['dataset'],x['name'])]=x
with np.load(OLD/'analysis_detailed/metric_arrays.npz',allow_pickle=False) as z:arrays={k:z[k] for k in z.files}
features={}
for k,v in arrays.items():
 fields=k.split('__')
 if len(fields)==4:
  w,c,d,field=fields;features.setdefault((w,c,d),{})[field]=v
names={d:arrays[d+'__names'].tolist() for d in plan['datasets']}
gate={d:arrays[d+'__gate_level'] for d in plan['datasets']}
refs={d:{n:records[(d,n)]['reference'] for n in names[d]} for d in names}
os.chdir(A);config=types.SimpleNamespace(**runpy.run_path(str(A/'config.py')))
ns=dict(np=np,pd=pd,re=re,os=os,glob=glob,config=config)
for f in ['toolkit/utils/functions.py','toolkit/utils/read_files.py','my_affectgpt/evaluation/wheel.py']:
 tree=ast.parse((A/f).read_text())
 defs=[x for x in tree.body if isinstance(x,ast.FunctionDef) and (f.endswith('wheel.py') or x.name in ['string_to_list','func_read_key_from_csv'])]
 exec(compile(ast.Module(body=defs,type_ignores=[]),f,'exec'),ns)
with contextlib.redirect_stdout(io.StringIO()):
 fm=ns['read_format2raws']();rm=ns['read_candidate_synonym_merge']()
wheels=[ns['func_get_wheel_cluster']('wheel'+str(i),'level1') for i in range(1,6)]
split=ns['string_to_list'];mapped_cache={}
def mapped(text,w):
 key=(str(text),w)
 if key not in mapped_cache:
  mapped_cache[key]=set(ns['func_map_label_to_synonym']([x.lower().strip() for x in split(text)],fm,rm,wheels[w],'case3_wheel'+str(w+1)+'_level1'))
 return mapped_cache[key]
def npmap(p):
 z=np.load(p,allow_pickle=True);return dict(zip(z['filenames'].tolist(),z['fileitems'].tolist()))
score=runpy.run_path(str(OLD/'analysis_detailed/replay_statistics.py'))['score']
official=read(OLD/'metrics_all.json')+read(R/'metrics_all.json')
lookup={(x['weight'],x['ablation'],x['dataset']):x for x in official}
newpred={};newlabels={};newsets={};Gmeta={}
reused=fresh=0
inputs={}
for row in read(R/'metrics_all.json'):
 w,d=row['weight'],row['dataset'];raw=pathlib.Path(row['raw_path'])
 assert sha(raw)==row['raw_sha256']
 opens=npmap(raw.with_name(raw.stem+'-openset.npz'));newlabels[(w,d)]=opens
 job=read(R/'jobs'/(row['job_id']+'.json'));pred={}
 with pathlib.Path(job['prediction_path']).open() as f:
  for line in f:
   x=json.loads(line);sid=x['sample_id'];pred[x['name']]=x
   assert x['plan_id']==plan['plan_id'] and x['checkpoint']['sha256']==plan['weights'][w]['sha256']
   bundle_path=R/'prompt_cache'/(canonical(sid)+'.json');bundle=read(bundle_path)
   assert bundle['bundle_id']==canonical({k:v for k,v in bundle.items() if k!='bundle_id'})
   assert x['prompt_info']['prompt_id']==bundle['expected_prompt_ids']['G']
   assert x['prompt_info']['ablation']=='G' and x['prompt_info']['emotion_candidates_displayed']==0 and x['prompt_info']['displayed_paths']==0
   if x.get('reused'):
    reused+=1
    assert x['response']==records[(d,x['name'])]['results'][w]['F']['response']
    assert x['prompt_info']['prompt_id']==records[(d,x['name'])]['results'][w]['F']['prompt_id']
   else:fresh+=1
   Gmeta[(w,d,x['name'])]=bundle
 newpred[(w,d)]=pred
 assert set(pred)==set(names[d])==set(opens)
 N=len(names[d])
 if d=='SIMS':
  sent=npmap(raw.with_name(raw.stem+'-openset-sentiment.npz'))
  y=np.array([float(refs[d][n]) for n in names[d]]);valid=y!=0;positive=y>0
  polarity=np.array([1 if sent[n]=='positive' else -1 if sent[n]=='negative' else 0 for n in names[d]])
  prediction=polarity>0;conf=np.eye(4)[2*positive.astype(int)+prediction.astype(int)]
  features[(w,'G',d)]=dict(conf=conf,valid=valid,correct=positive==prediction,prediction=prediction,polarity=polarity)
  newlabels[(w,'SIMS_sentiment')]=sent
 else:
  fields={k:np.full((N,5),np.nan) for k in ['p','r','hit','m']}
  fields['cards']=np.zeros((N,5));fields['valid']=np.zeros((N,5),bool);fields['full_cards']=np.zeros((N,5))
  newsets[(w,d)]={}
  for wi in range(5):
   candidates=set().union(*(mapped(x,wi) for x in set(refs[d].values()))) if d=='MER2023' else set()
   for i,n in enumerate(names[d]):
    gt=mapped(refs[d][n],wi);pr=mapped(opens[n],wi)
    newsets[(w,d)][(n,wi)]=pr
    fields['cards'][i,wi]=len(pr&candidates) if d=='MER2023' else len(pr)
    fields['full_cards'][i,wi]=len(pr)
    if not gt:continue
    fields['valid'][i,wi]=True;hit=len(gt&pr)
    fields['hit'][i,wi]=hit;fields['p'][i,wi]=hit/len(pr) if pr else 0
    fields['r'][i,wi]=hit/len(gt)
    fields['m'][i,wi]=hit/len(pr&candidates) if pr&candidates else 0
  features[(w,'G',d)]=fields
 for f in [raw,raw.with_name(raw.stem+'-openset.npz'),pathlib.Path(job['prediction_path'])]:inputs[str(f)]=sha(f)
 if d=='SIMS':
  f=raw.with_name(raw.stem+'-openset-sentiment.npz');inputs[str(f)]=sha(f)
assert (reused,fresh)==(1718,1082)
metricnames={'MER2023':['HIT','M'],'SIMS':['WAF','ACC'],'OVMERDPlus':['F_s','P_s','R_s']}
rng=np.random.default_rng(20261028);counts={}
for d in names:
 N=len(names[d]);counts[d]=rng.multinomial(N,np.full(N,1/N),size=5000).astype(float)
points={};boot={};maxerr=0.
for key,ft in features.items():
 d=key[2];points[key]=score(d,ft,np.ones(len(names[d])))[0];boot[key]=score(d,ft,counts[d])
 expect=np.array([lookup[key]['metrics'][k] for k in metricnames[d]])
 maxerr=max(maxerr,float(np.max(np.abs(points[key]-expect))))
 assert np.max(np.abs(points[key]-expect))<1e-12,(key,points[key],expect)
def compare(w,d,c,mask=None):
 g=features[(w,'G',d)];b=features[(w,c,d)]
 if mask is None:
  pa,pb=points[(w,'G',d)],points[(w,c,d)];ba,bb=boot[(w,'G',d)],boot[(w,c,d)]
 else:
  ix=np.where(mask)[0];a={k:v[ix] for k,v in g.items()};z={k:v[ix] for k,v in b.items()}
  rg=np.random.default_rng(20261028+int(np.sum(mask)));ct=rg.multinomial(len(ix),np.full(len(ix),1/len(ix)),size=3000).astype(float)
  pa,pb=score(d,a,np.ones(len(ix)))[0],score(d,z,np.ones(len(ix)))[0];ba,bb=score(d,a,ct),score(d,z,ct)
 delta=(pa-pb)*100;ci=np.quantile((ba-bb)*100,[.025,.975],axis=0)
 idx=np.arange(len(names[d])) if mask is None else np.where(mask)[0]
 out=dict(weight=w,dataset=d,comparison='G-'+c,samples=len(idx),G={k:100*float(pa[i]) for i,k in enumerate(metricnames[d])},reference={k:100*float(pb[i]) for i,k in enumerate(metricnames[d])},delta={k:float(delta[i]) for i,k in enumerate(metricnames[d])},ci95={k:ci[:,i].tolist() for i,k in enumerate(metricnames[d])})
 rawnew=[newpred[(w,d)][names[d][i]]['response'] for i in idx];rawold=[records[(d,names[d][i])]['results'][w][c]['response'] for i in idx]
 out['responses_changed']=sum(a!=b for a,b in zip(rawnew,rawold))
 out['response_change_rate']=out['responses_changed']/len(idx)
 if d=='SIMS':
  valid=g['valid'][idx];old=b['correct'][idx];cur=g['correct'][idx]
  y=np.array([float(refs[d][n])>0 for n in names[d]])[idx];pr=g['prediction'][idx]
  out.update(scored_samples=int(valid.sum()),corrected=int(np.sum(valid&~old&cur)),harmed=int(np.sum(valid&old&~cur)),stable_correct=int(np.sum(valid&old&cur)),stable_wrong=int(np.sum(valid&~old&~cur)),
   G_confusion=[[int(np.sum(valid&~y&~pr)),int(np.sum(valid&~y&pr))],[int(np.sum(valid&y&~pr)),int(np.sum(valid&y&pr))]],
   old_confusion=(b['conf'][idx]*valid[:,None]).sum(0).reshape(2,2).astype(int).tolist())
 else:
  hnew=g['hit'][idx];hold=b['hit'][idx];valid=g['valid'][idx]
  dif=np.divide(np.nansum(hnew-hold,axis=1),valid.sum(1),out=np.zeros(len(idx)),where=valid.sum(1)>0)
  if d=='MER2023':
   out.update(corrected_views=int(np.sum(valid&(hold==0)&(hnew>0))),harmed_views=int(np.sum(valid&(hold>0)&(hnew==0))),improved_samples=int(np.sum(dif>1e-12)),worsened_samples=int(np.sum(dif< -1e-12)))
  else:
   pn,rn=g['p'][idx],g['r'][idx];po,ro=b['p'][idx],b['r'][idx]
   fn=np.divide(2*pn*rn,pn+rn,out=np.zeros_like(pn),where=(pn+rn)>0);fo=np.divide(2*po*ro,po+ro,out=np.zeros_like(po),where=(po+ro)>0)
   dif=np.divide(np.nansum(fn-fo,axis=1),valid.sum(1),out=np.zeros(len(idx)),where=valid.sum(1)>0)
   out.update(diagnostic_sample_F_improved=int(np.sum(dif>1e-12)),diagnostic_sample_F_worsened=int(np.sum(dif< -1e-12)))
  out.update(G_mean_mapped_candidates=float(np.mean(g['cards'][idx])),old_mean_mapped_candidates=float(np.mean(b['cards'][idx])),G_mean_extracted_labels=float(np.mean([len(split(newlabels[(w,d)][names[d][i]])) for i in idx])),old_mean_extracted_labels=float(np.mean([len(records[(d,names[d][i])]['results'][w][c]['extracted_labels']) for i in idx])))
 return out
pairs=[];strata=[]
for w in plan['weights']:
 for d in names:
  for c in 'ABCDEF':pairs.append(compare(w,d,c))
  for c in ['B','C','F']:
   for level in [2,3]:
    mask=gate[d]==level
    if mask.sum()>0:
     x=compare(w,d,c,mask);x['gate_level']=level;strata.append(x)
print('POINT_REPLAY',len(points),'max_error',maxerr,flush=True)
for x in pairs:
 if x['comparison'] in ['G-B','G-C','G-F']:print('PAIR',json.dumps(x,ensure_ascii=False),flush=True)
# Appraisal uncertainty and coverage audit, independent of model weight.
graph=read(ROOT/'amg_graph10_rebuild/runs/wheel5_level1_alias10_full_20261025/graph/graph.json')
allowed=collections.defaultdict(set)
for e in graph['ontology_edges']:allowed[e['source_node_id']].add(e['target_node_id'])
appstats={}
for d in names:
 dim=collections.defaultdict(collections.Counter);card=[];tok=[]
 for n in names[d]:
  b=Gmeta[('base35',d,n)];apps=b['shared_fields']['apps'];card.append(sum(len(a['states']) for a in apps));tok.append(b['infos']['G']['graph_tokens'])
  for a in apps:
   st=set(a['states']);z=dim[a['dimension_id']];z['displayed']+=1;z['multi_state']+=len(st)>1;z['all_allowed_states']+=st==allowed[a['dimension_id']]
 appstats[d]=dict(mean_states=float(np.mean(card)),mean_graph_tokens=float(np.mean(tok)),dimensions={k:dict(v) for k,v in dim.items()})
# Explicit signed sentiment confusion for every A-G.
sims={}
for w in plan['weights']:
 sims[w]={}
 for c in 'ABCDEFG':
  f=features[(w,c,'SIMS')];valid=f['valid'];cm=(f['conf']*valid[:,None]).sum(0).reshape(2,2)
  sims[w][c]=dict(confusion=cm.astype(int).tolist(),negative_recall=float(cm[0,0]/cm[0].sum()),positive_recall=float(cm[1,1]/cm[1].sum()),correct=int(cm.trace()))
# Ranked examples with both improvements and harms.
examples=[]
for w,d,c in [('graph40','SIMS','B'),('base35','SIMS','C'),('graph40','OVMERDPlus','B'),('base35','OVMERDPlus','F'),('graph40','MER2023','C')]:
 g=features[(w,'G',d)];b=features[(w,c,d)]
 if d=='SIMS':diff=(g['correct'].astype(int)-b['correct'].astype(int))*g['valid']
 else:
  def samplef(ft):
   P,Q=ft['p'],ft['r'];F=np.divide(2*P*Q,P+Q,out=np.zeros_like(P),where=(P+Q)>0)
   return np.divide(np.nansum(F,1),ft['valid'].sum(1),out=np.zeros(F.shape[0]),where=ft['valid'].sum(1)>0)
  diff=samplef(g)-samplef(b) if d!='MER2023' else np.nanmean(g['hit']-b['hit'],axis=1)
 for sign in [-1,1]:
  candidates=np.where((diff*sign)>1e-12)[0]
  # Prefer genuinely different raw answers.
  candidates=[i for i in candidates if newpred[(w,d)][names[d][i]]['response']!=records[(d,names[d][i])]['results'][w][c]['response']]
  candidates=sorted(candidates,key=lambda i:-abs(diff[i]))
  for i in candidates[:2]:
   n=names[d][i];rec=records[(d,n)];pr=newpred[(w,d)][n];bndl=Gmeta[(w,d,n)]
   source_row=next(r for r in read(plan['datasets'][d]['path']) if r['name']==n)
   x=dict(weight=w,dataset=d,comparison='G-'+c,name=n,reference=rec['reference'],direction='improved' if sign>0 else 'harmed',gate=int(gate[d][i]),
    subtitle=source_row['subtitle'],old_response=rec['results'][w][c]['response'],G_response=pr['response'],G_prompt=bndl['texts']['G'],
    old_extracted=rec['results'][w][c]['extracted_labels'],G_extracted=split(newlabels[(w,d)][n]),G_reused=pr.get('reused',False))
   if d=='SIMS':x.update(old_sentiment=rec['results'][w][c]['sentiment'],G_sentiment=newlabels[(w,'SIMS_sentiment')][n])
   examples.append(x)
summary=dict(run=str(R),reference_run=str(OLD),audit=dict(completed=True,all_42_job_metrics_reproduced=True,max_metric_replay_error=maxerr,reused_predictions=reused,new_predictions=fresh,code_manifest_passed=True,reference_inputs_verified=True,no_gpu_loaded=not any(k in sys.modules for k in ['torch','vllm'])),
 scoring='Existing unified official scoring artifacts used unchanged; no rescoring,no new generation',
 metrics=official,pairs=pairs,stratified_pairs=strata,appraisal_audit=appstats,sims_class_confusion=sims,examples=examples,
 bootstrap=dict(replicates=5000,stratum_replicates=3000,seed=20261028,unit='paired sample IDs; all wheel measurements kept together',limitations='Conditional on fixed checkpoints and this generation realization; target-test exploration; no multiple-comparison adjustment or independent validation claim'),
 notes=['OV diagnostic per-sample F transitions are not an additive decomposition of official F.','G-F generation changes only on541 gate3 samples per weight; remaining859 raw answers per weight were reused by exact prompt/weight/seed identity.','No inference path text was provided.','Same content with different wording also changes token sequence and subsequent sampled generation; this experiment measures the complete wording treatment,not an isolated cognitive mechanism.'])
def clean(v):
 if isinstance(v,float) and not math.isfinite(v):return None
 if isinstance(v,dict):return {k:clean(x) for k,x in v.items()}
 if isinstance(v,list):return [clean(x) for x in v]
 if isinstance(v,(np.integer,np.floating)):return v.item()
 return v
(OUT/'analysis_results.json').write_text(json.dumps(clean(summary),ensure_ascii=False,indent=2,allow_nan=False))
(OUT/'input_sha256.json').write_text(json.dumps(inputs,ensure_ascii=False,indent=2))
save={}
for (w,c,d),ft in features.items():
 for field,v in ft.items():save['__'.join([w,c,d,field])]=v
for d in names:
 save[d+'__names']=np.array(names[d]);save[d+'__gate_level']=gate[d]
np.savez_compressed(OUT/'metric_arrays.npz',**save)
with (OUT/'paired_effects.csv').open('w') as f:
 writer=csv.writer(f);writer.writerow(['weight','dataset','comparison','metric','delta_pp','ci95_low','ci95_high','corrected','harmed','response_change_rate'])
 for x in pairs:
  for m,v in x['delta'].items():writer.writerow([x['weight'],x['dataset'],x['comparison'],m,v,*x['ci95'][m],x.get('corrected',x.get('corrected_views')),x.get('harmed',x.get('harmed_views')),x['response_change_rate']])
print('APPRAISAL',json.dumps(appstats,ensure_ascii=False),flush=True)
print('SIMS_CONFUSION',json.dumps(sims,ensure_ascii=False),flush=True)
print('EXAMPLES',json.dumps(examples[:4],ensure_ascii=False),flush=True)
print('SAVED',OUT,flush=True)

