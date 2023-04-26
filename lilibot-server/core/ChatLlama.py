# llama模型推理
from .core import CHAT,CHATReq,CHATResp

""" llama模型 """
llama_model=None

def chat(prompt,model_path:str,history:list,
         temperature=0.7,max_tokens=2048,top_p=1,
         frequence_penalty=0,presence_penalty=0):
    
    pass