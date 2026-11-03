"""Frozen Qwen API annotation: bilingual text, complete audio, complete silent video.
Credentials are read from QWEN_API_KEY or stdin and never saved.
"""
from graph_paths import hash_matches as _graph_hash_matches
from graph_paths import resolve_path as _graph_resolve_path
import argparse, base64, copy, csv, hashlib, io, json, math, os, shutil, subprocess, sys, threading, time
from graph_paths import Path
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
C=Path(__file__).resolve().parent
CONFIG=C/'protocols/qwen_omni_api'
RUN=C/'runs/pilot30'
MODEL='qwen3.8-omni-flash'
ENDPOINT='https://maas.qianwenaiapi.com/compatible-mode/v1/chat/completions'
VERSION='qwen_omni_api'
STATES={'positive','negative','uncertain','unobservable'}
HALT=threading.Event()
FFMPEG=os.environ.get('FFMPEG','/ai/sjq/miniconda3/envs/talkinghead/bin/ffmpeg')

def sha(data):
    return hashlib.sha256(data).hexdigest()


def dump(path, obj):
    path = Path(path)
    tmp = path.with_name(path.name + '.tmp.' + str(threading.get_ident()))
    tmp.write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding='utf-8')
    os.replace(tmp, path)


def unique(pairs):
    out = {}
    for k, v in pairs:
        if k in out:
            raise ValueError('Duplicate JSON key: ' + k)
        out[k] = v
    return out


def validate(raw, sid, modality, ids):
    obj = json.loads(raw, object_pairs_hook=unique)
    assert set(obj) == {'sample_id', 'modality', 'labels'}, 'Root schema mismatch'
    assert obj['sample_id'] == sid and obj['modality'] == modality, 'Identity mismatch'
    assert set(obj['labels']) == set(ids), 'Cue set mismatch'
    for v in obj['labels'].values():
        assert set(v) == {'state', 'evidence_note'}, 'Cue schema mismatch'
        assert v['state'] in STATES, 'Invalid state'
        assert isinstance(v['evidence_note'], str), 'Evidence must be text'
        assert v['state'] == 'negative' or v['evidence_note'].strip(), 'Missing evidence'
    return obj


def video_info(path):
    import av
    h=hashlib.sha256()
    with av.open(str(path)) as container:
        v=container.streams.video[0]
        info={'codec':v.codec_context.name,'width':v.width,'height':v.height,'fps':float(v.average_rate),
              'duration':float(v.duration*v.time_base),'audio_streams':len(container.streams.audio)}
        packets=0
        for packet in container.demux(v):
            if packet.size:h.update(bytes(packet));packets+=1
    info.update(video_packet_sha256=h.hexdigest(),video_packets=packets,bytes=Path(path).stat().st_size)
    return info


def prepare_audio(s):
    import numpy as np
    import soundfile as sf
    a,sr=sf.read(_graph_resolve_path(s['audio_path']), dtype='float32', always_2d=True);a=a.mean(axis=1)
    if sr!=16000:
        from scipy.signal import resample_poly
        g=math.gcd(sr,16000);a=resample_poly(a,16000//g,sr//g).astype(np.float32);sr=16000
    assert len(a)>0
    output=io.BytesIO();sf.write(output,a,sr,format='WAV',subtype='PCM_16');raw=output.getvalue()
    path=RUN/'media/audio'/f"{s['sample_id']}.wav";path.parent.mkdir(parents=True,exist_ok=True)
    if path.exists():assert path.read_bytes()==raw,'Existing full audio differs'
    else:
        archived_path=RUN/'inputs'/f"{s['sample_id']}.audio.json"
        if archived_path.exists():
            archived=json.loads(archived_path.read_text())
            assert _graph_hash_matches(Path(s['audio_path']).read_bytes(), archived['source_sha256'], sha(Path(s['audio_path']).read_bytes())),'Original audio changed since annotation'
            assert _graph_hash_matches(raw, archived['submitted_wav_sha256'], sha(raw)),'Rebuilt audio differs from archived API input'
        path.write_bytes(raw)
    return path,len(a)/sr,len(a)


def prepare_video(s,force_h264=False,allow_large=False):
    sid=s['sample_id'];path=RUN/'media/video'/f'{sid}.mp4';path.parent.mkdir(parents=True,exist_ok=True)
    meta_path=RUN/'inputs'/f'{sid}.video_file.json'
    archived=json.loads(meta_path.read_text()) if meta_path.exists() else None
    if path.exists() and archived and not force_h264:
        assert _graph_hash_matches(path.read_bytes(), archived['submitted_video_sha256'], sha(path.read_bytes()));return archived
    if path.exists() and force_h264 and archived and not archived['video_stream_copy']:
        assert _graph_hash_matches(path.read_bytes(), archived['submitted_video_sha256'], sha(path.read_bytes()));return archived
    restoring=bool(archived and not path.exists() and (not force_h264 or not archived['video_stream_copy']))
    if restoring:
        assert _graph_hash_matches(Path(s['video_path']).read_bytes(), archived['source_sha256'], sha(Path(s['video_path']).read_bytes())),'Original video changed since annotation'
        force_h264=not archived['video_stream_copy']
    original=video_info(s['video_path'])
    temp=path.with_name(path.stem+'.tmp.mp4')
    codec=['-c:v','libx264','-preset','medium','-crf','18','-pix_fmt','yuv420p','-vsync','0','-threads','2'] if force_h264 else ['-c:v','copy']
    subprocess.run([FFMPEG,'-hide_banner','-loglevel','error','-nostdin','-y','-i',s['video_path'],
                    '-map','0:v:0','-an','-sn','-dn','-map_metadata','-1','-map_chapters','-1',*codec,'-movflags','+faststart',str(temp)],check=True)
    actual=video_info(temp)
    assert actual['audio_streams']==0
    assert all(actual[k]==original[k] for k in ['width','height','fps','video_packets'])
    assert abs(actual['duration']-original['duration'])<.001
    if not force_h264:assert actual['video_packet_sha256']==original['video_packet_sha256']
    if not allow_large:
        assert 4*((actual['bytes']+2)//3)<10_000_000,'Complete video exceeds frozen Base64 budget; no truncation allowed'
    if restoring:
        assert _graph_hash_matches(temp.read_bytes(), archived['submitted_video_sha256'], sha(temp.read_bytes())),'Rebuilt video differs from archived API input; keep original metadata'
        temp.replace(path)
        return archived
    temp.replace(path)
    info={'sample_id':sid,'source_path':s['video_path'],'source_sha256':sha(Path(s['video_path']).read_bytes()),
          'submitted_video_path':str(path),'submitted_video_sha256':sha(path.read_bytes()),'source_video':original,'submitted_video':actual,
          'encoded_base64_bytes':4*((actual['bytes']+2)//3),'whole_file_uploaded':True,'client_frame_sampling':False,
          'client_temporal_truncation':False,'client_spatial_resize':False,'audio_included':False,'video_stream_copy':not force_h264,
          'server_processing':'provider_default; no internal sampling verification required'}
    if force_h264:info['compatibility_fallback']='Full-file H.264 CRF18; original duration/resolution/FPS/frame count preserved'
    dump(meta_path,info);return info


def build(s,m,prompt,media_url=None):
    sid=s['sample_id'];actual=prompt.replace('{SAMPLE_ID}',sid)
    content=[{'type':'text','text':actual}]
    meta={'sample_id':sid,'modality':m,'protocol_version':VERSION,'provider_internal_coverage_verified':False}
    if m=='text':
        fields={k:s['text'].get(k,'') for k in ['chinese','english']}
        content.append({'type':'text','text':'Actual bilingual fields:\n'+json.dumps(fields,ensure_ascii=False)})
        meta.update(actual_fields=fields,audio_included=False,video_included=False)
    elif m=='audio':
        path,duration,n=prepare_audio(s);raw=path.read_bytes()
        manifest={'mode':'one_complete_continuous_recording','duration_sec':duration,'sample_rate':16000,
                  'source_samples':n,'covered_time_sec':[0,duration],'no_input_padding_or_concatenation':True}
        content.extend([{'type':'text','text':'Actual audio manifest: '+json.dumps(manifest)},
                        {'type':'input_audio','input_audio':{'data':media_url or 'data:audio/wav;base64,'+base64.b64encode(raw).decode(),'format':'wav'}}])
        meta.update(manifest,source_path=s['audio_path'],source_sha256=sha(Path(s['audio_path']).read_bytes()),submitted_audio_path=str(path),
                    submitted_wav_sha256=sha(raw),submitted_bytes=len(raw),audio_encoding='WAV_PCM16',temporal_truncation=False,text_transcript_included=False,video_included=False)
    else:
        info=prepare_video(s,allow_large=bool(media_url));raw=Path(info['submitted_video_path']).read_bytes()
        if not media_url:assert 4*((len(raw)+2)//3)<10_000_000,'Complete video exceeds frozen Base64 budget; no truncation allowed'
        if not info['video_stream_copy']:
            actual=actual.replace('The client removes the soundtrack using video stream copy, without selecting frames, clipping time or resizing.',
                'The client removes the soundtrack and re-encodes this complete file to H.264 for API codec compatibility, retaining original duration, resolution, frame rate and all client-side frames. No frames are selected and no time is clipped.')
        manifest={'mode':'one_complete_video_file','duration_sec':info['submitted_video']['duration'],'soundtrack_removed':True,
                  'client_frame_sampling':False,'client_temporal_truncation':False,'server_processing':'provider_default; no internal sampling verification required'}
        content=[{'type':'text','text':actual+'\nActual video file manifest: '+json.dumps(manifest)},
                 {'type':'video_url','video_url':{'url':media_url or 'data:video/mp4;base64,'+base64.b64encode(raw).decode()}}]
        meta.update(info,duration_sec=info['submitted_video']['duration'],source_frame_count=info['source_video']['video_packets'],
                    original_fps=info['source_video']['fps'],input_view='complete_silent_video_file',server_frame_coverage_verification_required=False)
    if media_url:
        assert media_url.startswith('oss://'), 'Only provider private temporary uploads are supported'
        meta.update(media_transport='provider_private_temporary_oss',media_url=media_url)
    protocol=json.loads((RUN/'protocol.json').read_text())
    payload={'model':MODEL,'messages':[{'role':'user','content':content}],**protocol['generation']}
    data=json.dumps(payload,ensure_ascii=False,separators=(',',':')).encode()
    meta.update(actual_prompt_sha256=sha(actual.encode()),request_bytes=len(data),request_sha256=sha(data))
    return data,meta


def setup(samples_path=None):
    config=json.loads((CONFIG/'protocol.json').read_text());ids=json.loads((CONFIG/'ontology.json').read_text())['cue_ids']
    assert {m:len(x) for m,x in ids.items()}=={'text':15,'audio':17,'visual':10}
    for name in ['annotations','inputs','teacher_raw','failed','media/audio','media/video']: (RUN/name).mkdir(parents=True,exist_ok=True)
    if not (RUN/'protocol.json').exists():dump(RUN/'protocol.json',config)
    protocol=json.loads((RUN/'protocol.json').read_text())
    for k in ['protocol_version','model_requested','endpoint','generation','prompt_sha256','quality']:
        assert protocol[k]==config[k],f'Frozen protocol differs: {k}'
    if samples_path:
        assert not list((RUN/'annotations').glob('*.json')),'Use a new run directory for a new manifest'
        samples=json.loads(Path(samples_path).read_text());dump(RUN/'samples.json',samples)
    else:samples=json.loads((RUN/'samples.json').read_text())
    assert samples and len({s['sample_id'] for s in samples})==len(samples)
    assert all(__import__('re').fullmatch(r'[A-Za-z0-9_-]+',s['sample_id']) for s in samples)
    if not (RUN/'ontology.json').exists():shutil.copy2(_graph_resolve_path(CONFIG / 'ontology.json'), _graph_resolve_path(RUN / 'ontology.json'))
    (RUN/'prompts').mkdir(exist_ok=True)
    prompts={m:(CONFIG/f'{m}.txt').read_text() for m in ids}
    for m,prompt in prompts.items():
        assert _graph_hash_matches(prompt.encode(), protocol['prompt_sha256'][m], sha(prompt.encode())),'Frozen prompt changed'
        dest=RUN/'prompts'/f'{m}.txt'
        if dest.exists():assert dest.read_text()==prompt
        else:dest.write_text(prompt)
    return samples,ids,protocol,prompts


def one(s, m, ids, protocol, prompts, key):
    import requests
    sid = s['sample_id']
    dest = RUN / 'annotations' / f'{sid}.{m}.json'
    if dest.exists():
        record = json.loads(dest.read_text())
        validate(json.dumps(record['annotation']), sid, m, ids[m])
        return {'sample_id': sid, 'modality': m, 'status': 'cached'}
    if HALT.is_set():
        return {'sample_id': sid, 'modality': m, 'status': 'skipped_fatal_api_error'}
    started = time.time()
    try:
        data, meta = build(s, m, prompts[m])
        dump(RUN / 'inputs' / f'{sid}.{m}.json', meta)
    except Exception as exc:
        error = {'sample_id': sid, 'modality': m, 'status': 'input_failed', 'error': type(exc).__name__ + ': ' + str(exc)}
        dump(RUN / 'failed' / f'{sid}.{m}.input.json', error)
        return error
    errors = []
    previous = list((RUN / 'teacher_raw').glob(f'{sid}.{m}.attempt*.json'))
    first_attempt = max([int(p.name.split('.attempt')[1].split('.')[0]) for p in previous] or [0]) + 1
    last_attempt = first_attempt + 2
    for attempt in range(first_attempt, last_attempt + 1):
        if HALT.is_set():
            break
        start = time.time()
        result = {'sample_id': sid, 'modality': m, 'attempt': attempt, 'request_sha256': meta['request_sha256'], 'model_requested': MODEL, 'endpoint': ENDPOINT, 'started_unix': start}
        try:
            proxy = os.environ.get('QWEN_HTTPS_PROXY')
            proxies = {'http': proxy, 'https': proxy} if proxy else None
            r = requests.post(ENDPOINT, data=data, headers={'Authorization': 'Bearer ' + key, 'Content-Type': 'application/json'}, timeout=(20, 180), allow_redirects=False, proxies=proxies)
            result.update(http_status=r.status_code, seconds=time.time()-start, request_id=r.headers.get('x-request-id') or r.headers.get('request-id'))
            text = r.text.replace(key, '[REDACTED]')
            try:
                result['response'] = json.loads(text)
            except ValueError:
                result['response_text'] = text[:20000]
            dump(RUN / 'teacher_raw' / f'{sid}.{m}.attempt{attempt}.json', result)
            if m == 'visual' and r.status_code == 500 and 'STOP_ENGINE_ABORT' in text and attempt < last_attempt:
                prepare_video(s, force_h264=True)
                data,meta=build(s,m,prompts[m])
                dump(RUN/'inputs'/f'{sid}.{m}.json',meta)
                continue
            if r.status_code != 200:
                if r.status_code in [401, 402, 403] or (r.status_code == 429 and any(x in text.lower() for x in ['quota', 'balance', 'arrears'])):
                    HALT.set()
                raise RuntimeError('HTTP ' + str(r.status_code) + ': ' + text[:1000])
            response = result['response']
            choice = response['choices'][0]
            assert choice['finish_reason'] == 'stop', 'Incomplete generation: ' + str(choice['finish_reason'])
            raw = choice['message']['content']
            obj = validate(raw, sid, m, ids[m])
            record = {'status': 'ok', 'annotation': copy.deepcopy(obj), 'meta': meta, 'versions': {'protocol_version': VERSION, 'teacher': MODEL, 'prompt_sha256': protocol['prompt_sha256'][m]}, 'api': {'model_requested': MODEL, 'model_returned': response.get('model'), 'response_id': response.get('id'), 'usage': response.get('usage'), 'attempt': attempt, 'seconds': result['seconds'], 'total_seconds': time.time()-started}, 'origin': VERSION}
            dump(dest, record)
            stale=RUN/'failed'/f'{sid}.{m}.json'
            stale.unlink(missing_ok=True)
            return {'sample_id': sid, 'modality': m, 'status': 'ok', 'seconds': round(time.time()-started, 2), 'request_bytes': len(data), 'usage': response.get('usage')}
        except Exception as exc:
            error = (type(exc).__name__ + ': ' + str(exc)).replace(key, '[REDACTED]')
            errors.append({'attempt': attempt, 'error': error})
            if 'http_status' not in result:
                result.update(error=error, seconds=time.time()-start)
                dump(RUN / 'teacher_raw' / f'{sid}.{m}.attempt{attempt}.json', result)
            if HALT.is_set() or ('http_status' in result and result['http_status'] in [400, 404, 413, 422]):
                break
            if attempt < last_attempt:
                time.sleep(2 * (attempt - first_attempt + 1))
    error = {'sample_id': sid, 'modality': m, 'status': 'failed', 'errors': errors}
    dump(RUN / 'failed' / f'{sid}.{m}.json', error)
    return error


def summarize(samples,ids):
    rows=[];counts={m:Counter() for m in ids};states={m:Counter() for m in ids};usage=Counter();models=Counter();quality=[]
    for s in samples:
        sid=s['sample_id']
        for m,cues in ids.items():
            path=RUN/'annotations'/f'{sid}.{m}.json'
            if not path.exists():
                counts[m]['missing']+=1
                for cue in cues:rows.append(dict(sample_id=sid,modality=m,cue_id=cue,state='unlabeled',y='',mask=0,evidence_note='API task not completed',protocol_version=VERSION))
                continue
            rec=json.loads(path.read_text());validate(json.dumps(rec['annotation']),sid,m,cues);counts[m]['ok']+=1
            for k in ['prompt_tokens','completion_tokens','total_tokens']:usage[k]+=(rec['api'].get('usage') or {}).get(k,0)
            models[rec['api']['model_returned']]+=1
            for cue,label in rec['annotation']['labels'].items():
                st=label['state'];states[m][st]+=1
                rows.append(dict(sample_id=sid,modality=m,cue_id=cue,state=st,y=1 if st=='positive' else 0 if st=='negative' else '',mask=int(st in ['positive','negative']),evidence_note=label['evidence_note'],protocol_version=VERSION))
            for kind in ['human_review','quality_review']:
                if kind in rec:quality.append({'sample_id':sid,'kind':kind,**rec[kind]})
    with (RUN/'labels.csv').open('w',encoding='utf-8',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
    complete=all(counts[m]['ok']==len(samples) for m in ids)
    summary=dict(protocol_version=VERSION,n_samples=len(samples),expected_tasks=3*len(samples),counts=counts,cue_rows=len(rows),state_counts=states,
                 successful_response_usage=usage,model_returned_counts=models,quality_reviews=quality,human_gold_audit_completed=False,complete=complete,full_dataset_started=False)
    dump(RUN/'summary.json',summary);dump(RUN/'status.json',dict(phase='complete_pending_human_audit' if complete else 'incomplete',complete=complete,counts=counts,updated_unix=time.time(),full_batch_started=False))
    return summary


def main():
    global RUN
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--run-dir',type=Path,default=RUN);ap.add_argument('--samples',type=Path)
    ap.add_argument('--preflight',action='store_true');ap.add_argument('--summarize',action='store_true')
    args=ap.parse_args();RUN=args.run_dir.resolve()
    samples,ids,protocol,prompts=setup(args.samples)
    if args.summarize:print(json.dumps(summarize(samples,ids),ensure_ascii=False));return
    if args.preflight:
        checks=[]
        for s in samples:
            for m in ids:
                data,meta=build(s,m,prompts[m]);checks.append({'sample_id':s['sample_id'],'modality':m,'request_bytes':len(data),'request_sha256':meta['request_sha256']})
        dump(RUN/'preflight.json',dict(passed=True,generation_performed=False,tasks=checks));print('PREFLIGHT_COMPLETE',len(checks));return
    jobs=[(s,m) for s in samples for m in ids if not (RUN/'annotations'/f"{s['sample_id']}.{m}.json").exists()]
    if not jobs:print(json.dumps(summarize(samples,ids),ensure_ascii=False));return
    key=os.environ.get('QWEN_API_KEY')
    if not key:print('READY_FOR_API_KEY',flush=True);key=sys.stdin.readline().strip()
    assert key,'Missing API credential'
    with ThreadPoolExecutor(max_workers=protocol['workers']) as pool:
        futures=[pool.submit(one,s,m,ids,protocol,prompts,key) for s,m in jobs]
        for future in as_completed(futures):print(json.dumps(future.result(),ensure_ascii=False),flush=True)
    summary=summarize(samples,ids);print(json.dumps(summary,ensure_ascii=False),flush=True)
    if not summary['complete']:raise SystemExit(1)

if __name__=='__main__':main()
