from pathlib import Path
import hashlib,json,os,stat,time
BASE=Path('/ai/sjq/AffectGPT-sjq')
RUN=BASE/'appraisal_annotation/runs/mercaptionplus_v2_4'
AUDIT=BASE/'data_migrations/appraisal_media_cleanup_20261022'
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(4*1024*1024),b''):h.update(b)
 return h.hexdigest()
def write(p,d):
 temp=p.with_suffix(p.suffix+'.tmp')
 temp.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
 temp.replace(p)
proof=json.loads((AUDIT/'preflight_status.json').read_text())
assert proof['phase']=='verified_ready_for_cleanup'
assert proof['verified_original_files']==62510 and proof['verified_copied_files']==62510
assert sha(AUDIT/'deletion_manifest.json')==proof['manifest_sha256']
assert json.loads((AUDIT/'viewer_precleanup_verification.json').read_text())['passed']
for name,digest in proof['protected_file_hashes'].items():assert sha(RUN/name)==digest
manifest=json.loads((AUDIT/'deletion_manifest.json').read_text())
assert len(manifest['files'])==62510
assert not (RUN/'media').is_symlink()
allowed={RUN/'media/audio':'.wav',RUN/'media/video':'.mp4'}
assert all(not p.is_symlink() for p in allowed)
for r in manifest['files']:
 p=Path(r['path'])
 assert p.parent in allowed and p.suffix==allowed[p.parent]
 assert p.resolve().parent==p.parent.resolve()
 assert Path(r['original_path']).is_file()
state={'phase':'deleting','deleted_files':0,'deleted_bytes':0,'deleted_allocated_bytes':0,'expected_files':62510,'originals_and_annotations_preserved':True}
write(AUDIT/'cleanup_status.json',state)
try:
 for i,r in enumerate(manifest['files'],1):
  p=Path(r['path']);s=p.lstat()
  assert stat.S_ISREG(s.st_mode) and not p.is_symlink()
  assert (s.st_dev,s.st_ino,s.st_size,s.st_mtime_ns)==(r['device'],r['inode'],r['bytes'],r['mtime_ns']),'Copy changed after verification'
  p.unlink()
  state['deleted_files']=i;state['deleted_bytes']+=s.st_size;state['deleted_allocated_bytes']+=s.st_blocks*512
  if i%2000==0:write(AUDIT/'cleanup_status.json',state);print(json.dumps({k:state[k] for k in ['phase','deleted_files','expected_files']}),flush=True)
 for directory in allowed:
  assert not any(directory.iterdir())
  directory.rmdir()
 assert not any((RUN/'media').iterdir())
 (RUN/'media').rmdir()
 for name,digest in proof['protected_file_hashes'].items():assert sha(RUN/name)==digest
 for directory,count in proof['protected_directory_entry_counts'].items():assert sum(1 for _ in (RUN/directory).iterdir())==count
 assert state['deleted_bytes']==proof['candidate_bytes']
 state.update(phase='complete',protected_file_hashes_unchanged=True,annotations_raw_and_input_entry_counts_unchanged=True,media_directory_removed=True,no_model_calls=True,deleted_GiB=round(state['deleted_bytes']/1024**3,2))
 write(AUDIT/'cleanup_status.json',state)
 print(json.dumps(state),flush=True)
except Exception as exc:
 state.update(phase='failed',error_type=type(exc).__name__)
 write(AUDIT/'cleanup_status.json',state)
 raise
