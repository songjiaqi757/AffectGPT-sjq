import hashlib,sys
from pathlib import Path
PROJECT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(PROJECT/'emotion_nodes'))
from original_adapter import Resources
ALIASES={'anger':['anger','angry','mad'],'disgust':['disgust','disgusted'],'fear':['fear','fearful','scared'],'joy':['happy','joy','joyful'],'sad':['sad'],'surprised':['surprised'],'peaceful':['peaceful'],'powerful':['powerful'],'bad':['bad'],'genius':['genius']}
NAMES=list(ALIASES)
ALIAS={v:k for k,vs in ALIASES.items() for v in vs}
def node_id(name):return 'EMO10_'+hashlib.sha256(name.encode()).hexdigest()[:16]
class Mapper:
 def __init__(self):
  self.r=Resources();self.ns=self.r.readers
  self.maps={f'wheel{i}':self.ns['func_get_wheel_cluster'](f'wheel{i}','level1') for i in range(1,6)}
  self.cache={}
 def sample(self,raw):
  key=tuple(x.lower().strip() for x in raw)
  if key not in self.cache:
   views={w:sorted(set(self.ns['func_map_label_to_synonym'](list(key),self.r.original_formats,self.r.original_synonyms,m,'case3'))) for w,m in self.maps.items()}
   union=sorted(set(x for xs in views.values() for x in xs));assert set(union)<=set(ALIAS),union
   canonical=sorted({ALIAS[x] for x in union})
   self.cache[key]=(views,union,canonical)
  return self.cache[key]
