"""Auxiliary polarity at the last prompt token; no answer-token pooling."""
import torch
import torch.nn.functional as F
from amg_runtime.common import require
def prompt_positions(labels):
 valid=labels.ne(-100);require(bool(valid.any(dim=1).all()),"Missing generation supervision")
 first=valid.long().argmax(dim=1);require(bool((first>0).all()),"No prompt before answer");return first-1
class PolarityLoss:
 def __init__(self,model,optimizer,settings):
  self.model=model;self.weight=float(settings["polarity_loss_weight"]);self.positions=None;self.pooled=None;self.smoke_checked=False
  with torch.random.fork_rng(devices=[torch.cuda.current_device()]):
   torch.manual_seed(4242);torch.cuda.manual_seed_all(4242)
   model.polarity_head=torch.nn.Linear(model.llama_model.config.hidden_size,3).to("cuda:0")
  optimizer.add_param_group(dict(params=list(model.polarity_head.parameters()),lr=settings["learning_rate"],weight_decay=settings["weight_decay"]))
  norm=model.llama_model.get_base_model().model.norm
  self.handle=norm.register_forward_hook(self.capture)
 def capture(self,module,args,output):
  require(self.positions is not None and output.ndim==3,"Unexpected Qwen final hidden shape")
  require(output.shape[0]==len(self.positions) and bool((self.positions<output.shape[1]).all()),"Prompt index mismatch")
  self.pooled=output[torch.arange(output.shape[0],device=output.device),self.positions]
 def forward(self,batch):
  self.positions=prompt_positions(batch["labels"]);self.pooled=None
  generated=self.model(batch)["loss"];require(self.pooled is not None,"Qwen final hidden hook did not fire")
  logits=self.model.polarity_head(self.pooled);target=batch["polarity_labels"];valid=target.ne(-100)
  loss=F.cross_entropy(logits[valid].float(),target[valid],reduction="mean") if bool(valid.any()) else logits.float().sum()*0
  report=dict(generation_loss=float(generated.detach().float()),polarity_loss=float(loss.detach()),polarity_valid_samples=int(valid.sum()),polarity_weight=self.weight,prompt_positions=self.positions.detach().cpu().tolist(),head_logits_shape=list(logits.shape))
  return generated+self.weight*loss,loss,report
 def release(self):self.pooled=None;self.positions=None
