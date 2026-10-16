from pathlib import Path
import json,hashlib
root=Path(__file__).resolve().parent;p=json.loads((root/'protocol.json').read_text());project=root.parents[2]
def sha(path):
 h=hashlib.sha256()
 with Path(path).open('rb') as f:
  for block in iter(lambda:f.read(8*1024*1024),b''):h.update(block)
 return h.hexdigest()
files=set((project/'amg').glob('*.py'))|set((project/'amg/tests').glob('test_*.py'))
files.update([Path(__file__),root/'protocol.json',root/'unit_tests.log',Path(p['baseline_checkpoint']),Path(p['config']),Path(p['memory_bank']),Path(p['memory_bank']+'.json'),Path(p['shared_init']),Path(p['shared_init']+'.json')])
files.update(Path(x['checkpoint']) for x in p['null_arms']);files.update(Path(x['path']) for x in p['splits'].values());files.add(Path(p['evaluation_resource']))
files.update(Path(x) for x in p['query_caches'])
for pred in p['references'].values():files.update([Path(pred),Path(pred).with_name('dev.meta.json')])
files.update(project/x for x in ['config.py','my_affectgpt/models/affectgpt.py','my_affectgpt/models/encoder.py','my_affectgpt/datasets/datasets/base_dataset.py','my_affectgpt/datasets/datasets/mercaptionplus_dataset.py'])
locks={str(x.resolve()):sha(x) for x in sorted(files)}
assert locks[p['baseline_checkpoint']]==p['baseline_sha256'];assert locks[p['memory_bank']]==p['bank_sha256']
(root/'READY.json').write_text(json.dumps({'schema':'amg-reader-ready-v1','all_artifacts_server_only':True,'locked_files':locks},indent=2)+'\n')
(root/'PLAN.md').write_text('''# Reader validation\n\nTwo A800 80GB GPUs, two independent jobs per GPU. All files on this server.\n\nPhase A: old/zero-init retrieval checkpoint x zero/bank-mean prefix, 4 x 500 source-dev inference. Reuse on/off/random references.\n\nPhase B: scale1/50000 x retrieval/random training, four common zero-bias starts, seed42, 1334 iterations and 4002 exposures each. Every trained model then runs on/off/random inference and scoring.\n\nState: state.json. Logs: logs/. Outputs: predictions/, training/, reports/. Final report: SUMMARY.md.\n\nBase already supervised on all source31327. No automatic full-data/HGT expansion.\n''')
print('LOCKED',len(locks),flush=True)
