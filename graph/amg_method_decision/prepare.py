from graph_paths import resolve_path as _graph_resolve_path
import sys,copy,collections,random
from graph_paths import Path
ROOT=Path('/ai/sjq/AffectGPT-sjq/graph');sys.path.insert(0,str(ROOT))
from amg_method_decision.pipeline import read,dump,canonical,sha,now,key,records
from amg_188_audit.policy import freeze
from amg_d_multistart10.policy import readable
from amg_finetune_nogc.prompts import encode
SOURCE=ROOT/'amg_188_path_noemotion/runs/path_noemotion_20261028_170538'
def signature(e):
 return tuple((d['dimension_id'],len(d['display_candidates'])) for d in e['appraisal_dimensions'] if d['display_candidates'])
def sets(e):
 return tuple((d['dimension_id'],tuple(sorted(s['state_id'] for s in d['display_candidates']))) for d in e['appraisal_dimensions'] if d['display_candidates'])
def line(e):
 return 'Appraisal hypotheses: '+'; '.join(readable(d['dimension_id'])+': '+readable(s['state_id']) for d in e['appraisal_dimensions'] for s in d['display_candidates'])
def replace(text,new):return '\n'.join(new if x.startswith('Appraisal hypotheses:') else x for x in text.splitlines())
def prepare(run):
 from transformers import AutoTokenizer
 t=AutoTokenizer.from_pretrained(_graph_resolve_path(str(ROOT / 'AffectGPT/models/Qwen2.5-7B-Instruct')), local_files_only=True)
 rr=records(run);ev={r['sample_id']:read(run/'cue_cache'/(key(r)+'.json'))['evidence'] for r in rr}
 bb={sid:freeze(e,t) for sid,e in ev.items()};groups=collections.defaultdict(list);donors={};audit=[];counts=collections.Counter()
 for r in rr:
  sid=r['sample_id']
  if bb[sid]['source_gate_level']>=2:groups[(r['partition'],signature(ev[sid]))].append(sid)
 for g,sids in groups.items():
  sids.sort(key=lambda s:canonical('donor-v1::'+s));rng=random.Random(canonical(g))
  off=rng.randrange(1,len(sids)) if len(sids)>1 else 0
  for i,sid in enumerate(sids):donors[sid]=sids[(i+off)%len(sids)]
 for r in rr:
  sid=r['sample_id'];e=ev[sid];b=bb[sid];donor=donors.get(sid,sid);active=b['source_gate_level']>=2
  txt=replace(b['texts']['C'],line(ev[donor])) if active else b['texts']['C'];changed=active and sets(e)!=sets(ev[donor])
  b['texts']['S']=txt;b['infos']['S']=copy.deepcopy(b['infos']['C']);b['infos']['S'].update(ablation='S',graph_tokens=len(encode(t,txt)),graph_text_id=canonical(txt))
  b.update(donor_sample_id=donor,semantic_intervention=bool(changed));counts['total']+=1;counts['appraisal_active']+=active;counts['semantic_state_sets_changed']+=changed
  audit.append(dict(sample_id=sid,partition=r['partition'],donor=donor,dimension_and_state_counts_matched=signature(e)==signature(ev[donor]),semantic_state_set_changed=changed,original_tokens=len(encode(t,b['texts']['C'])),shuffled_tokens=len(encode(t,txt)),source_gate_level=b['source_gate_level']))
 coverage=counts['semantic_state_sets_changed']/max(1,counts['appraisal_active']);conditions=['A','B','C','S','P']
 if coverage<.5:
  conditions+=['T','R'];inp=read(ROOT/'amg_runtime/releases/p2p3_20261022_111315/inputs_p0.json');graph=read(inp['graph']['graph_file']);states=collections.defaultdict(list)
  for n in graph['nodes']:
   if n['node_type']=='AppraisalState':states[n['dimension_id']].append(n['id'])
  for r in rr:
   sid=r['sample_id'];e=ev[sid];b=bb[sid];top=[];other=[];control=[]
   if b['source_gate_level']>=2:
    for d in e['appraisal_dimensions']:
     if not d['display_candidates']:continue
     orig=d['display_candidates'][0]['state_id'];alts=[s for s in states[d['dimension_id']] if s!=orig];random.Random(canonical([sid,d['dimension_id'],'control-v1'])).shuffle(alts)
     alt=min(alts,key=lambda s:abs(len(encode(t,readable(s)))-len(encode(t,readable(orig)))));prefix=readable(d['dimension_id'])+': ';top.append(prefix+readable(orig));other.append(prefix+readable(alt));control.append([d['dimension_id'],orig,alt])
   for arm,items in [('T',top),('R',other)]:
    txt=replace(b['texts']['C'],'Appraisal hypotheses: '+'; '.join(items)) if items else b['texts']['B'];b['texts'][arm]=txt;b['infos'][arm]=copy.deepcopy(b['infos']['C']);b['infos'][arm].update(ablation=arm,graph_tokens=len(encode(t,txt)),graph_text_id=canonical(txt),appraisals_displayed=len(items))
   b['top_one_control']=control
  dump(run/'audit/protocol_amendment_pre_outcomes.json',dict(reason='Donor shuffle changes fewer than half of active state sets',semantic_coverage=coverage,added_conditions={'T':'Highest-associated single state per supported dimension','R':'Random different valid state in same dimension, one per dimension, nearest token length'},no_outcomes_observed=True,time_beijing=now()))
 for r in rr:
  b=bb[r['sample_id']]
  if any(len(encode(t,b['texts'][c]))>512 for c in conditions):raise ValueError('Graph token budget exceeded')
  b['bundle_id']=canonical(b);dump(run/'prompt_cache'/(key(r)+'.json'),b)
 old=read(SOURCE/'plan.json');plan={k:copy.deepcopy(old[k]) for k in ['generation','limits','prompt_question','judge_protocol_id','physical_nodes']}
 base=dict(path=str(ROOT/'AffectGPT/output/emercoarse_highlevelfilter4_outputhybird_bestsetup_bestfusion_lz/emercoarse_highlevelfilter4_outputhybird_bestsetup_bestfusion_lz_20261014230/checkpoint_000040_loss_0.664.pth'),sha256='cfcb328799605ebfa3839bd0a50a0f7f2b93efd2992550c3a7e482297c8fbfc0',epoch=40)
 plan['physical_nodes'][1]['slots']=[4,5,6,7];plan.update(schema='method_decision_v1',training_run=str(run),conditions=conditions,ablation_by_variant={c:c for c in conditions},checkpoints={'original_epoch40':base,'fixed_graph45_to54':old['checkpoint_by_variant']['path188_MER2024_P']},seeds=[42,2026,2027],source_protocol_sha256=sha(run/'protocol.json'),confirmation_requires='frozen_selection.json',source_independence_certified=False,created_at_beijing=now())
 plan['input_files']={str(run/'data'/f'{part}_{kind}.json'):sha(run/'data'/f'{part}_{kind}.json') for part in ['development','confirmation'] for kind in ['records','labels']};plan['plan_id']=canonical(plan);dump(run/'inference_plan.json',plan)
 (run/'original_config.json').write_bytes((SOURCE/'original_config.json').read_bytes());(run/'evaluation_resources.json').write_bytes((SOURCE/'evaluation_resources.json').read_bytes())
 for part in ['development','confirmation']:
  for ck in plan['checkpoints']:(run/'predictions'/part/ck).mkdir(parents=True,exist_ok=True)
 for stage in ['openset','sentiment']:(run/'judge_cache'/stage).mkdir(parents=True,exist_ok=True)
 dump(run/'audit/shuffle_intervention_audit.json',dict(counts=dict(counts),semantic_change_fraction_among_active=coverage,conditions=conditions,rows=audit,no_outcomes_observed=True,time_beijing=now()))
 print('PREPARED',dict(counts),'coverage',coverage,'conditions',conditions,flush=True)
if __name__=='__main__':prepare(Path(sys.argv[1]))
