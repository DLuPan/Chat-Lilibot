# chatGpt对接
# openai对接服务
from urllib.parse import urlparse
from http.client import HTTPSConnection
import requests
from requests import Response
import json
from util import getLogger, getChatGptConfig, getProxiesConfig

# 设置代理服务器的地址


class ChatGpt(object):
    def __init__(self) -> None:
        pass

    def chat_v1(self, prompt, model, open_key, messages: list):
        chatGptConfig = getChatGptConfig()
        chat_model_config = chatGptConfig['chat_model']
        if model in chat_model_config:
            chat_model = chat_model_config[model]
            if len(messages) == 0:
                messages.append({
                    "role": "system",
                    "content": chat_model['system']
                })
            messages.append({
                "role": "user",
                "content": prompt
            })
            payload = chat_model['payload']
            payload["messages"] = messages
        else:
            raise RuntimeError(f"选择模型不存在:{model}")

        resJson = self.openai_request(chatGptConfig['url'], payload=payload, open_key=open_key)
        messages.append(resJson['choices'][0]['message'])
        resJson['messages']=messages
        return resJson

    def openai_request(self, url, payload, open_key):
        # 定义一个函数，用于向 OpenAI 发送请求，并使用代理服务器
        # 向 OpenAI 发送请求，并使用代理服务器

        response = requests.post(
            url=url,
            json=payload,
            headers={"Authorization": f"Bearer {open_key}"},
            proxies=getProxiesConfig()
        )
        return response.json()

