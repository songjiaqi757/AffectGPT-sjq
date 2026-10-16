"""CPU checks for exact shared starts and single-parameter interventions."""
import copy
import json
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
import torch
from torch import nn
from amg.memory import MemoryAdapter
from amg.adapter_state import (INIT_SCHEMA, TARGET_BIAS, adapter_config,
    adapter_state_hashes, apply_value_last_bias_override, file_sha256,
    state_hashes, strict_load_adapter_init)
from amg.train import (ParameterChangeAudit, load_shared_adapter_initialization,
    save_initialization_audit)
from amg.infer import parser as infer_parser

def adapter():
    return MemoryAdapter(d_query=12, d_value=12, d_hidden=8, llm_dim=16,
                         num_tokens=4, num_heads=4)

class Trial(nn.Module):
    def __init__(self):
        super().__init__()
        self.base = nn.Module()
        self.base.llama_model = nn.Module()
        self.base.llama_model.lora_A = nn.Parameter(torch.arange(8).reshape(2,4).float())
        self.memory_adapter = adapter()

class BiasTests(unittest.TestCase):
    def payload(self, model):
        state = {k:v.detach().clone() for k,v in model.memory_adapter.state_dict().items()}
        return {"schema": INIT_SCHEMA, "seed":42, "baseline_sha256":"base",
                "config_sha256":"config", "adapter_config":adapter_config(model.memory_adapter),
                "state_dict":state, **state_hashes(state),
                "baseline_lora_float32":state_hashes({
                    "llama_model.lora_A":model.base.llama_model.lora_A.detach().float()})}
    def load(self, target, path):
        return strict_load_adapter_init(target,path,expected_baseline_sha256="base",
            expected_config_sha256="config",expected_seed=42)
    def test_none_preserves_every_tensor_and_rng(self):
        target=adapter(); before=adapter_state_hashes(target); rng=torch.get_rng_state().clone()
        record=apply_value_last_bias_override(target,"none")
        self.assertEqual(before,adapter_state_hashes(target))
        self.assertTrue(torch.equal(rng,torch.get_rng_state()))
        self.assertFalse(record["applied"])
        self.assertEqual(record["changed_parameters"],[])
    def test_zero_changes_only_target_and_keeps_trainable(self):
        target=adapter(); rng=torch.get_rng_state().clone()
        record=apply_value_last_bias_override(target,"zero")
        self.assertEqual(record["changed_parameters"],[TARGET_BIAS])
        self.assertEqual(record["target_after"]["nonzero"],0)
        self.assertTrue(target.value_projection[2].bias.requires_grad)
        self.assertTrue(torch.equal(rng,torch.get_rng_state()))
    def test_zero_idempotent(self):
        target=adapter(); apply_value_last_bias_override(target,"zero")
        record=apply_value_last_bias_override(target,"zero")
        self.assertEqual(record["changed_parameters"],[])
        self.assertTrue(record["applied"])
    def test_invalid_policy_rejected(self):
        with self.assertRaises(ValueError): apply_value_last_bias_override(adapter(),"scale")
    def test_strict_restore_matches_all_hashes_without_rng(self):
        model=Trial(); payload=self.payload(model)
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/"init.pth"; torch.save(payload,path); target=adapter()
            rng=torch.get_rng_state().clone(); loaded=self.load(target,path)
            self.assertEqual(adapter_state_hashes(target),state_hashes(payload["state_dict"]))
            self.assertTrue(torch.equal(rng,torch.get_rng_state()))
            self.assertEqual(loaded["file_sha256"],file_sha256(path))
    def test_bad_provenance_hash_dimensions_and_finite_rejected(self):
        payload=self.payload(Trial())
        variants=[]
        for key,value in (("seed",43),("baseline_sha256","other"),("config_sha256","other"),
                          ("schema","bad")):
            item=copy.deepcopy(payload); item[key]=value; variants.append(item)
        item=copy.deepcopy(payload); item["adapter_config"]["num_tokens"]=3; variants.append(item)
        item=copy.deepcopy(payload); item["state_dict"][TARGET_BIAS][0]+=1; variants.append(item)
        item=copy.deepcopy(payload); item["state_dict"][TARGET_BIAS][0]=float("nan"); variants.append(item)
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/"bad.pth"
            for item in variants:
                with self.subTest(keys=item.keys()):
                    torch.save(item,path)
                    with self.assertRaises(ValueError): self.load(adapter(),path)
    def test_strict_keys_rejected_even_with_recomputed_hash(self):
        payload=self.payload(Trial()); del payload["state_dict"][TARGET_BIAS]
        payload.update(state_hashes(payload["state_dict"]))
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/"bad.pth";torch.save(payload,path)
            with self.assertRaises(RuntimeError): self.load(adapter(),path)
    def test_matched_initial_audit_and_baseline_lora(self):
        reference=Trial(); payload=self.payload(reference)
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/"shared.pth";torch.save(payload,path); records=[]
            for policy in ("preserve","zero"):
                model=Trial()
                args=SimpleNamespace(adapter_init_state=str(path),value_last_bias_init=policy)
                run={"adapter_init_state":str(path),"adapter_init_state_sha256":file_sha256(path),
                     "base_sha256":"base","config_sha256":"config","seed":42}
                init=load_shared_adapter_initialization(model,args,run)
                snapshot=ParameterChangeAudit(model)
                save_initialization_audit(model,snapshot,run,Path(tmp)/policy,init)
                rec=json.loads((Path(tmp)/policy/"adapter_initialization.json").read_text())
                self.assertTrue(rec["saved_before_optimizer_and_first_update"])
                self.assertEqual(rec["initial_lora_float32"],payload["baseline_lora_float32"])
                records.append(rec)
            a,b=(r["initial_adapter"]["parameter_sha256"] for r in records)
            self.assertEqual([k for k in a if a[k]!=b[k]],[TARGET_BIAS])
            self.assertEqual(records[1]["bias_override"]["target_after"]["nonzero"],0)
    def test_wrong_actual_lora_rejected_before_optimizer(self):
        reference=Trial();payload=self.payload(reference)
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/"shared.pth";torch.save(payload,path);model=Trial()
            args=SimpleNamespace(adapter_init_state=str(path),value_last_bias_init="preserve")
            run={"adapter_init_state":str(path),"adapter_init_state_sha256":file_sha256(path),
                 "base_sha256":"base","config_sha256":"config","seed":42}
            init=load_shared_adapter_initialization(model,args,run)
            with torch.no_grad(): model.base.llama_model.lora_A.add_(1)
            with self.assertRaisesRegex(ValueError,"LoRA"):
                save_initialization_audit(model,ParameterChangeAudit(model),run,Path(tmp)/"out",init)
    def test_opt_in_default_does_nothing(self):
        model=Trial(); before=adapter_state_hashes(model.memory_adapter)
        self.assertIsNone(load_shared_adapter_initialization(model,SimpleNamespace(),{}))
        self.assertEqual(before,adapter_state_hashes(model.memory_adapter))
    def test_infer_flag_explicit_and_default_none(self):
        required=["--config","/c","--baseline-checkpoint","/b","--amg-checkpoint","/a",
                  "--manifest","/m","--output","/o"]
        self.assertEqual(infer_parser().parse_args(required).value_last_bias_override,"none")
        self.assertEqual(infer_parser().parse_args(required+[
            "--value-last-bias-override","zero"]).value_last_bias_override,"zero")

if __name__ == "__main__":
    unittest.main()
