"""Server-only stdlib summarization; no training, APIs or checkpoint changes."""
import csv,json,pathlib,statistics,datetime
from zoneinfo import ZoneInfo
R=pathlib.Path('/ai/sjq/AffectGPT-sjq');O=R/'analysis_reports'
def rows(p):return list(csv.DictReader((R/p).open()))
def table(h,data):return '\n'.join(['|'+'|'.join(h)+'|','|'+'|'.join(['---']*len(h))+'|']+['|'+'|'.join(map(str,r))+'|' for r in data])
def pc(x):return f'{float(x)*100:.2f}'
keys={'MER2023':'MER2023_HIT','MER2024':'MER2024_HIT','MELD':'MELD_HIT','IEMOCAPFour':'IEMOCAPFour_HIT','CMUMOSI':'CMUMOSI_WAF','CMUMOSEI':'CMUMOSEI_WAF','SIMS':'SIMS_WAF','SIMSv2':'SIMSv2_WAF','OVMERDPlus':'OVMERDPlus_F_s'}
b=rows('AffectGPT/output/evaluation_20261016_2140/metrics_all.csv')
g=rows('amg_inference/runs/graph_225_20261022_174537/evaluation_all_20261023_175630/per_checkpoint_summary.csv')
runs={'BCD':'amg_bcd/runs/bcd_20261024_161459','PolarityOOF':'amg_bcd_polarity_oof/runs/bcd_polarity_20261025_014715','GraphCompare':'amg_d_graph_compare/runs/d_compare_20261025_111800'}
assert len(b)==126 and len(g)==25
parts=['## 9. 自动生成的完整结果表','### 9.1 原始face/frame：14权重、126项'];bt=[]
for v in ['face','frame']:
 for e in sorted({int(r['epoch']) for r in b}):
  d={r['dataset']:float(r['main_score']) for r in b if r['variant']==v and int(r['epoch'])==e};assert len(d)==9
  bt.append([v,e,*[pc(d[k]) for k in keys],pc(statistics.mean(d.values()))])
parts.append(table(['变体','epoch',*keys,'九集均值'],bt))
parts+=['### 9.2 长证据图续训：25权重、225项',table(['起点','epoch',*keys,'九集均值'],[[r['base_epoch'],r['epoch'],*[pc(r[k]) for k in keys.values()],pc(r['dataset_wise_mean'])] for r in g])]
diag={'generated_at_beijing':datetime.datetime.now(ZoneInfo('Asia/Shanghai')).isoformat(),'completed_checkpoints':79,'completed_checkpoint_dataset_evaluations':471,'variant_summary':{}}
for name,path in runs.items():
 a=rows(path+'/per_checkpoint_summary.csv');assert len(a)==(10 if name=='GraphCompare' else 15)
 parts+=['### 9.3 '+name,table(['变体','起点','epoch','MER2023 HIT','SIMS WAF','OVMERDPlus F_s','三集均值'],[[r['variant'],r.get('base_epoch',''),r['epoch'],pc(r['MER2023_HIT']),pc(r['SIMS_WAF']),pc(r['OVMERDPlus_F_s']),pc(r['three_dataset_mean'])] for r in a])]
 for v in sorted({r['variant'] for r in a}):
  rr=[r for r in a if r['variant']==v];s=[float(r['three_dataset_mean'])*100 for r in rr]
  diag['variant_summary'][name+'/'+v]={'mean':statistics.mean(s),'epoch_sd':statistics.stdev(s),'best':max(s),'datasets':{k:statistics.mean(float(r[k])*100 for r in rr) for k in ['MER2023_HIT','SIMS_WAF','OVMERDPlus_F_s']}}
cue=json.loads((R/'cue_student/reports/cue_training_report_20261021.json').read_text());ct=[]
for name,r in cue['runs'].items():
 m=r['best_metrics'];ct.append([name,r['best_epoch'],pc(m['macro_ap']),pc(m['macro_f1']),pc(m['micro_f1'])])
assert len(ct)==9
parts+=['### 9.4 Cue九组完整最佳权重验证表',table(['实验','最佳轮','macro AP','macro F1@0.5','micro F1@0.5'],ct),'### 9.5 各数据集各自最佳（各行权重可以不同）']
co=[]
for d,k in keys.items():
 bm=max(float(r['main_score']) for r in b if r['variant']=='face' and r['dataset']==d);gm=max(float(r[k]) for r in g);co.append([d,pc(bm),pc(gm),f'{100*(gm-bm):+.2f}'])
parts.append(table(['数据集','原始face七权重最佳','长证据图25权重最佳','差值'],co))
text='\n\n'.join(parts)+'\n';(O/'completed_experiments_all_tables_20261025.md').write_text(text)
p=O/'completed_experiments_graph_gain_20261025.md';s=p.read_text().split('## 9. 自动生成的完整结果表')[0];p.write_text(s+'\n'+text)
(O/'completed_experiments_summary_20261025.json').write_text(json.dumps(diag,ensure_ascii=False,indent=2))
print(json.dumps({'report':str(p),'characters':len(p.read_text()),'checkpoints':79,'completed_evaluations':471,'cue_experiments':9},ensure_ascii=False))
