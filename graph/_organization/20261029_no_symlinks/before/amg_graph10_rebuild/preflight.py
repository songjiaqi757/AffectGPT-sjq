import collections,hashlib,json
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import numpy as np
from .data import PROJECT,BASE,read,write,sha
from cue_student.data import Release
from cue_student.prepare import load_labels,UnionFind
from cue_student.eligibility import annotation_eligibility
from cue_student.common import MODALITIES,STATES
RELEASE=PROJECT/'cue_student/artifacts/release_strict_all_modalities_20261020_163131'
RUN=PROJECT/'cue_annotation/runs/mercaptionplus'
def main():
 out=BASE/'preflight';assert not out.exists();out.mkdir()
 release=Release(RELEASE);samples=read(RUN/'samples.json');assert len(samples)==31327
 for name,h in release.manifest['source_artifacts'].items():assert sha(RUN/name)==h,name
 eligibility=annotation_eligibility(RUN,samples)
 for k,v in read(RELEASE/'eligibility.json').items():assert eligibility[k]==v,k
 assert len(eligibility['excluded_sample_ids'])==72
 allowed=set(eligibility['eligible_sample_ids']);assert {r['sample_id'] for r in release.rows}==allowed
 write(out/'recomputed_eligibility.json',eligibility)
 y,mask,states=load_labels(samples,release.ontology,RUN/'labels.csv')
 index={r['sample_id']:i for i,r in enumerate(samples)};take=[index[r['sample_id']] for r in release.rows]
 np.testing.assert_array_equal(y[take],release.targets)
 np.testing.assert_array_equal(mask[take],release.mask)
 np.testing.assert_array_equal(states[take],release.states)
 cues={m:release.ontology['cue_ids'][m] for m in MODALITIES}
 offsets={};n=0
 for m in MODALITIES:offsets[m]=n;n+=len(cues[m])
 uf=UnionFind(sorted(allowed));seen_hash={m:{} for m in ['audio','visual']}
 identity_checks=0
 for r in release.rows:
  for m in ['audio','visual']:
   a=r['media_assets'][m];p=Path(a['path']);st=p.stat()
   assert (st.st_size,st.st_mtime_ns)==(a['bytes'],a['mtime_ns']),(r['sample_id'],m)
   identity_checks+=1;h=a['sha256']
   if h in seen_hash[m]:uf.union(r['sample_id'],seen_hash[m][h])
   seen_hash[m][h]=r['sample_id']
 groups=collections.defaultdict(list)
 for r in release.rows:groups[uf.root(r['sample_id'])].append(r)
 for rows in groups.values():assert len({r['group_id'] for r in rows})==1
 frozen_group_sizes=collections.Counter(r['group_id'] for r in release.rows)
 assert max(frozen_group_sizes.values())==1 and max(map(len,groups.values()))==1
 members=[dict(sample_id=r['sample_id'],group_id=r['group_id'],role=r['role']) for r in release.rows if r['role'] in ('pseudo_train','pseudo_validation')]
 assert collections.Counter(r['role'] for r in members)=={'pseudo_train':27679,'pseudo_validation':3076}
 assert collections.Counter(r['role'] for r in release.rows)=={'pseudo_train':27679,'pseudo_validation':3076,'gold_audit':300,'diagnostic_reserved':200}
 write(out/'selected_members.json',members)
 def check(row):
  sid=row['sample_id'];digest=hashlib.sha256();i=index[sid]
  for m in MODALITIES:
   p=RUN/'annotations'/(sid+'.'+m+'.json');raw=p.read_bytes();ann=json.loads(raw)['annotation']
   assert ann['sample_id']==sid and ann['modality']==m and set(ann['labels'])==set(cues[m]),(sid,m)
   for j,c in enumerate(cues[m]):assert ann['labels'][c]['state']==STATES[states[i,offsets[m]+j]],(sid,m,c)
   digest.update(hashlib.sha256(raw).digest())
  return sid,digest.digest()
 ordered=hashlib.sha256();checked=0
 with ThreadPoolExecutor(max_workers=8) as ex:
  for sid,h in ex.map(check,release.rows):
   ordered.update(sid.encode());ordered.update(h);checked+=3
   if checked%15000==0:print(json.dumps(dict(phase='cue_annotation_verification',checked=checked,total=93765)),flush=True)
 assert checked==93765
 report=dict(passed=True,source_samples=31327,recomputed_eligible_samples=len(allowed),excluded_failed_samples=72,
  failed_tasks=eligibility['failed_tasks'],role_counts=dict(collections.Counter(r['role'] for r in release.rows)),
  graph_fit_samples=27679,selection_validation_samples=3076,excluded_reserved_samples=500,
  exact_hash_grouping_rechecked=True,all_frozen_groups_singleton=True,cross_role_group_leakage=False,
  raw_cue_csv_matrices_rebuilt=True,verified_cue_annotation_records=checked,cue_annotations_ordered_sha256=ordered.hexdigest(),
  raw_media_metadata_identity_checks=identity_checks,raw_media_content_rehashed=False,
  cue_frozen_labels_match=True,split_preserved=True,target_datasets_used=False,model_calls=0,
  files={str(p.relative_to(PROJECT)):sha(p) for p in [RUN/'samples.json',RUN/'labels.csv',RUN/'ontology.json',RUN/'protocol.json',RELEASE/'manifest.json',RELEASE/'members.json',RELEASE/'eligibility.json']},
  limitation='Exact-media grouping uses previously verified frozen SHA256 plus current byte/mtime checks; no new near-duplicate/source provenance or human audit.')
 write(out/'input_selection.json',report);print(json.dumps(report,ensure_ascii=False),flush=True)
if __name__=='__main__':main()
