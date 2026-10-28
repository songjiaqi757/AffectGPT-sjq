import csv,json,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
import numpy as np
import torch
from cue_student.common import PROJECT
from cue_student.data import Release,TextCollator,read_audio,sample_video,epoch_batches
from cue_student.prepare import load_labels,assign_roles
from cue_student.models import TemporalHead,CueModel
from cue_student.objectives import masked_bce_sum,training_weights,binary_metrics

class CoreTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp=tempfile.TemporaryDirectory(dir=PROJECT/"cue_student/artifacts")
        cls.root=Path(cls.tmp.name)
    @classmethod
    def tearDownClass(cls): cls.tmp.cleanup()
    def test_positive_and_negative_gradient(self):
        z=torch.zeros(1,2,requires_grad=True)
        loss,n=masked_bce_sum(z,torch.tensor([[1.,0.]]),torch.ones(1,2,dtype=torch.bool)); loss.backward()
        self.assertEqual(n,2); self.assertLess(z.grad[0,0],0); self.assertGreater(z.grad[0,1],0)
    def test_unknown_nan_target_has_zero_gradient(self):
        z=torch.zeros(1,3,requires_grad=True)
        loss,n=masked_bce_sum(z,torch.tensor([[1.,float("nan"),float("nan")]]),torch.tensor([[1,0,0]],dtype=torch.bool))
        loss.backward(); self.assertEqual(n,1); self.assertTrue(torch.isfinite(loss)); self.assertEqual(z.grad[0,1:].abs().sum(),0)
    def test_all_masked_batch(self):
        z=torch.zeros(2,3,requires_grad=True)
        loss,n=masked_bce_sum(z,torch.full_like(z,float("nan")),torch.zeros_like(z,dtype=torch.bool)); loss.backward()
        self.assertEqual(n,0); self.assertEqual(float(loss),0); self.assertEqual(float(z.grad.abs().sum()),0)
    def test_accumulation_matches_global_valid_denominator(self):
        x=torch.tensor([[1.,2.],[3.,4.],[2.,-1.]])
        y=torch.tensor([[1.,0.],[0.,1.],[1.,0.]])
        m=torch.tensor([[1,0],[1,1],[0,1]],dtype=torch.bool)
        a=torch.nn.Linear(2,2,bias=False); b=torch.nn.Linear(2,2,bias=False); b.load_state_dict(a.state_dict())
        loss,n=masked_bce_sum(a(x),y,m); (loss/n).backward()
        for sl in (slice(0,1),slice(1,3)):
            loss,_=masked_bce_sum(b(x[sl]),y[sl],m[sl]); (loss/n).backward()
        torch.testing.assert_close(a.weight.grad,b.weight.grad)
    def test_weights_use_only_valid_targets(self):
        y=np.array([[1,0],[0,1],[0,1]],np.float32); m=np.array([[1,1],[1,0],[1,0]],bool)
        w,p,n=training_weights(y,m,True)
        self.assertEqual(p.tolist(),[1,0]); self.assertEqual(n.tolist(),[2,1]); self.assertTrue(np.isfinite(w).all())
    def test_metrics_unsupported_ap_is_null(self):
        r=binary_metrics(np.zeros((3,1)),np.array([[.1],[.2],[.7]]),np.ones((3,1),bool),["cue"])
        self.assertIsNone(r["macro_ap"]); self.assertIsNone(r["per_cue"]["cue"]["ap"])
    def test_group_roles_never_leak(self):
        rows=[dict(sample_id=str(i),group_id=str(i//2)) for i in range(40)]
        y=np.tile(np.array([[1.,0.],[0.,1.]]),(20,1)); m=np.ones_like(y,bool)
        r=assign_roles(rows,y,m,4,4,.25)
        self.assertEqual(len(r["audit_sample_ids"]),4)
        for g in {x["group_id"] for x in rows}:
            roles={x["role"] for x in rows if x["group_id"]==g}
            self.assertTrue(len(roles)==1 or roles<={"gold_audit","audit_group_excluded"})
    def test_audit_excludes_development_exposure(self):
        rows=[dict(sample_id=str(i),group_id=str(i//2)) for i in range(40)]
        y=np.ones((40,2)); m=np.ones_like(y,bool)
        r=assign_roles(rows,y,m,4,4,.25,exposure=[str(i) for i in range(20)])
        self.assertTrue(all(int(i)>=20 for i in r["audit_sample_ids"]))
    def test_label_csv_duplicate_and_mapping(self):
        ontology={"cue_ids":{"text":["T"+str(i) for i in range(15)],"audio":["A"+str(i) for i in range(17)],"visual":["V"+str(i) for i in range(10)]}}
        rows=[dict(sample_id="s",modality=m,cue_id=c,state="negative",y="0",mask="1") for m,cs in ontology["cue_ids"].items() for c in cs]
        p=self.root/"labels.csv"
        def write(items):
            with p.open("w") as f:
                w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(items)
        write(rows); y,m,s=load_labels([{"sample_id":"s"}],ontology,p); self.assertEqual(m.sum(),42)
        write(rows+[rows[0]])
        with self.assertRaisesRegex(ValueError,"Duplicate"): load_labels([{"sample_id":"s"}],ontology,p)
        changed=[dict(r) for r in rows];changed[0]["state"]="uncertain";write(changed)
        with self.assertRaisesRegex(ValueError,"disagreement"): load_labels([{"sample_id":"s"}],ontology,p)
    def test_release_tamper_detected(self):
        import shutil
        src=PROJECT/"cue_student/artifacts/smoke_release_v1"; dest=self.root/"tampered"
        shutil.copytree(src,dest); (dest/"members.json").write_text((dest/"members.json").read_text()+" ")
        with self.assertRaisesRegex(ValueError,"changed"): Release(dest)
    def test_text_chunks_cover_without_overlap_double_count(self):
        collate=TextCollator(str(PROJECT/"AffectGPT/models/xlm-roberta-base"),128,32)
        text="hello world "*400
        item=dict(sample_id="s",text=dict(chinese=text,english=""),targets=np.zeros(15),label_mask=np.ones(15,bool))
        b=collate([item])
        self.assertLessEqual(b["input_ids"].shape[1],128)
        n=len(collate.tokenizer.encode(text,add_special_tokens=False))
        self.assertAlmostEqual(float(b["pool_weights"][b["owners"]==0].sum()),n,places=3)
        self.assertEqual(float(b["pool_weights"][b["owners"]==1].sum()),0)
        self.assertEqual(b["language_present"].tolist(),[[1.,0.]])
    def test_audio_resampling_multichannel(self):
        import soundfile as sf
        t=np.arange(4000)/8000; a=np.stack([np.sin(100*t),np.sin(200*t),np.sin(300*t)],axis=1)
        p=self.root/"multichannel.wav"; sf.write(p,a,8000)
        result=read_audio(p); self.assertEqual(len(result),8000); self.assertTrue(np.isfinite(result).all())
    def test_video_actual_pts_and_tail(self):
        import av
        from PIL import Image
        p=self.root/"toy.mp4"
        with av.open(str(p),"w") as c:
            stream=c.add_stream("mpeg4",rate=5);stream.width=64;stream.height=32;stream.pix_fmt="yuv420p"
            for i in range(6):
                frame=av.VideoFrame.from_image(Image.new("RGB",(64,32),(i*30,0,0)))
                for packet in stream.encode(frame):c.mux(packet)
            for packet in stream.encode():c.mux(packet)
        images,pts=sample_video(p,fps=2,size=224)
        self.assertAlmostEqual(pts[0],0);self.assertAlmostEqual(pts[-1],1.)
        self.assertEqual(len(pts),len(set(pts)));self.assertTrue(all(x.size==(224,224) for x in images))
    def test_temporal_padding_ignored(self):
        for pool in ("mean","attention","topk"):
            torch.manual_seed(42); h=TemporalHead(3,2,pool,0).eval()
            x=torch.randn(1,2,3); padded=torch.cat([x,torch.full((1,3,3),100.)],dim=1)
            torch.testing.assert_close(h(x,torch.ones(1,2,dtype=torch.bool)),h(padded,torch.tensor([[1,1,0,0,0]],dtype=torch.bool)))
    def test_frozen_encoder_stays_eval_when_head_trains(self):
        class Encoder(torch.nn.Module):
            def __init__(self):
                super().__init__();self.config=type("Cfg",(),{"hidden_size":4})();self.dropout=torch.nn.Dropout(.8);self.weight=torch.nn.Parameter(torch.ones(4))
        with patch("cue_student.models.AutoModel.from_pretrained",return_value=Encoder()):
            model=CueModel(dict(modality="text",model_dir="unused",encoder_train="frozen"))
            model.train();self.assertFalse(model.encoder.training);self.assertTrue(model.head.training)
            self.assertTrue(all(not p.requires_grad for p in model.encoder.parameters()))
    def test_epoch_sampler_reproducible_and_complete(self):
        class Data:
            costs=[1,3,2,6,1,10,2,3,4]
            def __len__(self):return len(self.costs)
        a=epoch_batches(Data(),3,epoch=2,max_units=5)
        self.assertEqual(a,epoch_batches(Data(),3,epoch=2,max_units=5))
        self.assertEqual(sorted(sum(a,[])),list(range(9)))

    def test_missing_both_text_fields_rejected_for_supervision(self):
        collate=TextCollator(str(PROJECT/"AffectGPT/models/xlm-roberta-base"))
        with self.assertRaisesRegex(ValueError,"Both text fields"):
            collate([dict(sample_id="empty",text={},targets=np.zeros(15),label_mask=np.ones(15,bool))])
    def test_observation_spans_persist_without_teacher_labels(self):
        from cue_student.observations import write_observations
        collate=TextCollator(str(PROJECT/"AffectGPT/models/xlm-roberta-base"))
        items=[dict(sample_id="observed_text",text=dict(chinese="你好",english=""),targets=np.ones(15),label_mask=np.ones(15,bool))]
        batch=collate(items);out=self.root/"text_observations"
        write_observations(batch,out,"text",{})
        record=json.loads(next(out.glob("*.json")).read_text())
        self.assertEqual(record["language_present"],[1.,0.]);self.assertTrue(record["token_spans"])
        self.assertNotIn("targets",record);self.assertNotIn("label_mask",record)
        batch["targets"].zero_();batch["label_mask"].zero_()
        write_observations(batch,out,"text",{})
    def test_observation_video_pts_persist(self):
        from cue_student.observations import write_observations
        batch=dict(sample_ids=["video_pts"],frame_times=[[0.,.6,1.]])
        out=self.root/"video_observations";write_observations(batch,out,"visual",dict(fps=2,spatial="letterbox"))
        record=json.loads(next(out.glob("*.json")).read_text())
        self.assertEqual(record["actual_frame_pts_seconds"],[0.,.6,1.])

if __name__=="__main__": unittest.main()
