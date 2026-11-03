from graph_paths import resolve_path as _graph_resolve_path
from graph_paths import Path
import gc,json
import torch
from cue_student.common import PROJECT,atomic_json,move_batch,seed_all,code_hash
from cue_student.data import Release,CueDataset,make_collator
from cue_student.models import CueModel,build_optimizer
from cue_student.objectives import masked_bce_sum
seed_all(42);torch.set_num_threads(8);torch.cuda.set_device(1)
checkpoint=PROJECT/"cue_student/artifacts/integration_20261020_123431/text_resume/last.pt"
old=torch.load(_graph_resolve_path(checkpoint), map_location='cpu', weights_only=False)
cfg=dict(old["config"],encoder_train="full",encoder_lr=2e-5,head_lr=1e-4)
release=Release(PROJECT/"cue_student/artifacts/smoke_release_v1")
ds=CueDataset(release,"text","pseudo_train",training=True)
batch=move_batch(make_collator(cfg)([ds[0]]),"cuda:1")
model=CueModel(cfg).to("cuda:1");model.restore_weights(old["model"],initializing=True)
optimizer=build_optimizer(model,cfg);model.train()
token_id=int(batch["input_ids"][0,1]);before=model.encoder.embeddings.word_embeddings.weight[token_id].detach().clone()
optimizer.zero_grad(set_to_none=True)
loss,n=masked_bce_sum(model(batch),batch["targets"],batch["label_mask"])
(loss/n).backward()
norm=torch.nn.utils.clip_grad_norm_([p for p in model.parameters() if p.requires_grad],1.)
assert torch.isfinite(norm)
assert torch.isfinite(model.encoder.embeddings.word_embeddings.weight.grad).all()
optimizer.step()
change=float((model.encoder.embeddings.word_embeddings.weight[token_id]-before).abs().max())
assert change>0
report=dict(passed=True,scope="in-memory full text encoder optimizer smoke step; no model weights saved",device="cuda:1",
            optimizer_steps=1,loss=float(loss.detach()/n),valid_labels=n,encoder_embedding_update_max_abs=change,
            optimizer_groups=[dict(lr=g["lr"],weight_decay=g["weight_decay"],parameter_tensors=len(g["params"])) for g in optimizer.param_groups],
            init_from_frozen_head_passed=True,final_code_hash=code_hash())
out=PROJECT/"cue_student/artifacts/full_text_optimizer_test.json";atomic_json(out,report)
print(json.dumps(report),flush=True)
del optimizer,model;gc.collect();torch.cuda.empty_cache()
