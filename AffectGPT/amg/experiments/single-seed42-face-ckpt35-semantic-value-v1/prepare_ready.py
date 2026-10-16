from pathlib import Path
import json,hashlib,tarfile
root=Path(__file__).resolve().parent;p=json.loads((root/'protocol.json').read_text());project=root.parents[2]
def sha(path):
 h=hashlib.sha256()
 with Path(path).open('rb') as f:
  for b in iter(lambda:f.read(8*1024*1024),b''):h.update(b)
 return h.hexdigest()
files=set((project/'amg').glob('*.py'))|set((project/'amg/tests').glob('test_*.py'))
files.update([Path(__file__),root/'prepare_shared_init.py',root/'protocol.json',root/'unit_tests.log',root/'source_before_semantic_change.tar.gz',
              Path(p['baseline_checkpoint']),Path(p['config']),Path(p['memory_bank']),Path(p['memory_bank']+'.json'),
              Path(p['shared_init']),Path(p['shared_init']+'.json'),Path(p['evaluation_resource'])])
files.update(Path(x['path']) for x in p['splits'].values());files.update(Path(x) for x in p['query_caches'])
files.update(project/x for x in ['config.py','my_affectgpt/models/affectgpt.py','my_affectgpt/models/encoder.py','my_affectgpt/datasets/datasets/base_dataset.py','my_affectgpt/datasets/datasets/mercaptionplus_dataset.py'])
files.update(x for x in Path(p['bge_model']).rglob('*') if x.is_file() and x.suffix in ['.json','.bin','.safetensors','.txt','.model'] and '.git' not in x.parts)
archive=root/'source_locked.tar.gz'
if not archive.exists():
 with tarfile.open(archive,'x:gz') as out:
  for x in sorted(files):
   if x.suffix=='.py':out.add(x,arcname=str(x.relative_to(project)))
files.add(archive)
locks={str(x.resolve()):sha(x) for x in sorted(files)}
assert locks[p['baseline_checkpoint']]==p['baseline_sha256'];assert locks[p['memory_bank']]==p['memory_bank_sha256']
(root/'READY.json').write_text(json.dumps({'schema':'amg-semantic-ready-v1','locked_files':locks,'derived_artifacts':'text caches generated then locked before training','all_artifacts_server_only':True},indent=2)+'\n')
print('READY_LOCKED',len(locks),flush=True)
