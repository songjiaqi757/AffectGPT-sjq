import copy,json,sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from annotate import DIMS,validate

def fixture():
    return dict(event_context='An event',dimensions=[dict(dimension_id=d,state=None,valid=False,
        evidence='',evidence_modalities=[],unknown_reason='insufficient_evidence') for d in DIMS])
class SchemaTests(unittest.TestCase):
    def test_invalid_is_distinct_from_negative(self):
        self.assertEqual(validate(json.dumps(fixture())),fixture())
    def test_valid_requires_evidence_and_correct_state(self):
        for did,states in DIMS.items():
            for state in states:
                obj=fixture();d=next(x for x in obj['dimensions'] if x['dimension_id']==did)
                d.update(valid=True,state=state,evidence='Observable evidence',evidence_modalities=['audio','video'],unknown_reason=None)
                self.assertEqual(validate(json.dumps(obj)),obj)
    def test_missing_and_duplicate_dimensions_rejected(self):
        for missing in [True,False]:
            obj=fixture()
            if missing:obj['dimensions'].pop()
            else:obj['dimensions'][0]=obj['dimensions'][1]
            with self.assertRaises(AssertionError):validate(json.dumps(obj))
    def test_invalid_state_and_evidence_combinations_rejected(self):
        for field,value in [('state','unknown'),('valid',1),('evidence','invented'),
                ('unknown_reason','undocumented'),('evidence_modalities',['text'])]:
            obj=fixture();obj['dimensions'][0][field]=value
            with self.assertRaises(AssertionError):validate(json.dumps(obj))
    def test_person_identification_fields_rejected(self):
        for field in ['focus_person','person_role','person_identity']:
            obj=fixture();obj[field]='Forbidden'
            with self.assertRaises(AssertionError):validate(json.dumps(obj))
    def test_new_reasons_accepted_and_old_focus_reasons_rejected(self):
        for reason in ['state_not_explicitly_supported','evidence_indirect_only','appraisal_holder_unclear']:
            obj=fixture();obj['dimensions'][0]['unknown_reason']=reason
            self.assertEqual(validate(json.dumps(obj)),obj)
        for reason in ['focus_person_ambiguous','focus_person_not_identifiable']:
            obj=fixture();obj['dimensions'][0]['unknown_reason']=reason
            with self.assertRaises(AssertionError):validate(json.dumps(obj))
    def test_duplicate_json_keys_rejected(self):
        with self.assertRaises(ValueError):validate('{"focus_person":{},"focus_person":{}}')
    def test_wrong_dimension_state_rejected(self):
        obj=fixture();obj['dimensions'][0].update(valid=True,state='AAG_SELF',evidence='x',
            evidence_modalities=['text'],unknown_reason=None)
        with self.assertRaises(AssertionError):validate(json.dumps(obj))
    def test_no_evidence_for_valid_state_rejected(self):
        for modalities in [[],['visual'],['text','text']]:
            obj=fixture();obj['dimensions'][0].update(valid=True,state='AGR_RELEVANT',evidence='x',
                evidence_modalities=modalities,unknown_reason=None)
            with self.assertRaises(AssertionError):validate(json.dumps(obj))
if __name__=='__main__':unittest.main()
