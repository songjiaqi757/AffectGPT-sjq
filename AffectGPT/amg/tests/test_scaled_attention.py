import unittest
import torch
from amg.scaled_attention import LogitScaledAttention
from amg.memory import MemoryAdapter, MemoryBank
from amg.model import AMGAffectGPT

class TestScaledAttention(unittest.TestCase):
    def test_scale_one_identical_default(self):
        torch.manual_seed(91)
        a=LogitScaledAttention(16,4,batch_first=True)
        b=torch.nn.MultiheadAttention(16,4,batch_first=True)
        b.load_state_dict(a.state_dict());q=torch.randn(2,3,16);v=torch.randn(2,5,16)
        mask=torch.tensor([[False,False,True,False,False],[False,True,False,False,False]])
        x,w=a(q,v,v,key_padding_mask=mask);y,z=b(q,v,v,key_padding_mask=mask)
        torch.testing.assert_close(x,y,rtol=0,atol=0);torch.testing.assert_close(w,z,rtol=0,atol=0)
    def test_scaled_scores_and_gradients(self):
        torch.manual_seed(92)
        a=LogitScaledAttention(16,4,batch_first=True,logit_scale=7)
        q=torch.randn(2,3,16,requires_grad=True);v=torch.randn(2,5,16,requires_grad=True)
        x,w=a(q,v,v,need_weights=True,average_attn_weights=False)
        ws=a.in_proj_weight.chunk(3);bs=a.in_proj_bias.chunk(3)
        qp=torch.nn.functional.linear(q,ws[0],bs[0]).reshape(2,3,4,4).transpose(1,2)
        kp=torch.nn.functional.linear(v,ws[1],bs[1]).reshape(2,5,4,4).transpose(1,2)
        expected=(qp@kp.transpose(-2,-1)*3.5).softmax(-1)
        torch.testing.assert_close(w,expected)
        x.square().sum().backward()
        for grad in [q.grad,v.grad,a.in_proj_weight.grad]:
            self.assertTrue(torch.isfinite(grad).all());self.assertGreater(float(grad.norm()),0)
    def test_mask_and_checkpoint_identity(self):
        a=LogitScaledAttention(16,4,batch_first=True,logit_scale=10000)
        b=LogitScaledAttention(16,4,batch_first=True)
        b.load_state_dict(a.state_dict(),strict=True)
        q=torch.randn(1,3,16);v=torch.randn(1,5,16);mask=torch.tensor([[False,True,False,True,False]])
        _,w=a(q,v,v,key_padding_mask=mask,average_attn_weights=False)
        self.assertEqual(float(w[:,:,:,1].sum()+w[:,:,:,3].sum()),0)
        with self.assertRaises(ValueError):a(q,v,v,key_padding_mask=torch.ones(1,5,dtype=torch.bool))
    def test_invalid_scale(self):
        for scale in [0,-1,float('nan'),float('inf')]:
            with self.assertRaises(ValueError):LogitScaledAttention(16,4,batch_first=True,logit_scale=scale)
class TestNullPrefix(unittest.TestCase):
    def test_zero_inserts_tokens_while_off_removes(self):
        from amg.tests.test_model import FakeBase, make_samples, make_bank
        torch.manual_seed(94)
        model=AMGAffectGPT(FakeBase(),make_bank(),hidden_dim=16).eval()
        sample=make_samples();model.prefix_control='zero'
        null,_,_=model.prepare(sample);off,_,_=model.prepare(sample,memory_mode='off')
        i=int(sample['memory_insert_indices'][0]);self.assertEqual(int(null.lengths[0]-off.lengths[0]),4)
        self.assertEqual(float(null.inputs_embeds[0,i:i+4].abs().sum()),0)
        self.assertTrue(bool(null.attention_mask[0,i:i+4].all()))
    def test_bank_mean_removes_neighbor_identity(self):
        from amg.tests.test_model import FakeBase, make_samples, make_bank
        torch.manual_seed(95)
        model=AMGAffectGPT(FakeBase(),make_bank(),hidden_dim=16).eval();model.prefix_control='bank_mean'
        seen=[]
        handle=model.memory_adapter.register_forward_pre_hook(lambda m,args: seen.append(args[1].detach().clone()))
        model.prepare(make_samples());handle.remove()
        expected=model.bank.features.mean(0).view(1,1,-1).expand_as(seen[0])
        torch.testing.assert_close(seen[0],expected)
if __name__=='__main__':unittest.main()
