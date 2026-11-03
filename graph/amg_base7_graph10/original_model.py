"""Native AffectGPT sample loop; graph append is its only prompt change."""
import os,sys,copy
from graph_paths import Path
from amg_runtime.common import read,sha,require,canonical
from amg_bcd.policy import format_evidence
ROOT=Path('/ai/sjq/AffectGPT-sjq/graph')
NATIVE_ROOT=ROOT/'AffectGPT'
GENERATION=dict(num_beams=1,temperature=1,do_sample=True,top_p=0.9,max_new_tokens=1200,max_length=2000)
def native_module():
 os.chdir(NATIVE_ROOT);sys.path.insert(0,str(NATIVE_ROOT))
 import inference_hybird
 return inference_hybird
def original_reader(native,d,config):
 reader=native.get_name2cls(d)
 reader.needed_data=reader.get_needed_data('multiface_audio_face_text')
 reader.vis_processor=native.BaseProcessor();reader.img_processor=native.BaseProcessor()
 vis=config['inference'].get('vis_processor');img=config['inference'].get('img_processor')
 from omegaconf import OmegaConf
 if vis is not None:reader.vis_processor=native.registry.get_processor_class(vis['train']['name']).from_config(OmegaConf.create(vis['train']))
 if img is not None:reader.img_processor=native.registry.get_processor_class(img['train']['name']).from_config(OmegaConf.create(img['train']))
 reader.n_frms=config['model']['vis_processor']['train']['n_frms']
 return reader
def get_user_message(dataset_cls,zeroshot,outside_user_message):
 return native_module().get_user_message(dataset_cls,zeroshot,outside_user_message)

def original_sample_with_graph(dataset_cls, chat, face_or_frame, name, graph_text):
    subtitle = dataset_cls.name2subtitle[name]
    sample = {'name': name}
    (video_path, image_path, audio_path, face_npy) = (None, None, None, None)
    if hasattr(dataset_cls, '_get_video_path'):
        video_path = dataset_cls._get_video_path(sample)
    if hasattr(dataset_cls, '_get_audio_path'):
        audio_path = dataset_cls._get_audio_path(sample)
    if hasattr(dataset_cls, '_get_face_path'):
        face_npy = dataset_cls._get_face_path(sample)
    if hasattr(dataset_cls, '_get_image_path'):
        image_path = dataset_cls._get_image_path(sample)
    sample_data = dataset_cls.read_frame_face_audio_text(video_path, face_npy, audio_path, image_path)
    (audio_llms, frame_llms, face_llms, image_llms, multi_llms) = (None, None, None, None, None)
    (audio_hiddens, audio_llms) = chat.postprocess_audio(sample_data)
    (frame_hiddens, frame_llms) = chat.postprocess_frame(sample_data)
    (face_hiddens, face_llms) = chat.postprocess_face(sample_data)
    (_, image_llms) = chat.postprocess_image(sample_data)
    if face_or_frame.startswith('multiface'):
        (_, multi_llms) = chat.postprocess_multi(face_hiddens, audio_hiddens)
    elif face_or_frame.startswith('multiframe'):
        (_, multi_llms) = chat.postprocess_multi(frame_hiddens, audio_hiddens)
    img_list = {}
    img_list['audio'] = audio_llms
    img_list['frame'] = frame_llms
    img_list['face'] = face_llms
    img_list['image'] = image_llms
    img_list['multi'] = multi_llms
    user_message = get_user_message(dataset_cls, True, None)
    user_message = user_message + ('\n' + graph_text if graph_text else '')
    prompt = dataset_cls.get_prompt_for_multimodal(face_or_frame, subtitle, user_message)
    response = chat.answer_sample(prompt=prompt, img_list=img_list, num_beams=1, temperature=1, do_sample=True, top_p=0.9, max_new_tokens=1200, max_length=2000)
    print(response)
    return (response, prompt)

class Predictor:
 def __init__(self,p):
  self.p=p;self.native=native_module();self.config=read(Path(p['training_run'])/'original_config.json')
  from omegaconf import OmegaConf
  self.model_cfg=OmegaConf.create(copy.deepcopy(self.config['model']))
  self.model=None;self.chat=None;self.loaded=None;self.readers={}
 def load(self,spec,job=None):
  if self.loaded==spec['sha256']:return
  require(sha(spec['path'])==spec['sha256'],'Original checkpoint changed')
  self.model_cfg.ckpt_3=spec['path']
  if self.model is None:
   model_cls=self.native.registry.get_model_class(self.model_cfg.arch)
   self.model=model_cls.from_config(self.model_cfg)
  else:
   ckpt=self.native.torch.load(spec['path'],map_location='cpu',weights_only=True)
   self.model.load_state_dict(ckpt['model'],strict=False)
  self.model=self.model.to('cuda:0').eval()
  self.chat=self.native.Chat(self.model,self.model_cfg,device='cuda:0')
  self.loaded=spec['sha256'];self.readers={}
 def predict(self,row,evidence,seed=None,stress=False):
  require(not stress,'Production native adapter does not alter generation for stress probes')
  d=row['dataset']
  if d not in self.readers:self.readers[d]=original_reader(self.native,d,self.config)
  reader=self.readers[d]
  graph,info=format_evidence(evidence,self.chat.tokenizer,512,variant='D')
  response,prompt=original_sample_with_graph(reader,self.chat,'multiface_audio_face_text',row['name'],graph)
  info.update(prompt_id=canonical(prompt),subtitle_truncated=False,generation=GENERATION,randomness_policy='Original script; no added per-sample RNG reseeding',native_script_sha256=self.p['native_script_sha256'])
  return response,info
