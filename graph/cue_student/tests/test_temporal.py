import copy, json, unittest
from unittest.mock import patch
import numpy as np
import torch
from torch import nn
from PIL import Image
from cue_student.common import PROJECT, load_config
from cue_student.data import VisualCollator
from cue_student.models import CueModel, TemporalHead
from cue_student.temporal import VideoTemporalHead, temporal_spec, relative_frame_times

def config(**updates):
    return dict(modality="visual", model_dir="unused", temporal_model="transformer",
                temporal_dim=16, temporal_heads=4, temporal_layers=2,
                temporal_ffn_dim=32, temporal_dropout=0., dropout=0.,
                **updates)

class FakeCLIP(nn.Module):
    def __init__(self):
        super().__init__()
        self.config=type("Cfg",(),{"projection_dim":8})()
        self.proj=nn.Linear(3,8)
    def forward(self,pixel_values):
        return type("Out",(),{"image_embeds":self.proj(pixel_values.mean((-1,-2)))})()

class VideoTemporalTests(unittest.TestCase):
    def setUp(self):
        torch.manual_seed(42)
        self.head=VideoTemporalHead(8,config()).eval()
        self.x=torch.randn(2,5,8)
        self.mask=torch.tensor([[1,1,1,1,1],[1,1,0,0,0]],dtype=torch.bool)
        self.times=torch.tensor([[0.,.5,1.,1.5,2.],[0.,.8,0.,0.,0.]])

    def test_content_order_changes_logits(self):
        order=torch.tensor([4,3,2,1,0])
        a=self.head(self.x[:1],self.mask[:1],self.times[:1])
        b=self.head(self.x[:1,order],self.mask[:1],self.times[:1])
        self.assertGreater(float((a-b).abs().max()),1e-5)

    def test_real_timing_changes_logits(self):
        altered=self.times.clone();altered[0]=torch.tensor([0.,.1,.2,1.5,2.])
        a=self.head(self.x,self.mask,self.times);b=self.head(self.x,self.mask,altered)
        self.assertGreater(float((a[0]-b[0]).abs().max()),1e-5)
        torch.testing.assert_close(a[1],b[1],rtol=0,atol=0)

    def test_absolute_origin_does_not_change_logits(self):
        shifted=self.times+100.
        torch.testing.assert_close(self.head(self.x,self.mask,self.times),self.head(self.x,self.mask,shifted),atol=1e-6,rtol=1e-5)

    def test_padding_nan_and_single_vs_batch(self):
        poisoned=self.x.clone();poisoned[~self.mask]=float("nan")
        times=self.times.clone();times[~self.mask]=float("nan")
        actual=self.head(poisoned,self.mask,times)
        expected=self.head(self.x[1:2,:2],self.mask[1:2,:2],self.times[1:2,:2])
        torch.testing.assert_close(actual[1:2],expected,atol=2e-6,rtol=2e-5)
        self.assertTrue(torch.isfinite(actual).all())

    def test_single_frame(self):
        result=self.head(self.x[:1,:1],self.mask[:1,:1],self.times[:1,:1])
        self.assertEqual(tuple(result.shape),(1,10));self.assertTrue(torch.isfinite(result).all())

    def test_padding_has_zero_gradient(self):
        x=self.x.clone().requires_grad_()
        self.head(x,self.mask,self.times).sum().backward()
        self.assertEqual(float(x.grad[~self.mask].abs().sum()),0.)
        self.assertTrue(torch.isfinite(x.grad).all())
        for p in self.head.parameters():
            self.assertIsNotNone(p.grad);self.assertTrue(torch.isfinite(p.grad).all())

    def test_invalid_mask_and_timestamps_rejected(self):
        for mask,times in [
            (torch.zeros_like(self.mask),self.times),
            (torch.tensor([[1,0,1,1,1],[1,1,0,0,0]],dtype=torch.bool),self.times),
            (self.mask,torch.zeros_like(self.times)),
            (self.mask,torch.full_like(self.times,float("nan")))]:
            with self.assertRaises(ValueError):self.head(self.x,mask,times)
        with self.assertRaisesRegex(ValueError,"timestamp tensor"):
            self.head(self.x,self.mask,self.times[:,:2])

    def test_relative_offsets_computed_before_float32(self):
        times=relative_frame_times([[1e9,1e9+.125,1e9+.625],[40.]])
        torch.testing.assert_close(times,torch.tensor([[0.,.125,.625],[0.,0.,0.]]),rtol=0,atol=0)
        for bad in ([],[[]],[[0.,0.]],[[0.,float("nan")]],[[1.,0.]]):
            with self.assertRaises(ValueError):relative_frame_times(bad)

    def test_layers_have_independent_initialization(self):
        a,b=self.head.transformer.layers
        self.assertFalse(torch.equal(a.self_attn.in_proj_weight,b.self_attn.in_proj_weight))

    def test_invalid_architecture_rejected(self):
        for changes in [
            dict(temporal_dim=15),dict(temporal_heads=3),dict(temporal_layers=0),
            dict(temporal_dropout=1.),dict(temporal_time_unit_seconds=0.),
            dict(temporal_position_encoding="unknown"),dict(temporal_model="unknown"),
            dict(modality="text"),dict(pooling="attention")]:
            cfg=config();cfg.update(changes)
            with self.assertRaises(ValueError):temporal_spec(cfg)
        self.assertEqual(temporal_spec(dict(modality="visual")),{"temporal_model":"none"})
        cfg=load_config(PROJECT/"cue_student/configs/visual_temporal.json")
        self.assertEqual(temporal_spec(cfg)["temporal_layers"],2)

    def test_cue_model_wiring_and_frozen_encoder(self):
        with patch("cue_student.models.CLIPVisionModelWithProjection.from_pretrained",side_effect=lambda *a,**k:FakeCLIP()):
            model=CueModel(config()).train()
            batch=dict(pixel_values=torch.randn(5,3,4,4),frame_owners=torch.tensor([0,0,0,1,1]),
                       frame_time_offsets=torch.tensor([[0.,.5,1.],[0.,.8,0.]]),batch_size=2)
            a=model(batch);a.sum().backward()
            self.assertFalse(model.encoder.training)
            self.assertTrue(all(p.grad is None for p in model.encoder.parameters()))
            self.assertEqual(tuple(a.shape),(2,10))
            with torch.no_grad():
                torch.testing.assert_close(a,model(dict(batch,targets=torch.ones(2,10),label_mask=torch.zeros(2,10))),atol=0,rtol=0)
            restored=CueModel(config());restored.restore_weights(model.checkpoint_state());restored.eval();model.eval()
            # Frozen encoder is external to the checkpoint.
            restored.encoder.load_state_dict(model.encoder.state_dict())
            torch.testing.assert_close(model(batch),restored(batch),atol=0,rtol=0)

    def test_baseline_needs_no_timestamp_tensor(self):
        with patch("cue_student.models.CLIPVisionModelWithProjection.from_pretrained",side_effect=lambda *a,**k:FakeCLIP()):
            cfg=dict(modality="visual",model_dir="unused",dropout=0.)
            model=CueModel(cfg).eval()
            self.assertIsInstance(model.head,TemporalHead)
            batch=dict(pixel_values=torch.randn(3,3,4,4),frame_owners=torch.tensor([0,0,0]),batch_size=1)
            result=model(batch)
            restored=CueModel(cfg);restored.restore_weights(model.checkpoint_state());restored.encoder.load_state_dict(model.encoder.state_dict());restored.eval()
            torch.testing.assert_close(result,restored(batch),atol=0,rtol=0)

    def test_collator_time_offsets_align_with_frame_owners(self):
        collator=VisualCollator(str(PROJECT/"AffectGPT/models/clip-vit-large-patch14"))
        image=Image.new("RGB",(224,224),(10,20,30))
        rows=[dict(sample_id=str(i),video_path="unused",targets=np.zeros(10),label_mask=np.ones(10,bool)) for i in range(2)]
        with patch("cue_student.data.sample_video",side_effect=[([image]*3,[100.,100.5,101.1]),([image],[200.])]):
            batch=collator(rows)
        self.assertEqual(batch["frame_owners"].tolist(),[0,0,0,1])
        self.assertEqual(batch["frame_times"],[[100.,100.5,101.1],[200.]])
        torch.testing.assert_close(batch["frame_time_offsets"],torch.tensor([[0.,.5,1.1],[0.,0.,0.]]))
        self.assertEqual(len(batch["pixel_values"]),4)

if __name__=="__main__":unittest.main()
