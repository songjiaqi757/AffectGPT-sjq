from graph_paths import resolve_path as _graph_resolve_path

from graph_paths import Path
import os,json,cv2,io,base64,sys
from PIL import Image,ImageDraw
OUT=Path(__file__).resolve().parent
xs=json.loads((OUT/'expanded_cases.json').read_text())
groups=[
['sample_00000491','test_dia12_utt6','Ses05M_script02_2_F015','Ses05F_script01_3_F015','sample_00004856','sample_00002192','test_dia216_utt1','Ses05M_impro06_M008','Ses05F_script03_2_F038','samplenew_00029298','test_dia195_utt0','Ses05F_impro04_F000'],
['video_0029_0007','video_0045_0040','video_0027_0023','video_0035_0011','video_0013_0035','video_0001_0031','cXypl4FnoZo_11','jUzDDGyPkXU_20','208592_7','BRSyH6yfDLk_3','200941_12','video_0040_0022'],
['samplenew3_00055533','samplenew3_00098820','sample_00000653','sample_00000680','sample_00002465','sample_00002078','sample_00000338','aqgy4_0012_00051','aqgy5_0020_00020','video_0045_0011','samplenew3_00019671','samplenew3_00024731']]
ix=int(sys.argv[1]);names=groups[ix];canvas=Image.new('RGB',(1200,190*len(names)),'white');metadata=[]
for i,n in enumerate(names):
 x=next(x for x in xs if x['name']==n);cap=cv2.VideoCapture(_graph_resolve_path(x['media']['video_path']));N=int(cap.get(cv2.CAP_PROP_FRAME_COUNT));fps=cap.get(cv2.CAP_PROP_FPS)
 draw=ImageDraw.Draw(canvas);draw.text((4,i*190+2),x['dataset']+' '+n+' GT='+str(x['reference']),fill='black')
 oknum=0
 for j,f in enumerate([0,N//3,2*N//3,max(0,N-2)]):
  cap.set(cv2.CAP_PROP_POS_FRAMES,f);ok,im=cap.read()
  if ok:
   oknum+=1;im=Image.fromarray(cv2.cvtColor(im,cv2.COLOR_BGR2RGB));im.thumbnail((295,163));canvas.paste(im,(j*300+(295-im.width)//2,i*190+22))
 cap.release();metadata.append(dict(dataset=x['dataset'],name=n,frames=N,fps=fps,decoded_positions=oknum))
path=OUT/('expanded_media_'+str(ix+1)+'.jpg');canvas.save(path,quality=85)
(OUT/('expanded_media_'+str(ix+1)+'.json')).write_text(json.dumps(metadata,ensure_ascii=False,indent=2))
b=io.BytesIO();canvas.save(b,format='JPEG',quality=78);print(base64.b64encode(b.getvalue()).decode())
