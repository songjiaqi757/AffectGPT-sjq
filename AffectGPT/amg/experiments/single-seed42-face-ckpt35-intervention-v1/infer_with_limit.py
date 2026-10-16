"""Apply a memory allocator cap to this inference process only."""
import sys
sys.path.insert(0, "/ai/sjq/AffectGPT-sjq/AffectGPT")
import torch
torch.cuda.set_per_process_memory_fraction(0.35, device=0)
from amg.infer import main
raise SystemExit(main())
