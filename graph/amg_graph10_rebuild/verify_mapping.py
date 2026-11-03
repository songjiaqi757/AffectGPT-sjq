from graph_paths import hash_matches as _graph_hash_matches
import collections,csv,hashlib,json
from .data import BASE,PROJECT,read,write,sha
from .mapping import Resources,ALIASES,ALIAS,NAMES,node_id
def main():
 root=BASE/'emotion_release';prot=read(root/'protocol.json');identity={k:v for k,v in prot.items() if k!='release_id'}
 assert hashlib.sha256(json.dumps(identity,sort_keys=True,ensure_ascii=False,separators=(',',':')).encode()).hexdigest()==prot['release_id']
 for rel,h in prot['source_sha256'].items():assert _graph_hash_matches(PROJECT / rel, h, sha(PROJECT / rel)),rel
 for rel,h in prot['artifacts'].items():assert _graph_hash_matches(root / rel, h, sha(root / rel)),rel
 for rel,h in read(BASE/'original_preservation_baseline.json').items():assert _graph_hash_matches(PROJECT / rel, h, sha(PROJECT / rel)),rel
 R=Resources();ns=R.readers
 maps={f'wheel{i}':ns['func_get_wheel_cluster'](f'wheel{i}','level1') for i in range(1,6)}
 # Verify term-by-term original mapper independently of build's batched mapping.
 cache={}
 def term(t,w):
  key=(t,w)
  if key not in cache:cache[key]=set(ns['func_map_label_to_synonym']([t.lower().strip()],R.original_formats,R.original_synonyms,maps[w],'case3'))
  return cache[key]
 with (PROJECT/'dataset/mer2025-dataset/track2_train_mercaptionplus.csv').open(encoding='utf-8-sig',newline='') as f:raw_csv={r['name']:r['openset'] for r in csv.DictReader(f)}
 members=read(PROJECT/'cue_student/artifacts/release_strict_all_modalities_20261020_163131/members.json')
 selected={m['sample_id']:m for m in members if m['role'] in ('pseudo_train','pseudo_validation')}
 counts=collections.Counter();roles=collections.Counter();empty=collections.Counter();seen=set();observed_endpoints=set()
 for line in (root/'labels.jsonl').open():
  r=json.loads(line);sid=r['sample_id'];assert sid not in seen;seen.add(sid);m=selected[sid]
  assert r['data_role']==m['role'] and r['source_group_id']==m['group_id']
  raw=R.parse(raw_csv[sid]);assert raw==r['raw_labels']
  views={w:sorted(set().union(*(term(t,w) for t in raw))) for w in maps}
  assert views==r['original_wheel_level1_views']
  union=set().union(*map(set,views.values()));observed_endpoints|=union
  assert sorted(union)==r['wheel_level1_union']
  truth=sorted({ALIAS[x] for x in union});assert truth==r['canonical_labels']
  assert len(truth)==len(set(truth)) and r['emotion_set_mask']==int(bool(truth))
  assert r['emotion_node_ids']==[node_id(x) for x in truth] and not r['oov_canonical_labels']
  assert r['alias_provenance']=={k:sorted(x for x in union if ALIAS[x]==k) for k in truth}
  assert r['eligible_for_graph_statistics']==(m['role']=='pseudo_train' and bool(truth))
  roles[m['role']]+=1;empty[m['role']]+=int(not truth)
  if m['role']=='pseudo_train':counts.update(truth)
 assert seen==set(selected) and observed_endpoints==set(ALIAS) and len(observed_endpoints)==17
 nodes=read(root/'nodes.json');assert [n['canonical_name'] for n in nodes]==NAMES and len(nodes)==10
 for n in nodes:assert n['train_support_samples']==counts[n['canonical_name']]
 out=dict(passed=True,verified_raw_sample_mappings=len(seen),independent_original_termwise_case3_verified=True,
  original_level1_endpoints=17,alias_emotion_nodes=10,original_graph_preserved=True,original_cached_views_matched_during_build=True,
  roles=dict(roles),empty_masked_by_role=dict(empty),train_deduplicated_support=dict(counts),model_calls=0)
 write(root/'verification.json',out);print(json.dumps(out,ensure_ascii=False))
if __name__=='__main__':main()
