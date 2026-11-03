"""Execute exact lightweight upstream tokenizer/prompt methods without loading model weights."""
import ast,types
from transformers import AutoTokenizer
from .common import *
MARKERS=['<ImageHere>','<AudioHere>','<FrameHere>','<FaceHere>','<MultiHere>']
def extract(path,name,klass=None):
 tree=ast.parse(Path(path).read_text());body=tree.body
 if klass:body=next(n for n in body if isinstance(n,ast.ClassDef) and n.name==klass).body
 fn=next(n for n in body if isinstance(n,ast.FunctionDef) and n.name==name);return ast.Module(body=[fn],type_ignores=[])
def actual_interfaces():
 cfg=types.SimpleNamespace(PATH_TO_LLM={'Qwen25':str(PROJECT/'AffectGPT/models/Qwen2.5-7B-Instruct')},**dict(zip(['DEFAULT_IMAGE_PATCH_TOKEN','DEFAULT_AUDIO_PATCH_TOKEN','DEFAULT_FRAME_PATCH_TOKEN','DEFAULT_FACE_PATCH_TOKEN','DEFAULT_MULTI_PATCH_TOKEN'],MARKERS)))
 path=PROJECT/'AffectGPT/my_affectgpt/models/tokenizer.py';ns=dict(AutoTokenizer=AutoTokenizer,config=cfg);exec(compile(extract(path,'load_tokenizer_from_LLM'),str(path),'exec'),ns);tokenizer=ns['load_tokenizer_from_LLM']('Qwen25')
 readerpath=PROJECT/'AffectGPT/my_affectgpt/datasets/datasets/base_dataset.py';ns={};exec(compile(extract(readerpath,'get_prompt_for_multimodal','BaseDataset'),str(readerpath),'exec'),ns);Reader=type('ActualUpstreamPromptReader',(),dict(get_prompt_for_multimodal=ns['get_prompt_for_multimodal']));reader=Reader()
 chatpath=PROJECT/'AffectGPT/my_affectgpt/conversation/conversation_video.py';ns=dict(config=cfg);exec(compile(extract(chatpath,'replace_token_for_multimodal','Chat'),str(chatpath),'exec'),ns);Chat=type('ActualUpstreamTokenExpansion',(),dict(replace_token_for_multimodal=ns['replace_token_for_multimodal']));chat=Chat();chat.tokenizer=tokenizer;chat.num_video_query_token=1;chat.num_audio_query_token=1;chat.num_multi_query_token=1;chat.num_image_query_token=1
 metadata=dict(method='Exact upstream function ASTs compiled in isolated namespaces; no model weights or generate() loaded',tokenizer_source=str(path),tokenizer_source_sha256=sha(path),prompt_source=str(readerpath),prompt_source_sha256=sha(readerpath),chat_source=str(chatpath),chat_source_sha256=sha(chatpath),assets={f.name:sha(f) for f in (PROJECT/'AffectGPT/models/Qwen2.5-7B-Instruct').iterdir() if f.is_file() and f.suffix in ('.json','.txt') and not f.name.startswith('model')},special_token_ids={m:tokenizer.convert_tokens_to_ids(m) for m in MARKERS})
 return tokenizer,reader,chat,metadata
