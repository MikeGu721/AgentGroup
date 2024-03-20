
import json
import requests

from transformers import AutoTokenizer, AutoModel,AutoModelForCausalLM
from transformers import LlamaForCausalLM, LlamaTokenizer
# GPT-3.5
deployment_id = ""
api_version = ""
your_resource_name = ""

gpt3_key = ""
gpt3_url = ""

# GPT-4
gpt4_key = ""
gpt4_url = ""

# GPT-4 turbo
gpt4_turbo_key = ""
gpt4_turbo_url = ""

# GPT Embedding
embedding_url = ""
embedding_key = ""

# Tencent
tencent_appid = 000
tencent_secretid = ""
tencent_secretkey = ""

# GLM4 API
glm_key = ""


model_list = {'THUDM/chatglm3-6b':[AutoTokenizer, AutoModel],
              'THUDM/chatglm3-6b-32k':[AutoTokenizer, AutoModel],
              'THUDM/chatglm3-6b-128k':[AutoTokenizer, AutoModel],
              'tiiuae/falcon-7b': [AutoTokenizer, AutoModelForCausalLM],
              'mistralai/Mistral-7B-Instruct-v0.2':[AutoTokenizer, AutoModelForCausalLM],
              'meta-llama/Llama-2-7b-chat-hf':[LlamaTokenizer, LlamaForCausalLM],
              }

debug = True
