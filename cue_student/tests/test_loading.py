import copy,unittest
import torch
from cue_student.loading import loader_for
from cue_student.common import PROJECT
from cue_student.data import Release,CueDataset,make_collator
from cue_student.common import load_config

class TinyDataset(torch.utils.data.Dataset):
    def __len__(self):return 8
    def __getitem__(self,i):return {"sample_id":str(i),"x":torch.tensor([i],dtype=torch.float32)}
class TinyCollator:
    def __call__(self,items):return {"sample_ids":[x["sample_id"] for x in items],"x":torch.stack([x["x"] for x in items])}

class LoadingTests(unittest.TestCase):
    def test_spawn_order_and_main_rng_unchanged(self):
        expected=None
        for workers in (0,2):
            torch.manual_seed(42);state=torch.get_rng_state().clone()
            result=list(loader_for(TinyDataset(),[[0,3],[7,1],[2,6],[4,5]],TinyCollator(),dict(num_workers=workers,prefetch_factor=2)))
            self.assertTrue(torch.equal(state,torch.get_rng_state()))
            values=[(r["sample_ids"],r["x"].tolist()) for r in result]
            if expected is None:expected=values
            else:self.assertEqual(values,expected)

    def test_invalid_worker_settings_rejected(self):
        for cfg in (dict(num_workers=-1),dict(num_workers=1,prefetch_factor=0)):
            with self.assertRaises(ValueError):loader_for(TinyDataset(),[[0]],TinyCollator(),cfg)

    def test_real_video_decoder_threads_preserve_pixels_and_pts(self):
        release=Release(PROJECT/"cue_student/artifacts/smoke_release_v1")
        ds=CueDataset(release,"visual","pseudo_train",training=True)
        cfg=load_config(PROJECT/"cue_student/configs/visual.json")
        original=make_collator(dict(cfg,decode_threads=0))([ds[0],ds[1]])
        single=make_collator(dict(cfg,decode_threads=1))([ds[0],ds[1]])
        self.assertEqual(original["frame_times"],single["frame_times"])
        torch.testing.assert_close(original["pixel_values"],single["pixel_values"],rtol=0,atol=0)
        torch.testing.assert_close(original["frame_time_offsets"],single["frame_time_offsets"],rtol=0,atol=0)

if __name__=="__main__":unittest.main()
