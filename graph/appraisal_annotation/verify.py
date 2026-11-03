"""Offline verification only: never calls the model API."""
from graph_paths import hash_matches as _graph_hash_matches
import argparse, csv, json, sys
from graph_paths import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from annotate import ROOT,CUE_ROOT,setup,validate,build,DIMS,sha

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--allow-incomplete',action='store_true');args=ap.parse_args()
    samples,protocol,prompt=setup()
    summary=json.loads((ROOT/'summary.json').read_text())
    checks=[];failed_checks=[];valid_count=0;invalid_count=0
    for s in samples:
        sid=s['sample_id'];data,meta=build(s,protocol,prompt)
        content=json.loads(data)['messages'][0]['content']
        assert [c['type'] for c in content]==['text','input_audio','video_url']
        runtime=json.loads(content[0]['text'].split('\nRuntime input:\n',1)[1])
        assert set(runtime)=={'sample_id','available_modalities','text','audio','video'}
        assert set(runtime['text'])=={'chinese','english'}
        assert meta['annotation_schema_version']=='appraisal_annotation_schema_v2.4'
        assert _graph_hash_matches((ROOT / 'media/audio' / f'{sid}.wav').read_bytes(), sha((CUE_ROOT / 'media/audio' / f'{sid}.wav').read_bytes()), sha((ROOT / 'media/audio' / f'{sid}.wav').read_bytes()))
        assert _graph_hash_matches((ROOT / 'media/video' / f'{sid}.mp4').read_bytes(), sha((CUE_ROOT / 'media/video' / f'{sid}.mp4').read_bytes()), sha((ROOT / 'media/video' / f'{sid}.mp4').read_bytes()))
        p=ROOT/'annotations'/f'{sid}.json'
        if not p.exists():
            fp=ROOT/'failed'/f'{sid}.json'
            if not fp.exists():
                assert args.allow_incomplete,'Sample not tested: '+sid
                continue
            failure=json.loads(fp.read_text())
            assert failure['semantic_unknown'] is False
            raw_path=ROOT/'teacher_raw'/f"{sid}.attempt{failure['errors'][-1]['attempt']}.json"
            attempt=json.loads(raw_path.read_text())
            assert attempt['request_sha256']==meta['request_sha256']
            assert attempt['http_status']==200 and attempt['json_parse_status']=='invalid'
            token_detail=attempt['response']['usage']['prompt_tokens_details']
            assert all(token_detail.get(k,0)>0 for k in ['text_tokens','audio_tokens','video_tokens'])
            try:validate(attempt['response']['choices'][0]['message']['content'])
            except AssertionError:pass
            else:raise AssertionError('Failure unexpectedly passes schema: '+sid)
            failed_checks.append(dict(sample_id=sid,status='technical_schema_failure',attempts=len(list(
                (ROOT/'teacher_raw').glob(f'{sid}.attempt*.json'))),actual_joint_tokens=token_detail,
                raw_response_preserved=True,semantic_unknown=False))
            continue
        rec=json.loads(p.read_text());a=validate(json.dumps(rec['annotation']))
        assert rec['versions']['annotation_schema_version']=='appraisal_annotation_schema_v2.4'
        assert 'focus_person' not in a
        assert rec['meta']==meta and rec['api']['model_returned']==protocol['model_requested']
        raw=json.loads((ROOT/'teacher_raw'/f"{sid}.attempt{rec['api']['attempt']}.json").read_text())
        assert raw['http_status']==200 and raw['json_parse_status']=='valid'
        assert a==validate(raw['response']['choices'][0]['message']['content'])
        tokens=rec['api']['usage']['prompt_tokens_details']
        assert all(tokens.get(k,0)>0 for k in ['text_tokens','audio_tokens','video_tokens']),'Unverified joint input: '+sid
        valid_count+=sum(d['valid'] for d in a['dimensions'])
        invalid_count+=sum(not d['valid'] for d in a['dimensions'])
        checks.append(dict(sample_id=sid,model=rec['api']['model_returned'],response_id=rec['api']['response_id'],
            text_tokens=tokens['text_tokens'],audio_tokens=tokens['audio_tokens'],video_tokens=tokens['video_tokens'],
            same_audio_as_cue=True,same_video_as_cue=True,raw_response_matches_annotation=True))
    assert len(checks)==summary['successful_samples']
    assert valid_count==summary['valid_dimension_count'] and invalid_count==summary['invalid_dimension_count']
    if checks:
        with (ROOT/'labels.csv').open(encoding='utf-8-sig',newline='') as f:rows=list(csv.DictReader(f))
        assert len(rows)==len(checks)*6
        assert len({(r['sample_id'],r['dimension_id']) for r in rows})==len(rows)
        for r in rows:
            if r['valid']=='False':assert not r['state'] and not r['evidence'] and not r['evidence_modalities']
    if not args.allow_incomplete:assert len(checks)+len(failed_checks)==30 and summary['test_complete']
    result=dict(passed=True,api_called=False,verified_joint_samples=len(checks),all_input_preflights=30,
        tested_samples=len(checks)+len(failed_checks),technical_failures=len(failed_checks),successful_rows=len(checks)*6,valid_dimensions=valid_count,invalid_dimensions=invalid_count,
        prompt_sha256=protocol['prompt_sha256'],prompt_version=protocol['prompt_version'],
        ontology_version=protocol['ontology_version'],annotation_schema_version=protocol['annotation_schema_version'],human_gold_audit_completed=False,samples=checks,failed_samples=failed_checks)
    (ROOT/'verification.json').write_text(json.dumps(result,ensure_ascii=False,indent=2))
    print(json.dumps({k:v for k,v in result.items() if k not in {'samples','failed_samples'}},ensure_ascii=False))
if __name__=='__main__':main()
