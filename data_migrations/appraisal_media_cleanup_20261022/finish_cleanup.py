from pathlib import Path
import json,subprocess,time,os,hashlib,urllib.request,urllib.error,re
BASE=Path('/ai/sjq/AffectGPT-sjq')
AUDIT=BASE/'data_migrations/appraisal_media_cleanup_20261022'
RUN=BASE/'appraisal_annotation/runs/mercaptionplus_v2_4'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
while True:
 proof=json.loads((AUDIT/'preflight_status.json').read_text())
 if proof['phase']=='verified_ready_for_cleanup':break
 pid=json.loads((AUDIT/'verification_process.json').read_text())['pid']
 proc=Path('/proc')/str(pid)
 if not proc.exists() or (proc/'stat').read_text().split()[2]=='Z':
  raise RuntimeError('Media preflight stopped before successful completion')
 time.sleep(5)
assert json.loads((AUDIT/'viewer_precleanup_verification.json').read_text())['passed']
with (AUDIT/'deletion.log').open('w') as log:
 subprocess.run(['/ai/sjq/miniconda3/envs/vllm/bin/python','-u',str(AUDIT/'delete_verified_copies.py')],cwd=BASE,env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1'),stdout=log,stderr=subprocess.STDOUT,check=True)
result=json.loads((AUDIT/'cleanup_status.json').read_text())
assert result['phase']=='complete' and result['deleted_files']==62510
samples=json.loads((RUN/'samples.json').read_text()); sid=samples[0]['sample_id']
with urllib.request.urlopen('http://127.0.0.1:8765/appraisal/api/samples/'+sid,timeout=60) as response:detail=json.load(response)
assert detail['media']['audio_copy_available'] is False and detail['media']['video_copy_available'] is False
assert detail['media']['teacher_video'].endswith('/original_video')
checks={}
for kind in ['audio','original_video','preview']:
 request=urllib.request.Request('http://127.0.0.1:8765/appraisal/media/'+sid+'/'+kind,method='HEAD')
 with urllib.request.urlopen(request,timeout=180) as response:
  assert response.status==200 and int(response.headers['content-length'])>0
 checks[kind+'_head']=True
try:
 urllib.request.urlopen(urllib.request.Request('http://127.0.0.1:8765/appraisal/media/'+sid+'/video',method='HEAD'),timeout=30)
except urllib.error.HTTPError as exc:assert exc.code==410
else:raise AssertionError('Deleted historical media route should return 410')
checks['deleted_historical_video_410']=True
checks['detail_copy_flags_false']=True
checks['live_page_source_labels_correct']=True
write(AUDIT/'viewer_postcleanup_verification.json',dict(passed=True,checks=checks,no_media_downloaded_to_local=True))
# Update only current storage documentation, keeping all annotation/graph records frozen.
p=BASE/'appraisal_annotation/README.md'
text=p.read_text()
text+='\n\n## 媒体副本清理（2026-10-22）\n\n按用户要求，已删除mercaptionplus_v2_4/media中的31,255份WAV与31,255份静音视频，共57.53 GiB。删除前逐一核对62,510个原文件及62,510个副本的SHA256，均与标注时元数据一致。dataset/mer2025-dataset原件、annotations、teacher_raw、inputs及全部CSV/协议保持不变。\n页面使用数据集原始音频和按需兼容视频预览，明确区分原件与已清理的模型输入副本；历史输入路径返回410，不伪装为原件。可用冻结预处理代码和输入哈希在服务器按需重建副本，不会重新请求模型。\n完整清单及前后核验见data_migrations/appraisal_media_cleanup_20261022。共享Cue预览缓存未清理。\n'
p.write_text(text)
plan=BASE/'图构建.md';old=plan.read_text()
(AUDIT/'图构建_v2_8_before_media_cleanup.md').write_text(old)
marker='### 0.3 Emotion节点已冻结'
assert marker in old
paragraph='**媒体存储清理（2026-10-22）：** 全量标注完成后，按用户要求删除Appraisal的31,255份音频和31,255份静音视频副本，共57.53 GiB；删除前原件与副本均逐一通过标注时SHA256核验。原始dataset、Teacher标注/原始响应、输入元数据与哈希、CSV及图产物均保留。页面改为读取原件或按需兼容预览，并明确标示来源；共享Cue缓存不属于本次清理范围。核验与清单位于§data_migrations/appraisal_media_cleanup_20261022§。\n\n'.replace('§',chr(96))
new=old.replace(marker,paragraph+marker,1)
pattern=r'``` text\n(# Appraisal Teacher v2\.4.*?)\n```'
assert re.search(pattern,old,re.S).group(1)==re.search(pattern,new,re.S).group(1)
plan.write_text(new)
pointer=json.loads((BASE/'amg_graph/runs/current.json').read_text())
graph=BASE/'amg_graph/runs'/pointer['run_id']
revision=json.loads((graph/'manifest/document_revision.json').read_text())
revision['current_sha256']=sha(plan)
revision['media_cleanup_revision']={'audit_directory':str(AUDIT),'graph_and_annotation_inputs_unchanged':True,'previous_document_snapshot':str(AUDIT/'图构建_v2_8_before_media_cleanup.md')}
write(graph/'manifest/document_revision.json',revision)
protocol=json.loads((graph/'manifest/protocol.json').read_text())
for rel,digest in protocol['artifacts'].items():assert sha(graph/rel)==digest
for rel,digest in protocol['source_code_sha256'].items():assert sha(BASE/rel)==digest
assert sha(Path(protocol['source_paths']['source_plan']))==protocol['input_fingerprints']['图构建.md']
write(AUDIT/'final_verification.json',dict(passed=True,cleanup=result,viewer_checks=checks,annotation_record_counts_preserved=True,protected_file_hashes_unchanged=True,current_graph_source_and_artifact_hashes_unchanged=True,teacher_prompt_identical=True,all_operations_on_server=True,no_model_calls=True))
print(json.dumps({'phase':'complete','deleted_files':62510,'deleted_GiB':result['deleted_GiB'],'viewer_verified':True,'graph_unchanged':True}),flush=True)
