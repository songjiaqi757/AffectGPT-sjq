from pathlib import Path
import concurrent.futures,hashlib,json,os,stat,time,sqlite3
BASE=Path('/ai/sjq/AffectGPT-sjq')
RUN=BASE/'appraisal_annotation/runs/mercaptionplus_v2_4'
AUDIT=BASE/'data_migrations/appraisal_media_cleanup_20261022'
def sha(path):
 h=hashlib.sha256()
 with path.open('rb') as f:
  for block in iter(lambda:f.read(4*1024*1024),b''):h.update(block)
 return h.hexdigest()
def write(path,data):
 tmp=path.with_suffix(path.suffix+'.tmp')
 tmp.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
 tmp.replace(path)
def inspect(s):
 sid=s['sample_id']
 result=[]
 for kind,suffix,ext in [('audio','audio.json','.wav'),('video','video_file.json','.mp4')]:
  metadata_path=RUN/'inputs'/f'{sid}.{suffix}'
  metadata=json.loads(metadata_path.read_text())
  original=Path(s[kind+'_path'])
  assert original.is_file(), 'Original media absent'
  assert str(original).startswith(str(BASE/'dataset/mer2025-dataset')+'/'), 'Unexpected original path'
  original_hash=sha(original)
  assert original_hash==metadata['source_sha256'],'Original hash differs from annotation-time hash'
  copy=RUN/'media'/kind/(sid+ext)
  st=copy.lstat()
  assert stat.S_ISREG(st.st_mode) and not copy.is_symlink(),'Copy is not a regular file'
  assert not os.path.samefile(original,copy),'Copy aliases original'
  expected=metadata['submitted_wav_sha256'] if kind=='audio' else metadata['submitted_video_sha256']
  assert sha(copy)==expected,'Copy hash differs from annotation-time input'
  result.append(dict(path=str(copy),bytes=st.st_size,device=st.st_dev,inode=st.st_ino,mtime_ns=st.st_mtime_ns,original_path=str(original),original_sha256=original_hash,submitted_sha256=expected,metadata_path=str(metadata_path),metadata_sha256=sha(metadata_path)))
 return result
status=json.loads((RUN/'status.json').read_text())
assert status['complete'] and status['queue_counts']=={'succeeded':31255}
db=sqlite3.connect('file:'+str(RUN/'tasks.sqlite3')+'?mode=ro',uri=True)
assert dict(db.execute('select state,count(*) from tasks group by state'))=={'succeeded':31255}
db.close()
samples=json.loads((RUN/'samples.json').read_text())
assert len(samples)==31255 and len({s['sample_id'] for s in samples})==31255
expected={RUN/'media'/kind/(s['sample_id']+ext) for s in samples for kind,ext in [('audio','.wav'),('video','.mp4')]}
actual=set((RUN/'media/audio').iterdir())|set((RUN/'media/video').iterdir())
assert expected==actual,'Unexpected or missing copied files'
small=['samples.json','protocol.json','labels.csv','summary.json','status.json','current_split_verification.json','format_normalization_audit.json']
proof={'phase':'verifying','total_samples':len(samples),'verified_samples':0,'original_and_copy_hashes_checked':True,'metadata_and_labels_preserved':True,'protected_file_hashes':{f:sha(RUN/f) for f in small},'protected_directory_entry_counts':{d:sum(1 for _ in (RUN/d).iterdir()) for d in ['annotations','teacher_raw','inputs']}}
write(AUDIT/'preflight_status.json',proof)
records=[]
with concurrent.futures.ThreadPoolExecutor(max_workers=16) as pool:
 futures=[pool.submit(inspect,s) for s in samples]
 for n,f in enumerate(concurrent.futures.as_completed(futures),1):
  records.extend(f.result())
  if n%2000==0 or n==len(samples):
   proof['verified_samples']=n
   write(AUDIT/'preflight_status.json',proof)
   print(json.dumps({'verified_samples':n,'total_samples':len(samples)}),flush=True)
records.sort(key=lambda x:x['path'])
write(AUDIT/'deletion_manifest.json',{'run':str(RUN),'files':records})
proof.update(phase='verified_ready_for_cleanup',verified_samples=len(samples),verified_original_files=len(records),verified_copied_files=len(records),candidate_bytes=sum(r['bytes'] for r in records),manifest_sha256=sha(AUDIT/'deletion_manifest.json'))
write(AUDIT/'preflight_status.json',proof)
print(json.dumps({k:v for k,v in proof.items() if k not in ['protected_file_hashes','protected_directory_entry_counts']}),flush=True)
