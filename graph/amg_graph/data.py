import collections,hashlib,json,sys
from graph_paths import Path
import numpy as np
BASE=Path(__file__).resolve().parent
PROJECT=BASE.parent
def read(p):return json.loads(Path(p).read_text())
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,value):
 p=Path(p);p.parent.mkdir(parents=True,exist_ok=True)
 tmp=p.with_name(p.name+".tmp");tmp.write_text(json.dumps(value,ensure_ascii=False,indent=2,allow_nan=False));tmp.replace(p)
def load(release_path=None,emotion_run=None,plan_path=None,annotation_verification=None):
 from cue_student.data import Release
 sys.path.insert(0,str(PROJECT/"appraisal_annotation"));import annotate
 pointer=read(PROJECT/"cue_student/artifacts/current_release.json");release=Release(release_path or pointer["path"])
 emotion_run=Path(emotion_run) if emotion_run else PROJECT/"emotion_nodes/runs"/read(PROJECT/"emotion_nodes/runs/current.json")["run_id"]
 assert read(emotion_run/"protocol.json")["derived_from_cue_release_id"]==release.manifest["release_id"]
 app=PROJECT/"appraisal_annotation/runs/mercaptionplus_v2_4";assert read(app/"status.json")["complete"]
 annotation_verification=Path(annotation_verification) if annotation_verification else app/("current_split_verification.json" if (app/"current_split_verification.json").exists() else "final_verification.json")
 plan_path=Path(plan_path) if plan_path else PROJECT/"图构建.md"
 cue_ids=sum([release.ontology["cue_ids"][m] for m in ["text","audio","visual"]],[])
 ontology=read(app/"ontology.json");dims=list(ontology["dimensions"]);states=sum(ontology["dimensions"].values(),[])
 nodes=read(emotion_run/"nodes.json");emo_ids=[n["id"] for n in nodes];emo_names=[n["canonical_name"] for n in nodes]
 assert len(cue_ids)==42 and len(states)==16 and len(nodes)==188
 selected=[(i,r) for i,r in enumerate(release.rows) if r["role"] in ("pseudo_train","pseudo_validation")]
 rows=[r for i,r in selected];ids=[r["sample_id"] for r in rows];index={sid:i for i,sid in enumerate(ids)}
 indices=[i for i,r in selected]
 Cmask=release.mask[indices].copy();C=(release.targets[indices]==1)&Cmask
 A=np.zeros((len(rows),16),bool);Am=np.zeros((len(rows),6),bool);E=np.zeros((len(rows),188),bool);Em=np.zeros(len(rows),bool)
 dim_of_state=np.array([dims.index(d) for d in dims for s in ontology["dimensions"][d]],dtype=int)
 audit_hash=hashlib.sha256();source_hashes={}
 for i,row in enumerate(rows):
  p=app/"annotations"/(row["sample_id"]+".json");raw=p.read_bytes();rec=json.loads(raw)
  assert rec["sample_id"]==row["sample_id"]
  assert rec["versions"]["prompt_version"]=="appraisal_teacher_v2.4"
  annotation=annotate.validate(json.dumps(rec["annotation"],ensure_ascii=False))
  audit_hash.update(row["sample_id"].encode());audit_hash.update(hashlib.sha256(raw).digest())
  for item in annotation["dimensions"]:
   d=dims.index(item["dimension_id"]);Am[i,d]=item["valid"]
   if item["valid"]:A[i,states.index(item["state"])]=True
 seen=set();name_to_i={n:i for i,n in enumerate(emo_names)}
 with (emotion_run/"labels.jsonl").open() as f:
  for line in f:
   rec=json.loads(line);sid=rec["sample_id"]
   if sid not in index:continue
   i=index[sid];seen.add(sid);assert rec["data_role"]==rows[i]["role"]
   Em[i]=bool(rec["emotion_set_mask"])
   if Em[i]:
    assert not rec["oov_canonical_labels"] and rec["canonical_labels"]
    for name in rec["canonical_labels"]:E[i,name_to_i[name]]=True
 assert seen==set(ids)
 P=np.concatenate([C,A,E],axis=1)
 M=np.concatenate([Cmask,Am[:,dim_of_state],np.repeat(Em[:,None],188,axis=1)],axis=1)
 train=np.array([r["role"]=="pseudo_train" for r in rows]);val=~train
 assert train.sum()==release.manifest["split"]["role_counts"]["pseudo_train"] and val.sum()==release.manifest["split"]["role_counts"]["pseudo_validation"]
 groups=[r["group_id"] for r,t in zip(rows,train) if t]
 group_sizes=collections.Counter(groups);assert max(group_sizes.values())==1,"Non-singleton groups require a cluster-aware permutation implementation"
 assert not ({r["group_id"] for r,t in zip(rows,train) if t}&{r["group_id"] for r,t in zip(rows,train) if not t})
 for p in [Path(release.path)/"manifest.json",Path(release.path)/"members.json",Path(release.path)/"labels.npz",
  emotion_run/"protocol.json",emotion_run/"nodes.json",emotion_run/"labels.jsonl",app/"protocol.json",annotation_verification,app/"format_normalization_audit.json"]:
  source_hashes[str(p.relative_to(PROJECT))]=sha(p)
 source_hashes["图构建.md"]=sha(plan_path)
 source_hashes["appraisal_selected_annotations_ordered_digest"]=audit_hash.hexdigest()
 return dict(source_paths=dict(release=str(release.path),emotion_run=str(emotion_run),source_plan=str(plan_path),annotation_verification=str(annotation_verification)),P=P,M=M,train=train,val=val,rows=rows,ids=ids,cue_ids=cue_ids,states=states,dims=dims,dim_of_state=dim_of_state,
  emotion_ids=emo_ids,emotion_names=emo_names,emotion_nodes=nodes,ontology=ontology,release=release,emotion_run=emotion_run,app_root=app,
  source_hashes=source_hashes,node_ids=cue_ids+states+emo_ids,Am=Am,E=E,Em=Em)
