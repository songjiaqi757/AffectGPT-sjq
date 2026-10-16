"""Fit-only semantic Memory value ablation; 2 GPUs x 2 training slots."""
import argparse,fcntl,json,signal,traceback
from pathlib import Path
from .run_reader_validation import ReaderValidation,PYTHON,now
from .run_experiment import sha,write_json,exposure_signature

class SemanticValidation(ReaderValidation):
    def __init__(self,root):
        super().__init__(root);self.state['schema']='amg-semantic-validation-state-v1'
    def validate(self):
        result=super().validate()
        fit=[json.loads(x) for x in Path(self.p['splits']['fit']['path']).read_text().splitlines()]
        dev=[json.loads(x) for x in Path(self.p['splits']['dev']['path']).read_text().splitlines()]
        for key in ['name','group_id']:
            if {x[key] for x in fit}&{x[key] for x in dev}:raise ValueError('Fit/dev identity/group overlap')
        if sha(self.p['baseline_checkpoint'])!=self.p['baseline_sha256']:raise ValueError('Base mismatch')
        return result
    def infer(self,key,checkpoint,gpu,mode='retrieval',override=None):
        dest=self.root/'predictions'/key/'dev.jsonl';dest.parent.mkdir(parents=True,exist_ok=True)
        args=[PYTHON,'-B','-m','amg.infer','--config',self.p['config'],'--baseline-checkpoint',self.p['baseline_checkpoint'],
              '--amg-checkpoint',str(checkpoint),'--memory-bank',self.p['memory_bank'],'--manifest',self.p['splits']['dev']['path'],
              '--output',str(dest),'--device','cuda:0','--cuda-memory-fraction','0.35','--memory-mode',mode,
              '--task','ovlabel','--max-new-tokens','128','--seed','42']
        if override:args+=['--semantic-content-override',override]
        self.execute(key+'-infer',args,gpu)
        meta=json.loads(dest.with_name('dev.meta.json').read_text())
        if meta.get('successes')!=500 or meta.get('errors')!=0:raise RuntimeError('Incomplete inference '+key)
        if meta.get('semantic_values_sha256')!=sha(self.p['semantic_values']):raise RuntimeError('Wrong semantic cache')
        self.score(key,dest)
    def train(self,arm):
        key=arm['name'];output=self.root/'training'/key
        args=[PYTHON,'-B','-m','amg.train','--config',self.p['config'],'--baseline-checkpoint',self.p['baseline_checkpoint'],
              '--manifest',self.p['splits']['fit']['path'],'--memory-bank',self.p['memory_bank'],'--output-dir',str(output),
              '--mode','retrieval','--steps','1334','--batch-size','1','--grad-accum','3','--lr','1e-5','--weight-decay','0.05',
              '--memory-dropout','0.2','--num-tokens','4','--hidden-dim','256','--adapter-init-state',self.p['shared_init'],
              '--value-last-bias-init','zero','--attention-logit-scale','1','--seed','42','--workers','2',
              '--device','cuda:0','--cuda-memory-fraction','0.35','--save-every','1334','--log-every','10',
              '--semantic-values',self.p['semantic_values'],'--semantic-content',arm['content']]
        self.execute(key+'-train',args,arm['gpu'])
        c=json.loads((output/'coverage.json').read_text())
        if c['completed_iterations']!=1334 or c['examples']!=4002:raise RuntimeError('Budget mismatch '+key)
        checkpoint=output/'checkpoint_001334.pth'
        for mode in ['retrieval','off','random']:self.infer(key+'-'+mode,checkpoint,arm['gpu'],mode)
    def analyze(self):
        from .evaluate import paired_comparison
        arms=self.p['training_arms'];init=[];exposures=[];retrieval_signatures=[]
        def retrieval_hash(path,training):
            import hashlib
            selected=[]
            for line in Path(path).read_text().splitlines():
                d=json.loads(line)
                if training:selected.extend((x['actual_clip_id'],x['retrieved_ids']) for x in d['examples'])
                else:selected.append((d['name'],d['retrieval']['retrieved_ids'][0]))
            return hashlib.sha256(json.dumps(selected,sort_keys=True).encode()).hexdigest()
        for arm in arms:
            out=self.root/'training'/arm['name'];d=json.loads((out/'adapter_initialization.json').read_text())
            init.append((d['initial_adapter']['state_sha256'],d['initial_lora_float32']['state_sha256']))
            exposures.append(exposure_signature(out/'exposure.jsonl'))
            retrieval_signatures.append((retrieval_hash(out/'exposure.jsonl',True),retrieval_hash(self.root/'predictions'/(arm['name']+'-retrieval')/'dev.retrieval.jsonl',False)))
        if len(set(init))!=1 or len(set(exposures))!=1 or len(set(retrieval_signatures))!=1:raise RuntimeError('Matched start/exposure/candidates failed')
        write_json(self.root/'MATCHED_VALIDATION.json',{'same_initialization':True,'same_exposure':True,'same_training_and_dev_retrieval_ids':True,
                   'initialization':init[0],'exposure':exposures[0],'retrieval_hashes':retrieval_signatures[0]})
        pairs=[]
        for arm in arms:
            key=arm['name'];pairs.extend([(key+'-retrieval',key+'-off'),(key+'-retrieval',key+'-random')])
        pairs += [(x+'-retrieval','av-only-retrieval') for x in ['subtitle','caption','shuffled-caption']]
        pairs += [('caption-retrieval','shuffled-caption-retrieval'),('caption-retrieval','subtitle-retrieval'),
                  ('caption-retrieval','caption-override-shuffled_caption'),('caption-retrieval','caption-override-av_only'),('subtitle-retrieval','subtitle-override-av_only'),('caption-retrieval','caption-override-subtitle')]
        for a,b in pairs:
            x=json.loads(Path(self.reports[a]).read_text());y=json.loads(Path(self.reports[b]).read_text())
            write_json(self.root/'reports'/(a+'-vs-'+b+'.json'),paired_comparison(x,y,resamples=1000,bootstrap_seed=42))
        from .semantic_audit import audit
        audit(self.root,self.p)
        lines=['# Semantic Memory value results','','Seed42; fixed AV candidates, 4000 fit/500 source dev. Base already supervised all source31327.',
               'All arms have identical 2816-dimensional value inputs, 4 tokens and common initialization.','','|Condition|micro-F1 %|sample macro-F1 %|','|---|---:|---:|']
        for key in sorted(self.reports):
            m=json.loads(Path(self.reports[key]).read_text())['metrics'];lines.append(f"|{key}|{100*m['micro_f1']:.4f}|{100*m['sample_macro_f1']:.4f}|")
        lines += ['','Matched initialization, exposure and exact retrieved IDs verified. Bootstrap is exploratory sample uncertainty for one seed.',
                  'Practical gate: aligned caption must exceed capacity-matched AV-only, shuffled captions and its own off/random; +0.5pp is predeclared.',
                  'No automatic target/holdout, full31327, graph or Situation experiments.']
        (self.root/'SUMMARY.md').write_text('\n'.join(lines)+'\n')
    def run(self):
        try:
            write_json(self.root/'VALIDATION.json',self.validate());self.save()
            def build(field,gpu):
                label='subtitle' if field=='subtitle' else 'caption'
                self.execute('cache-'+label,[PYTHON,'-B','-m','amg.build_semantic_values','--manifest',self.p['splits']['fit']['path'],
                    '--memory-bank',self.p['memory_bank'],'--field',field,'--output',str(self.root/'artifacts'/(label+'.pt')),
                    '--model',self.p['bge_model'],'--device','cuda:0','--batch-size','16','--max-length','256'],gpu)
            self.phase('fit_text_caching',[lambda:build('subtitle',0),lambda:build('description',1)])
            from .semantic_values import merge_caches
            merge_caches(self.root/'artifacts/subtitle.pt',self.root/'artifacts/caption.pt',self.p['semantic_values'],
                         self.p['memory_bank_sha256'],self.p['splits']['fit']['sha256'])
            paths=[self.root/'artifacts/subtitle.pt',self.root/'artifacts/caption.pt',self.root/'artifacts/subtitle.pt.json',self.root/'artifacts/caption.pt.json',Path(self.p['semantic_values'])]
            write_json(self.root/'DERIVED_READY.json',{'locked_files':{str(p):sha(p) for p in paths},'created_at':now()})
            self.phase('matched_semantic_training_and_inference',[lambda a=a:self.train(a) for a in self.p['training_arms']])
            tasks=[('caption','shuffled_caption',0),('caption','av_only',0),('subtitle','av_only',1),('caption','subtitle',1)]
            self.phase('same_checkpoint_content_interventions',[lambda a=a,b=b,gpu=gpu:self.infer(a+'-override-'+b,self.root/'training'/a/'checkpoint_001334.pth',gpu,override=b) for a,b,gpu in tasks])
            self.state['status']='cpu_analysis';self.save();self.analyze()
            self.state.update(status='complete',finished_at=now());self.save();return 0
        except BaseException as e:
            self.terminate();self.state.update(status='failed',error=f'{type(e).__name__}: {e}',finished_at=now());self.save()
            (self.root/'FAILURE.txt').write_text(traceback.format_exc());traceback.print_exc();return 1

def main():
    p=argparse.ArgumentParser();p.add_argument('--output-dir',required=True);p.add_argument('--validate-only',action='store_true');a=p.parse_args()
    job=SemanticValidation(a.output_dir)
    with (job.root/'.run.lock').open('a') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        if a.validate_only:print(json.dumps(job.validate()));return 0
        if (job.root/'state.json').exists():raise FileExistsError('Existing run state')
        def stop(sig,frame):job.terminate();raise KeyboardInterrupt('signal '+str(sig))
        for sig in [signal.SIGINT,signal.SIGTERM]:signal.signal(sig,stop)
        return job.run()
if __name__=='__main__':raise SystemExit(main())
