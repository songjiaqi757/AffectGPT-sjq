"""Bound one new training process; spawned CPU workers never enter the trainer."""
from pathlib import Path
import sys,json,os

def run():
    project=Path("/ai/sjq/AffectGPT-sjq")
    sys.path.insert(0,str(project))
    if "--config" not in sys.argv:raise ValueError("Explicit config required")
    cfg=json.loads(Path(sys.argv[sys.argv.index("--config")+1]).read_text())
    fraction=cfg["cuda_memory_fraction"]
    if not 0<fraction<=0.20:raise ValueError("Each new process is capped at 20% GPU allocator memory")
    if "," in os.environ.get("CUDA_VISIBLE_DEVICES",""):raise ValueError("Exactly one visible GPU required")
    import torch
    torch.cuda.set_device(0)
    torch.cuda.set_per_process_memory_fraction(fraction,0)
    from cue_student.train import main
    main()

if __name__=="__main__":
    run()
