import copy,json,sqlite3,unittest
from concurrent.futures import ThreadPoolExecutor
from functools import partial
import numpy as np
from cue_student.common import PROJECT
from cue_student.data import Release
from cue_student.prepare import verify_member,RUN

class ParallelPreparationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.release=Release(PROJECT/"cue_student/artifacts/smoke_release_v1")
        db=sqlite3.connect("file:"+str(RUN/"tasks.sqlite3")+"?mode=ro",uri=True)
        cls.tasks={(sid,m):state for sid,m,state in db.execute("select sid,modality,state from tasks")};db.close()
        cls.index={r["sample_id"]:i for i,r in enumerate(cls.release.rows)}

    def verify(self,rows,states,workers):
        function=partial(verify_member,run=RUN,ontology=self.release.ontology,tasks=self.tasks,all_index=self.index,state_all=states)
        with ThreadPoolExecutor(max_workers=workers) as pool:return list(pool.map(function,rows))

    def test_serial_parallel_matches_frozen_release(self):
        one=self.verify(copy.deepcopy(self.release.rows),self.release.states,1)
        eight=self.verify(copy.deepcopy(self.release.rows),self.release.states,8)
        self.assertEqual(one,eight)
        self.assertEqual([r for r,_,_ in eight],self.release.rows)
        self.assertEqual(sum(n for _,n,_ in eight),self.release.manifest["verified_annotation_records"])
        self.assertEqual(sum(n for _,_,n in eight),self.release.manifest["verified_original_media"])

    def test_parallel_annotation_mismatch_still_raises(self):
        states=self.release.states.copy();states[0,0]=(int(states[0,0])+1)%5
        with self.assertRaisesRegex(ValueError,"Annotation/CSV state mismatch"):
            self.verify(copy.deepcopy(self.release.rows[:2]),states,8)

if __name__=="__main__":unittest.main()
