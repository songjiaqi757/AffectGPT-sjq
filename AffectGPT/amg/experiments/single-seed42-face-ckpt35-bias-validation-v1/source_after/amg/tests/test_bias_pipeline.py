"""CPU checks for matched-start rejection and bounded stage orchestration."""
import copy
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from amg.run_bias_validation import BiasExperiment, compare_initializations

def records():
    shared={"file_sha256":"file","state_sha256":"normal",
            "baseline_lora_float32":{"state_sha256":"lora","parameter_sha256":{"lora":"l"}}}
    a={"policy":"preserve","shared":{"file_sha256":"file"},
       "initial_adapter":{"state_sha256":"normal","parameter_sha256":{
           "other":"same","value_projection.2.bias":"nonzero"}},
       "initial_lora_float32":copy.deepcopy(shared["baseline_lora_float32"]),
       "saved_before_optimizer_and_first_update":True}
    b=copy.deepcopy(a);b["policy"]="zero"
    b["initial_adapter"]={"state_sha256":"zero","parameter_sha256":{
        "other":"same","value_projection.2.bias":"zero"}}
    b["bias_override"]={"target_after":{"nonzero":0}}
    return a,b,shared

class PipelineTests(unittest.TestCase):
    def test_exact_matching_pair_accepted(self):
        self.assertTrue(compare_initializations(*records())["same_baseline_lora"])
    def test_extra_changed_parameter_rejected(self):
        a,b,s=records();b["initial_adapter"]["parameter_sha256"]["other"]="different"
        with self.assertRaises(RuntimeError): compare_initializations(a,b,s)
    def test_baseline_or_initial_timing_mismatch_rejected(self):
        for key,value in (("initial_lora_float32",{}),("saved_before_optimizer_and_first_update",False)):
            a,b,s=records();b[key]=value
            with self.subTest(key=key):
                with self.assertRaises(RuntimeError): compare_initializations(a,b,s)
    def test_stage_a_negative_scores_do_not_skip_matched_training(self):
        with tempfile.TemporaryDirectory() as tmp:
            experiment=object.__new__(BiasExperiment)
            experiment.output=Path(tmp);experiment.state={};experiment.interrupted_signal=None
            events=[]
            experiment.validate=lambda:{"validated":True}
            experiment.event=lambda *args,**kwargs:events.append(args)
            experiment.score_refs=lambda:events.append(("refs",))
            experiment.paired=lambda pairs:events.append(("pairs",len(pairs)))
            experiment.check_starts=lambda **kwargs:None
            experiment.finish=lambda:events.append(("finish",))
            experiment.stop_children=lambda:events.append(("stop",))
            experiment.intervention=lambda mode,gpu:events.append(("A",mode,gpu))
            experiment.train_arm=lambda arm,gpu:events.append(("B",arm,gpu))
            experiment.gpus=(0,1);experiment.stop_event=None
            def queue(items,gpus,fn,*unused):
                for item,gpu in zip(items,gpus): fn(item,gpu)
            with patch("amg.run_bias_validation.run_gpu_queue",side_effect=queue), \
                 patch("amg.run_bias_validation.exposure_signature",return_value=("equal",4002)):
                self.assertEqual(experiment.run(),0)
            self.assertEqual([x[1] for x in events if x[0]=="B"],["control","zero_init"])
            self.assertIn(("finish",),events)
            self.assertNotIn(("stop",),events)
    def test_technical_failure_stops_and_records_failure(self):
        with tempfile.TemporaryDirectory() as tmp:
            experiment=object.__new__(BiasExperiment)
            experiment.output=Path(tmp);experiment.state={};experiment.interrupted_signal=None
            def fail(): raise RuntimeError("locked artifact changed")
            experiment.validate=fail;stopped=[]
            experiment.stop_children=lambda:stopped.append(True)
            experiment.event=lambda *args,**kwargs:None
            self.assertEqual(experiment.run(),1)
            self.assertTrue(stopped)
            self.assertEqual(experiment.state["status"],"failed")
            self.assertIn("locked artifact changed",(Path(tmp)/"FAILURE.txt").read_text())

if __name__=="__main__": unittest.main()
