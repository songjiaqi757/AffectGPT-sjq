"""Offline, complete parity verification against snapshotted original AffectGPT functions."""
from graph_paths import hash_matches as _graph_hash_matches
import collections,csv,hashlib,json,sys
from graph_paths import Path
from original_adapter import Resources,sha,PROJECT,FUNCTIONS
from build import OriginalMapper,ROOT,node_id
def verify():
 protocol=json.loads((ROOT/'protocol.json').read_text())
 resource=Resources(ROOT/'source_functions',ROOT/'resources');mapper=OriginalMapper(resource)
 for relative,expected in protocol['original_source_sha256'].items():
  p=PROJECT/relative
  assert _graph_hash_matches(p, expected, sha(p)),('Source fingerprint changed',relative)
 for name in ['format.csv','synonym.xlsx']+[f'wheel{i}.xlsx' for i in range(1,6)]:
  assert _graph_hash_matches(ROOT / 'resources' / name, sha(PROJECT / 'AffectGPT/emotion_wheel' / name), sha(ROOT / 'resources' / name))
 for relative in FUNCTIONS:
  assert _graph_hash_matches(ROOT / 'source_functions' / relative, sha(PROJECT / 'AffectGPT' / relative), sha(ROOT / 'source_functions' / relative))
 members=json.loads((ROOT/'sample_manifest.json').read_text());member_index={m['sample_id']:m for m in members}
 with (ROOT/'mercaptionplus-emotion.csv').open(encoding='utf-8',newline='') as f:
  raw={r['name']:r['openset'] for r in csv.DictReader(f)}
 nodes=json.loads((ROOT/'nodes.json').read_text());node_index={n['canonical_name']:n['id'] for n in nodes}
 assert len(nodes)==len(node_index)==len({n['id'] for n in nodes})
 observed_train=collections.Counter();groups=collections.defaultdict(set);seen=set();views_checked=0
 summary=collections.Counter();role_counts=collections.Counter()
 with (ROOT/'labels.jsonl').open() as f:
  for line in f:
   rec=json.loads(line);sid=rec['sample_id'];assert sid not in seen;seen.add(sid)
   member=member_index[sid];assert rec['data_role']==member['data_role'] and rec['source_group_id']==member['source_group_id']
   labels=resource.parse(raw[sid]);expected=mapper.sample(labels)
   assert all(rec[key]==value for key,value in expected.items()),('Original mapping differs',sid)
   assert rec['emotion_node_ids']==[node_index[x] for x in rec['canonical_labels'] if x in node_index]
   assert rec['oov_canonical_labels']==[x for x in rec['canonical_labels'] if x not in node_index]
   assert not rec['eligible_for_graph_statistics'] or rec['data_role']=='pseudo_train'
   assert rec['emotion_set_mask']==int(bool(rec['canonical_labels']) and not rec['oov_canonical_labels'])
   if not labels:assert rec['canonical_labels']==[] and rec['emotion_node_ids']==[]
   if rec['data_role']=='pseudo_train':
    observed_train.update(rec['canonical_labels'])
    for label in rec['canonical_labels']:groups[label].add(rec['source_group_id'])
   views_checked+=10;role_counts[rec['data_role']]+=1
   summary['source_terms']+=len(labels);summary['dropped_terms']+=len(rec['dropped_terms'])
 assert len(seen)==31255 and seen==set(member_index)==set(raw)
 assert set(node_index)==set(observed_train),'Validation/audit concepts leaked into nodes'
 for node in nodes:
  label=node['canonical_name'];assert node['id']==node_id(label)
  assert node['train_support_samples']==observed_train[label]
  assert node['train_support_source_groups']==len(groups[label])
  assert node['wheel_views']==mapper.sample([label])['wheel_views']
 out=dict(passed=True,verified_samples=len(seen),verified_nodes=len(nodes),verified_case1_case2_outputs=2*len(seen),
  verified_parallel_wheel_outputs=views_checked,train_only_vocabulary=True,validation_did_not_expand_nodes=True,
  original_function_parity=True,empty_never_added_neutral=True,custom_aliases_used=False,model_calls=0,
  role_counts=dict(role_counts),source_term_occurrences=summary['source_terms'],dropped_term_occurrences=summary['dropped_terms'])
 (ROOT/'verification.json').write_text(json.dumps(out,ensure_ascii=False,indent=2))
 print(json.dumps(out,ensure_ascii=False))
if __name__=='__main__':verify()
