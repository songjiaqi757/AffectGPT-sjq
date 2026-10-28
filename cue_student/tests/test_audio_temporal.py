import copy,unittest
from unittest.mock import patch
import torch
from torch import nn
from cue_student.temporal import AudioTemporalHead,temporal_spec
from cue_student.models import CueModel,TemporalHead,build_optimizer
from cue_student.observations import describe

def config(**kw):
    cfg=dict(modality="audio",model_dir="unused",encoder_train="frozen",pooling="mean",
             temporal_model="transformer",temporal_dim=16,temporal_heads=4,temporal_layers=2,
             temporal_ffn_dim=32,temporal_dropout=0.,dropout=0.,head_lr=1e-3)
    cfg.update(kw);return cfg

class FakeHubert(nn.Module):
    def __init__(self):
        super().__init__();self.proj=nn.Linear(1,8)
        self.config=type("Cfg",(),dict(hidden_size=8,conv_kernel=[400],conv_stride=[320]))()
    def forward(self,input_values,attention_mask):
        x=input_values.unfold(1,400,320).mean(-1,keepdim=True)
        return type("Out",(),dict(last_hidden_state=self.proj(x)))()
    def _get_feature_vector_attention_mask(self,steps,attention_mask):
        lengths=(attention_mask.sum(1)-400)//320+1
        return torch.arange(steps)[None,:]<lengths[:,None]

class AudioTemporalTests(unittest.TestCase):
    def setUp(self):
        torch.manual_seed(42);self.head=AudioTemporalHead(8,config()).eval()
        self.x=torch.randn(2,6,8)
        self.mask=torch.tensor([[1]*6,[1,1,1,0,0,0]],dtype=torch.bool)
    def test_shape_order_and_timebase(self):
        a=self.head(self.x,self.mask)
        self.assertEqual(tuple(a.shape),(2,17))
        self.assertGreater(float((a[:1]-self.head(self.x[:1].flip(1),self.mask[:1])).abs().max()),1e-5)
        other=AudioTemporalHead(8,config(audio_feature_stride_samples=640)).eval()
        other.load_state_dict(self.head.state_dict())
        self.assertGreater(float((a-other(self.x,self.mask)).abs().max()),1e-5)
    def test_padding_nan_and_batch_invariance(self):
        x=self.x.clone();x[~self.mask]=float("nan")
        a=self.head(x,self.mask)
        torch.testing.assert_close(a[1:2],self.head(x[1:2,:3],self.mask[1:2,:3]),atol=2e-6,rtol=2e-5)
        self.assertTrue(torch.isfinite(a).all())
    def test_padding_has_zero_gradient(self):
        x=self.x.clone().requires_grad_();self.head(x,self.mask).sum().backward()
        self.assertEqual(float(x.grad[~self.mask].abs().sum()),0.)
        self.assertTrue(all(p.grad is not None and torch.isfinite(p.grad).all() for p in self.head.parameters()))
        self.assertTrue(torch.isfinite(self.head(self.x[:1,:1],self.mask[:1,:1])).all())
    def test_encoder_freeze_checkpoint_and_baseline(self):
        batch=dict(input_values=torch.randn(2,2000),attention_mask=torch.tensor([[1]*2000,[1]*1040+[0]*960]))
        with patch("cue_student.models.AutoModel.from_pretrained",side_effect=lambda *a,**k:FakeHubert()):
            model=CueModel(config()).train();before=copy.deepcopy(model.encoder.state_dict())
            optimizer=build_optimizer(model,config());out=model(batch);out.square().mean().backward();optimizer.step()
            self.assertEqual(tuple(out.shape),(2,17));self.assertFalse(model.encoder.training)
            self.assertTrue(all(p.grad is None and not p.requires_grad for p in model.encoder.parameters()))
            for k,v in before.items():torch.testing.assert_close(v,model.encoder.state_dict()[k],rtol=0,atol=0)
            state=model.checkpoint_state();self.assertFalse(any(k.startswith("encoder.") for k in state))
            restored=CueModel(config());restored.encoder.load_state_dict(before);restored.restore_weights(state)
            model.eval();restored.eval()
            torch.testing.assert_close(model(batch),restored(batch),rtol=0,atol=0)
            cfg=config(temporal_model="none");baseline=CueModel(cfg)
            self.assertIsInstance(baseline.head,TemporalHead);self.assertEqual(tuple(baseline(batch).shape),(2,17))
            with self.assertRaisesRegex(ValueError,"geometry"):CueModel(config(audio_feature_stride_samples=640))
    def test_audio_observation_covers_all_frames(self):
        row=describe(dict(sample_ids=["a"],audio_lengths=torch.tensor([2000])),0,"audio",config())
        self.assertEqual(row["valid_feature_frames"],6);self.assertEqual(row["feature_step_seconds"],.02)
        self.assertEqual(row["model_feature_time_offsets_seconds"],[0.,.02,.04,.06,.08,.1])
        self.assertFalse(row["temporal_truncation"])
    def test_bad_geometry_and_text_rejected(self):
        for cfg in (config(audio_feature_stride_samples=0),config(audio_feature_receptive_field_samples=-1),config(modality="text")):
            with self.assertRaises(ValueError):temporal_spec(cfg)
if __name__=="__main__":unittest.main()
