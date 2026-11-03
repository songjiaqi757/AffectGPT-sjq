"""Full source input preflight and paired P0-P5 prompt export, with no model generation."""
import collections,copy,gzip,json,os,subprocess,time
from datetime import datetime
from zoneinfo import ZoneInfo
import numpy as np
from .common import *
from .tokenization import actual_interfaces
from .adapter import UnifiedAMGPromptAdapter
from .integration import AffectGPTUnifiedBridge
from .validate import validate
QUESTION="Please infer the person's emotional state and provide your reasoning process."

def categories(g,packet):
 ca=any(n['node_type']=='AppraisalEvidence' for n in g['nodes']);ce=any(n['node_type']=='EmotionEvidence' for n in g['nodes']);cats=['CA_and_CE' if ca and ce else 'CA_only' if ca else 'CE_only' if ce else 'Cue_only'];formal={n['ontology_id'] for n in g['nodes'] if n['node_type']=='CueEvidence'};scores=[n['source_calibrated_score'] for n in g['nodes'] if n['node_type']=='CueEvidence']
 if scores and max(scores)>=.9 and min(scores)<=.6:cats.append('high_and_low_formal_scores')
 if ('TXT_EVALUATION_POSITIVE' in formal or 'TXT_AFFECT_WORD_POSITIVE' in formal) and ('VIS_BROWS_FURROWED' in formal or 'AUD_VOICE_TENSE' in formal):cats.append('contrasting_modality_pattern_not_verified_emotional_conflict')
 if any(r['contribution']<0 for b in packet['audit']['blocks'] for r in b['relations']):cats.append('negative_signed_relation')
 if any(b['relation_type']=='CE' for b in packet['audit']['blocks']):cats.append('serialized_CE')
 return cats

def main():
 c=read(ROOT/'config.json');tok,reader,chat,binding=actual_interfaces();adapter=UnifiedAMGPromptAdapter(tok);bridge=AffectGPTUnifiedBridge(adapter);work=ROOT/'work';work.mkdir(exist_ok=True);write(work/'tokenizer_binding.json',binding);rows={r['sample_id']:r for r in read(BASE/'data/input_rows.json')};source=GRAPH_RELEASE/'runtime/internal_evaluation_sample_graphs.jsonl.gz';manifest=read(GRAPH_RELEASE/'release_manifest.json');stats=collections.Counter();tokens=[];fulltokens=[];allids=[];kept={};bycat=collections.Counter();worst=None;category_ids=collections.defaultdict(list);start=time.time()
 resume=(work/'source_probe_manifest.json').exists() and (work/'all_internal_P4_packets.jsonl.gz').exists();cached=gzip.open(work/'all_internal_P4_packets.jsonl.gz','rt',encoding='utf-8') if resume else None;output_path=work/('all_internal_P4_packets.resumed.jsonl.gz' if resume else 'all_internal_P4_packets.jsonl.gz')
 with gzip.open(source,'rt',encoding='utf-8') as stream,gzip.open(output_path,'wt',encoding='utf-8',compresslevel=4) as out:
  for i,line in enumerate(stream):
   g=json.loads(line);sid=g['sample_id'];row=rows[sid];cached_record=json.loads(next(cached)) if cached else None
   if cached_record is not None:
    assert cached_record['sample_id']==sid;prepared=dict(prompt=cached_record['final_prompt'],evidence=cached_record['packet'])
   else:prepared=bridge.prepare(reader,chat,g,QUESTION,row['text']['english'])
   packet=prepared['evidence'];audit=packet['audit'];tokens.append(audit['evidence_tokens']);fulltokens.append(audit['full_prompt_tokens']);allids.append(sid);stats['samples']+=1;stats['fallback']+=int(audit['fallback']);stats['formal_Cue_nodes']+=sum(n['node_type']=='CueEvidence' for n in g['nodes']);stats['serialized_Cue_nodes']+=len(audit['cue_ids']);stats['CA_targets']+=sum(b['relation_type']=='CA' for b in audit['blocks']);stats['CE_targets']+=sum(b['relation_type']=='CE' for b in audit['blocks']);stats['CA_edges']+=audit['CA_edge_count'];stats['CE_edges']+=audit['CE_edge_count'];stats['negative_edges']+=sum(r['contribution']<0 for b in audit['blocks'] for r in b['relations']);cats=categories(g,packet)
   for cat in cats:
    bycat[cat]+=1
    if len(category_ids[cat])<3:category_ids[cat].append(sid);kept[sid]=g
   if sid=='samplenew3_00000827':kept[sid]=g
   if worst is None or audit['evidence_tokens']>worst[0]:worst=(audit['evidence_tokens'],sid,g)
   face=PROJECT/'dataset/mer2025-dataset/openface_face'/sid/(sid+'.npy');original_input=dict(sample_id=sid,video_path=row['video_path'],audio_path=row['audio_path'],face_path=str(face),subtitle=row['text']['english'],question=QUESTION);stats['missing_face_assets']+=int(not face.is_file());out.write(json.dumps(dict(sample_id=sid,original_input=original_input,final_prompt=prepared['prompt'],packet=packet),ensure_ascii=False,separators=(',',':'))+'\n')
   if i%100==0:event('unified_full_input_preflight',done=i,total=1538,elapsed_seconds=round(time.time()-start,1))
 if cached is not None:cached.close();output_path.replace(work/'all_internal_P4_packets.jsonl.gz')
 kept[worst[1]]=worst[2];ids=sorted(kept,key=lambda sid:digest(['frozen_source_probe_v1',sid]));graphs=[kept[sid] for sid in ids];write(work/'source_probe_manifest.json',dict(sample_ids=ids,category_sample_ids=dict(category_ids),category_population_counts=dict(bycat),selection='First three original-order source samples per frozen structural/probe category, plus named documentation sample and maximum token stress case; no labels or target data selected',source_graph_type_scope='Contrasting modality Cue pattern is an input-contract probe, not verified semantic/emotional conflict',source_graph_count=1538,source_question=QUESTION,excluded_samples=0))
 acceptance=validate(adapter,reader,chat,graphs,rows);write(work/'acceptance_report.json',acceptance)
 comparisons={k:[] for k in ['P0','P1','P2','P3','P4','P5']};examples=work/'examples';examples.mkdir(exist_ok=True)
 with (work/'source_probe_P0_P5.jsonl').open('w') as out:
  for g in graphs:
   sid=g['sample_id'];row=rows[sid]
   for condition in comparisons:
    prepared=bridge.prepare_ablation(reader,chat,g,QUESTION,row['text']['english'],condition);a=prepared['evidence']['audit'];comparisons[condition].append(dict(sample_id=sid,evidence_tokens=a['evidence_tokens'],full_prompt_tokens=a['full_prompt_tokens'],fallback=a['fallback'],CA_edges=a.get('CA_edge_count',0),CE_edges=a.get('CE_edge_count',0),CA_targets=sum(b['relation_type']=='CA' for b in a.get('blocks',[])),CE_targets=sum(b['relation_type']=='CE' for b in a.get('blocks',[]))));out.write(json.dumps(dict(sample_id=sid,condition=condition,final_prompt=prepared['prompt'],packet=prepared['evidence'],original_question=QUESTION,subtitle=row['text']['english'],actual_model_generation_run=False),ensure_ascii=False)+'\n')
    if sid=='samplenew3_00000827':(examples/(sid+'_'+condition+'.txt')).write_text(prepared['evidence']['text'])
   p=adapter.build(g);cats=categories(g,p)
   for cat in cats:
    path=examples/(cat+'.json')
    if not path.exists():write(path,p);(examples/(cat+'.txt')).write_text(p['text'])
 summaries={k:dict(samples=len(v),mean_evidence_tokens=float(np.mean([x['evidence_tokens'] for x in v])),maximum_evidence_tokens=max(x['evidence_tokens'] for x in v),maximum_full_prompt_tokens=max(x['full_prompt_tokens'] for x in v),CA_edges=sum(x['CA_edges'] for x in v),CE_edges=sum(x['CE_edges'] for x in v),fallback=sum(x['fallback'] for x in v)) for k,v in comparisons.items()};write(work/'P0_P5_paired_input_report.json',dict(status='paired_input_preflight_complete_not_generation',summaries=summaries,per_sample=comparisons,same_checkpoint_required_for_generation=True,original_questions_and_subtitles_preserved=True,actual_model_generation_run=False))
 report=dict(passed=True,samples=len(allids),source_membership_sha256=digest(allids),original_source_member_ids_sha256=digest(np.load(GRAPH_RELEASE/'data/internal_evaluation.npz')['sample_ids'].tolist()),excluded_samples=0,mean_evidence_tokens=float(np.mean(tokens)),maximum_evidence_tokens=max(tokens),p95_evidence_tokens=float(np.quantile(tokens,.95)),maximum_full_prompt_tokens=max(fulltokens),evidence_token_budget=c['evidence_token_budget'],prompt_token_budget=c['max_prompt_tokens'],max_new_tokens=c['default_max_new_tokens'],total_context_limit=c['default_context_limit'],statistics=dict(stats),graph_category_counts=dict(bycat),actual_generation_run=False,elapsed_seconds=time.time()-start)
 assert report['samples']==1538 and report['source_membership_sha256']==report['original_source_member_ids_sha256'];assert report['maximum_evidence_tokens']<=1000 and report['maximum_full_prompt_tokens']+512<=2048;write(work/'full_source_input_report.json',report)
 write(work/'frozen_assets_report.json',dict(passed=True,graph_release_id=manifest['release_id'],graph_release_manifest_sha256=sha(GRAPH_RELEASE/'release_manifest.json'),G1_sha256=sha(GRAPH_RELEASE/'learned_relations/G1.npz'),Cue_admission_sha256=sha(GRAPH_RELEASE/'admission/cue_admission_policy.json'),all_graph_release_assets_unchanged=all(sha(GRAPH_RELEASE/p)==h for p,h in manifest['artifact_sha256'].items()),Student_retrained=False,G1_refitted=False,calibration_changed=False,threshold_changed=False))
 gpu=subprocess.run(['nvidia-smi','--query-gpu=name,memory.total,memory.used,utilization.gpu','--format=csv'],capture_output=True,text=True);write(work/'paired_generation_status.json',dict(status='not_run',reason='This run validates actual tokenization, prompt serialization and integration contracts. No AffectGPT model generation was executed; the inspected GPU is occupied by existing work.',GPU_snapshot=gpu.stdout,existing_jobs_modified=False,nine_target_evaluation_run=False,production_default_adopted=False))
 write(work/'complete.json',dict(complete=True,scope='Unified adapter implementation, complete source input preflight and paired P0-P5 input export',acceptance_checks=len(acceptance['checks']),samples=1538,paired_probe_samples=len(graphs),actual_generation_run=False,stats=report));event('unified_preflight_complete',samples=1538,probe_samples=len(graphs),checks=len(acceptance['checks']))
if __name__=='__main__':main()
