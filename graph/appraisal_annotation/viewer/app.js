'use strict';
const $=s=>document.getElementById(s);
const DIM={'APP_GOAL_RELEVANCE':'目标相关性','APP_GOAL_CONGRUENCE':'目标一致性','APP_EXPECTEDNESS':'预期性','APP_AGENCY':'因果归属','APP_CERTAINTY':'确定性','APP_COPING_POTENTIAL':'应对潜力'};
const STATE={'AGR_RELEVANT':'相关','AGR_IRRELEVANT':'不相关','AGC_CONGRUENT':'促进目标','AGC_INCONGRUENT':'阻碍目标','AGC_MIXED':'混合影响','AEX_EXPECTED':'符合预期','AEX_UNEXPECTED':'违背预期','AAG_SELF':'自身','AAG_OTHER':'他人','AAG_CIRCUMSTANCE':'环境 / 偶然','AAG_SHARED':'共同原因','ACT_CERTAIN':'确定','ACT_UNCERTAIN':'不确定','ACP_HIGH':'高','ACP_LOW':'低','ACP_MIXED':'能力与限制并存'};
const REASON={'state_not_explicitly_supported':'没有明确支持该状态的证据','evidence_indirect_only':'只有间接证据，不足以标注','appraisal_holder_unclear':'证据无法关联到同一明确的评价','goal_not_identifiable':'无法识别相关目标','event_goal_relation_unclear':'事件与目标关系不清','prior_expectation_not_identifiable':'缺少先前预期的证据','causal_attribution_ambiguous':'因果归属不明','certainty_not_expressed':'未表达对结果的确定程度','coping_evidence_absent':'缺少应对能力或资源的证据','conflicting_evidence':'证据存在无法化解的冲突','insufficient_evidence':'证据不足','dimension_not_applicable':'该维度不适用'};
const MOD={text:'文本',audio:'音频',video:'视频'};
const ROLE={pseudo_train:'伪标签训练分区',pseudo_validation:'伪标签验证分区',gold_audit:'固定人工审计分区',diagnostic_reserved:'诊断保留分区'};
let data=null,active=null,detail=null,visible=[],seq=0,synced=false,pageOffset=0,searchTimer=null;
function el(tag,text,cls){const e=document.createElement(tag);if(text!==undefined)e.textContent=text;if(cls)e.className=cls;return e}
async function get(url){const r=await fetch(url,{cache:'no-store'});if(!r.ok)throw new Error('读取失败 HTTP '+r.status);return r.json()}
function error(e){$('error').hidden=false;$('error').textContent=e.message||String(e)}
function list(){
 const query=$('search').value.trim().toLowerCase(),status=$('statusFilter').value;
 visible=data.samples.filter(s=>{
 const all=[s.id,s.text.chinese,s.text.english,...s.dimensions.map(d=>[d.state,d.evidence,d.unknown_reason,DIM[d.dimension_id]].join(' '))].join(' ').toLowerCase();
 return (!query||all.includes(query))&&(status==='all'||status==='invalid'&&s.status==='ok'&&s.valid_count<6||s.status===status);
 });
 $('listCount').textContent=data.full_run?data.total_matches+' / '+data.summary.total_samples:visible.length+' / '+data.samples.length;
 $('listPrev').disabled=!data.full_run||data.offset<=0;
 $('listNext').disabled=!data.full_run||!data.has_more;
 $('pageInfo').textContent=data.full_run?(data.offset+1)+'–'+(data.offset+data.samples.length):'';
 $('samples').replaceChildren(...visible.map(s=>{
 const b=el('button',undefined,s.id===active?'active':'');b.type='button';b.setAttribute('aria-current',s.id===active?'true':'false');
 b.append(el('strong',s.id),el('p',s.text.chinese||s.text.english||'无文本'),el('small',s.status==='ok'?s.valid_count+' / 6 维有效':s.status==='technical_failure'?'技术失败':'等待标注'));
 b.onclick=()=>select(s.id);return b;
 }));
 if(!visible.length)$('samples').append(el('p','没有匹配的样本','muted'));
 nav();
}
function nav(){
 const i=visible.findIndex(s=>s.id===active);$('prev').disabled=i<=0;$('next').disabled=i<0||i>=visible.length-1;
 $('position').textContent='CURRENT SAMPLE · '+(i>=0?(i+1)+' / '+visible.length:'当前样本不在筛选结果中');
}
function dimensions(){
 const root=$('dimensions');root.replaceChildren();
 if(!detail?.record){
 root.append(el('div',detail?.failure?'技术失败：本条未生成有效标注；不将失败转成六维 unknown。':'等待模型返回联合标注结果。','empty'));return;
 }
 const mode=$('dimensionFilter').value;
 const ds=detail.record.annotation.dimensions.filter(d=>mode==='all'||mode==='valid'&&d.valid||mode==='invalid'&&!d.valid);
 for(const d of ds){
 const card=el('article',undefined,'dimension '+(d.valid?'valid':'invalid'));
 const top=el('div',undefined,'dimension-top');top.append(el('h3',DIM[d.dimension_id]),el('span',d.valid?'有效':'无效 · unknown','tag'));
 card.append(top,el('code',d.dimension_id),el('span',d.valid?STATE[d.state]||d.state:'证据不足','state'),el('div',d.state||'state = null · valid = false','state-id'));
 if(d.valid){card.append(el('p',d.evidence,'evidence'));for(const m of d.evidence_modalities)card.append(el('span',MOD[m]||m,'modality'))}
 else{const reason=el('div',REASON[d.unknown_reason]||d.unknown_reason,'reason');reason.append(el('code',d.unknown_reason));card.append(reason)}
 root.append(card);
 }
 if(!ds.length)root.append(el('div','没有符合筛选条件的维度。','empty'));
}
function render(d,keepMedia=false){
 detail=d;$('workspace').hidden=false;$('sampleId').textContent=active;
 $('sampleRole').textContent=(ROLE[d.sample.data_role]||d.sample.data_role)+' · source_group_id: '+d.sample.source_group_id;
 $('zh').textContent=d.sample.text.chinese||'（空字段）';$('en').textContent=d.sample.text.english||'（空字段）';
 const a=d.record?.annotation;
 $('event').textContent=a?.event_context||'—';
 $('sampleValid').textContent=a?a.dimensions.filter(x=>x.valid).length+' / 6 维有效':d.failure?'技术失败':'尚无有效响应';
 const m=d.input_metadata;
 $('duration').textContent=m.audio.duration_sec.toFixed(2)+' 秒 · '+m.video.submitted_video.width+' × '+m.video.submitted_video.height;
 const audioCopy=d.media.audio_copy_available!==false,videoCopy=d.media.video_copy_available!==false;
 $('audioNote').textContent=!audioCopy?'当前播放数据集原始完整录音；历史模型输入副本已清理，输入哈希与处理记录仍保留。':m.input_pending?'原始完整录音；实际模型输入将在本条任务执行时生成。':'与 cue 输入哈希一致的完整连续 WAV。';
 $('audioFormat').textContent=audioCopy?'16 kHz · 单声道':'数据集原始音频';
 $('audio').setAttribute('aria-label',audioCopy?'实际模型音频输入':'数据集原始完整音频');
 $('videoMode').options[1].textContent=videoCopy?'实际模型输入':'原始数据集视频';
 $('videoNote').textContent=videoCopy?'完整静音视频；兼容预览仅用于播放，实际模型输入保留 cue 原始预处理。':'历史模型输入视频副本已清理；兼容预览来自原数据集，原始视频在页面默认静音。输入哈希与处理记录仍保留。';
 $('videoMode').options[1].disabled=Boolean(m.input_pending);
 if(m.input_pending)$('videoMode').value='video';
 $('raw').textContent=JSON.stringify({sample_provenance:d.sample,input_metadata:m,record:d.record,raw_response:d.raw_response,technical_failure:d.failure},null,2);
 dimensions();
 if(!keepMedia){
 synced=false;$('sync').textContent='▶ 音视频同步播放';
 for(const name of ['video','audio']){$(name).pause();$(name+'Error').hidden=true}
 $('video').src=d.media[$('videoMode').value];$('audio').src=d.media.audio;
 }
 nav();
}
async function select(id){
 active=id;const token=++seq;list();$('error').hidden=true;
 for(const n of ['video','audio'])$(n).pause();synced=false;
 try{const d=await get('/appraisal/api/samples/'+encodeURIComponent(id));if(token!==seq)return;render(d);history.replaceState(null,'','#'+id)}
 catch(e){if(token===seq)error(e)}
}
async function refresh(first=false){
 try{
 if(first&&location.hash)$('search').value=decodeURIComponent(location.hash.slice(1));
 const params=new URLSearchParams({q:$('search').value.trim(),status:$('statusFilter').value,offset:String(pageOffset),limit:'100'});
 data=await get('/appraisal/api/bootstrap?'+params);const s=data.summary;
 $('promptVersion').textContent=data.protocol.prompt_version;
 $('schemaVersion').textContent=data.protocol.annotation_schema_version||'';
 $('completed').textContent=s.successful_samples+' / '+s.total_samples;$('validCount').textContent=s.valid_dimension_count;
 $('invalidCount').textContent=s.invalid_dimension_count;$('failureCount').textContent=s.counts.failed||0;
 $('progress').textContent=s.complete?s.total_samples+' 条联合标注已完成；尚未经人工金标审计。':s.test_complete?s.total_samples+' 条已结束：'+s.successful_samples+' 条成功，'+(s.counts.failed||0)+' 条技术失败。':s.phase==='stopped'?'标注已停止：'+(s.halt_reason||'请查看服务器状态'):s.successful_samples+' / '+s.total_samples+' 条完成，'+(s.counts.running||0)+' 条进行中，'+(s.counts.pending||0)+' 条等待，'+(s.counts.failed||0)+' 条失败；'+(s.limits?.request_concurrency||data.protocol.workers)+' 路并发，每 15 秒刷新。';
 $('csv').hidden=!s.dimension_rows;
 $('groupLimit').textContent='来源组限制：沿用当前 release；原视频来源及近重复隔离尚未全部核验。本页不代表人工审计完成。';
 list();
 if(!data.samples.length){$('workspace').hidden=true}
 else if(first||!data.samples.some(x=>x.id===active)){const hash=decodeURIComponent(location.hash.slice(1));await select(data.samples.some(x=>x.id===hash)?hash:data.samples[0].id)}
 else if(active){const token=seq;const d=await get('/appraisal/api/samples/'+encodeURIComponent(active));if(token===seq)render(d,true)}
 }catch(e){error(e)}
}
$('search').oninput=()=>{if(data?.full_run){pageOffset=0;clearTimeout(searchTimer);searchTimer=setTimeout(()=>refresh(),300)}else list()};
 $('statusFilter').onchange=()=>{if(data?.full_run){pageOffset=0;refresh()}else list()};
 $('listPrev').onclick=()=>{pageOffset=Math.max(0,pageOffset-(data?.page_size||100));refresh()};
 $('listNext').onclick=()=>{pageOffset+=(data?.page_size||100);refresh()};$('dimensionFilter').onchange=dimensions;
$('prev').onclick=()=>{const i=visible.findIndex(s=>s.id===active);if(i>0)select(visible[i-1].id)};
$('next').onclick=()=>{const i=visible.findIndex(s=>s.id===active);if(i>=0&&i<visible.length-1)select(visible[i+1].id)};
$('videoMode').onchange=()=>{if(detail){synced=false;$('audio').pause();$('video').pause();$('video').src=detail.media[$('videoMode').value];$('videoError').hidden=true;$('sync').textContent='▶ 音视频同步播放'}};
$('sync').onclick=async()=>{
 const a=$('audio'),v=$('video');
 if(synced){synced=false;a.pause();v.pause();$('sync').textContent='▶ 音视频同步播放';return}
 try{v.currentTime=a.currentTime;synced=true;await Promise.all([a.play(),v.play()]);$('sync').textContent='Ⅱ 暂停同步播放'}
 catch(e){synced=false;a.pause();v.pause();error(e)}
};
$('audio').ontimeupdate=()=>{if(synced&&Math.abs($('video').currentTime-$('audio').currentTime)>.3)$('video').currentTime=$('audio').currentTime};
$('audio').onseeked=()=>{if(synced)$('video').currentTime=$('audio').currentTime};
for(const n of ['audio','video']){
 $(n).onerror=()=>{$(n+'Error').hidden=false};
 $(n).onended=()=>{if(synced){synced=false;$('audio').pause();$('video').pause();$('sync').textContent='▶ 音视频同步播放'}};
}
document.addEventListener('keydown',e=>{if(/INPUT|TEXTAREA|SELECT/.test(e.target.tagName)||e.ctrlKey||e.metaKey||e.altKey)return;if(e.key==='j')$('next').click();if(e.key==='k')$('prev').click()});
refresh(true);setInterval(()=>{if(data&&!data.summary.test_complete)refresh()},15000);
