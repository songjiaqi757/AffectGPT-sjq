
from pathlib import Path
import json,os,collections,warnings
os.environ['CUDA_VISIBLE_DEVICES']='';warnings.filterwarnings('ignore',category=RuntimeWarning)
OUT=Path(__file__).resolve().parent
exec(compile((OUT/'common.py').read_text(),'common.py','exec'))
d='OVMERDPlus';w=max([s for s in scores if s['dataset']==d],key=lambda s:s['main_score']);a=arrays(w['raw_path'],d);raw=npdict(w['raw_path'])
lost=collections.Counter();examples=[];zero=[];gtlost=collections.Counter()
for i,n in enumerate(a['names']):
 z=a['opens'][n]
 for word in split(z):
  if not any(mapped(word,j) for j in range(5)):lost[word]+=1
 for word in split(refs[d][n]):
  if not any(mapped(word,j) for j in range(5)):gtlost[word]+=1
 if np.any(np.isfinite(a['prec'][i])) and not any(mapped(z,j) for j in range(5)):
  examples.append(dict(name=n,gt=refs[d][n],raw=raw[n],opens=z))
 if np.any(np.isfinite(a['prec'][i])) and np.all(np.nan_to_num(a['hit'][i])==0):
  zero.append(n)
out=dict(winner=w['job_id'],zero_overlap=len(zero),no_prediction_wheel_mapping=len(examples),no_mapping_examples=examples,pred_unmapped_words=lost.most_common(),reference_unmapped_words=gtlost.most_common(),word_probes={word:[sorted(mapped(word,j)) for j in range(5)] for word in ['gratitude','grateful','thankful','appreciation','appreciative','positivity','positive','happy','calm','rational','fearlessness','fear','serious']},notes='Unmapped words are not automatically erroneous dictionary entries; some are intentionally outside emotional wheel coverage. Literal comparisons diagnose coverage; no scores changed.')
(OUT/'expanded_mapping_audit.json').write_text(json.dumps(out,ensure_ascii=False,indent=2))
print(json.dumps(out,ensure_ascii=False,indent=2))
