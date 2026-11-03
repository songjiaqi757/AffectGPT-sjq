#!/usr/bin/env python
"""Run relocated graph packages with their original module names."""
import argparse,os,runpy,sys
from pathlib import Path
GRAPH=Path(__file__).resolve().parent
ROOT=GRAPH.parent
sys.path[:0]=[str(GRAPH),str(ROOT)]
if __name__=='__main__':
    p=argparse.ArgumentParser(description='Run graph module: python graph/run.py MODULE [arguments]')
    p.add_argument('module')
    p.add_argument('arguments',nargs=argparse.REMAINDER)
    args=p.parse_args()
    if args.module.split('.')[0] not in ['amg_188_audit', 'amg_188_path_noemotion', 'amg_bcd', 'amg_bcd_polarity', 'amg_bcd_polarity_oof', 'amg_d_graph_compare', 'amg_d_multistart10', 'amg_finetune', 'amg_finetune_nogc', 'amg_graph', 'amg_graph10', 'amg_graph10_rebuild', 'amg_inference', 'amg_method_decision', 'amg_polarity', 'amg_prompt_ablation', 'amg_prompt_ablation_g', 'amg_repair_cpu', 'amg_runtime', 'amg_validation', 'analysis_reports', 'appraisal_annotation', 'cue_annotation', 'cue_student', 'data_migrations', 'emotion_nodes', 'human_annotation']:
        p.error('Choose a graph package listed in graph/paths.json')
    os.chdir(ROOT)
    os.environ['PYTHONPATH']=os.pathsep.join([str(GRAPH),str(ROOT),os.environ.get('PYTHONPATH','')])
    sys.argv=[args.module]+args.arguments
    runpy.run_module(args.module,run_name='__main__',alter_sys=True)
