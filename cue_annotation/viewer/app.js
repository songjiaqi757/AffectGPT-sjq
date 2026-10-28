"use strict";
const $=id=>document.getElementById(id);
const state={boot:null,sample:null,filtered:[],modality:"all",epoch:0,run:"pilot30",runEpoch:0};
const node=(tag,cls,text)=>{const el=document.createElement(tag);if(cls)el.className=cls;if(text!==undefined)el.textContent=text;return el;};
const format=n=>Number(n).toLocaleString("zh-CN");
function fail(message){$("error").textContent=message;$("error").hidden=false;}
async function api(url,options){const target=new URL(url,location.origin);if(state.run)target.searchParams.set("run",state.run);const res=await fetch(target,options);if(!res.ok)throw new Error("服务器返回 "+res.status);return res.json();}
function renderSamples(){
 const q=$("sampleSearch").value.trim().toLowerCase(),review=$("reviewOnly").checked;
 state.filtered=state.boot.samples.filter(s=>(!review||s.review_count>0)&&(!q||[s.id,s.text.chinese,s.text.english].some(x=>(x||"").toLowerCase().includes(q))));
 $("sampleCount").textContent=state.filtered.length+" / "+state.boot.samples.length;$("sampleList").replaceChildren();
 for(const s of state.filtered){
  const button=node("button","sample-item"+(state.sample?.id===s.id?" active":""));button.type="button";button.setAttribute("aria-current",String(state.sample?.id===s.id));
  button.append(node("strong","",s.id),node("p","",s.text.chinese||s.text.english||"（文本缺失）"));
  const meta=node("div","sample-meta");meta.append(node("span","",s.duration.toFixed(2)+"s · 存在 "+(s.counts.positive||0)),node("span",s.review_count?"review-mark":"",s.review_count?"待复核 "+s.review_count:s.cue_count?s.cue_count+" Cue":"未标注"));
  button.append(meta);button.addEventListener("click",()=>choose(s.id));$("sampleList").append(button);
 }
 if(!state.filtered.length)$("sampleList").append(node("p","empty","没有匹配的样本"));updateNavigation();
}
function updateNavigation(){
 const i=state.filtered.findIndex(s=>s.id===state.sample?.id);
 $("position").textContent=i>=0?(i+1)+" / "+state.filtered.length:"当前样本不在筛选列表";
 $("prev").disabled=i<=0;$("next").disabled=i<0||i>=state.filtered.length-1;
}
function move(step){const i=state.filtered.findIndex(s=>s.id===state.sample?.id),s=state.filtered[i+step];if(i>=0&&s)choose(s.id);}
async function choose(id,updateHash=true){
 const epoch=++state.epoch;if(state.controller)state.controller.abort();state.controller=new AbortController();
 $("error").hidden=true;$("loading").hidden=false;$("workspace").hidden=true;$("video").pause();$("audio").pause();
 try{
  const d=await api("/api/samples/"+encodeURIComponent(id),{signal:state.controller.signal});if(epoch!==state.epoch)return;state.sample=d;
  $("visualView").value="original";
  if(updateHash)history.replaceState(null,"","#"+encodeURIComponent(id));
  $("sampleId").textContent=d.id;$("duration").textContent=d.duration.toFixed(2)+" 秒";
  $("chinese").textContent=d.text.chinese||"（中文文本缺失）";$("english").textContent=d.text.english||"（英文文本缺失）";
  $("videoError").hidden=true;$("audioError").hidden=true;
  renderVisualView();
  $("audio").src=d.media[$("audioSource").value];$("audio").load();
  $("humanReviewNotice").hidden=!d.human_review;
  $("humanReviewNotice").textContent=d.human_review?"流泪项已按你的人工复核纠正为「未观察到」。模型原始判断单独保留，人工纠正优先。其余线索仍待人工复核。":"";
  renderLabels();renderProvenance();renderSamples();$("workspace").hidden=false;$("loading").hidden=true;
  document.querySelector(".sample-item.active")?.scrollIntoView({block:"nearest",inline:"nearest"});
 }catch(e){if(e.name==="AbortError"||epoch!==state.epoch)return;$("loading").hidden=true;fail("加载失败："+e.message+"。请刷新页面重试。");}
}
function renderVisualView(){
 const d=state.sample;if(!d)return;d.active_frames=d.frames;
 const teacher=$("visualView").value==="teacher";
 $("frameHeading").textContent="浏览缩略图8张 · API上传完整视频文件";
 $("video").setAttribute("aria-label",teacher?"完整静音模型输入视频":"原视频内容的兼容播放副本");
 $("video").pause();$("video").poster=d.frames[0]?.url||"";$("video").src=teacher?d.media.teacher_video:d.media.video;$("video").load();
 $("videoError").hidden=true;$("frames").replaceChildren();
 for(const f of d.frames){
  const b=node("button","frame");b.type="button";b.title="原画面 · 帧"+f.index+" · "+f.time.toFixed(2)+"s";b.setAttribute("aria-label",b.title);
  const img=node("img");img.src=f.url;img.alt=b.title;img.loading="lazy";b.append(img,node("span","",f.time.toFixed(2)+"s"));b.addEventListener("click",()=>openFrame(f.slot));$("frames").append(b);
 }
}
$("visualView").addEventListener("change",renderVisualView);
function renderLabels(){
 if(!state.sample)return;const q=$("cueSearch").value.trim().toLowerCase(),filter=$("stateFilter").value;
 const rows=state.sample.labels.filter(r=>(state.modality==="all"||r.modality===state.modality)&&(filter==="all"||r.state===filter)&&(!q||[r.cue_id,r.name,r.evidence_note].some(x=>(x||"").toLowerCase().includes(q))));
 $("labelCount").textContent=rows.length+" / "+state.sample.labels.length;$("labelRows").replaceChildren();$("noLabels").hidden=rows.length>0;
 for(const r of rows){
  const tr=node("tr");tr.dataset.cue=r.cue_id;const cue=node("td");cue.append(node("span","cue-name",r.name),node("span","cue-id",r.cue_id));
  if(r.quality_review)cue.append(node("span","review-chip","◇ 流泪候选待人工确认 · mask=0"));
  if(r.human_review)cue.append(node("span","revision-chip","✓ 人工纠正 · 流泪负例"));
  const mod=node("td");mod.append(node("span","modality-tag",state.boot.modality_names[r.modality]||r.modality));
  const status=node("td");status.append(node("span","badge "+r.state,state.boot.states[r.state]||r.state),node("div","state-en",r.state));
  const evidence=node("td");evidence.append(node("span",r.evidence_note?"evidence":"no-evidence",r.evidence_note||"未提供证据说明"));
  if(r.human_review){const machine=node("details","previous-evidence");machine.append(node("summary","","查看本轮模型判断与人工纠正"),node("pre","",JSON.stringify(r.human_review,null,2)));evidence.append(machine);}
  if(r.quality_review){const candidate=node("details","previous-evidence");candidate.append(node("summary","","查看模型候选与保留原因"),node("pre","",JSON.stringify(r.quality_review,null,2)));evidence.append(candidate);}
  const mask=node("td");mask.append(node("div","mask","mask="+r.mask),node("div","state-en",r.y===null?"y=—":"y="+r.y));
  tr.append(cue,mod,status,evidence,mask);$("labelRows").append(tr);
 }
}
function renderProvenance(){
 const d=state.sample,p=d.provenance,dl=node("dl");
 for(const [k,v] of [["标注模型",p.model],["结果目录",p.run],["原始音频",p.audio],["原始视频",p.video],["文本输入",p.text_input],["音频输入",p.audio_input],["视觉输入",p.visual_input],["人工复核",p.human_audit]])dl.append(node("dt","",k),node("dd","",v));
 $("provenance").replaceChildren(dl);$("rawAnnotations").replaceChildren();
 if(!Object.keys(d.annotations).length)$("rawAnnotations").append(node("p","helper","原标注JSON和API原始响应已删除。"));
 for(const [mod,r] of Object.entries(d.annotations)){
  const details=node("details","raw-detail");details.append(node("summary","",state.boot.modality_names[mod]+" · "+(r.versions?.prompt_version||r.versions?.protocol_version||"")+" · 最终标注与来源 JSON"),node("pre","",JSON.stringify(r,null,2)));$("rawAnnotations").append(details);
  if(d.teacher_responses?.[mod]){const raw=node("details","raw-detail");raw.append(node("summary","",state.boot.modality_names[mod]+" · API 原始响应（含人工纠正前判断）"),node("pre","",JSON.stringify(d.teacher_responses[mod],null,2)));$("rawAnnotations").append(raw);}
 }
}
document.querySelectorAll("[data-modality]").forEach(b=>b.addEventListener("click",()=>{
 state.modality=b.dataset.modality;document.querySelectorAll("[data-modality]").forEach(x=>{x.classList.toggle("active",x===b);x.setAttribute("aria-selected",String(x===b));});renderLabels();
}));
$("sampleSearch").addEventListener("input",renderSamples);$("reviewOnly").addEventListener("change",renderSamples);
$("cueSearch").addEventListener("input",renderLabels);$("stateFilter").addEventListener("change",renderLabels);
$("prev").addEventListener("click",()=>move(-1));$("next").addEventListener("click",()=>move(1));
$("audioSource").addEventListener("change",()=>{if(!state.sample)return;$("audio").pause();$("audioError").hidden=true;$("audio").src=state.sample.media[$("audioSource").value];$("audio").load();});
$("video").addEventListener("error",()=>{$("videoError").hidden=false;});$("audio").addEventListener("error",()=>{$("audioError").hidden=false;});
$("video").addEventListener("timeupdate",()=>{if(!state.sample)return;let closest=0;state.sample.active_frames.forEach((f,i)=>{if(f.time<=$("video").currentTime)closest=i;});document.querySelectorAll(".frame").forEach((el,i)=>el.classList.toggle("current",i===closest));});
document.addEventListener("keydown",e=>{if(e.altKey||e.ctrlKey||e.metaKey||e.target.closest("input,textarea,select,video,audio,button,summary"))return;if(e.key==="j"||e.key==="ArrowRight"){e.preventDefault();move(1);}if(e.key==="k"||e.key==="ArrowLeft"){e.preventDefault();move(-1);}});
window.addEventListener("hashchange",()=>{let id;try{id=decodeURIComponent(location.hash.slice(1));}catch{return;}if(state.boot?.samples.some(s=>s.id===id)&&id!==state.sample?.id)choose(id,false);});
async function loadRun(run=state.run){
 const epoch=++state.runEpoch,previousRun=state.boot?.run_id||state.run;
 state.run=run;state.epoch++;state.controller?.abort();$("video").pause();$("audio").pause();$("workspace").hidden=true;$("loading").hidden=false;$("error").hidden=true;
 try{
 const b=await api("/api/bootstrap");if(epoch!==state.runEpoch)return;state.boot=b;state.run=b.run_id;
 $("runLabel").textContent=b.run_label;
 const target=new URL(location.href);target.searchParams.set("run",b.run_id);history.replaceState(null,"",target);
 $("runNotice").textContent=b.model+" · "+b.human_audit+"。固定协议：中英独立文本、完整连续音频、完整静音视频。";
 $("downloadLabels").hidden=!b.exports.includes("labels.csv");
 $("downloadLabels").href="/api/export/labels.csv?run="+encodeURIComponent(b.run_id);
 $("totalSamples").textContent=format(b.completed_samples);$("sourceCount").textContent="源数据 "+format(b.source_count)+" 条 · 当前试标";
 $("totalCues").textContent=format(b.cue_rows);$("positiveCount").textContent=format(b.counts.positive||0);$("maskedCount").textContent=format((b.counts.unobservable||0)+(b.counts.uncertain||0)+(b.counts.unlabeled||0));
 $("auditBadge").textContent=b.cue_rows?"模型试标 · 待人工复核":"暂无标注结果";
 $("noLabels").textContent=b.cue_rows?"没有符合当前条件的标注。":"试标标签已删除，暂无标注结果。";
 $("runId").textContent=b.run_id;document.querySelector(".status-pill").textContent="● "+b.samples.length+" 条试标 · "+b.run_label;renderSamples();
 let id;try{id=decodeURIComponent(location.hash.slice(1));}catch{id="";}if(!b.samples.length)throw new Error("没有样本");
 await choose(b.samples.some(s=>s.id===id)?id:b.samples[0].id);showPilotProgress();
 }catch(e){if(epoch!==state.runEpoch)return;state.run=previousRun;$("loading").hidden=true;fail("无法读取标注结果："+e.message);}
}
loadRun();

let frameSlot=0;
function openFrame(slot){
 if(!state.sample)return;
 frameSlot=slot;
 const f=state.sample.active_frames.find(x=>x.slot===slot);
 if(!f)return;
 $("frameTitle").textContent="原视频浏览帧 · 第 "+(slot+1)+" / "+state.sample.active_frames.length+" 帧";
 $("frameCaption").textContent=f.time.toFixed(2)+" 秒 · 原视频帧号 "+f.index;
 $("frameLoadStatus").textContent="加载原图…";$("frameLoadStatus").hidden=false;
 $("fullFrame").alt=state.sample.id+" · 第 "+(slot+1)+" 帧";
 $("fullFrame").src=f.url+"/full";
 $("prevFrame").disabled=slot===0;$("nextFrame").disabled=slot===state.sample.active_frames.length-1;
 if(!$("frameDialog").open)$("frameDialog").showModal();
}
$("fullFrame").addEventListener("load",()=>{$("frameLoadStatus").hidden=true;});
$("fullFrame").addEventListener("error",()=>{$("frameLoadStatus").textContent="原图加载失败，请检查连接后重试。";checkConnection();});
$("closeFrame").addEventListener("click",()=>$("frameDialog").close());
$("prevFrame").addEventListener("click",()=>openFrame(frameSlot-1));
$("nextFrame").addEventListener("click",()=>openFrame(frameSlot+1));
$("seekFrame").addEventListener("click",()=>{
 const f=state.sample?.active_frames.find(x=>x.slot===frameSlot);if(!f)return;
 const seek=()=>{$("video").currentTime=f.time;};
 if($("video").readyState>=1)seek();else $("video").addEventListener("loadedmetadata",seek,{once:true});
 $("frameDialog").close();$("video").focus();
});
$("frameDialog").addEventListener("click",e=>{if(e.target===$("frameDialog")){const r=$("frameDialog").getBoundingClientRect();if(e.clientX<r.left||e.clientX>r.right||e.clientY<r.top||e.clientY>r.bottom)$("frameDialog").close();}});
$("frameDialog").addEventListener("keydown",e=>{if(e.key==="ArrowLeft"&&frameSlot>0){e.preventDefault();e.stopPropagation();openFrame(frameSlot-1);}if(e.key==="ArrowRight"&&frameSlot<state.sample.active_frames.length-1){e.preventDefault();e.stopPropagation();openFrame(frameSlot+1);}});

let connectionOkay=null,checking=false;
function reloadMedia(){
 if(!state.sample)return;
 $("videoError").hidden=true;$("audioError").hidden=true;
 $("video").load();$("audio").load();
 document.querySelectorAll(".frame img").forEach(img=>{img.src=img.getAttribute("src").split("?")[0]+"?retry="+Date.now();});
 if($("frameDialog").open)openFrame(frameSlot);
}
async function checkConnection(){
 if(checking)return false;checking=true;
 const controller=new AbortController(),timer=setTimeout(()=>controller.abort(),5000);
 try{
  const res=await fetch("/api/health",{signal:controller.signal,cache:"no-store"});
  if(!res.ok)throw new Error();
  const h=await res.json();if(!h.ok)throw new Error();
  const recovered=connectionOkay===false;connectionOkay=true;$("connectionBanner").hidden=true;
  if(recovered)reloadMedia();return true;
 }catch{
  connectionOkay=false;$("connectionMessage").textContent="与服务器的连接已断开，音视频和采样帧暂不可用。请恢复 SSH 隧道；连接恢复后将重新加载媒体。";
  $("connectionBanner").hidden=false;return false;
 }finally{clearTimeout(timer);checking=false;}
}
$("retryMedia").addEventListener("click",async()=>{if(await checkConnection())reloadMedia();});
$("audio").addEventListener("error",checkConnection);$("video").addEventListener("error",checkConnection);
document.addEventListener("visibilitychange",()=>{if(!document.hidden)checkConnection();});
window.addEventListener("focus",checkConnection);
setInterval(()=>{if(!document.hidden)checkConnection();},15000);
checkConnection();

async function showPilotProgress(){
 try{
  const full=await api("/api/full-progress");
  if(full.available){
   const c=full.counts||{};$("pilotProgress").hidden=false;
   $("pilotProgress").textContent="MER-Caption+ 全量："+(c.succeeded||0)+" / "+full.total_tasks+" 个模态任务成功 · "+full.completed_samples+" / "+full.total_samples+" 条三模态齐全 · 并发上限 "+(full.limits?.request_concurrency||"—")+" · 进行中 "+(c.running||0)+" · 失败 "+(c.failed||0)+"。"+(full.phase==="stopped"?"任务已停止："+full.halt_reason:full.complete?"全量完成。":full.phase==="complete_with_failures"?"本轮结束，失败项待处理；失败不作为负例。":"后台运行；下方保留30条输入浏览，旧试标标签已删除。");return;
  }
  $("pilotProgress").hidden=true;
 }catch{}
}
setInterval(()=>{if(!document.hidden)showPilotProgress();},15000);
showPilotProgress();
