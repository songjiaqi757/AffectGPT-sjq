"""Actual graph paths plus explicit resolution of paths stored in frozen historical records.

No filesystem aliases are created. Hash compatibility is restricted to audited,
byte-for-byte before/after source migrations; sha() itself always remains truthful.
"""
import hashlib,json,os
from pathlib import Path as NativePath
PROJECT_ROOT=NativePath('/ai/sjq/AffectGPT-sjq')
GRAPH_ROOT=PROJECT_ROOT/'graph'
AUDIT=GRAPH_ROOT/'_organization/20261029_no_symlinks'
_MOVED=json.loads((GRAPH_ROOT/'_organization/20261029/plan.json').read_text())['moves']
def resolve_path(value):
    if not isinstance(value,(str,os.PathLike)):
        return value
    raw=os.fspath(value)
    if isinstance(raw,bytes):
        return value
    for old,new in _MOVED.items():
        if raw==old or raw.startswith(old+'/'):
            return new+raw[len(old):]
    for name in ('AffectGPT','dataset'):
        old=str(GRAPH_ROOT/name)
        if raw==old or raw.startswith(old+'/'):
            return str(PROJECT_ROOT/name)+raw[len(old):]
    return raw
class Path(type(NativePath())):
    """Normal native path with explicit legacy-record relocation at construction."""
    def __new__(cls,*args,**kwargs):
        raw=NativePath(*args,**kwargs)
        return super().__new__(cls,resolve_path(raw))
    def __truediv__(self,key):
        return type(self)(super().__truediv__(key))
    def __rtruediv__(self,key):
        return type(self)(super().__rtruediv__(key))
    def joinpath(self,*other):
        return type(self)(super().joinpath(*other))
def sha256_file(path):
    h=hashlib.sha256()
    with NativePath(resolve_path(path)).open('rb') as f:
        for block in iter(lambda:f.read(8*1024*1024),b''):
            h.update(block)
    return h.hexdigest()
def hash_matches(path,expected,actual=None):
    """Accept unchanged content or one exact, archived, audited source relocation."""
    if actual is None:
        actual=sha256_file(path)
    if actual==expected:
        return True
    if not isinstance(path,(str,os.PathLike)):
        return False
    physical=NativePath(resolve_path(path)).absolute()
    try:
        relative=str(physical.relative_to(GRAPH_ROOT))
    except ValueError:
        return False
    manifest=json.loads((AUDIT/'source_migration.json').read_text())
    record=manifest['files'].get(relative)
    if not record or record['before_sha256']!=expected or record['after_sha256']!=actual:
        return False
    if sha256_file(physical)!=actual:
        return False
    return sha256_file(AUDIT/'before'/relative)==expected
