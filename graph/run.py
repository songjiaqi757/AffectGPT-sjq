#!/usr/bin/env python
"""Run graph modules from the actual workspace."""
import argparse,os,runpy,sys
from pathlib import Path
GRAPH=Path(__file__).resolve().parent
sys.path.insert(0,str(GRAPH))
if __name__=='__main__':
    p=argparse.ArgumentParser(description='python graph/run.py MODULE [arguments]')
    p.add_argument('module')
    p.add_argument('arguments',nargs=argparse.REMAINDER)
    args=p.parse_args()
    roots={x.name for x in GRAPH.iterdir() if x.is_dir() and not x.name.startswith('_')}
    if args.module.split('.')[0] not in roots:p.error('Choose a package in graph/paths.json')
    os.chdir(GRAPH)
    os.environ['PYTHONPATH']=os.pathsep.join([str(GRAPH),os.environ.get('PYTHONPATH','')])
    sys.argv=[args.module]+args.arguments
    runpy.run_module(args.module,run_name='__main__',alter_sys=True)
