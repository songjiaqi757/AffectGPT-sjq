import collections,csv,hashlib,json,shutil
from pathlib import Path
from .mapping import PROJECT,Mapper,ALIASES,NAMES,ALIAS,node_id
from .data import BASE,read,write,sha
RELEASE=PROJECT/'cue_student/artifacts/release_strict_all_modalities_20261020_163131'
OLD=PROJECT/'emotion_nodes/runs/affectgpt_original_v1'
ROOT=BASE/'emotion_release'
def main():
 assert not ROOT.exists()
 # Freeze original graph and prior ten-node graph artifacts.
 frozen=PROJECT/'amg_graph/runs/amg_edges_v2_restore_diagnostic_20261022'
 oldprot=read(frozen/'manifest/protocol.json')
 baseline={str(p.relative_to(PROJECT)):sha(p) for p in [PROJECT/'amg_graph/runs/current.json',PROJECT/'emotion_nodes/runs/current.json',frozen/'manifest/protocol.json',OLD/'protocol.json',OLD/'nodes.json',OLD/'labels.jsonl']}
 for rel in oldprot['artifacts']:baseline[str((frozen/rel).relative_to(PROJECT))]=sha(frozen/rel)
 for rel in oldprot['source_code_sha256']:baseline[rel]=sha(PROJECT/rel)
 prior=PROJECT/'amg_graph10/runs/wheel5_level1_alias10_20261025'
 for relative in read(prior/'manifest/protocol.json')['artifacts']:
  path=prior/relative;baseline[str(path.relative_to(PROJECT))]=sha(path)
 for path in [PROJECT/'amg_graph10/runs/current.json',prior/'manifest/protocol.json']+list((PROJECT/'amg_graph10').glob('*.py')):
  baseline[str(path.relative_to(PROJECT))]=sha(path)
 write(BASE/'original_preservation_baseline.json',baseline)
 source=read(OLD/'protocol.json')['original_source_sha256']
 for rel,h in source.items():assert sha(PROJECT/rel)==h,rel
 members=read(RELEASE/'members.json');members=[r for r in members if r['role'] in ('pseudo_train','pseudo_validation')]
 assert collections.Counter(r['role'] for r in members)=={'pseudo_train':27679,'pseudo_validation':3076}
 selected={r['sample_id'] for r in members}
 with (PROJECT/'dataset/mer2025-dataset/track2_train_mercaptionplus.csv').open(encoding='utf-8-sig',newline='') as f:
  rows={r['name']:r for r in csv.DictReader(f)}
 cached={}
 with (OLD/'labels.jsonl').open() as f:
  for line in f:
   r=json.loads(line)
   if r['sample_id'] in selected:cached[r['sample_id']]=r
 assert set(cached)==selected
 mapper=Mapper();records=[];counts=collections.Counter();role_stats=collections.defaultdict(collections.Counter)
 for m in members:
  sid=m['sample_id'];raw=mapper.r.parse(rows[sid]['openset'])
  assert raw==cached[sid]['raw_labels'],sid
  views,union,labels=mapper.sample(raw)
  for w,v in views.items():assert v==cached[sid]['wheel_views'][w]['level1'],(sid,w)
  valid=bool(labels)
  r=dict(sample_id=sid,source_group_id=m['group_id'],data_role=m['role'],raw_labels=raw,
   original_wheel_level1_views=views,wheel_level1_union=union,canonical_labels=labels,
   alias_provenance={k:sorted(x for x in union if ALIAS[x]==k) for k in labels},
   emotion_node_ids=[node_id(x) for x in labels],emotion_set_mask=int(valid),oov_canonical_labels=[],
   eligible_for_graph_statistics=m['role']=='pseudo_train' and valid)
  records.append(r);st=role_stats[m['role']];st['samples']+=1;st['valid_samples']+=int(valid);st['empty_masked_samples']+=int(not valid)
  if m['role']=='pseudo_train':counts.update(labels)
 assert set(counts)==set(NAMES)
 ROOT.mkdir()
 nodes=[dict(id=node_id(n),node_type='EmotionConcept',canonical_name=n,original_level1_aliases=ALIASES[n],
  ontology_origin='five original AffectGPT wheel level1 endpoint union + user-confirmed aliases',
  train_support_samples=counts[n],train_support_source_groups=counts[n]) for n in NAMES]
 write(ROOT/'nodes.json',nodes);write(ROOT/'wheel_mappings.json',dict(original_case3_level1=mapper.maps,aliases_17_to_10=ALIASES))
 with (ROOT/'labels.jsonl').open('w') as f:
  for r in records:f.write(json.dumps(r,ensure_ascii=False,separators=(',',':'))+'\n')
 write(ROOT/'summary.json',dict(emotion_nodes=10,original_endpoint_count=17,role_summary={k:dict(v) for k,v in role_stats.items()},train_support_samples=dict(counts),model_calls=0,original_cached_wheel_views_exact_match=True))
 files=list(source)+['emotion_nodes/original_adapter.py','amg_graph10_rebuild/mapping.py','amg_graph10_rebuild/prepare.py','amg_graph10_rebuild/original_preservation_baseline.json']
 sources={rel:sha(PROJECT/rel) for rel in files}
 sources[str((OLD/'labels.jsonl').relative_to(PROJECT))]=sha(OLD/'labels.jsonl')
 prot=dict(version='five_original_level1_wheels_alias10_v1',derived_from_cue_release_id=read(RELEASE/'manifest.json')['release_id'],
  mapping='raw openset -> original case3 independently for each wheel1..5 level1 -> set union -> explicit alias -> set dedup',
  aliases=ALIASES,empty_policy='mask all Emotion labels; no neutral and no all-negative conversion',
  source_sha256=sources,artifacts={n:sha(ROOT/n) for n in ['nodes.json','labels.jsonl','wheel_mappings.json','summary.json']},
  graph_fit_role='pseudo_train',validation_role='finite 3x4 source-domain grid; no target datasets',gold_and_target_used=False,model_calls=0,
  original_evaluation_resources_modified=False,original_wheel4_genius_preserved=True)
 prot['release_id']=hashlib.sha256(json.dumps(prot,sort_keys=True,ensure_ascii=False,separators=(',',':')).encode()).hexdigest()
 write(ROOT/'protocol.json',prot)
 print(json.dumps(read(ROOT/'summary.json'),ensure_ascii=False),flush=True)
if __name__=='__main__':main()
