"""Exercise full-input regeneration after deleting disposable API media."""
import json,subprocess,tempfile,unittest
from graph_paths import Path
from unittest.mock import patch
import numpy as np
import soundfile as sf
import annotate_api as core

class Tests(unittest.TestCase):
    def test_archived_h264_file_is_rebuilt_with_original_hash_and_metadata(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);run=root/'run';(run/'inputs').mkdir(parents=True);source=root/'source.mp4'
            subprocess.run([core.FFMPEG,'-hide_banner','-loglevel','error','-nostdin','-y','-f','lavfi','-i',
                'color=c=red:s=96x64:r=25:d=1.2','-c:v','mpeg4','-threads','1',str(source)],check=True)
            sample=dict(sample_id='sample',video_path=str(source))
            with patch.object(core,'RUN',run):
                first=core.prepare_video(sample,force_h264=True,allow_large=True)
                metadata=(run/'inputs/sample.video_file.json').read_bytes()
                Path(first['submitted_video_path']).unlink()
                second=core.prepare_video(sample,allow_large=True)
                self.assertFalse(second['video_stream_copy'])
                self.assertEqual(core.sha(Path(second['submitted_video_path']).read_bytes()),first['submitted_video_sha256'])
                self.assertEqual((run/'inputs/sample.video_file.json').read_bytes(),metadata)
    def test_audio_regeneration_preserves_full_recording_bytes(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);source=root/'source.wav';sf.write(source,np.linspace(-.5,.5,16000,dtype=np.float32),16000,subtype='PCM_16')
            with patch.object(core,'RUN',root/'run'):
                path,duration,n=core.prepare_audio(dict(sample_id='sample',audio_path=str(source)))
                before=path.read_bytes();path.unlink()
                rebuilt,duration_after,n_after=core.prepare_audio(dict(sample_id='sample',audio_path=str(source)))
                self.assertEqual(rebuilt.read_bytes(),before)
                self.assertEqual((duration_after,n_after),(duration,n))
    def test_audio_rebuild_rejects_a_changed_original(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);source=root/'source.wav';run=root/'run';(run/'inputs').mkdir(parents=True)
            sf.write(source,np.linspace(-.5,.5,16000,dtype=np.float32),16000,subtype='PCM_16')
            sample=dict(sample_id='sample',audio_path=str(source))
            with patch.object(core,'RUN',run):
                path,_,_=core.prepare_audio(sample)
                core.dump(run/'inputs/sample.audio.json',dict(source_sha256=core.sha(source.read_bytes()),submitted_wav_sha256=core.sha(path.read_bytes())))
                path.unlink();sf.write(source,np.zeros(16000,dtype=np.float32),16000,subtype='PCM_16')
                with self.assertRaisesRegex(AssertionError,'Original audio changed'):core.prepare_audio(sample)

if __name__=='__main__':unittest.main()
