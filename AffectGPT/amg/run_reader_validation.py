"""Server-only four-slot null-prefix and matched attention-scale validation."""
from __future__ import annotations
import argparse, concurrent.futures, fcntl, hashlib, json, os, signal, subprocess, threading, time, traceback
from pathlib import Path
from datetime import datetime, timezone
from .run_experiment import sha, write_json, exposure_signature, first_five_validation
PROJECT=Path(__file__).resolve().parents[1]
PYTHON='/ai/sjq/miniconda3/envs/vllm/bin/python'
def now():return datetime.now(timezone.utc).isoformat()

class ReaderValidation:
    def __init__(self,root):
        self.root=Path(root).resolve();self.p=json.loads((self.root/'protocol.json').read_text())
        self.lock=threading.RLock();self.stop=threading.Event();self.children={}
        self.state={'schema':'amg-reader-validation-state-v1','status':'validating','created_at':now(),
                    'max_gpu_jobs':4,'slots_per_gpu':2,'jobs':{},'reports':{}}
        self.reports={}
    def save(self):
        with self.lock:write_json(self.root/'state.json',self.state)
    def validate(self):
        locks=json.loads((self.root/'READY.json').read_text())['locked_files']
        for path,digest in locks.items():
            if sha(path)!=digest:raise RuntimeError('Locked artifact changed: '+path)
        for name,expected in [('fit',4000),('dev',500)]:
            rows=[json.loads(x) for x in Path(self.p['splits'][name]['path']).read_text().splitlines() if x.strip()]
            if len(rows)!=expected or len({r['name'] for r in rows})!=expected:raise ValueError('Bad split '+name)
        if self.p['max_gpu_jobs']!=4 or self.p['slots_per_gpu']!=2:raise ValueError('Bad concurrency')
        return {'validated':True,'locked_files':len(locks),'time':now()}
    def terminate(self):
        self.stop.set()
        with self.lock:processes=list(self.children.values())
        for proc in processes:
            if proc.poll() is None:
                try:os.killpg(proc.pid,signal.SIGTERM)
                except ProcessLookupError:pass
    def execute(self,key,args,gpu=None):
        if self.stop.is_set():raise InterruptedError('Controller stopped')
        env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',HF_HUB_OFFLINE='1',TRANSFORMERS_OFFLINE='1',
                 OMP_NUM_THREADS='2',MKL_NUM_THREADS='2',PYTHONUNBUFFERED='1',TOKENIZERS_PARALLELISM='false',
                 CUDA_VISIBLE_DEVICES='' if gpu is None else str(gpu))
        if gpu is not None:
            free=int(subprocess.check_output(['nvidia-smi',f'--id={gpu}','--query-gpu=memory.free','--format=csv,noheader,nounits'],text=True).strip())
            if free<self.p['min_free_mib']:
                with self.lock:self.state['jobs'][key]={'status':'waiting_for_memory','gpu':gpu,'free_mib':free};self.save()
                while free<self.p['min_free_mib']:
                    if self.stop.wait(15):raise InterruptedError('Stopped waiting')
                    free=int(subprocess.check_output(['nvidia-smi',f'--id={gpu}','--query-gpu=memory.free','--format=csv,noheader,nounits'],text=True).strip())
        with (self.root/'logs'/(key+'.log')).open('x') as log:
            log.write(json.dumps({'time':now(),'gpu':gpu,'args':args})+'\n');log.flush()
            with self.lock:
                proc=subprocess.Popen(args,cwd=PROJECT,env=env,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
                self.children[key]=proc;self.state['jobs'][key]={'status':'running','gpu':gpu,'pid':proc.pid,'started_at':now(),'argv':args};self.save()
            try:
                checked_first_five = False
                while proc.poll() is None:
                    if key.endswith('-train') and not checked_first_five:
                        telemetry = self.root/'training'/key.removesuffix('-train')/'train.jsonl'
                        if telemetry.exists():
                            check = first_five_validation(telemetry)
                            if check is not None:
                                write_json(telemetry.parent/'first-five-validation.json',check)
                                checked_first_five = True
                    if self.stop.wait(2):
                        try:os.killpg(proc.pid,signal.SIGTERM)
                        except ProcessLookupError:pass
                        raise InterruptedError('Cancelled')
                if proc.returncode:raise RuntimeError(f'{key} exited {proc.returncode}; see log')
                with self.lock:self.state['jobs'][key].update(status='complete',finished_at=now());self.save()
            finally:
                with self.lock:self.children.pop(key,None)
    def infer(self,key,checkpoint,gpu,mode='retrieval',prefix='none'):
        dest=self.root/'predictions'/key/'dev.jsonl';dest.parent.mkdir(parents=True,exist_ok=True)
        args=[PYTHON,'-B','-m','amg.infer','--config',self.p['config'],'--baseline-checkpoint',self.p['baseline_checkpoint'],
              '--amg-checkpoint',str(checkpoint),'--memory-bank',self.p['memory_bank'],'--manifest',self.p['splits']['dev']['path'],
              '--output',str(dest),'--device','cuda:0','--cuda-memory-fraction','0.35','--memory-mode',mode,
              '--prefix-control',prefix,'--task','ovlabel','--max-new-tokens','128','--seed','42']
        self.execute(key+'-infer',args,gpu)
        meta=json.loads(dest.with_name('dev.meta.json').read_text())
        if meta.get('successes')!=500 or meta.get('errors')!=0 or meta['prefix_control']!=prefix:raise RuntimeError('Incomplete inference '+key)
        self.score(key,dest)
    def score(self,key,prediction):
        out=self.root/'reports'/(key+'.json')
        args=[PYTHON,'-B','-m','amg.evaluate','--manifest',self.p['splits']['dev']['path'],'--split','dev',
              '--predictions',str(prediction),'--metadata',str(Path(prediction).with_name('dev.meta.json')),
              '--resource',self.p['evaluation_resource'],'--output',str(out)]
        self.execute(key+'-score',args)
        d=json.loads(out.read_text())
        if d['metrics']['N']!=500 or any(r['status']!='success' for r in d['per_clip']):raise RuntimeError('Scoring denominator/failure '+key)
        with self.lock:self.reports[key]=str(out);self.state['reports'][key]=str(out);self.save()
    def phase(self,name,jobs):
        self.state['status']=name;self.save()
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
            futures=[pool.submit(job) for job in jobs]
            try:
                for f in concurrent.futures.as_completed(futures):f.result()
            except BaseException:self.terminate();raise
    def train(self,arm):
        key=arm['name'];output=self.root/'training'/key
        args=[PYTHON,'-B','-m','amg.train','--config',self.p['config'],'--baseline-checkpoint',self.p['baseline_checkpoint'],
              '--manifest',self.p['splits']['fit']['path'],'--memory-bank',self.p['memory_bank'],'--output-dir',str(output),
              '--mode',arm['mode'],'--steps','1334','--batch-size','1','--grad-accum','3','--lr','1e-5','--weight-decay','0.05',
              '--memory-dropout','0.2','--num-tokens','4','--hidden-dim','256','--adapter-init-state',self.p['shared_init'],
              '--value-last-bias-init','zero','--attention-logit-scale',str(arm['scale']),'--seed','42','--workers','2',
              '--device','cuda:0','--cuda-memory-fraction','0.35','--save-every','1334','--log-every','10']
        self.execute(key+'-train',args,arm['gpu'])
        coverage=json.loads((output/'coverage.json').read_text())
        if coverage['completed_iterations']!=1334:raise RuntimeError('Incomplete train '+key)
        checkpoint=output/'checkpoint_001334.pth'
        for mode in ['retrieval','off','random']:self.infer(key+'-'+mode,checkpoint,arm['gpu'],mode)
    def analyze(self):
        from .evaluate import paired_comparison
        arms=self.p['training_arms'];init=[];exposures=[]
        for arm in arms:
            directory=self.root/'training'/arm['name']
            d=json.loads((directory/'adapter_initialization.json').read_text())
            init.append((d['initial_adapter']['state_sha256'],d['initial_lora_float32']['state_sha256']))
            exposures.append(exposure_signature(directory/'exposure.jsonl'))
        if len(set(init))!=1 or len(set(map(str,exposures)))!=1:raise RuntimeError('Matched initialization/exposure failed')
        pairs=[]
        for arm in arms:
            key=arm['name'];pairs.extend([(key+'-retrieval',key+'-off'),(key+'-retrieval',key+'-random')])
        pairs.extend([('scaled-retrieval-retrieval','native-retrieval-retrieval'),('scaled-random-random','native-random-random')])
        for family in ['old','zero_init']:
            for null in ['zero','bank_mean']:
                for ref in ['normal','off','random']:pairs.append((family+'-null-'+null,family+'-ref-'+ref))
        for current,reference in pairs:
            a=json.loads(Path(self.reports[current]).read_text());b=json.loads(Path(self.reports[reference]).read_text())
            comparison=paired_comparison(a,b,resamples=1000,bootstrap_seed=42)
            write_json(self.root/'reports'/(current+'-vs-'+reference+'.json'),comparison)
        from .reader_audit import audit_arms
        audit_arms(self.root,self.p)
        lines=['# Reader validation results','','All artifacts on server; seed42, fit4000/dev500. Base already saw all source31327.',
               'Sample bootstrap is exploratory; no cross-seed claim. Null prefixes are inference distribution interventions.','',
               '|Condition|micro-F1 %|sample macro-F1 %|','|---|---:|---:|']
        for key in sorted(self.reports):
            d=json.loads(Path(self.reports[key]).read_text())['metrics']
            lines.append(f"|{key}|{100*d['micro_f1']:.4f}|{100*d['sample_macro_f1']:.4f}|")
        lines+=['','Matched starts/exposures passed. Pairwise exploratory intervals and mechanism audit are in reports/.',
                'Predeclared practical gain threshold: +0.5pp, positive paired interval against native and own off/random.',
                'No automatic full31327, Situation/HGT or target evaluation is authorized by this pipeline.']
        (self.root/'SUMMARY.md').write_text('\n'.join(lines)+'\n')
    def run(self):
        try:
            write_json(self.root/'VALIDATION.json',self.validate());self.save()
            for name,ref in self.p['references'].items():self.score(name,ref)
            self.phase('phase_a_null_inference',[lambda a=a:self.infer(a['name'],a['checkpoint'],a['gpu'],prefix=a['prefix']) for a in self.p['null_arms']])
            self.phase('phase_b_matched_training_and_inference',[lambda a=a:self.train(a) for a in self.p['training_arms']])
            self.state['status']='cpu_analysis';self.save();self.analyze()
            self.state.update(status='complete',finished_at=now());self.save();return 0
        except BaseException as e:
            self.terminate();self.state.update(status='failed',error=f'{type(e).__name__}: {e}',finished_at=now());self.save()
            (self.root/'FAILURE.txt').write_text(traceback.format_exc());traceback.print_exc();return 1

def main():
    p=argparse.ArgumentParser();p.add_argument('--output-dir',required=True);p.add_argument('--validate-only',action='store_true');a=p.parse_args()
    job=ReaderValidation(a.output_dir)
    with (job.root/'.run.lock').open('a') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        if a.validate_only:print(json.dumps(job.validate()));return 0
        if (job.root/'state.json').exists():raise FileExistsError('Existing run state')
        def stop(signum,frame):job.terminate();raise KeyboardInterrupt('signal '+str(signum))
        for sig in [signal.SIGINT,signal.SIGTERM]:signal.signal(sig,stop)
        return job.run()
if __name__=='__main__':raise SystemExit(main())
