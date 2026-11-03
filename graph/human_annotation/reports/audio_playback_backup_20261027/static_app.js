'use strict';
const $=id=>document.getElementById(id), clone=o=>JSON.parse(JSON.stringify(o));
const STATUS={pending:'未开始',draft:'草稿',submitted:'已提交'};
let data,detail,active=null,tab='text',visible=[],form=null,dirty=false,editSerial=0,timer,saveChain=Promise.resolve(),moving=false,synced=false;
function el(tag,text,cls){const e=document.createElement(tag);if(text!==undefined)e.textContent=text;if(cls)e.className=cls;return e}
function report(e){$('error').hidden=false;$('error').textContent=e.message||String(e)}
async function api(url,options={}){const r=await fetch(url,{cache:'no-store',...options});const j=await r.json();if(!r.ok)throw new Error(typeof j.detail==='string'?j.detail:'请求失败：HTTP '+r.status);return j}
function selectBox(options,value,label){const e=el('select');e.setAttribute('aria-label',label);for(const [v,t] of options){const o=el('option',t);o.value=v;e.append(o)}e.value=value??'';return e}
function stateText(s){return s==null?'null · 无效／证据不足':(data.state_names[s]||s)+' · '+s}
function mark(){dirty=true;editSerial++;$('saveStatus').textContent='正在编辑 · 等待自动保存';clearTimeout(timer);timer=setTimeout(()=>persist('draft').catch(()=>{}),1200);nodeProgress()}
function nodeProgress(){if(!form)return;const n=Object.values(form.cues).filter(x=>x.state).length+Object.values(form.appraisal).filter(x=>typeof x.valid==='boolean'&&(x.valid===false?x.unknown_reason:x.state)).length;$('nodeProgress').textContent=n+' / 48 已标注'}
function queue(){
 const scrollTop=$('samples').scrollTop,scrollLeft=$('samples').scrollLeft;
 const query=$('search').value.trim().toLowerCase(),role=$('role').value,status=$('status').value;
 visible=data.samples.filter(s=>(role==='all'||s.role===role)&&(status==='all'||s.status===status)&&(!query||[s.id,s.text.chinese,s.text.english].join(' ').toLowerCase().includes(query)));
 $('listCount').textContent=visible.length+' / 500 个样本';
 $('samples').replaceChildren(...visible.map(s=>{const b=el('button',undefined,(s.id===active?'active ':'')+s.status);b.type='button';b.setAttribute('aria-current',s.id===active?'true':'false');b.append(el('strong',s.id),el('p',s.text.chinese||s.text.english),el('small',STATUS[s.status]+' · '+data.role_names[s.role]));b.onclick=()=>selectSample(s.id);return b}));
 $('samples').scrollTop=scrollTop;$('samples').scrollLeft=scrollLeft;
 const done=data.samples.filter(s=>s.status==='submitted').length,draft=data.samples.filter(s=>s.status==='draft').length;
 $('submitted').textContent=done;$('drafted').textContent=draft;$('pending').textContent=500-done-draft;$('progress').value=done;
 const i=visible.findIndex(s=>s.id===active);$('prev').disabled=i<=0;$('next').disabled=i<0||i>=visible.length-1;
}
function updateSaved(r){Object.assign(detail.human,r);const s=data.samples.find(x=>x.id===active);Object.assign(s,r);queue();$('saveStatus').textContent=r.status==='submitted'?'已提交 · 保存成功':'草稿已保存至服务器';$('revision').textContent='版本 '+r.revision+' · '+new Date(r.updated_at).toLocaleString('zh-CN')}
function persist(status='draft'){
 clearTimeout(timer);
 const job=async()=>{
  if(!form||(!dirty&&status==='draft'))return;
  const sid=active,serial=editSerial,payload=clone(form);
  $('saveStatus').textContent='正在保存至服务器…';
  const result=await api('/api/samples/'+encodeURIComponent(sid),{method:'PUT',headers:{'Content-Type':'application/json'},body:JSON.stringify({...payload,revision:detail.human.revision,status})});
  if(sid===active){updateSaved(result);if(serial===editSerial)dirty=false;else{$('saveStatus').textContent='正在编辑 · 有新修改待保存';clearTimeout(timer);timer=setTimeout(()=>persist('draft').catch(()=>{}),1200)}}
 };
 const task=saveChain.then(job).catch(e=>{$('saveStatus').textContent='保存失败 · 请保留当前页面并重试';report(e);throw e});saveChain=task.catch(()=>{});return task;
}
async function flush(){clearTimeout(timer);await saveChain;while(dirty)await persist('draft')}
function blank(){const p={annotator:'1',notes:'',event_context:'',cues:{},appraisal:{}};for(const ids of Object.values(data.cue_ids))for(const id of ids)p.cues[id]={state:null,evidence_note:''};for(const id of Object.keys(data.dimensions))p.appraisal[id]={state:null,valid:null,evidence:'',evidence_modalities:[],unknown_reason:null};return p}
function normalizeApp(d){const v=d.valid===true;return {state:v?d.state:null,valid:v,evidence:v?d.evidence:'',evidence_modalities:v?d.evidence_modalities:[],unknown_reason:v?null:d.unknown_reason}}
function nodeBase(id,name){const row=el('article',undefined,'node');row.dataset.node=id;const title=el('div',undefined,'node-title');title.append(el('h3',name),el('code',id));row.append(title);return row}
function originalCell(row,id,t,isApp){const c=el('div',undefined,'original');const st=el('span',isApp?(t.valid?data.state_names[t.state]:'无效 · 证据不足'):data.state_names[t.state],'state '+(t.state||'unobservable'));c.append(st,el('code',t.state??'state=null · valid=false'));
 if(isApp&&t.valid)c.append(el('small','valid=true · '+t.evidence_modalities.map(m=>data.modality_names[m]).join(' / ')));
 if(isApp&&!t.valid)c.append(el('p',data.reason_names[t.unknown_reason]||t.unknown_reason,'evidence'),el('code',t.unknown_reason));
 else c.append(el('p',(isApp?t.evidence:t.evidence_note)||'未提供证据说明','evidence'));
 const copy=el('button','采用此原标注 →','copy');copy.type='button';copy.setAttribute('aria-label','采用 '+id+' 的 Qwen 原标注');copy.onclick=()=>{if(isApp)form.appraisal[id]=normalizeApp(t);else form.cues[id]={state:t.state,evidence_note:t.evidence_note||''};mark();renderNodes()};c.append(copy);row.append(c);return c}
function cueRow(id){
 const t=detail.teacher.cues[id],h=form.cues[id],row=nodeBase(id,data.cue_names[id]);originalCell(row,id,t,false);
 const c=el('div',undefined,'human-cell');const select=selectBox([['','— 请选择 —'],...['positive','negative','uncertain','unobservable'].map(s=>[s,stateText(s)])],h.state,id+' 人工标签');
 const note=el('textarea');note.value=h.evidence_note;note.rows=2;note.maxLength=6000;note.placeholder='填写可观察证据；存在／不确定／不可观测时必填';note.setAttribute('aria-label',id+' 人工证据');
 const diff=el('p',undefined,'edited');function changed(){const d=h.state&&(h.state!==t.state||h.evidence_note!==(t.evidence_note||''));row.classList.toggle('changed',!!d);diff.textContent=d?'与 Qwen 原标注不同':''}
 select.onchange=()=>{h.state=select.value||null;mark();changed()};note.oninput=()=>{h.evidence_note=note.value;mark();changed()};c.append(select,note,diff);row.append(c);changed();return row;
}
function appraisalRow(id){
 const t=detail.teacher.appraisal.dimensions.find(d=>d.dimension_id===id),h=form.appraisal[id],row=nodeBase(id,data.dimension_names[id]);originalCell(row,id,t,true);
 const c=el('div',undefined,'human-cell');const choices=[['','— 请选择 —'],['invalid','无效 · state=null / valid=false'],...data.dimensions[id].map(s=>[s,stateText(s)])];const select=selectBox(choices,h.valid===false?'invalid':h.state,id+' 人工标签');
 select.onchange=()=>{const v=select.value;if(!v)form.appraisal[id]={state:null,valid:null,evidence:'',evidence_modalities:[],unknown_reason:null};else if(v==='invalid')form.appraisal[id]={state:null,valid:false,evidence:'',evidence_modalities:[],unknown_reason:h.unknown_reason};else form.appraisal[id]={state:v,valid:true,evidence:h.valid===true?h.evidence:'',evidence_modalities:h.valid===true?h.evidence_modalities:[],unknown_reason:null};mark();renderNodes()};c.append(select);
 if(h.valid===false){const reason=selectBox([['','— 选择无效原因 —'],...Object.entries(data.reason_names).map(([v,n])=>[v,n+' · '+v])],h.unknown_reason,id+' 无效原因');reason.className='reason';reason.onchange=()=>{h.unknown_reason=reason.value||null;mark();changed()};c.append(reason)}
 if(h.valid===true){const note=el('textarea');note.rows=3;note.value=h.evidence;note.maxLength=6000;note.placeholder='填写直接支持当前状态的具体证据（必填）';note.setAttribute('aria-label',id+' 人工证据');note.oninput=()=>{h.evidence=note.value;mark();changed()};c.append(note);const mods=el('div',undefined,'modality-picks');for(const m of ['text','audio','video']){const label=el('label'),check=el('input');check.type='checkbox';check.checked=h.evidence_modalities.includes(m);check.setAttribute('aria-label',id+' '+data.modality_names[m]+'证据');check.onchange=()=>{h.evidence_modalities=['text','audio','video'].filter(x=>x===m?check.checked:h.evidence_modalities.includes(x));mark();changed()};label.append(check,document.createTextNode(data.modality_names[m]));mods.append(label)}c.append(mods)}
 const diff=el('p',undefined,'edited');function changed(){const d=h.valid!==null&&JSON.stringify(h)!==JSON.stringify(normalizeApp(t));row.classList.toggle('changed',!!d);diff.textContent=d?'与 Qwen 原标注不同':''}c.append(diff);row.append(c);changed();return row;
}
function renderNodes(){if(!detail)return;const isApp=tab==='appraisal';$('nodes').replaceChildren(...(isApp?Object.keys(data.dimensions).map(appraisalRow):data.cue_ids[tab].map(cueRow)));$('nodes').setAttribute('aria-labelledby','tab-'+tab);
 const guide={text:'文本 Cue：仅依据中英文文本。positive＝存在；negative＝充分观察后未发现；uncertain＝证据模糊；unobservable＝无法充分观察。',audio:'音频 Cue：仅依据原始音频判断。不要用文本含义或面部表情推断语音线索；相对音高、音量和语速需要可判断的基线。',visual:'视觉 Cue：仅依据完整静音视频判断。请检查可见面部与姿态；看不清或覆盖不足时使用 unobservable。',appraisal:'Appraisal：联合参考文本、音频和视频。有效状态需要直接证据和证据模态；证据不足选择无效并填写原因。每个维度独立判断，null 不等于负向状态。'};$('guidance').textContent=guide[tab];nodeProgress();}
function stopMedia(){synced=false;for(const id of ['audio','video'])$(id).pause();$('sync').textContent='▶ 同步播放'}
function renderDetail(d){detail=d;form=d.human.payload?clone(d.human.payload):blank();if(!form.annotator?.trim())form.annotator='1';dirty=false;editSerial=0;$('workspace').hidden=false;$('loading').hidden=true;$('sampleId').textContent=active;const s=data.samples.find(x=>x.id===active);$('samplePosition').textContent='SAMPLE '+String(data.samples.indexOf(s)+1).padStart(3,'0')+' / 500';$('sampleMeta').textContent=data.role_names[s.role]+' · '+s.role+' · '+d.sample.audio_duration.toFixed(2)+' 秒';$('zh').textContent=d.sample.text.chinese||'（无中文文本）';$('en').textContent=d.sample.text.english||'（无英文文本）';for(const [id,k] of [['annotator','annotator'],['eventContext','event_context'],['notes','notes']])$(id).value=form[k];$('video').src=d.media.video;$('audio').src=d.media.audio;$('raw').textContent=JSON.stringify(d.teacher,null,2);$('saveStatus').textContent=d.human.status==='submitted'?'已提交 · 可继续修改':d.human.status==='draft'?'已恢复服务器草稿':'尚未标注 · 编辑后自动保存';$('revision').textContent=d.human.revision?'版本 '+d.human.revision+' · '+new Date(d.human.updated_at).toLocaleString('zh-CN'):'所有标注保存至服务器';renderNodes();queue();}
async function selectSample(id){if(moving||id===active)return;moving=true;$('workspace').inert=true;$('error').hidden=true;try{await flush();stopMedia();const d=await api('/api/samples/'+encodeURIComponent(id));active=id;renderDetail(d);history.replaceState(null,'','#'+id)}catch(e){report(e)}finally{moving=false;$('workspace').inert=false}}
for(const id of ['search','role','status'])$(id).addEventListener(id==='search'?'input':'change',()=>{if(data)queue()});
for(const b of document.querySelectorAll('[data-tab]'))b.onclick=()=>{tab=b.dataset.tab;for(const x of document.querySelectorAll('[data-tab]')){x.classList.toggle('active',x===b);x.setAttribute('aria-selected',x===b?'true':'false')}renderNodes()};
for(const [id,key] of [['annotator','annotator'],['eventContext','event_context'],['notes','notes']])$(id).oninput=()=>{if(form){form[key]=$(id).value;mark()}};
$('prev').onclick=()=>{const i=visible.findIndex(s=>s.id===active);if(i>0)selectSample(visible[i-1].id)};
$('next').onclick=()=>{const i=visible.findIndex(s=>s.id===active);if(i>=0&&i<visible.length-1)selectSample(visible[i+1].id)};
$('save').onclick=async()=>{try{$('error').hidden=true;await persist('draft')}catch(e){$('error').scrollIntoView({block:'center',behavior:'smooth'})}};
$('submit').onclick=async()=>{
 if(moving||!form)return;moving=true;$('workspace').inert=true;$('error').hidden=true;
 try{await persist('submitted');const i=visible.findIndex(s=>s.id===active);const next=visible.slice(i+1).find(s=>s.status!=='submitted')||visible.find(s=>s.id!==active&&s.status!=='submitted');moving=false;$('workspace').inert=false;if(next)await selectSample(next.id);else{$('saveStatus').textContent='已提交 · 当前筛选内没有待标注样本'}}
 catch(e){report(e);$('error').scrollIntoView({block:'center',behavior:'smooth'})}
 finally{moving=false;$('workspace').inert=false}
};
$('export').onclick=async()=>{if(moving)return;$('export').disabled=true;try{await flush();const r=await api('/api/export',{method:'POST'});$('exportResult').hidden=false;$('exportResult').textContent='已在服务器生成 '+r.saved_samples+' 条样本（已提交 '+r.submitted+' 条）。JSONL：'+r.jsonl+'；CSV：'+r.csv;$('exportResult').scrollIntoView({block:'center',behavior:'smooth'})}catch(e){report(e)}finally{$('export').disabled=false}};
$('sync').onclick=async()=>{if(!detail)return;const a=$('audio'),v=$('video');if(synced){stopMedia();return}try{v.currentTime=a.currentTime;synced=true;await Promise.all([a.play(),v.play()]);$('sync').textContent='Ⅱ 暂停同步播放'}catch(e){stopMedia();$('mediaNote').textContent='同步播放失败，请分别使用音频和视频播放器。'}};
$('audio').ontimeupdate=()=>{if(synced&&Math.abs($('audio').currentTime-$('video').currentTime)>.3)$('video').currentTime=$('audio').currentTime};
$('audio').onseeked=()=>{if(synced)$('video').currentTime=$('audio').currentTime};
for(const id of ['audio','video']){$(id).onended=()=>{if(synced)stopMedia()};$(id).onerror=()=>{$('mediaNote').textContent=(id==='audio'?'音频':'视频')+'加载失败，请重选样本或联系维护者。'}};
window.addEventListener('beforeunload',e=>{if(dirty){e.preventDefault();e.returnValue=''}});
document.addEventListener('keydown',e=>{if((e.metaKey||e.ctrlKey)&&e.key.toLowerCase()==='s'){e.preventDefault();persist('draft').catch(()=>{})}});
(async()=>{try{data=await api('/api/bootstrap');queue();const hash=decodeURIComponent(location.hash.slice(1));const s=data.samples.find(s=>s.id===hash)||data.samples.find(s=>s.status!=='submitted')||data.samples[0];await selectSample(s.id)}catch(e){$('loading').hidden=true;report(e)}})();
