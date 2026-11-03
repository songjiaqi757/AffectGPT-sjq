"""Ordered, deterministic CPU preprocessing with optional spawn workers and prefetch."""
import torch
from torch.utils.data import DataLoader

PERFORMANCE_KEYS=frozenset(("num_workers","pin_memory","prefetch_factor","persistent_workers","decode_threads"))

def initialize_worker(worker_id):
    torch.set_num_threads(1)
    try:
        from threadpoolctl import threadpool_limits
        threadpool_limits(1)
    except ImportError:
        pass

def loader_for(dataset,batches,collator,cfg):
    workers=cfg.get("num_workers",0)
    if type(workers) is not int or workers<0:raise ValueError("num_workers must be a nonnegative integer")
    generator=torch.Generator().manual_seed(cfg.get("seed",42)+9000)
    kwargs={}
    if workers:
        prefetch=cfg.get("prefetch_factor",2)
        if type(prefetch) is not int or prefetch<1:raise ValueError("prefetch_factor must be positive")
        kwargs.update(multiprocessing_context="spawn",worker_init_fn=initialize_worker,
                      prefetch_factor=prefetch,persistent_workers=cfg.get("persistent_workers",False))
    return DataLoader(dataset,batch_sampler=batches,collate_fn=collator,num_workers=workers,
                      generator=generator,pin_memory=cfg.get("pin_memory",False),**kwargs)
