import math,unittest
from amg_validation.evaluation import state_metrics,appraisal_metrics,emotion_case,rerank,feature_prediction
from amg_validation.finalize import selection_key
class MetricTests(unittest.TestCase):
 def test_invalid_appraisal_is_unscorable_not_negative(self):
  m=state_metrics(["a",None,"b"],["a","a",None],["a","b"])
  self.assertEqual(m["valid_reference"],2);self.assertEqual(m["states"]["a"]["fp"],0);self.assertEqual(m["unscorable_predictions"],1);self.assertAlmostEqual(m["macro_f1"],.5)
 def test_abstention_on_valid_reference_is_a_miss(self):
  m=state_metrics(["a","a"],[None,"a"],["a"])
  self.assertEqual(m["states"]["a"]["fn"],1);self.assertAlmostEqual(m["macro_f1"],2/3)
 def test_unsupported_state_is_reported_undefined(self):
  m=state_metrics(["a"],["b"],["a","b"])
  self.assertIsNone(m["states"]["b"]["f1"]);self.assertIsNone(m["states"]["b"]["precision"]);self.assertEqual(m["macro_f1"],0.)
 def test_macro_states_equal_weight(self):
  m=state_metrics(["a","a","b"],["a","a",None],["a","b"])
  self.assertEqual(m["macro_f1"],.5)
 def result(self,ids):
  return dict(query_cues=[],appraisal_dimensions=[],emotion_candidates=[{"emotion_id":e} for e in ids],explanation_paths=[],available_candidate_count=len(ids),available_selected_path_count=0,query_coverage=0.)
 def test_f1_penalizes_extra_incorrect_candidates(self):
  ref=dict(emotion_ids=["a"],emotion_valid=True)
  one=emotion_case(ref,self.result(["a"]));many=emotion_case(ref,self.result(["a","b","c"]))
  self.assertEqual(one[2],1.);self.assertEqual(many[1],1.);self.assertEqual(many[2],.5)
 def test_invalid_emotion_reference_not_a_negative(self):
  ref=dict(emotion_ids=[],emotion_valid=False);m=emotion_case(ref,self.result(["a"]))
  self.assertTrue(all(math.isnan(x) for x in m[:3]))
 def test_empty_query_is_miss_on_valid_emotion(self):
  self.assertEqual(emotion_case(dict(emotion_ids=["a"],emotion_valid=True),self.result([]))[:3],[0.,0.,0.])
 def test_direct_fallback_is_not_scaled_by_lambda(self):
  base=dict(sample_id="x",query_cues=[],appraisal_dimensions=[],candidate_audit=[dict(emotion_id="e",association_score=.4,direct_available=True,two_hop_available=False,direct_score=.4,two_hop_score=None)],path_audit=[],coverage={"query":1.})
  for lam in [0.,.5,1.]:self.assertEqual(rerank(base,lam,3,5)["emotion_candidates"][0]["association_score"],.4)
 def test_two_available_branches_use_registered_fusion(self):
  base=dict(sample_id="x",query_cues=[],appraisal_dimensions=[],candidate_audit=[dict(emotion_id="e",association_score=.4,direct_available=True,two_hop_available=True,direct_score=.2,two_hop_score=.6)],path_audit=[],coverage={"query":1.})
  self.assertAlmostEqual(rerank(base,.25,3,5)["emotion_candidates"][0]["association_score"],.5)
 def test_feature_threshold_gate_is_dimension_specific(self):
  f=dict(dimension_evidence={"d":.2},dimension_coverage={"d":.8},state_support={"a":.15,"b":.05},state_coverage={"a":.6,"b":.8})
  self.assertEqual(feature_prediction(f,{"d":["a","b"]},{"d":.1},.5),{"d":"a"})
  self.assertEqual(feature_prediction(f,{"d":["a","b"]},{"d":.3},.5),{"d":None})
 def test_score_tie_uses_node_id(self):
  f=dict(dimension_evidence={"d":.2},dimension_coverage={"d":1.},state_support={"b":.1,"a":.1},state_coverage={"b":1.,"a":1.})
  self.assertEqual(feature_prediction(f,{"d":["b","a"]},{"d":0.},0.),{"d":"a"})
 def test_grid_ties_prefer_smaller_k_then_conservative_support(self):
  base=dict(metrics=dict(objective=.2,emotion_valid_query_coverage=1.,appraisal_valid_dimension_coverage=.8),emotion_top_k=3,minimum_coverage=0.,query_min_support_groups=5,query_path_min_joint_support_groups=0,direct_two_hop_lambda=.5)
  more=dict(base,emotion_top_k=5);strict=dict(base,query_min_support_groups=20,query_path_min_joint_support_groups=5)
  self.assertLess(selection_key(base),selection_key(more));self.assertLess(selection_key(strict),selection_key(base))
if __name__=="__main__":unittest.main()
