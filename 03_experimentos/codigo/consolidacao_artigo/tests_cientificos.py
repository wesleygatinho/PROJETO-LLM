"""Casos adversos, resultados calculáveis à mão e integridade independente de ordem."""
from comum import *
import unittest
class ScientificInvariants(unittest.TestCase):
    def test_auc_ties_known(self):
        self.assertEqual(auc([1,0,1,0],[1,1,0,0]),.5)
        self.assertEqual(auc([1,0],[4,1]),1)
    def test_strict_threshold(self):
        m=metrics([1,0,1],[2,2,3],2)
        self.assertEqual((m['tp'],m['fp'],m['fn'],m['tn']),(1,0,1,1))
    def test_calibration_tied_values(self):
        t,f=best_f1([1,0,0],[2,1,1])
        self.assertLess(t,2);self.assertEqual(f,1);self.assertEqual(metrics([1,0,0],[2,1,1],t)['f1'],1)
    def test_fpr_bound_in_dev_with_ties(self):
        y=np.r_[np.zeros(1000),np.ones(10)];s=np.r_[np.repeat(3.,8),np.zeros(992),np.ones(10)*4]
        t=fpr_threshold(y,s);self.assertEqual(t,3);self.assertEqual(metrics(y,s,t)['fpr'],0)
    def test_order_and_categories_not_same(self):
        p=np.array([[0,1],[2,3]])
        r=paired([2,1,3,3],p,0)
        self.assertEqual(r['ordenacao'],.75);self.assertEqual(r['P_V'],2);self.assertEqual(r['P_C'],0)
    def test_identity_order_and_duplicate(self):
        d=[dict(idx=i,project='p',commit_id='c',target=i%2) for i in range(2)]
        l=[dict(pos=i,**r) for i,r in enumerate(d)]
        self.assertEqual(verify_alignment(l[::-1],d),l)
        with self.assertRaises(ValueError):verify_alignment([l[0],l[0]],d)
    def test_no_fallback_pairs(self):
        d=[dict(idx=i,project='p',commit_id='c',target=1) for i in range(2)]
        with self.assertRaises(ValueError):official_pairs(d)
    def test_documented_official_reuse_only(self):
        d=[dict(idx=i,project='p',commit_id='c',target=t,func=str(i)) for i,t in [(1,1),(2,0),(3,1),(2,0)]]
        with self.assertRaises(ValueError):official_pairs(d)
        self.assertEqual(len(official_pairs(d,True)),2)
        d[-1]['func']='different'
        with self.assertRaises(ValueError):official_pairs(d,True)
if __name__=='__main__':unittest.main()
