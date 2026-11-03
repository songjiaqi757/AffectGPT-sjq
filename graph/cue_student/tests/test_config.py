import json,tempfile,unittest
from graph_paths import Path
from unittest.mock import patch
import torch
from cue_student.common import PROJECT,load_config
from cue_student.models import CueModel,build_optimizer

class ConfigParsingTests(unittest.TestCase):
    def test_all_json_configs_preserve_numeric_learning_rates(self):
        for name in ("text","audio","visual","visual_temporal"):
            path=PROJECT/"cue_student/configs"/(name+".json")
            original=json.loads(path.read_text());cfg=load_config(path)
            self.assertEqual(cfg["encoder_lr"],original["encoder_lr"])
            self.assertIsInstance(cfg["encoder_lr"],(int,float))
            self.assertIsInstance(cfg["head_lr"],(int,float))

    def test_full_encoder_optimizer_scheduler_accepts_scientific_lr(self):
        class Encoder(torch.nn.Module):
            def __init__(self):
                super().__init__();self.weight=torch.nn.Parameter(torch.ones(4))
                self.config=type("Cfg",(),{"hidden_size":4})()
        cfg=load_config(PROJECT/"cue_student/configs/text.json")
        with patch("cue_student.models.AutoModel.from_pretrained",return_value=Encoder()):
            model=CueModel(cfg);optimizer=build_optimizer(model,cfg)
            scheduler=torch.optim.lr_scheduler.LambdaLR(optimizer,lambda step:.5)
        self.assertIn(cfg["encoder_lr"]*.5,scheduler.get_last_lr())
        self.assertIn(cfg["head_lr"]*.5,scheduler.get_last_lr())

    def test_quoted_learning_rate_rejected_early(self):
        with tempfile.TemporaryDirectory(dir=PROJECT/"cue_student/artifacts") as tmp:
            path=Path(tmp)/"bad.json"
            cfg=json.loads((PROJECT/"cue_student/configs/text.json").read_text())
            cfg["encoder_lr"]="2e-05";path.write_text(json.dumps(cfg))
            with self.assertRaisesRegex(ValueError,"encoder_lr must be a finite number"):load_config(path)

    def test_yaml_scientific_number_and_actionable_error(self):
        with tempfile.TemporaryDirectory(dir=PROJECT/"cue_student/artifacts") as tmp:
            path=Path(tmp)/"cfg.yaml"
            source="modality: text\nmodel_dir: unused\nencoder_lr: "
            path.write_text(source+"2.0e-5\n");self.assertEqual(load_config(path)["encoder_lr"],2e-5)
            path.write_text(source+"2e-5\n")
            with self.assertRaisesRegex(ValueError,"2.0e-5"):load_config(path)

if __name__=="__main__":unittest.main()
