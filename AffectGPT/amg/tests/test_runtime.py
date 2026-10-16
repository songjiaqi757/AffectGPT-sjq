import json
from pathlib import Path
import tempfile
from types import SimpleNamespace as NS
import unittest
from unittest.mock import patch
from amg.runtime import sha256_file, validate_bank_metadata

class RuntimeMetadataTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.bank = self.root / "bank.pt"
        self.bank.write_bytes(b"tiny bank bytes")
        self.manifest = self.root / "main.jsonl"
        self.manifest.write_text('{"name":"one"}\n')
        self.cfg = NS(datasets=NS(mercaptionplus=NS(face_or_frame="multiface_audio_face_text")),
            model=NS(vis_processor=NS(train=NS(n_frms=8)), visual_encoder="CLIP_VIT_LARGE", acoustic_encoder="HUBERT_LARGE"))
        self.meta = {"schema":"amg-m0-bank-v1", "face_or_frame":"multiface_audio_face_text",
            "num_frames":8, "visual_encoder":"CLIP_VIT_LARGE", "acoustic_encoder":"HUBERT_LARGE",
            "records":1, "total_manifest_records":1, "complete":True,
            "manifest_path":str(self.manifest), "manifest_sha256":sha256_file(self.manifest),
            "bank_sha256":sha256_file(self.bank)}
        self.write()
    def tearDown(self):
        self.temp.cleanup()
    def write(self):
        Path(str(self.bank)+".json").write_text(json.dumps(self.meta))
    def test_accepts_complete_matching_space(self):
        self.assertEqual(validate_bank_metadata(self.bank, self.cfg)["records"],1)
    def test_rejects_face_frame_mix(self):
        self.cfg.datasets.mercaptionplus.face_or_frame="multiframe_audio_frame_text"
        with self.assertRaisesRegex(ValueError,"face_or_frame"):
            validate_bank_metadata(self.bank,self.cfg)
    def test_rejects_sampling_change(self):
        self.cfg.model.vis_processor.train.n_frms=4
        with self.assertRaisesRegex(ValueError,"num_frames"):
            validate_bank_metadata(self.bank,self.cfg)
    def test_partial_requires_explicit_smoke_mode(self):
        self.meta["complete"]=False
        self.write()
        with self.assertRaisesRegex(ValueError,"Partial"):
            validate_bank_metadata(self.bank,self.cfg)
        validate_bank_metadata(self.bank,self.cfg,allow_partial=True)
    def test_rejects_modified_bank(self):
        self.bank.write_bytes(b"modified")
        with self.assertRaisesRegex(ValueError,"SHA256"):
            validate_bank_metadata(self.bank,self.cfg)
    def test_rejects_modified_manifest(self):
        self.manifest.write_text('changed')
        with self.assertRaisesRegex(ValueError,"manifest"):
            validate_bank_metadata(self.bank,self.cfg)
    def test_rejects_false_complete_count(self):
        self.meta["records"]=2
        self.write()
        with self.assertRaisesRegex(ValueError,"counts"):
            validate_bank_metadata(self.bank,self.cfg)


    def test_rejects_changed_encoder_weights(self):
        import config
        directory=self.root/"encoder"
        directory.mkdir()
        weight=directory/"model.bin"
        weight.write_bytes(b"old weights")
        self.meta["encoder_artifacts"]={"visual":{"path":str(directory),"files":{
            "model.bin":{"bytes":weight.stat().st_size,"sha256":sha256_file(weight)}}}}
        self.write()
        with patch.dict(config.PATH_TO_VISUAL,{"CLIP_VIT_LARGE":str(directory)}):
            validate_bank_metadata(self.bank,self.cfg)
            weight.write_bytes(b"new weights")
            with self.assertRaisesRegex(ValueError,"artifact changed"):
                validate_bank_metadata(self.bank,self.cfg)

    def test_rejects_encoder_path_change(self):
        self.meta["encoder_artifacts"]={"visual":{"path":str(self.root/"other"),"files":{}}}
        self.write()
        with self.assertRaisesRegex(ValueError,"path changed"):
            validate_bank_metadata(self.bank,self.cfg)

if __name__ == "__main__":
    unittest.main()
