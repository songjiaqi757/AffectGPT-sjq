"""Exact AffectGPT mapping baseline; no API calls, no custom lexical aliases."""
from graph_paths import hash_matches as _graph_hash_matches
from graph_paths import resolve_path as _graph_resolve_path
import argparse,collections,csv,hashlib,json,os,shutil,subprocess,sys,time
from graph_paths import Path
from original_adapter import Resources,ORIGINAL,RESOURCE,PROJECT,FUNCTIONS,sha
VERSION='emotion_ontology_affectgpt_original_v1'
RUNS=Path(__file__).resolve().parent/'runs'
ROOT=Path(os.environ['EMOTION_RUN_ROOT']) if 'EMOTION_RUN_ROOT' in os.environ else RUNS/(json.loads((RUNS/'current.json').read_text())['run_id'] if (RUNS/'current.json').exists() else 'affectgpt_original_v1_no_diagnostic')
_RELEASE_POINTER=PROJECT/'cue_student/artifacts/current_release.json'
RELEASE=Path(json.loads(_RELEASE_POINTER.read_text())['path']) if _RELEASE_POINTER.exists() else PROJECT/'cue_student/artifacts/release_strict_all_modalities_20261020_163131'
SOURCE=PROJECT/'dataset/mer2025-dataset'
def digest(text):return hashlib.sha256(text.encode('utf-8')).hexdigest()
def dump(path,value):Path(path).write_text(json.dumps(value,ensure_ascii=False,indent=2))
def node_id(label):return 'EMO_'+digest(label)[:16]
def read_unique(path,key='name'):
 with Path(path).open(encoding='utf-8-sig',newline='') as f:
  rows=list(csv.DictReader(f))
 ids=[row[key] for row in rows];assert len(ids)==len(set(ids)),f'Duplicate IDs in {path}'
 return {row[key]:row for row in rows}
class OriginalMapper:
 def __init__(self,resources):
  self.r=resources;self.ns=resources.readers;self.fm=resources.original_formats;self.sm=resources.original_synonyms
  self.wheel_maps={(f'wheel{i}',f'level{level}'):self.ns['func_get_wheel_cluster'](f'wheel{i}',f'level{level}') for i in range(1,6) for level in [1,2]}
  self.cache={}
 def term(self,raw):
  term=raw.lower().strip()
  if term not in self.cache:
   forms=self.fm.get(term,[]);selected_form=sorted(forms)[0] if forms else None
   synonyms=self.sm.get(selected_form,[]) if selected_form else []
   mapped=self.ns['func_backward_case2'](term,self.fm,self.sm)
   self.cache[term]=dict(term=term,format_candidates=sorted(set(forms)),selected_format=selected_form,
    synonym_candidates=sorted(set(synonyms)),canonical=mapped or None,
    lexicographic_tie_break=len(set(forms))>1 or len(set(synonyms))>1,
    drop_reason='not_in_format_mapping' if not forms else 'empty_mapping_result' if not mapped else None)
  return self.cache[term]
 def map(self,labels,metric,wheel_map=None):
  return sorted(set(self.ns['func_map_label_to_synonym']([x.lower().strip() for x in labels],self.fm,self.sm,wheel_map,metric)))
 def sample(self,raw_labels):
  trace=[dict(raw=raw,**self.term(raw)) for raw in raw_labels]
  canonical=self.map(raw_labels,'case2')
  views={f'wheel{i}':{f'level{level}':self.map(raw_labels,'case3',self.wheel_maps[(f'wheel{i}',f'level{level}')]) for level in [1,2]} for i in range(1,6)}
  return dict(raw_labels=raw_labels,format_labels=self.map(raw_labels,'case1'),canonical_labels=canonical,
   wheel_views=views,term_trace=trace,dropped_terms=[t['raw'] for t in trace if t['canonical'] is None],
   contains_lexicographic_choice=any(t['lexicographic_tie_break'] for t in trace),empty_after_mapping=not canonical)
def build():
 assert not ROOT.exists(),'A frozen run already exists; verify or use a new version'
 resource=Resources();mapper=OriginalMapper(resource)
 release=json.loads((RELEASE/'manifest.json').read_text())
 assert _graph_hash_matches(RELEASE / 'members.json', release['files']['members.json'], sha(RELEASE / 'members.json')),'Frozen member hash changed'
 members=json.loads((RELEASE/'members.json').read_text())
 cue=json.loads((PROJECT/'cue_annotation/runs/mercaptionplus/samples.json').read_text())
 labels=read_unique(SOURCE/'track2_train_mercaptionplus.csv');descriptions=read_unique(SOURCE/'track3_train_mercaptionplus.csv')
 assert len(labels)==len(descriptions)==31327
 assert set(labels)==set(descriptions)=={s['sample_id'] for s in cue}
 assert len(members)==31255 and {s['sample_id'] for s in members}<=set(labels)
 records=[]
 for member in members:
  sid=member['sample_id'];raw=resource.parse(labels[sid]['openset'])
  mapped=mapper.sample(raw)
  records.append(dict(sample_id=sid,source_group_id=member['group_id'],data_role=member['role'],
   source_description_sha256=digest(descriptions[sid]['reason']),mapping_status='empty_after_original_mapping' if mapped['empty_after_mapping'] else 'mapped',
   **mapped))
 train_counts=collections.Counter();train_groups=collections.defaultdict(set);variants=collections.defaultdict(set)
 for rec in records:
  if rec['data_role']!='pseudo_train':continue
  for label in rec['canonical_labels']:
   train_counts[label]+=1;train_groups[label].add(rec['source_group_id'])
  for trace in rec['term_trace']:
   if trace['canonical']:variants[trace['canonical']].add(trace['raw'])
 nodes=[]
 for label,count in sorted(train_counts.items()):
  nodes.append(dict(id=node_id(label),node_type='EmotionConcept',canonical_name=label,discovered_in='pseudo_train',
   train_support_samples=count,train_support_source_groups=len(train_groups[label]),raw_variants=sorted(variants[label]),
   wheel_views=mapper.sample([label])['wheel_views'],edge_status='not_constructed'))
 node_index={node['canonical_name']:node['id'] for node in nodes}
 stats=collections.defaultdict(collections.Counter);token_stats=collections.Counter();mapping_counts=collections.defaultdict(collections.Counter)
 projected_mismatch=collections.Counter()
 for rec in records:
  rec['emotion_node_ids']=[node_index[x] for x in rec['canonical_labels'] if x in node_index]
  rec['oov_canonical_labels']=[x for x in rec['canonical_labels'] if x not in node_index]
  rec['mapping_nonempty']=bool(rec['canonical_labels'])
  rec['normalization_complete_without_drops']=not rec['dropped_terms']
  rec['emotion_set_mask']=int(rec['mapping_nonempty'] and not rec['oov_canonical_labels'])
  rec['eligible_for_graph_statistics']=bool(rec['data_role']=='pseudo_train' and rec['emotion_set_mask'])
  stat=stats[rec['data_role']];stat['samples']+=1
  stat['mapping_nonempty_samples']+=int(rec['mapping_nonempty'])
  stat['empty_after_mapping_samples']+=int(not rec['mapping_nonempty'])
  stat['samples_with_dropped_terms']+=int(bool(rec['dropped_terms']))
  stat['samples_with_lexicographic_choices']+=int(rec['contains_lexicographic_choice'])
  stat['oov_samples']+=int(bool(rec['oov_canonical_labels']))
  stat['graph_eligible_samples']+=int(rec['eligible_for_graph_statistics'])
  stat['explicit_empty_source_samples']+=int(len(rec['raw_labels'])==0)
  for trace in rec['term_trace']:
   token_stats['source_term_occurrences']+=1
   token_stats['dropped_term_occurrences']+=int(trace['canonical'] is None)
   token_stats['lexicographic_choice_occurrences']+=int(trace['lexicographic_tie_break'])
   mapping_counts[trace['term']][rec['data_role']]+=1
  projected=mapper.sample(rec['canonical_labels'])['wheel_views']
  for w in rec['wheel_views']:
   for level in ['level1','level2']:
    if projected[w][level]!=rec['wheel_views'][w][level]:projected_mismatch[w+'_'+level]+=1
 ROOT.mkdir(parents=True);(ROOT/'resources').mkdir();(ROOT/'source_functions').mkdir()
 for name in ['format.csv','synonym.xlsx']+[f'wheel{i}.xlsx' for i in range(1,6)]:shutil.copy2(_graph_resolve_path(RESOURCE / name), _graph_resolve_path(ROOT / 'resources' / name))
 for relative in FUNCTIONS:
  path=ROOT/'source_functions'/relative;path.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(_graph_resolve_path(ORIGINAL / relative), _graph_resolve_path(path))
 prompt=resource.readers['reason_to_openset_qwen'](reason='<SOURCE_DESCRIPTION>')
 (ROOT/'original_reason_to_openset_prompt.txt').write_text(prompt)
 dump(ROOT/'nodes.json',nodes)
 dump(ROOT/'sample_manifest.json',[dict(sample_id=m['sample_id'],source_group_id=m['group_id'],data_role=m['role']) for m in members])
 with (ROOT/'mercaptionplus-emotion.csv').open('w',newline='',encoding='utf-8') as f:
  writer=csv.DictWriter(f,fieldnames=['name','openset']);writer.writeheader()
  writer.writerows(dict(name=m['sample_id'],openset=labels[m['sample_id']]['openset']) for m in members)
 with (ROOT/'labels.jsonl').open('w',encoding='utf-8') as f:
  for rec in records:f.write(json.dumps(rec,ensure_ascii=False,separators=(',',':'))+'\n')
 fields=['sample_id','source_group_id','data_role','raw_labels','canonical_labels','emotion_node_ids','dropped_terms','oov_canonical_labels','emotion_set_mask','eligible_for_graph_statistics']
 with (ROOT/'labels.csv').open('w',newline='',encoding='utf-8-sig') as f:
  writer=csv.DictWriter(f,fieldnames=fields);writer.writeheader()
  for rec in records:writer.writerow({key:json.dumps(rec[key],ensure_ascii=False) if isinstance(rec[key],list) else rec[key] for key in fields})
 with (ROOT/'mapping_decisions.csv').open('w',newline='',encoding='utf-8-sig') as f:
  fields=['term','selected_format','canonical','format_candidates','synonym_candidates','lexicographic_tie_break','drop_reason',
   'pseudo_train','pseudo_validation','gold_audit','diagnostic_reserved']
  writer=csv.DictWriter(f,fieldnames=fields);writer.writeheader()
  for term,counts in sorted(mapping_counts.items()):
   trace=mapper.term(term)
   writer.writerow({key:json.dumps(trace[key],ensure_ascii=False) if isinstance(trace.get(key),list) else trace.get(key,counts.get(key,0)) for key in fields})
 with (ROOT/'nodes.csv').open('w',newline='',encoding='utf-8-sig') as f:
  fields=['id','canonical_name','train_support_samples','train_support_source_groups','raw_variants','wheel_views']
  writer=csv.DictWriter(f,fieldnames=fields);writer.writeheader()
  for node in nodes:writer.writerow({key:json.dumps(node[key],ensure_ascii=False) if isinstance(node[key],(list,dict)) else node[key] for key in fields})
 dump(ROOT/'wheel_mappings.json',{w:{level:mapper.wheel_maps[(w,level)] for level in ['level1','level2']} for w in [f'wheel{i}' for i in range(1,6)]})
 summary=dict(version=VERSION,total_source_samples=31327,eligible_samples=len(records),excluded_by_cue_policy=72,
  emotion_nodes=len(nodes),canonical_discovery_role='pseudo_train',role_summary={k:dict(v) for k,v in stats.items()},
  term_statistics=dict(token_stats),raw_distinct_terms=len(mapping_counts),original_format_inputs=len(mapper.fm),
  original_synonym_inputs=len(mapper.sm),original_wheel_labels=len(resource.canonical),model_calls=0,
  custom_aliases_used=False,original_empty_to_neutral_conversion_used=False,
  source_labels='official track2_train_mercaptionplus.csv; same file read by original MERCaptionPlus_Dataset',
  lexical_tiebreak_policy='exact original sorted(...)[0]',out_of_dictionary_policy='exact original drop',
  graph_nodes_frozen=True,graph_edges_constructed=False,wheel_projection_noncommutation_samples=dict(projected_mismatch),
  note='Sample Wheel views are computed from raw labels with original case3; projecting case2 nodes can differ and is preserved separately.')
 dump(ROOT/'summary.json',summary)
 source_files={str(p.relative_to(PROJECT)):sha(p) for p in [SOURCE/'track2_train_mercaptionplus.csv',SOURCE/'track3_train_mercaptionplus.csv',
  RELEASE/'members.json',RELEASE/'manifest.json']+[RESOURCE/n for n in ['format.csv','synonym.xlsx']+[f'wheel{i}.xlsx' for i in range(1,6)]]+[ORIGINAL/p for p in FUNCTIONS]}
 protocol=dict(version=VERSION,canonical_metric='case2',wheel_metrics=[f'case3_wheel{i}_level{level}' for i in range(1,6) for level in [1,2]],
  original_git_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=PROJECT,text=True).strip(),
  original_source_sha256=source_files,derived_from_cue_release_id=release['release_id'],
  node_discovery='pseudo_train only; deterministic content-hash IDs',validation_policy='never expand node vocabulary; record canonical OOV labels',
  source_extraction_model='unknown for the supplied official labels; no model was run or claimed',
  fallback_extractor='original reason_to_openset_qwen(), inspected only, not invoked',
  preserves_original_alphabetic_choices=True,preserves_original_unmapped_drops=True,
  custom_semantic_normalization=False,overrides_graph_plan_multicandidate_semantic_review_rule=True,
  override_reason='Original mapping baseline requested in the current conversation',
  forbidden_data_used=False,appraisal_process_modified=False)
 protocol['release_id']=digest(json.dumps(protocol,ensure_ascii=False,sort_keys=True))
 dump(ROOT/'protocol.json',protocol)
 dump(ROOT.parent/'current.json',dict(run_id=ROOT.name,release_id=protocol['release_id'],node_count=len(nodes)))
 print(json.dumps(summary,ensure_ascii=False))
if __name__=='__main__':build()
