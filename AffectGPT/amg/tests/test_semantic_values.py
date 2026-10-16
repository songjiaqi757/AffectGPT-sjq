import unittest,tempfile
from pathlib import Path
import torch
from amg.semantic_values import SemanticValues
from amg.memory import MemoryBank
from amg.model import AMGAffectGPT

def make_values(ids=None,groups=None):
    ids=ids or [f'm{i}' for i in range(8)];groups=groups or ids
    n=len(ids);x=torch.nn.functional.normalize(torch.randn(n,1024),dim=-1);v=torch.ones(n,dtype=torch.bool)
    return SemanticValues(ids,groups,x,x.flip(0),v,v,bank_sha256='b',fit_sha256='f')

class SemanticTests(unittest.TestCase):
    def test_content_controls_and_zero_capacity(self):
        m=make_values();neighbors=[['m1','m2',None]]
        zero,src=m.lookup(neighbors,['q'],['qg'],'av_only');self.assertEqual(zero.shape,(1,3,1024));self.assertEqual(float(zero.norm()),0);self.assertEqual(src,[[None]*3])
        text,src=m.lookup(neighbors,['q'],['qg'],'subtitle');torch.testing.assert_close(text[0,0],m.features['subtitle'][1]);self.assertEqual(src[0][0],'m1');self.assertEqual(float(text[0,2].norm()),0)
    def test_no_query_or_same_group_caption_after_shuffle(self):
        m=make_values()
        for q in m.ids:
            neighbors=[[n for n in m.ids if n!=q]]
            x,ids=m.lookup(neighbors,[q],[q],'shuffled_caption')
            self.assertNotIn(q,ids[0])
            for original,donor in zip(neighbors[0],ids[0]):self.assertNotEqual(original,donor)
        _,a=m.lookup([['m1','m2']],['q'],['qg'],'shuffled_caption');_,b=m.lookup([['m1','m2']],['q'],['qg'],'shuffled_caption');self.assertEqual(a,b)
    def test_caption_self_lookup_rejected(self):
        m=make_values()
        with self.assertRaises(ValueError):m.lookup([['m0']],['m0'],['m0'],'caption')
    def test_missing_text_stays_missing(self):
        m=make_values();m.valid['subtitle'][1]=False;m.features['subtitle'][1].zero_()
        x,ids=m.lookup([['m1']],['q'],['qg'],'subtitle');self.assertEqual(float(x.norm()),0);self.assertEqual(ids,[[None]])
    def test_shape_and_nonfinite_rejected(self):
        x=torch.zeros(4,1024);x[0,0]=float('nan')
        with self.assertRaises(ValueError):SemanticValues(list('abcd'),list('abcd'),x,x,torch.ones(4,dtype=torch.bool),torch.ones(4,dtype=torch.bool),bank_sha256='b',fit_sha256='f')
    def test_model_same_candidates_capacity_and_tokens(self):
        from amg.tests.test_model import FakeBase,make_samples,make_bank
        bank=make_bank();m=make_values(bank.clip_ids,bank.group_ids)
        model=AMGAffectGPT(FakeBase(),bank,hidden_dim=16,semantic_values=m,semantic_content='av_only').eval()
        sample=make_samples();sample['clip_ids']=['unseen'];sample['group_ids']=['unseen-group']
        a,ra,_=model.prepare(sample);count=sum(p.numel() for p in model.parameters() if p.requires_grad)
        model.semantic_content='caption';b,rb,_=model.prepare(sample)
        self.assertEqual(ra.ids,rb.ids);self.assertEqual(a.lengths.tolist(),b.lengths.tolist())
        self.assertEqual(count,sum(p.numel() for p in model.parameters() if p.requires_grad));self.assertEqual(model.memory_adapter.d_value,2816)
        self.assertGreater(float((a.inputs_embeds-b.inputs_embeds).abs().sum()),0)
if __name__=='__main__':unittest.main()
