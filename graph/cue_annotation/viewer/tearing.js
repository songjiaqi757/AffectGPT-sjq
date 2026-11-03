"use strict";
const $=id=>document.getElementById(id);
let samples=[],filtered=[],selected=null,epoch=0,controller=null;
function filter(){
 const q=$("search").value.trim().toLowerCase();
 filtered=samples.filter(s=>[s.id,s.evidence,s.text.chinese,s.text.english].some(x=>(x||"").toLowerCase().includes(q)));
 $("count").textContent=filtered.length+" / "+samples.length+" 条样本";$("list").replaceChildren();
 const fragment=document.createDocumentFragment();
 for(const s of filtered){const b=document.createElement("button");b.type="button";b.className="sample"+(s.id===selected?.id?" active":"");b.setAttribute("aria-current",String(s.id===selected?.id));
 const title=document.createElement("strong");title.textContent=s.id;const text=document.createElement("span");text.textContent=s.duration.toFixed(2)+" 秒 · "+(s.final_state==='positive'?'流泪':'不确定');
 b.append(title,text);b.addEventListener("click",()=>choose(s.id));fragment.append(b);}
 $("list").append(fragment);navigation();
}
function navigation(){const i=filtered.findIndex(s=>s.id===selected?.id);$("position").textContent=i<0?"不在当前筛选结果中":`${i+1} / ${filtered.length}`;$("prev").disabled=i<=0;$("next").disabled=i<0||i>=filtered.length-1;}
function move(step){const i=filtered.findIndex(s=>s.id===selected?.id);if(i>=0&&filtered[i+step])choose(filtered[i+step].id);}
async function choose(id){
 const ticket=++epoch;controller?.abort();controller=new AbortController();$("video").pause();$("error").hidden=true;$("loading").hidden=false;$("workspace").hidden=true;
 try{const response=await fetch("/api/tearing/"+encodeURIComponent(id),{signal:controller.signal});if(!response.ok)throw new Error("读取样本失败："+response.status);const d=await response.json();if(ticket!==epoch)return;
 selected=d;history.replaceState(null,"","#"+encodeURIComponent(id));$("sid").textContent=id;$("videoMeta").textContent=`${d.resolution.join(" × ")} · ${d.fps} fps · ${d.frames} 帧`;
 $("evidence").textContent=d.teacher_label.evidence_note;$("duration").textContent=d.duration.toFixed(2)+" 秒";$("chinese").textContent=d.text.chinese||"（中文缺失）";$("english").textContent=d.text.english||"（英文缺失）";
 $("currentLabel").textContent=d.final_label.state+" · y="+(d.y===null?'—':d.y)+" · mask="+d.mask;
 $("currentLabel").style.color=d.final_label.state==='positive'?'#267653':'#7372a0';
 $("labelStatus").textContent=d.final_label.state==='positive'?'positive · 存在':'uncertain · 不确定';
 $("labelNote").textContent='采用大模型原始标注，与其他标签使用相同的 y / mask 规则。';
 $("mediaError").hidden=true;$("video").src=d.video_url;$("video").load();
 const match=d.teacher_label.evidence_note.match(/(?:at|around|约|在)\s*(\d+(?:\.\d+)?)\s*(?:s|秒)/i);
 const time=match?Number(match[1]):null;$("seek").hidden=time===null||time>=d.duration;
 $("seek").onclick=()=>{const seek=()=>{$("video").currentTime=time;$("video").focus();};if($("video").readyState)seek();else $("video").addEventListener("loadedmetadata",seek,{once:true});};
 $("loading").hidden=true;$("workspace").hidden=false;filter();document.querySelector(".sample.active")?.scrollIntoView({block:"nearest"});
 }catch(e){if(e.name==="AbortError"||ticket!==epoch)return;$("loading").hidden=true;$("error").textContent=e.message;$("error").hidden=false;}
}
$("search").addEventListener("input",filter);$("prev").addEventListener("click",()=>move(-1));$("next").addEventListener("click",()=>move(1));$("video").addEventListener("error",()=>{$("mediaError").hidden=false;});
document.addEventListener("keydown",e=>{if(e.altKey||e.ctrlKey||e.metaKey||e.target.closest("input,button,video,summary"))return;if(e.key==="ArrowLeft"){e.preventDefault();move(-1);}if(e.key==="ArrowRight"){e.preventDefault();move(1);}});
window.addEventListener("hashchange",()=>{const id=decodeURIComponent(location.hash.slice(1));if(samples.some(s=>s.id===id)&&id!==selected?.id)choose(id);});
(async()=>{try{const response=await fetch("/api/tearing");if(!response.ok)throw new Error("读取候选清单失败："+response.status);const data=await response.json();samples=data.samples;$("cohortIntro").textContent=`流泪标签为 positive 的 ${samples.length} 条样本。`;filter();const id=decodeURIComponent(location.hash.slice(1));if(!samples.length)throw new Error("没有候选样本");await choose(samples.some(s=>s.id===id)?id:samples[0].id);}catch(e){$("loading").hidden=true;$("error").textContent=e.message;$("error").hidden=false;}})();
