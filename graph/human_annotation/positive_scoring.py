"""Compare confirmed positive sets on submitted samples; never score four-state accuracy."""
import json
POLICY='positive_set_comparison_v1'

def sets(annotation,teacher=False):
 groups={k:set() for k in ('text','audio','visual','appraisal')}
 prefixes={'TXT_':'text','AUD_':'audio','VIS_':'visual'}
 for key,value in annotation.get('cues',{}).items():
  if value.get('state')!='positive':continue
  group=next((v for p,v in prefixes.items() if key.startswith(p)),None)
  if group:groups[group].add(key)
 appraisal=annotation.get('appraisal',{})
 dims={d['dimension_id']:d for d in appraisal.get('dimensions',[])} if teacher else appraisal
 for key,value in dims.items():
  if value.get('valid') is True and value.get('state'):
   groups['appraisal'].add(key+'='+value['state'])
 return groups

def rates(counts):
 tp,fp,fn=(counts[k] for k in ('tp','fp','fn'))
 return dict(counts,precision=tp/(tp+fp) if tp+fp else None,recall=tp/(tp+fn) if tp+fn else None,f1=2*tp/(2*tp+fp+fn) if 2*tp+fp+fn else None)

def compare_records(rows,get_teacher):
 groups={k:dict(tp=0,fp=0,fn=0,human_positive=0,teacher_positive=0) for k in ('text','audio','visual','appraisal')}
 submitted=0
 for row in rows:
  if row['status']!='submitted':continue
  submitted+=1
  human=row['payload']
  if isinstance(human,str):human=json.loads(human)
  predicted=get_teacher(row['sid'])
  h,t=sets(human),sets(predicted,teacher=True)
  for group in groups:
   g=groups[group];g['tp']+=len(h[group]&t[group]);g['fp']+=len(t[group]-h[group]);g['fn']+=len(h[group]-t[group]);g['human_positive']+=len(h[group]);g['teacher_positive']+=len(t[group])
 total={k:sum(g[k] for g in groups.values()) for k in ('tp','fp','fn','human_positive','teacher_positive')}
 return dict(scoring_policy=POLICY,submitted_samples=submitted,scope='submitted_samples_only',definition='TP=human_positive & teacher_positive; FP=teacher_positive - human_positive; FN=human_positive - teacher_positive. No true-negative or four-state accuracy. Blank fields are not stored as negative.',overall=rates(total),groups={k:rates(v) for k,v in groups.items()})
