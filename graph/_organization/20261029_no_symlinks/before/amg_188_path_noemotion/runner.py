"""Server-only path/list factorial follow-up; original artifacts are read-only."""
import argparse,ast,collections,copy,csv,io,json,math,os,runpy,signal,subprocess,sys,time,traceback,types,warnings
from pathlib import Path
from amg_d_graph_compare.common import ROOT,PYTHON,read,sha,canonical,atomic_json,require,now,plan,verify_code,environment,locked,sid_key
from amg_188_audit.policy import make_prompt
from amg_188_audit.metrics import judge_key,npdict,npwrite
SOURCE=ROOT/"amg_188_audit/runs/winner188_20261028_114057"
PACKAGE="amg_188_path_noemotion"
CONDS=["C","E","P","H"]
CAT={"MER2023","MER2024","MELD","IEMOCAPFour"}
POL={"CMUMOSI","CMUMOSEI","SIMS","SIMSv2"}
def dump(path,x): atomic_json(path,x)
def bundle(run,row):
 x=read(Path(run)/"prompt_cache"/(sid_key(row["sample_id"])+".json"))
 require(x["bundle_id"]==canonical({k:v for k,v in x.items() if k!="bundle_id"}),"Bundle drift")
 return x
def extend(b,t):
 b=copy.deepcopy(b);txt=b["texts"]["P"]
 lines=txt.splitlines()
 require(sum(x.startswith("Emotion hypotheses: ") for x in lines)<=1,"Unexpected Emotion line count")
 text="\n".join(x for x in lines if not x.startswith("Emotion hypotheses: "))
 require([x for x in text.splitlines() if x.startswith("Supporting links:")]==[x for x in lines if x.startswith("Supporting links:")],"Path changed")
 from amg_finetune_nogc.prompts import encode
 info=copy.deepcopy(b["infos"]["P"]);info.update(ablation="H",ablation_description="Cue+Appraisal+exact P paths; explicit Emotion list removed",emotion_candidates_displayed=0,graph_text_id=canonical(text),graph_tokens=len(encode(t,text)),emotion_words_in_paths_retained=True)
 b["texts"]["H"]=text;b["infos"]["H"]=info;b.get("expected_prompt_ids",{}).pop("H",None);b.pop("bundle_id",None)
 return b
def setup():
 require(os.environ.get("CUDA_VISIBLE_DEVICES")=="","CPU-only setup required")
 verify_code(SOURCE);old=plan(SOURCE);require(read(SOURCE/"final_verification.json")["passed"],"Parent not complete")
 root=ROOT/PACKAGE;root.mkdir(exist_ok=True)
 require(not (root/"current_run.json").exists(),"Follow-up already exists; inspect it instead of duplicating")
 import datetime
 from zoneinfo import ZoneInfo
 run=root/"runs"/("path_noemotion_"+datetime.datetime.now(ZoneInfo("Asia/Shanghai")).strftime("%Y%m%d_%H%M%S"));run.mkdir(parents=True)
 for n in ["jobs","predictions","scores","prompt_cache","generation_cache","judge_cache/openset","judge_cache/sentiment","analysis","workers"]:(run/n).mkdir(parents=True,exist_ok=True)
 p=copy.deepcopy(old)
 p.update(schema_version="188_path_emotion_list_factorial_v1",created_at_beijing=now(),source_run=str(SOURCE),training_run=str(run),conditions=CONDS,condition_descriptions={"C":"Cue+Appraisal, no paths, no Emotion list","E":"Cue+Appraisal+Emotion list, no paths","P":"Original complete prompt","H":"P with only the Emotion hypotheses line deleted; paths verbatim"},variants=[],variant_epochs={},variant_bases={},checkpoint_by_variant={},ablation_by_variant={},dataset_by_variant={},logical_jobs=36,sample_predictions_total=51196,physical_nodes=[{"name":"A800","ssh_port":34989,"index":0,"slots":[0,1,2,3],"gpu_uuid":"GPU-be2112e9-43e2-43e7-da85-ff9198a7c875"},{"name":"A100","ssh_port":31764,"index":1,"slots":[4],"gpu_uuid":"GPU-efe8cc5b-b9d6-ac76-5e9e-9712559eb942"}],inference_processes_per_node={"A800":4,"A100":1},max_inference_seconds=43200,max_judge_stage_seconds=21600,
 protocol=dict(scope="Exploratory mechanism follow-up on previously inspected tests, not independent development validation",intervention="Delete only explicit Emotion hypotheses line from exact P; path Emotion endpoints retained",active_samples="All samples whose H differs from C or P; all four arms freshly regenerated on same GPU and same worker per sample",inactive_samples="All four prompts equal; reuse parent exact same-input responses after verification",hardware="Two separate single-GPU nodes, local CUDA device 0 on each; paired arms for a sample never split across hardware",primary_contrasts=["H-C: paths without explicit Emotion list","H-P: remove explicit Emotion list with paths fixed"],secondary_contrasts=["E-C: explicit Emotion list without paths","P-E: paths with explicit Emotion list"],interaction="(P-E)-(H-C)",automatic_training=False,graph_rebuild=False,judge_protocol="Exact parent content-seeded global cache; reuse parent judge outputs only on exact protocol/stage/input key",generation_seeds="Unchanged per-sample seed; all active arms rerun to avoid mixing old/new GPU results"))
 p.pop("plan_id",None)
 for d in p["datasets"]:
  for c in CONDS:
   v="path188_"+d+"_"+c;ov="winner_"+d+"_"+("P" if c=="H" else c)
   p["variants"].append(v);p["variant_epochs"][v]=old["variant_epochs"][ov];p["variant_bases"][v]=old["variant_bases"][ov];p["checkpoint_by_variant"][v]=old["checkpoint_by_variant"][ov];p["ablation_by_variant"][v]=c;p["dataset_by_variant"][v]=d
 for fn in ["original_config.json","evaluation_resources.json","references.json","train_records.json"]:dump(run/fn,read(SOURCE/fn))
 assets=read(SOURCE/"input_assets.json")
 for f,s in assets.items():
  st=Path(f).stat();require(st.st_size==s["bytes"] and st.st_mtime_ns==s["mtime_ns"],"Parent media stat changed: "+f)
 for f,s in {v["path"]:v for v in p["checkpoint_by_variant"].values()}.items():require(sha(f)==s["sha256"],"Checkpoint changed")
 from amg_188_audit.setup import extracted
 os.chdir(ROOT/"AffectGPT")
 config=types.SimpleNamespace(**runpy.run_path("config.py"))
 from transformers import AutoTokenizer
 scope=dict(AutoTokenizer=AutoTokenizer,config=config);exec(extracted(ROOT/"AffectGPT/my_affectgpt/models/tokenizer.py","load_tokenizer_from_LLM"),scope)
 t=scope["load_tokenizer_from_LLM"]("Qwen25");scope={};exec(extracted(ROOT/"AffectGPT/my_affectgpt/datasets/datasets/base_dataset.py","get_prompt_for_multimodal"),scope)
 reader=types.SimpleNamespace();reader.get_prompt_for_multimodal=types.MethodType(scope["get_prompt_for_multimodal"],reader)
 chat=types.SimpleNamespace(tokenizer=t,replace_token_for_multimodal=lambda x:x)
 counts={};tasks=[[] for _ in range(5)];max_tokens=0;fingerprints={}
 for d,di in p["datasets"].items():
  require(sha(di["path"])==di["sha256"],"Dataset drift")
  rows=read(di["path"]);count=collections.Counter()
  for row in rows:
   f=SOURCE/"prompt_cache"/(sid_key(row["sample_id"])+".json");original=read(f)
   require(original["bundle_id"]==canonical({k:v for k,v in original.items() if k!="bundle_id"}),"Parent bundle drift")
   b=extend(original,t)
   for c in CONDS:
    _,info=make_prompt(reader,chat,row,b,dict(p,variant="path188_"+d+"_"+c))
    if c!="H":require(info["prompt_id"]==original["expected_prompt_ids"][c],"Parent prompt drift")
    b["expected_prompt_ids"][c]=info["prompt_id"];max_tokens=max(max_tokens,info["prompt_tokens"])
   active=len({b["expected_prompt_ids"][c] for c in CONDS})>1
   require(active==bool(b["infos"]["P"]["displayed_paths"]),"Unexpected path/list gate mismatch")
   if not active:require(len({b["texts"][c] for c in CONDS})==1,"Inactive text mismatch")
   count["samples"]+=1;count["active"]+=active;count["reused_inactive"]+=not active
   if active:tasks[int(canonical(row["sample_id"])[:8],16)%5].append(dict(dataset=d,name=row["name"],sample_id=row["sample_id"]))
   b["bundle_id"]=canonical(b);dump(run/"prompt_cache"/f.name,b);fingerprints[str(f)]=sha(f)
  counts[d]=dict(count)
  for c in CONDS:
   v="path188_"+d+"_"+c;(run/"predictions"/v).mkdir()
   dump(run/"jobs"/(v+".json"),dict(job_id=v,variant=v,dataset=d,epoch=p["checkpoint_by_variant"][v]["epoch"],samples=len(rows),state="pending"))
  print("FROZEN",d,counts[d],flush=True)
 probe=extend(read(SOURCE/"source_probe_bundle.json"),t);sr=read(run/"train_records.json")[0]
 for c in CONDS:probe["expected_prompt_ids"][c]=make_prompt(reader,chat,sr,probe,dict(p,variant="path188_"+list(p["datasets"])[0]+"_"+c))[1]["prompt_id"]
 probe["bundle_id"]=canonical({k:v for k,v in probe.items() if k!="bundle_id"});dump(run/"source_probe_bundle.json",probe)
 active=sum(x["active"] for x in counts.values());require(active==4777,"Active count changed")
 p.update(active_samples=active,new_generations_planned=active*4,reused_logical_predictions=(12799-active)*4,unique_generation_inputs=active*4)
 p["plan_id"]=canonical(p);dump(run/"plan.json",p)
 for i,items in enumerate(tasks):dump(run/"workers"/("tasks_"+str(i)+".json"),items)
 dump(run/"parent_prompt_hashes.json",fingerprints)
 protected=[SOURCE/x for x in ["plan.json","code_manifest.json","metrics_all.json","final_verification.json","original_config.json","evaluation_resources.json","input_assets.json","analysis/ANALYSIS.md"]]
 for d in p["datasets"]:
  for c in ["C","E","P"]:
   j=read(SOURCE/"jobs"/("winner_"+d+"_"+c+".json"));protected.extend([Path(j["official_npz"]),Path(j["prediction_path"])])
 dump(run/"parent_artifact_hashes.json",{str(f):sha(f) for f in protected})
 files=copy.deepcopy(read(SOURCE/"code_manifest.json")["files"]);files[PACKAGE+"/runner.py"]=sha(root/"runner.py");files[PACKAGE+"/__init__.py"]=sha(root/"__init__.py")
 files["amg_d_graph_compare/common.py"]=sha(ROOT/"amg_d_graph_compare/common.py");files["amg_runtime/common.py"]=sha(ROOT/"amg_runtime/common.py")
 dump(run/"code_manifest.json",dict(files=files))
 pre=dict(passed=True,counts=counts,active_samples=active,new_generations=active*4,reused_logical_predictions=(12799-active)*4,max_prompt_tokens=max_tokens,paths_verbatim=True,only_Emotion_line_deleted=True,all_parent_C_E_P_prompt_ids_matched=True,task_counts=[len(x) for x in tasks],CUDA_initialized=__import__("torch").cuda.is_initialized(),time_beijing=now())
 dump(run/"cpu_preflight.json",pre)
 (run/"EXPERIMENT.md").write_text("# 原188类图：路径与显式Emotion列表的四条件补测\n\n用户确认：H只删除Emotion hypotheses行，原路径逐字保留，路径中的Emotion词仍存在。\nC=无列表/无路径；E=有列表/无路径；P=有列表/有路径；H=无列表/有路径。\n原图、Cue、门控、7个逐集赢家权重、媒体、字幕、逐样本seed、解码和评分协议全部冻结。\n主要比较H-C和H-P；次要比较E-C和P-E；交互(P-E)-(H-C)。\n\n12799条九集记录，4777条活跃样本四组同GPU/同worker重新生成，共19108次；8022条零干预样本复用原来已完全相同的回答，共32088条逻辑复用。复用不作为独立重复。\nA800端口34989、A100端口31764，各单卡80GB，A800四进程、A100单进程（主机内存32GB），先通过1536输入+1200输出的源样本容量测试再读目标媒体。物理GPU UUID与数据记录绑定。\n所有推理退出并释放显存后才启动评分。按唯一内容复用父轮抽取/极性缓存；新内容使用同协议内容seed。原结果不覆盖。\n\n两台GPU同一样本的四组始终在同一硬件，历史C/E/P仅作锚点并报告本轮差异。正式指标同时报告HIT/M、WAF/ACC/类召回、OV F/P/R、纠错/伤害和输出规模。2000次配对bootstrap，可识别来源按视频/对话聚类，其余按样本；不包含生成或训练多种子不确定性。\n这仍是已查看测试集的机制诊断，不解决1253条开发候选的媒体缺失和SIMS系列来源重叠；不自动训练、改图或按测试集选权重。\n")
 dump(run/"status.json",dict(phase="prepared",plan_id=p["plan_id"],time_beijing=now()))
 dump(root/"current_run.json",dict(run=str(run),plan_id=p["plan_id"]))
 print(json.dumps(dict(run=str(run),preflight=pre),ensure_ascii=False),flush=True)
def gpu():
 return subprocess.check_output(["nvidia-smi","--query-gpu=uuid,name,memory.used","--format=csv,noheader,nounits"],text=True).strip()
def worker(run,slot):
 run=Path(run);p=plan(run);verify_code(run);idx=slot//4;node=p["physical_nodes"][idx]["name"]
 dest=run/"workers"/("worker_"+str(slot)+".json");state=dict(state="loading",slot=slot,node=node,pid=os.getpid(),started_at_beijing=now())
 def update(**kw):state.update(kw,updated_at_beijing=now());dump(dest,state)
 try:
  update();import torch
  import amg_inference.model as original
  original.make_prompt=make_prompt;cfg=copy.deepcopy(p);cfg["variant"]=p["variants"][0];cfg["training_plan_id"]=p["plan_id"]
  BasePredictor=original.Predictor
  load_lock=ROOT/PACKAGE/(p["physical_nodes"][idx]["gpu_uuid"]+".model_loading.lock")
  class SerializedPredictor(BasePredictor):
   def __init__(self,settings):
    with locked(load_lock,blocking=True):super().__init__(settings)
   def load(self,spec,job=None):
    if self.loaded==spec["sha256"]:return
    with locked(load_lock,blocking=True):return super().load(spec,job)
  model=SerializedPredictor(cfg) if idx==1 else BasePredictor(cfg)
  model.load(p["checkpoint_by_variant"][cfg["variant"]]);update(state="probe_loaded")
  while not (run/("probe_go_"+node+".json")).exists():time.sleep(2)
  oldstop=model.chat.stopping_criteria
  try:_,info=model.predict(read(run/"train_records.json")[0],read(run/"source_probe_bundle.json"),42+slot%4,stress=True)
  finally:model.chat.stopping_criteria=oldstop
  require(1530<=info["stress_prompt_tokens"]<=1536 and info["stress_generated_tokens"]==1200,"Full-window capacity failed")
  update(state="probe_passed",capacity_passed=True,probe_info=info,peak_memory_bytes=int(torch.cuda.max_memory_allocated()))
  override=read(run/"execution_override.json") if (run/"execution_override.json").exists() else {}
  four_lane_gate=idx==1 and len(override.get("slots_by_node",{}).get("A100",[]))==4
  while not (run/"inference_approved.json").exists() or (four_lane_gate and not (run/"fourprocess_inference_approved_A100.json").exists()):
   require(not (run/"failure.json").exists(),"Peer/controller failed");time.sleep(2)
  items=read(run/"workers"/("tasks_"+str(slot)+".json"));lookup={};assets=read(SOURCE/"input_assets.json")
  for d in p["datasets"]:lookup[d]={r["sample_id"]:r for r in read(p["datasets"][d]["path"])}
  items.sort(key=lambda x:(p["checkpoint_by_variant"]["path188_"+x["dataset"]+"_P"]["sha256"],x["dataset"],x["sample_id"]))
  hardware=dict(node=node,gpu_uuid=p["physical_nodes"][idx]["gpu_uuid"],gpu_snapshot=gpu(),slot=slot,cuda_version=torch.version.cuda,torch_version=torch.__version__,compute_capability=list(torch.cuda.get_device_capability()))
  completed=0;generated=0
  for item in items:
   row=lookup[item["dataset"]][item["sample_id"]];b=bundle(run,row);seed=(42+int(canonical(row["sample_id"])[:8],16))%2**32
   for k in ["audio_path","face_path"]:
    st=Path(row[k]).stat();ex=assets[row[k]];require(st.st_size==ex["bytes"] and st.st_mtime_ns==ex["mtime_ns"],"Media changed")
   for c in CONDS:
    v="path188_"+row["dataset"]+"_"+c;cfg["variant"]=v;spec=p["checkpoint_by_variant"][v];out=run/"predictions"/v/(sid_key(row["sample_id"])+".json")
    if out.exists():
     x=read(out);require(x["plan_id"]==p["plan_id"] and x["seed"]==seed and x["prompt_info"]["prompt_id"]==b["expected_prompt_ids"][c],"Stale partial output");continue
    update(state="inference",dataset=row["dataset"],sample_id=row["sample_id"],condition=c,completed_active_samples=completed,generated_responses=generated,total_active_samples=len(items))
    model.load(spec);response,pi=model.predict(row,b,seed)
    require(pi["prompt_id"]==b["expected_prompt_ids"][c],"GPU prompt mismatch")
    key=canonical(dict(checkpoint=spec["sha256"],sample_id=row["sample_id"],prompt_id=pi["prompt_id"],seed=seed,generation=p["generation"],dataset_input=p["datasets"][row["dataset"]]["sha256"]))
    pi.update(generation_key=key,generation_cache_hit=False)
    dump(run/"generation_cache"/(key+".json"),dict(generation_key=key,response=response,checkpoint_sha256=spec["sha256"],sample_id=row["sample_id"],prompt_id=pi["prompt_id"],seed=seed,hardware=hardware))
    dump(out,dict(sample_id=row["sample_id"],name=row["name"],dataset=row["dataset"],variant=v,epoch=spec["epoch"],response=response,checkpoint=spec,plan_id=p["plan_id"],seed=seed,prompt_info=pi,hardware=hardware,reused=False,created_at_beijing=now()))
    generated+=1
   completed+=1
  update(state="complete",completed_active_samples=completed,generated_responses=generated,finished_at_beijing=now())
 except BaseException as e:update(state="failed",error=repr(e),traceback=traceback.format_exc());raise
def materialize(run):
 import numpy as np
 run=Path(run);p=plan(run);reuse=0;fresh=0;baseline=collections.defaultdict(collections.Counter)
 for d in p["datasets"]:
  rows=read(p["datasets"][d]["path"]);prior={}
  for c in ["C","E","P"]:
   j=read(SOURCE/"jobs"/("winner_"+d+"_"+c+".json"));prior[c]={x["name"]:x for x in map(json.loads,Path(j["prediction_path"]).read_text().splitlines())}
  for c in CONDS:
   v="path188_"+d+"_"+c;out=run/"predictions"/v;spec=p["checkpoint_by_variant"][v];values={};records=[]
   for row in rows:
    b=bundle(run,row);f=out/(sid_key(row["sample_id"])+".json");active=len({b["expected_prompt_ids"][q] for q in CONDS})>1
    if not active:
     require(len({prior[q][row["name"]]["response"] for q in ["C","E","P"]})==1,"Inactive parent answers unequal")
     src=prior["C" if c=="H" else c][row["name"]];require(src["prompt_info"]["prompt_id"]==b["expected_prompt_ids"][c],"Inactive reuse mismatch")
     x=copy.deepcopy(src);x.update(variant=v,plan_id=p["plan_id"],prompt_info=copy.deepcopy(b["infos"][c]),reused=True,reuse_source_run=str(SOURCE),reuse_source_variant=src["variant"])
     x["prompt_info"].update(prompt_id=b["expected_prompt_ids"][c],prompt_tokens=src["prompt_info"]["prompt_tokens"]);dump(f,x);reuse+=1
    else:fresh+=1
    x=read(f);require(x["plan_id"]==p["plan_id"] and x["checkpoint"]["sha256"]==spec["sha256"] and x["prompt_info"]["prompt_id"]==b["expected_prompt_ids"][c],"Prediction provenance mismatch")
    if active and c!="H":
     baseline[d][c+"_checked"]+=1;baseline[d][c+"_same_answer"]+=x["response"]==prior[c][row["name"]]["response"]
    values[row["name"]]=x["response"];records.append(x)
   with (out/"predictions.jsonl").open("w") as f:
    for x in records:f.write(json.dumps(x,ensure_ascii=False)+"\n")
   npwrite(out/"name2reason.npz",name2reason=values)
   j=read(run/"jobs"/(v+".json"));j.update(state="complete",checkpoint=spec,prediction_path=str(out/"predictions.jsonl"),official_npz=str(out/"name2reason.npz"),finished_at_beijing=now());dump(run/"jobs"/(v+".json"),j)
  print("MATERIALIZED",d,flush=True)
 require(reuse==p["reused_logical_predictions"] and fresh==p["new_generations_planned"],"Materialization count changed")
 dump(run/"baseline_reproduction.json",dict(active_answer_matches={k:dict(v) for k,v in baseline.items()},fresh_predictions=fresh,reused_predictions=reuse,note="All active controls regenerated on same GPU as H; historical equality is diagnostic, not assumed."))
def prepare_judge(run,stage):
 from amg_188_audit.metrics import prepare
 run=Path(run);total=prepare(run,stage);p=plan(run);reused=0
 for x in read(run/("judge_inputs_"+stage+".json")):
  f=run/"judge_cache"/stage/(x["key"]+".json");src=SOURCE/"judge_cache"/stage/f.name
  if not f.exists() and src.exists():
   y=read(src);require(y["key"]==x["key"] and y["text"]==x["text"] and y["seed"]==x["seed"] and y["judge_protocol_id"]==p["judge_protocol_id"],"Parent judge cache mismatch")
   f.symlink_to(src);reused+=1
 dump(run/("judge_preparation_"+stage+".json"),dict(total=total,reused_parent_exact_content=reused,time_beijing=now()))
 return total
def judge(run,index,stage):
 run=Path(run);p=plan(run);verify_code(run);require(read(run/"evaluation_barrier.json")["passed"],"Inference barrier missing")
 rows=[x for x in read(run/("judge_inputs_"+stage+".json")) if int(x["key"][:8],16)%2==index]
 dest=run/("judge_"+stage+"_"+str(index)+".json");state=dict(state="loading",index=index,stage=stage,pid=os.getpid(),total=len(rows))
 def update(**kw):state.update(kw,time_beijing=now());dump(dest,state)
 try:
  update();pending=[x for x in rows if not (run/"judge_cache"/stage/(x["key"]+".json")).exists()]
  for f,h in read(run/"evaluation_resources.json")["files"].items():require(sha(f)==h,"Evaluation resource changed")
  if pending:
   os.chdir(ROOT/"AffectGPT");sys.path.insert(0,str(ROOT/"AffectGPT"));import evaluation
   llm,t,params=evaluation.func_read_batch_calling_model("Qwen25")
   fn=evaluation.reason_to_openset_qwen if stage=="openset" else evaluation.openset_to_sentiment_qwen
   for start in range(0,len(pending),8):
    batch=pending[start:start+8];settings=[]
    for x in batch:q=copy.deepcopy(params);q.seed=x["seed"];settings.append(q)
    outputs=fn(llm=llm,tokenizer=t,sampling_params=settings,batch_reasons=[x["text"] for x in batch])
    require(len(outputs)==len(batch),"Judge cardinality drift")
    for x,y in zip(batch,outputs):require(isinstance(y,str),"Judge output not string");dump(run/"judge_cache"/stage/(x["key"]+".json"),dict(**x,output=y,judge_protocol_id=p["judge_protocol_id"]))
    update(state="scoring",completed=start+len(batch),pending_total=len(pending))
  update(state="complete",completed=len(rows))
 except BaseException as e:update(state="failed",error=repr(e),traceback=traceback.format_exc());raise
def assemble(run):
 import numpy as np
 run=Path(run);p=plan(run);refs=read(run/"references.json")
 os.chdir(ROOT/"AffectGPT");sys.path.insert(0,str(ROOT/"AffectGPT"));import evaluation
 scores=[]
 for d in p["datasets"]:
  for c in CONDS:
   v="path188_"+d+"_"+c;raw=run/"predictions"/v/"name2reason.npz";answers=npdict(raw);names=list(refs[d]);require(set(answers)==set(names),"Membership drift")
   opens={n:read(run/"judge_cache"/"openset"/(judge_key(p,"openset",answers[n])+".json"))["output"] for n in names}
   npwrite(raw.with_name("name2reason-openset.npz"),filenames=names,fileitems=[opens[n] for n in names])
   if d in POL:
    sent={n:read(run/"judge_cache"/"sentiment"/(judge_key(p,"sentiment",opens[n])+".json"))["output"] for n in names}
    npwrite(raw.with_name("name2reason-openset-sentiment.npz"),filenames=names,fileitems=[sent[n] for n in names])
    value,acc=evaluation.calculate_dimension_zeroshot(str(raw),refs[d],None,None,None,False);ms=dict(WAF=float(value),ACC=float(acc));main="WAF"
   elif d in CAT:
    value,m=evaluation.calculate_discrete_zeroshot(str(raw),refs[d],None,None,None,False);ms=dict(HIT=float(value),M=float(m));main="HIT"
   else:
    value,pre,rec=evaluation.calculate_ov_zeroshot(str(raw),refs[d],None,None,None,False);ms=dict(F_s=float(value),P_s=float(pre),R_s=float(rec));main="F_s"
   sizes=[len(evaluation.string_to_list(opens[n])) for n in names];ms.update(mean_extracted_labels=float(np.mean(sizes)),empty_extracted_labels=int(sum(x==0 for x in sizes)))
   require(all(math.isfinite(z) for z in ms.values()),"Nonfinite metric")
   x=dict(job_id=v,variant=v,condition=c,dataset=d,samples=len(names),main_metric=main,main_score=float(value),metrics=ms,checkpoint=p["checkpoint_by_variant"][v],raw_path=str(raw),raw_sha256=sha(raw),plan_id=p["plan_id"],judge_protocol_id=p["judge_protocol_id"])
   scores.append(x);dump(run/"scores"/(v+".json"),x)
 dump(run/"metrics_all.json",scores)
 cols=["dataset","condition","main_metric","main_score","HIT","M","WAF","ACC","F_s","P_s","R_s","mean_extracted_labels","empty_extracted_labels"];o=io.StringIO();w=csv.DictWriter(o,fieldnames=cols,extrasaction="ignore");w.writeheader()
 for x in scores:w.writerow(dict(x,**x["metrics"]))
 (run/"metrics_all.csv").write_text(o.getvalue())
 return scores
def analyze(run,scores):
 import numpy as np
 run=Path(run);p=plan(run);out=run/"analysis"
 with warnings.catch_warnings():
  warnings.simplefilter("ignore",RuntimeWarning);h=runpy.run_path(str(ROOT/"analysis_reports/sample_audit_75_43_20261028/common.py"))
 scope=dict(np=np)
 text=(SOURCE/"analysis/analyze.py").read_text()
 tree=ast.parse(text)
 for n in tree.body:
  if isinstance(n,ast.FunctionDef) and n.name in ["cluster","sufficient","value"]:exec(compile(ast.Module(body=[n],type_ignores=[]),"<frozen parent statistics>","exec"),scope)
 L={(x["dataset"],x["condition"]):x for x in scores};pairs=[("H","C"),("H","P"),("E","C"),("P","E"),("H","E")]
 summary=dict(means={c:100*float(np.mean([L[d,c]["main_score"] for d in p["datasets"]])) for c in CONDS},contrasts=[],interactions=[],scope=p["protocol"]["scope"],bootstrap_repetitions=2000);classstats=[];cases=[];samechecks=0;records=[]
 for d in p["datasets"]:
  ar={c:h["arrays"](L[d,c]["raw_path"],d) for c in CONDS};a=ar["C"];names=a["names"];used=[n for i,n in enumerate(names) if "valid" not in a or a["valid"][i]]
  groups=sorted({scope["cluster"](d,n) for n in used});gi={v:i for i,v in enumerate(groups)};gidx=np.array([gi[scope["cluster"](d,n)] for n in used]);G=len(groups)
  import hashlib
  rng=np.random.default_rng(20261028+int(hashlib.sha256(d.encode()).hexdigest()[:6],16));weights=rng.multinomial(G,np.full(G,1/G),size=2000);boot={}
  raws={c:npdict(L[d,c]["raw_path"]) for c in CONDS}
  preds={c:{x["name"]:x for x in map(json.loads,(run/"predictions"/("path188_"+d+"_"+c)/"predictions.jsonl").read_text().splitlines())} for c in CONDS}
  rows={x["name"]:x for x in read(p["datasets"][d]["path"])};quality={}
  for c in CONDS:
   st=scope["sufficient"](ar[c],d,used,gidx,G);observed=float(scope["value"](st.sum(axis=0),d));require(abs(observed-L[d,c]["main_score"])<1e-9,"Independent metric mismatch")
   boot[c]=scope["value"](weights@st,d)
   with warnings.catch_warnings():
    warnings.simplefilter("ignore",RuntimeWarning)
    quality[c]=np.where(ar[c]["all_y"]==0,np.nan,(ar[c]["all_y"]>0)==(ar[c]["all_z"]>0)).astype(float) if d in POL else np.nanmean(ar[c]["hit"],axis=1) if d in CAT else np.nanmean(ar[c]["prec"]+ar[c]["rec"],axis=1)/2
  for i,n in enumerate(names):
   x=dict(dataset=d,name=n,reference=h["refs"][d][n],subtitle=rows[n]["subtitle"],responses={c:raws[c][n] for c in CONDS},opens={c:ar[c]["opens"][n] for c in CONDS},quality={c:float(quality[c][i]) if np.isfinite(quality[c][i]) else None for c in CONDS},prompt_ids={c:preds[c][n]["prompt_info"]["prompt_id"] for c in CONDS},reused=preds["H"][n]["reused"])
   if d in POL:x["sentiment"]={c:int(ar[c]["all_z"][i]) for c in CONDS}
   records.append(x)
  for c,b in pairs:
   active=[n for n in names if preds[c][n]["prompt_info"]["prompt_id"]!=preds[b][n]["prompt_info"]["prompt_id"]]
   for n in names:
    if preds[c][n]["prompt_info"]["prompt_id"]==preds[b][n]["prompt_info"]["prompt_id"]:
     require(raws[c][n]==raws[b][n] and ar[c]["opens"][n]==ar[b]["opens"][n],"Zero-treatment mismatch");samechecks+=1
   diff=quality[c]-quality[b];up=np.where(diff>1e-12)[0];down=np.where(diff< -1e-12)[0];valid=np.isfinite(diff)
   delta=100*(L[d,c]["main_score"]-L[d,b]["main_score"]);ci=np.percentile(100*(boot[c]-boot[b]),[2.5,97.5]).tolist()
   summary["contrasts"].append(dict(dataset=d,condition=c,reference=b,delta_pp=delta,bootstrap95_pp=ci,resampling="source-video/dialogue cluster" if d not in ["MER2023","MER2024","OVMERDPlus"] else "sample iid; source groups unavailable",clusters=G,evaluated_samples=len(used),prompt_changed_samples=len(active),improved=len(up),worsened=len(down),unchanged=int(valid.sum())-len(up)-len(down)))
   if c=="H" and b in ["C","P"]:
    for direction,ids in [("improved",up),("worsened",down)]:
     for i in sorted(ids,key=lambda i:names[i])[:2]:
      n=names[i];r=rows[n];cases.append(dict(dataset=d,name=n,contrast=c+"-"+b,direction=direction,reference=h["refs"][d][n],subtitle=r["subtitle"],responses={z:raws[z][n] for z in CONDS},evidence=bundle(run,r)["texts"]))
  inter=100*((boot["P"]-boot["E"])-(boot["H"]-boot["C"]))
  summary["interactions"].append(dict(dataset=d,definition="(P-E)-(H-C)",delta_pp=100*((L[d,"P"]["main_score"]-L[d,"E"]["main_score"])-(L[d,"H"]["main_score"]-L[d,"C"]["main_score"])),bootstrap95_pp=np.percentile(inter,[2.5,97.5]).tolist()))
  if d in CAT:
   for label in sorted(set(h["refs"][d].values())):
    ids=[i for i,n in enumerate(names) if h["refs"][d][n]==label]
    with warnings.catch_warnings():
     warnings.simplefilter("ignore",RuntimeWarning)
     vals={c:{k:float(np.nanmean(ar[c][k][ids]))*100 for k in ["hit","m"]} for c in CONDS}
    classstats.append(dict(dataset=d,label=label,n=len(ids),metrics=vals))
  if d in POL:
   summary.setdefault("polarity_detail",{})[d]={c:dict(positive_recall=float(np.mean(ar[c]["z"][ar[c]["y"]])),negative_recall=float(np.mean(~ar[c]["z"][~ar[c]["y"]])),predicted_sentiment=ar[c]["sent"],neutral_as_error_accuracy=float(np.mean(ar[c]["all_z"][ar[c]["valid"]]==np.sign(ar[c]["all_y"][ar[c]["valid"]])))) for c in CONDS}
  print("ANALYZED",d,flush=True)
 def safe(v):
  if isinstance(v,float) and not math.isfinite(v):return None
  if isinstance(v,dict):return {k:safe(z) for k,z in v.items()}
  if isinstance(v,list):return [safe(z) for z in v]
  return v
 summary["zero_treatment_checks"]=samechecks
 dump(out/"summary.json",safe(summary));dump(out/"class_effects.json",safe(classstats));dump(out/"case_comparisons.json",safe(cases))
 with (out/"all_samples.jsonl").open("w") as f:
  for x in records:f.write(json.dumps(x,ensure_ascii=False,allow_nan=False)+"\n")
 parent={(x["dataset"],x["condition"]):x for x in read(SOURCE/"metrics_all.json")}
 drift=[dict(dataset=d,condition=c,old_pct=100*parent[d,c]["main_score"],current_pct=100*L[d,c]["main_score"],delta_pp=100*(L[d,c]["main_score"]-parent[d,c]["main_score"])) for d in p["datasets"] for c in ["C","E","P"]]
 dump(out/"historical_baseline_differences.json",drift)
 lines=["# 原188类图：保留路径、删除显式Emotion列表","","H只删除Emotion hypotheses行，原路径逐字保留；路径末端仍含情绪词。C/E/P/H在4777条实际干预样本上同GPU/同worker重生成，其余8022条复用严格相同回答。","这是已查看测试集的机制诊断；九集固定的是各集原赢家（7个checkpoint），不能解释为统一模型或独立开发验证。","","|数据集|C 无列表无路径|E 有列表无路径|P 原完整|H 无列表有路径|","|---|---:|---:|---:|---:|"]
 for d in p["datasets"]:lines.append("|"+d+"|"+"|".join(f'{100*L[d,c]["main_score"]:.3f}' for c in CONDS)+"|")
 lines+=["|九集混合指标均值|"+"|".join(f'{summary["means"][c]:.4f}' for c in CONDS)+"|","","|数据集|比较|差值pp|95%配对区间|改善/变差|提示改变条数|","|---|---|---:|---|---|---:|"]
 for x in summary["contrasts"]:lines.append("|"+x["dataset"]+"|"+x["condition"]+"-"+x["reference"]+"|"+f'{x["delta_pp"]:+.3f}'+"|"+", ".join(f"{z:+.3f}" for z in x["bootstrap95_pp"])+"|"+str(x["improved"])+"/"+str(x["worsened"])+"|"+str(x["prompt_changed_samples"])+"|")
 lines+=["","主对照H-C检验无显式列表时的路径块，H-P检验路径固定时删除列表；二者均不能宣称完全移除Emotion信息。交互(P-E)-(H-C)见summary.json。","2000次配对bootstrap，已知名称来源按视频/对话聚类，MER/OV按样本；区间仅覆盖本次固定生成/裁判的样本不确定性，未校正多重比较，不含多生成种子方差。","HIT改善/变差按样本平均轮命中；OV按样本平均(P+R)/2诊断，不能相加当作官方F增量。neutral补充指标不替代官方WAF。","历史C/E/P差异见analysis/historical_baseline_differences.json；原图和父运行文件保持只读。HIT/M、WAF/ACC、OV P/R及输出规模见metrics_all.csv。","开发媒体/来源隔离仍未解决；本轮不据测试选分支、不改图、不训练。"]
 (run/"RESULTS.md").write_text("\n".join(lines)+"\n");(out/"ANALYSIS.md").write_text("\n".join(lines)+"\n")
 case_lines=["# H-C / H-P 净纠错与伤害案例","","按dataset/方向/样本名固定取最多2条，不作为错误总体频率。"]
 for x in cases:case_lines+=["",f'## {x["dataset"]} {x["name"]} {x["contrast"]} {x["direction"]}',"参考："+str(x["reference"]),"字幕："+x["subtitle"]]+[c+"："+x["responses"][c] for c in CONDS]+["H证据：",x["evidence"]["H"]]
 (out/"CASE_COMPARISONS.md").write_text("\n".join(case_lines)+"\n")
 for f,digest in read(run/"parent_artifact_hashes.json").items():require(sha(f)==digest,"Protected parent artifact changed: "+f)
 for f,digest in read(run/"parent_prompt_hashes.json").items():require(sha(f)==digest,"Protected parent prompt changed")
 verify_code(run)
 dump(run/"final_verification.json",dict(passed=True,jobs=len(scores),logical_predictions=sum(x["samples"] for x in scores),fresh_predictions=p["new_generations_planned"],reused_predictions=p["reused_logical_predictions"],all_36_main_metrics_independently_recomputed=True,zero_treatment_checks=samechecks,zero_treatment_violations=0,original_artifacts_hashes_unchanged=True,paths_verbatim=True,source_only_full_window_probes=True,finished_at_beijing=now()))
def node(run,index):
 run=Path(run);p=plan(run);verify_code(run);node=p["physical_nodes"][index]["name"];dest=run/("node_"+node+".json");state=dict(node=node,index=index,pid=os.getpid(),phase="starting",time_beijing=now());children=[];owner=None;gh=None
 def update(**kw):state.update(kw,updated_at_beijing=now());dump(dest,state)
 def abort(*unused):raise KeyboardInterrupt("Node controller interrupted")
 signal.signal(signal.SIGTERM,abort);signal.signal(signal.SIGINT,abort)
 def check():
  if (run/"failure.json").exists():raise RuntimeError("Experiment peer failure: "+str(read(run/"failure.json")))
 def waitfor(test,timeout,label):
  deadline=time.monotonic()+timeout
  while not test():
   check();require(time.monotonic()<deadline,label+" timeout");time.sleep(3)
 def launch(mode,args,log):
  with (run/log).open("ab",buffering=0) as f:
   z=subprocess.Popen([str(PYTHON),"-u","-B","-m",PACKAGE+".runner",mode,"--run",str(run)]+args,cwd=ROOT,env=environment(0),stdin=subprocess.DEVNULL,stdout=f,stderr=subprocess.STDOUT,start_new_session=True);children.append(z);return z
 def mem():return int(subprocess.check_output(["nvidia-smi","--query-gpu=memory.used","--format=csv,noheader,nounits"],text=True).strip())
 try:
  owner=locked(run/("node_"+node+".lock"));require(owner is not None,"Node controller already running")
  expected=p["physical_nodes"][index]["gpu_uuid"];snapshot=gpu();require(snapshot.split(",")[0].strip()==expected,"Wrong physical GPU: "+snapshot)
  gh=locked(ROOT/PACKAGE/(expected+".lock"));require(gh is not None,"GPU held by another follow-up");require(mem()<256,"GPU is not idle")
  update(gpu_snapshot=snapshot,phase="loading")
  override=read(run/"execution_override.json") if (run/"execution_override.json").exists() else {}
  if override:require(override["plan_id"]==p["plan_id"],"Execution override bound to wrong plan")
  slots=override.get("slots_by_node",{}).get(node,p["physical_nodes"][index]["slots"])
  procs={slot:launch("worker",["--slot",str(slot)],"worker_"+str(slot)+".log") for slot in slots}
  def snapshots():return [read(run/"workers"/("worker_"+str(s)+".json")) if (run/"workers"/("worker_"+str(s)+".json")).exists() else {} for s in procs]
  def alive():
   for s,z in procs.items():require(z.poll() is None or z.returncode==0,"Inference worker failed: "+str(s)+" returncode="+str(z.returncode))
  deadline=time.monotonic()+1800;go=False;passed=False
  while not passed:
   check();alive();ss=snapshots()
   if not go and all(x.get("state")=="probe_loaded" for x in ss):dump(run/("probe_go_"+node+".json"),dict(source_only=True,time_beijing=now()));go=True
   if all(x.get("capacity_passed",False) for x in ss):dump(run/("probe_accepted_"+node+".json"),dict(passed=True,reports=ss,source_only=True));passed=True
   update(phase="capacity_probe",capacity_passed=passed,worker_states=[x.get("state") for x in ss]);require(time.monotonic()<deadline,"Capacity probe timeout");time.sleep(3)
  if index==1 and len(procs)==4:
   dump(run/"fourprocess_inference_approved_A100.json",dict(passed=True,slots=sorted(procs),serialized_model_loading=True,time_beijing=now()))
  if index==0:
   waitfor(lambda:all((run/("probe_accepted_"+x["name"]+".json")).exists() for x in p["physical_nodes"]),1800,"Both-node capacity")
   dump(run/"inference_approved.json",dict(passed=True,all_nodes_capacity_passed=True,time_beijing=now()))
  deadline=time.monotonic()+p["max_inference_seconds"]
  while any(z.poll() is None for z in procs.values()):
   check();alive();ss=snapshots();update(phase="inference",completed_active_samples=sum(x.get("completed_active_samples",0) for x in ss),generated_responses=sum(x.get("generated_responses",0) for x in ss),worker_states=[x.get("state") for x in ss]);require(time.monotonic()<deadline,"Inference time budget exceeded");time.sleep(10)
  require(all(z.returncode==0 for z in procs.values()),"Worker exit failure")
  waitfor(lambda:mem()<256,180,"GPU release");dump(run/("inference_exit_"+node+".json"),dict(all_workers_exited=True,memory_used_mib=mem(),time_beijing=now()));update(phase="inference_complete")
  if index==0:
   waitfor(lambda:all((run/("inference_exit_"+x["name"]+".json")).exists() for x in p["physical_nodes"]),p["max_inference_seconds"],"All-node inference exit")
   dump(run/"evaluation_barrier.json",dict(passed=True,all_inference_exited=True,physical_nodes=2,time_beijing=now()));update(phase="materializing");dump(run/"status.json",dict(phase="materializing",time_beijing=now()));materialize(run)
  for stage in ["openset","sentiment"]:
   ready=run/("stage_"+stage+"_ready.json")
   if index==0:
    total=prepare_judge(run,stage);dump(ready,dict(total=total,time_beijing=now()));dump(run/"status.json",dict(phase="judge_"+stage,total_unique_inputs=total,time_beijing=now()))
   waitfor(ready.exists,p["max_inference_seconds"],stage+" preparation")
   z=launch("judge",["--index",str(index),"--stage",stage],"judge_"+stage+"_"+node+".log");update(phase="judge_"+stage)
   deadline=time.monotonic()+p["max_judge_stage_seconds"]
   while z.poll() is None:check();require(time.monotonic()<deadline,"Judge time budget exceeded");time.sleep(10)
   require(z.returncode==0,"Judge failed: "+stage);waitfor(lambda:mem()<256,180,"Judge GPU release")
   dump(run/("stage_"+stage+"_done_"+node+".json"),dict(complete=True,time_beijing=now()))
   waitfor(lambda:all((run/("stage_"+stage+"_done_"+x["name"]+".json")).exists() for x in p["physical_nodes"]),p["max_judge_stage_seconds"],"Both-node "+stage)
  if index==0:
   update(phase="cpu_metrics");dump(run/"status.json",dict(phase="cpu_metrics",time_beijing=now()))
   scores=assemble(run);analyze(run,scores);dump(run/"status.json",dict(phase="complete",scores_complete=len(scores),result=str(run/"RESULTS.md"),finished_at_beijing=now(),automatic_training=False))
  else:waitfor(lambda:(run/"final_verification.json").exists(),7200,"Final metrics")
  update(phase="complete",finished_at_beijing=now())
 except BaseException as e:
  dump(run/"failure.json",dict(node=node,error=repr(e),traceback=traceback.format_exc(),time_beijing=now()));update(phase="failed",error=repr(e),traceback=traceback.format_exc())
  dump(run/"status.json",dict(phase="failed",node=node,error=repr(e),time_beijing=now()))
  for z in children:
   if z.poll() is None:
    try:os.killpg(z.pid,signal.SIGTERM)
    except ProcessLookupError:pass
  raise
 finally:
  if gh:gh.close()
  if owner:owner.close()
def main():
 ap=argparse.ArgumentParser();ap.add_argument("mode",choices=["setup","node","worker","judge"]);ap.add_argument("--run");ap.add_argument("--slot",type=int);ap.add_argument("--index",type=int);ap.add_argument("--stage");a=ap.parse_args()
 if a.mode=="setup":setup()
 elif a.mode=="node":node(a.run,a.index)
 elif a.mode=="worker":worker(a.run,a.slot)
 else:judge(a.run,a.index,a.stage)
if __name__=="__main__":main()
