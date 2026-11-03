import sys,unittest
from graph_paths import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from original_adapter import Resources
from build import OriginalMapper,node_id
class ExactOriginalTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.resources=Resources();cls.mapper=OriginalMapper(cls.resources)
 def test_original_anxiety_mapping_is_preserved(self):
  result=self.mapper.sample(['anxiety'])
  self.assertEqual(result['canonical_labels'],['fear'])
  self.assertEqual(result['term_trace'][0]['selected_format'],'anxiety')
  self.assertTrue(result['contains_lexicographic_choice'])
 def test_original_unmapped_label_is_dropped_but_audited(self):
  result=self.mapper.sample(['concern','pessimism'])
  self.assertEqual(result['canonical_labels'],['care'])
  self.assertEqual(result['dropped_terms'],['pessimism'])
  self.assertEqual(result['raw_labels'],['concern','pessimism'])
 def test_empty_stays_empty_and_neutral_not_invented(self):
  result=self.mapper.sample([])
  self.assertEqual(result['canonical_labels'],[])
  self.assertTrue(result['empty_after_mapping'])
  self.assertEqual(self.mapper.sample(['neutral'])['dropped_terms'],['neutral'])
 def test_order_and_duplicate_independence(self):
  a=self.mapper.sample(['happy','sad','happy'])
  b=self.mapper.sample(['sad','happy'])
  self.assertEqual(a['canonical_labels'],b['canonical_labels'])
  self.assertEqual(a['wheel_views'],b['wheel_views'])
 def test_five_parallel_wheels_not_one_parent(self):
  result=self.mapper.sample(['anxiety','joy'])
  self.assertEqual(set(result['wheel_views']),{'wheel1','wheel2','wheel3','wheel4','wheel5'})
  for view in result['wheel_views'].values():self.assertEqual(set(view),{'level1','level2'})
 def test_content_ids_stable_without_vocabulary_order(self):
  self.assertEqual(node_id('care'),node_id('care'))
  self.assertNotEqual(node_id('care'),node_id('fear'))
if __name__=='__main__':unittest.main()
