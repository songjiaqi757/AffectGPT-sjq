"""Audit development roles, known groups and text duplicate proxies, without audit-label access."""
import collections,difflib,hashlib,json,re,shutil
import numpy as np
from .common import *
def normalized(row):
 text=' '.join(row.get('text',{}).get(k) or '' for k in ['chinese','english']).lower()
 return re.sub(r'[^\w]+','',text)
def simhash(text):
 grams=set(text[i:i+3] for i in range(max(1,len(text)-2)))
 if not grams:return 0
 raw=np.array([int.from_bytes(hashlib.blake2b(g.encode(),digest_size=8).digest(),'little') for g in grams],np.uint64)
 bits=((raw[:,None]>>np.arange(64,dtype=np.uint64))&1).sum(0)*2>=len(raw)
 return sum(int(b)<<i for i,b in enumerate(bits))
def main():
 c=read(ROOT/'config.json');z=np.load(BASE/'data/labels.npz');rows=read(BASE/'data/input_rows.json');q=np.load(BASE/'data/cue_scores.npz');n=len(rows);parent=list(range(n));size=[1]*n
 def find(a):
  while parent[a]!=a:parent[a]=parent[parent[a]];a=parent[a]
  return a
 def union(a,b):
  a,b=find(a),find(b)
  if a!=b:
   if size[a]<size[b]:a,b=b,a
   parent[b]=a;size[a]+=size[b]
 keys={};texts={};buckets=collections.defaultdict(list);matches=[]
 for i,r in enumerate(rows):
  for key in ['group:'+str(z['groups'][i])]+[m+':'+a['sha256'] for m,a in r['media_assets'].items()]:
   if key in keys:union(i,keys[key])
   else:keys[key]=i
  text=normalized(r)
  if len(text)<c['near_duplicate_text_min_length']:continue
  if text in texts:union(i,texts[text]);matches.append(dict(a=rows[texts[text]]['sample_id'],b=r['sample_id'],kind='exact_long_normalized_transcript'))
  else:texts[text]=i
 # Conservative content-similarity proxy; never infer Speaker/Session identities.
 for text,i in texts.items():
  fingerprint=simhash(text);candidates=set()
  for band in range(4):candidates.update(buckets[(band,(fingerprint>>(16*band))&65535)])
  for j,otherfp,othertext in candidates:
   if abs(len(text)-len(othertext))>max(len(text),len(othertext))*.06:continue
   if (fingerprint^otherfp).bit_count()>c['near_duplicate_simhash_max_hamming']:continue
   if difflib.SequenceMatcher(None,text,othertext,autojunk=False).ratio()>=c['near_duplicate_text_min_ratio']:union(i,j);matches.append(dict(a=rows[j]['sample_id'],b=rows[i]['sample_id'],kind='conservative_long_transcript_near_duplicate_proxy'))
  for band in range(4):buckets[(band,(fingerprint>>(16*band))&65535)].append((i,fingerprint,text))
 groups=np.array(['G21_'+str(find(i)) for i in range(n)]);train_groups=set(groups[z['train']]);original_dev=np.flatnonzero(z['tune']);eligible=original_dev.copy();excluded=[];flagged_near_training=[rows[i]['sample_id'] for i in original_dev if groups[i] in train_groups];eval_idx=np.flatnonzero(z['evaluation']);devgroups=set(groups[eligible]);eval_eligible=eval_idx.copy()
 assert all(rows[i]['role']=='pseudo_validation' for i in eligible);assert not(set(z['sample_ids'][eligible])&set(z['sample_ids'][z['train']]))
 out=ROOT/'data';out.mkdir(exist_ok=True);ids=z['sample_ids'];save(out/'development.npz',scores=q['scores'][eligible],available=q['available'][eligible],targets=z['cue_y'][eligible],label_mask=z['cue_mask'][eligible],groups=groups[eligible],sample_ids=ids[eligible],original_indices=eligible)
 save(out/'internal_evaluation.npz',scores=q['scores'][eval_eligible],available=q['available'][eval_eligible],targets=z['cue_y'][eval_eligible],label_mask=z['cue_mask'][eval_eligible],groups=groups[eval_eligible],sample_ids=ids[eval_eligible],original_indices=eval_eligible)
 counts=collections.Counter(groups[eligible]);write(out/'group_manifest.json',dict(sample_ids=ids.tolist(),group_ids=groups.tolist(),development_groups=len(counts),group_size_distribution=dict(collections.Counter(counts.values())),all_development_groups_singleton=max(counts.values())==1,group_method='Existing manifest groups + exact media SHA256 + conservative long normalized transcript duplicate/SimHash proxies',near_duplicate_pairs=matches,metadata_availability=dict(original_source_video_id=False,speaker=False,session=False,conversation=False,exact_media_sha256=True),limitations='Speaker/Session/source provenance absent; exact hashes and text proxies do not establish true source independence. Audio/visual perceptual near duplicates not fully audited. Text proxies may conservatively over-group repeated utterances.'))
 write(out/'student_overlap_report.json',dict(passed=True,development_count=len(eligible),student_parameter_training_overlap=0,relation_parameter_training_overlap=0,historical_student_selection_exposure=True,historical_v2_calibration_exposure=True,historical_affectgpt_continuation_exposure=True,excluded_development_near_training_groups=excluded,retained_development_near_training_text_proxy_flags=flagged_near_training,Student_checkpoints=read(BASELINE/'runtime/student_binding.json')['checkpoints'],Student_retrained=False))
 write(out/'split_audit_report.json',dict(passed=True,original_calibration_development=len(original_dev),retained_development=len(eligible),internal_evaluation_original=len(eval_idx),internal_evaluation_retained=len(eval_eligible),development_vs_student_train_exact_ID_overlap=0,text_proxy_groups_shared_with_training=len(set(groups[eligible])&train_groups),text_proxy_groups_shared_with_internal_evaluation=len(set(groups[eligible])&set(groups[eval_eligible])),sample_exclusion_performed=False,original_membership_preserved=True,unknown_labels_masked=True,used_target_datasets=False,manual_audit_labels_read=False,label_provenance=c['label_provenance']))
 write(out/'calibration_sample_manifest.json',dict(sample_ids=ids[eligible].tolist(),groups=groups[eligible].tolist(),original_indices=eligible.tolist(),role='historically_exposed_source_pseudolabel_calibration_development',student_parameter_training=False,Student_selection_exposure=True))
 write(out/'split_manifest.json',dict(calibration_development_ids=ids[eligible].tolist(),internal_evaluation_ids=ids[eval_eligible].tolist(),student_training_ids_digest=digest(ids[z['train']].tolist()),human_audit_role='not_used_in_this_round',target_datasets='not_used'))
 audit=dict(status='not_required_for_current_internal_implementation',eligible_for_independent_precision_audit=False,reason='Existing human protocol is positive_confirmation_v1 with Teacher-visible assisted review; unselected labels remain unknown, not explicit negatives. No complete blinded 42-Cue locked audit has been verified. No audit labels read or used.',requires_future_action='Optional later independent manual audit before claiming externally verified Evidence precision; not blocking internal v2.1 release',human_labels_used=False)
 write(out/'locked_audit_eligibility.json',audit);write(out/'audit_sample_manifest.json',dict(role='reserved_not_used',human_labels_read=False,eligible=False));write(out/'prepared.json',dict(complete=True,source_plan_sha256=sha(PROJECT/'改进方案.md'),baseline_manifest_sha256=sha(BASELINE/'release_manifest.json'),baseline_G1_sha256=sha(BASELINE/'learned_relations/G1.npz'),baseline_student_binding_sha256=sha(BASELINE/'runtime/student_binding.json'),development_count=len(eligible),internal_evaluation_count=len(eval_eligible),files_sha256={f.name:sha(f) for f in out.iterdir() if f.is_file() and f.name!='prepared.json'}))
 snap=ROOT/'source_snapshot';snap.mkdir(exist_ok=True);shutil.copy2(PROJECT/'改进方案.md',snap/'改进方案.md');event('v21_data_prepared',development=len(eligible),internal_evaluation=len(eval_eligible),excluded_near_training=len(excluded),near_duplicate_pairs=len(matches),membership_preserved=True,text_proxy_flags_retained=len(flagged_near_training))
if __name__=='__main__':main()
