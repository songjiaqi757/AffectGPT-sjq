"""Reuse only vetted pure reader functions from the original AffectGPT sources."""
import ast,contextlib,csv,glob,hashlib,io,json,os,re,types,unicodedata
from graph_paths import Path
import numpy as np
import pandas as pd
PROJECT=Path(__file__).resolve().parents[1]
ORIGINAL=PROJECT/'AffectGPT'
RESOURCE=ORIGINAL/'emotion_wheel'

FUNCTIONS={
 'toolkit/utils/functions.py':['string_to_list'],
 'toolkit/utils/read_files.py':['func_read_key_from_csv'],
 'my_affectgpt/evaluation/wheel.py':['read_wheel_to_map','convert_all_wheels_to_candidate_labels',
   'func_merge_map','read_candidate_synonym_onerun','read_candidate_synonym_merge','read_format2raws',
   'func_backward_case1','func_backward_case2','func_get_wheel_cluster','func_backward_case3','func_map_label_to_synonym'],
 'toolkit/utils/qwen.py':['reason_to_openset_qwen']
}
def normalize(text):
    return ' '.join(unicodedata.normalize('NFKC',str(text)).casefold().strip().split())
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def original_readers(root=ORIGINAL,resources=RESOURCE):
    namespace=dict(os=os,glob=glob,re=re,pd=pd,np=np,
        config=types.SimpleNamespace(EMOTION_WHEEL_ROOT=str(Path(resources).resolve())))
    for relative,names in FUNCTIONS.items():
        path=Path(root)/relative;tree=ast.parse(path.read_text())
        selected=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in names]
        assert {n.name for n in selected}==set(names),(path,names)
        exec(compile(ast.Module(body=selected,type_ignores=[]),str(path),'exec'),namespace)
    # Inspect the exact original prompt using a capture stub; never call a model.
    namespace['get_completion_qwen']=lambda model,tokenizer,prompt:prompt
    return namespace

class Resources:
    def __init__(self,root=ORIGINAL,resources=RESOURCE):
        self.root=Path(root);self.resource=Path(resources)
        self.readers=original_readers(root,resources)
        with contextlib.redirect_stdout(io.StringIO()):
            formats=self.readers['read_format2raws']()
            synonyms=self.readers['read_candidate_synonym_merge']()
            words=self.readers['convert_all_wheels_to_candidate_labels']()
        self.original_formats=formats;self.original_synonyms=synonyms
        self.formats={normalize(k):frozenset(normalize(v) for v in vs) for k,vs in formats.items()}
        self.synonyms={normalize(k):frozenset(normalize(v) for v in vs) for k,vs in synonyms.items()}
        self.canonical=frozenset(normalize(w) for w in words)
        self.wheels={f'wheel{i}':self.readers['read_wheel_to_map'](str(self.resource/f'wheel{i}.xlsx')) for i in range(1,6)}
    def parse(self,value):
        return self.readers['string_to_list'](value)
    def stages(self,term):
        first=self.formats.get(normalize(term),frozenset())
        second=frozenset(c for form in first for c in self.synonyms.get(form,()))
        return first,second
    def view(self,canonical,wheel):
        # Preserve all exact paths. A level1 match never invents a level2 descendant.
        paths=set()
        for l1,seconds in self.wheels[wheel].items():
            if canonical==l1:paths.add((l1,))
            for l2,thirds in seconds.items():
                if canonical==l2:paths.add((l1,l2))
                for l3 in thirds:
                    if canonical==l3:paths.add((l1,l2,l3))
        ordered=sorted(paths)
        return dict(available=bool(paths),paths=[list(p) for p in ordered],
            level1=sorted({p[0] for p in paths}),level2=sorted({p[1] for p in paths if len(p)>1}),
            reason=None if paths else 'canonical_not_in_this_wheel')
