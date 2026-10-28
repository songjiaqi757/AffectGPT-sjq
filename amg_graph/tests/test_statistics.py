import unittest,itertools
import numpy as np
from scipy.stats import fisher_exact
from amg_graph.stats import npmi,table,exact_positive_p,bh,edge_bootstrap
class StatisticsTests(unittest.TestCase):
 def test_reference_independence_and_direction(self):
  self.assertAlmostEqual(float(npmi([25,25,25,25])),0.)
  self.assertGreater(float(npmi([40,10,10,40])),0)
  self.assertLess(float(npmi([10,40,40,10])),0)
 def test_exact_positive_permutation(self):
  x=np.array([1,1,1,1,0,0,0,0],bool);y=np.array([1,1,1,0,1,0,0,0],bool)
  joint=int((x&y).sum());extreme=0;total=0
  for positions in itertools.combinations(range(8),4):
   perm=np.zeros(8,bool);perm[list(positions)]=True
   extreme+=int((x&perm).sum()>=joint);total+=1
  cells=table(x,y,np.ones(8,bool)).astype(int)
  self.assertAlmostEqual(float(exact_positive_p(cells)),extreme/total)
  self.assertAlmostEqual(float(exact_positive_p(cells)),fisher_exact(cells.reshape(2,2),alternative="greater").pvalue)
 def test_group_weights_use_eligible_members(self):
  t=table([1,1,0,0],[1,0,1,0],[1,0,1,1],["a","a","b","b"])
  np.testing.assert_allclose(t,[1,0,.5,.5])
 def test_missing_is_excluded_not_negative(self):
  t=table([1,1,0],[1,0,1],[1,0,1])
  np.testing.assert_array_equal(t,[1,0,1,0])
 def test_fdr_complete_family(self):
  p=np.array([.001,.01,.2,.8]);q=bh(p)
  np.testing.assert_allclose(q,[.004,.02,.26666666666666666,.8])
  self.assertGreater(q[0],bh(p[:1])[0])
 def test_shared_cluster_draws_match_explicit_resampling(self):
  P=np.array([[1,1],[1,0],[0,1],[0,0]],bool);M=np.ones_like(P)
  W=np.array([[2,0,1,1],[0,2,2,0],[1,1,1,1]],np.float32)
  cells,boot,_=edge_bootstrap(P,M,[0],[1],W,chunk=1)
  np.testing.assert_array_equal(cells[0],[1,1,1,1])
  for i,w in enumerate(W):
   rows=np.repeat(np.arange(4),w.astype(int));expected=npmi(table(P[rows,0],P[rows,1],np.ones(len(rows),bool)))
   self.assertAlmostEqual(float(boot[i,0]),float(expected),places=6)
 def test_degenerate_has_no_arbitrary_weight(self):
  self.assertTrue(np.isnan(npmi([0,0,4,6])))
if __name__=="__main__":unittest.main()
