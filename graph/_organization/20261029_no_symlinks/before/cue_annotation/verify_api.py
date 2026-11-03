"""Offline integrity and viewer checks; never makes paid API requests."""
import hashlib,json,csv,sys
from pathlib import Path
import annotate_api as runner

def verify_prepared(samples,ids,prompts):
    root=runner.RUN
    assert not list((root/'annotations').glob('*.json')) and not list((root/'teacher_raw').glob('*.json'))
    assert not (root/'labels.csv').exists()
    for s in samples:
        for m in ids:
            data,meta=runner.build(s,m,prompts[m])
            original=json.loads((root/'inputs'/f"{s['sample_id']}.{m}.json").read_text())
            assert meta['request_sha256']==original['request_sha256']
    from fastapi.testclient import TestClient
    sys.path.insert(0,str(root.parent.parent/'viewer'));import server
    with TestClient(server.app) as client:
        boot=client.get('/api/bootstrap').json();assert boot['cue_rows']==0 and boot['completed_samples']==0 and boot['exports']==[]
        assert client.get('/api/export/labels.csv').status_code==404
        for s in samples:
            detail=client.get('/api/samples/'+s['sample_id']).json()
            assert detail['labels']==[] and detail['annotations']=={} and detail['teacher_responses']=={}
            for url in [detail['media']['teacher_audio'],detail['media']['video']]:
                assert client.get(url,headers={'Range':'bytes=0-63'}).status_code==206
        assert client.get('/api/pilot-progress').json()['counts']['done']==0
    result=dict(passed=True,phase='labels_removed',retained_samples=len(samples),completed_tasks=0,cue_rows=0,
                original_label_files_present=False,raw_api_responses_present=False,paid_api_calls=0,prepared_request_payloads_reproduced=90)
    runner.dump(root/'verification.json',result);print(json.dumps(result,ensure_ascii=False,indent=2))


def verify():
    samples,ids,protocol,prompts=runner.setup()
    root=runner.RUN
    if not (root/'labels.csv').exists():return verify_prepared(samples,ids,prompts)
    rows=list(csv.DictReader((root/'labels.csv').open()))
    assert len(samples)==30 and len(rows)==1260
    assert len({(r['sample_id'],r['cue_id']) for r in rows})==1260
    for r in rows:
        assert r['state'] in runner.STATES
        assert int(r['mask'])==int(r['state'] in ['positive','negative'])
        assert r['y']==('1' if r['state']=='positive' else '0' if r['state']=='negative' else '')
    semantic=hashlib.sha256();seconds=0;compat=[]
    for s in samples:
        sid=s['sample_id']
        assert len(s['visual']['frames'])==8
        for f in s['visual']['frames']:assert runner.sha(Path(f['path']).read_bytes())==f['sha256']
        for m in ids:
            rec=json.loads((root/'annotations'/f'{sid}.{m}.json').read_text())
            runner.validate(json.dumps(rec['annotation']),sid,m,ids[m])
            semantic.update(json.dumps(rec['annotation'],sort_keys=True,ensure_ascii=False).encode())
            raw=json.loads((root/'teacher_raw'/f"{sid}.{m}.attempt{rec['api']['attempt']}.json").read_text())
            assert raw['http_status']==200 and raw['response']['model']==runner.MODEL
            assert raw['request_sha256']==rec['meta']['request_sha256']
            data,meta=runner.build(s,m,prompts[m])
            assert meta['request_sha256']==rec['meta']['request_sha256'],f'Payload changed: {sid}.{m}'
            if m=='audio':
                assert meta['covered_time_sec']==[0,meta['duration_sec']] and not meta['temporal_truncation']
                seconds+=meta['duration_sec']
            if m=='visual':
                assert not any(meta[k] for k in ['client_frame_sampling','client_temporal_truncation','client_spatial_resize','audio_included'])
                info=runner.video_info(Path(meta['submitted_video_path']));assert info==meta['submitted_video']
                assert all(info[k]==meta['source_video'][k] for k in ['width','height','fps','video_packets','duration'])
                if not meta['video_stream_copy']:compat.append(sid)
        assert (root.parent.parent/'viewer/cache/videos'/f'{sid}.mp4').is_file()
    if (root/'freeze.json').exists():
        freeze=json.loads((root/'freeze.json').read_text())
        assert semantic.hexdigest()==freeze['annotation_content_sha256'],'Label content changed during cleanup'
    from fastapi.testclient import TestClient
    sys.path.insert(0,str(root.parent.parent/'viewer'))
    import server
    with TestClient(server.app) as client:
        b=client.get('/api/bootstrap').json();assert b['run_id']=='pilot30' and b['cue_rows']==1260 and 'runs' not in b
        assert client.get('/api/bootstrap?run=deleted').status_code==404
        assert len(list(csv.DictReader(client.get('/api/export/labels.csv').text.splitlines())))==1260
        assert client.get('/api/export/disagreements_vs_allframes_api.csv').status_code==404
        for s in samples:
            sid=s['sample_id'];detail=client.get('/api/samples/'+sid).json();assert len(detail['labels'])==42
            for url in [detail['media']['teacher_audio'],detail['media']['teacher_video'],detail['media']['video']]:
                response=client.get(url,headers={'Range':'bytes=0-63'});assert response.status_code==206 and len(response.content)==64
            assert client.get(detail['frames'][0]['url']+'/full').status_code==200
        assert client.get('/api/pilot-progress').json()['ready']
    result=dict(passed=True,paid_api_calls=0,samples=30,tasks=90,cue_rows=1260,annotation_content_sha256=semantic.hexdigest(),
                exact_request_payloads_reproduced=90,complete_audio_seconds=seconds,h264_compatibility_samples=compat,
                viewer_samples_verified=30,media_range_checks=90,old_versions_required=False,human_accuracy_audit_completed=False)
    runner.dump(root/'verification.json',result)
    manifest={str(p.relative_to(root)):runner.sha(p.read_bytes()) for p in sorted(root.rglob('*')) if p.is_file() and p.name!='artifact_sha256.json'}
    runner.dump(root/'artifact_sha256.json',manifest)
    print(json.dumps(result,ensure_ascii=False,indent=2))

if __name__=='__main__':verify()
