# 对外暴露的open AI相关接口服务
# OpenAI对外暴露得API
from http.client import HTTPSConnection
from urllib.parse import urlparse

import requests
from flask import Blueprint, jsonify, request
from server.ChatGptServer import ChatGpt
from flask_jwt_extended import jwt_required,get_jwt_identity
from util import getUserInfo,getLogger

logger=getLogger("ChatGptController")

chatGpt=ChatGpt()

chatGptController = Blueprint("chatGptController", __name__, url_prefix="")


@chatGptController.route('/chat', methods=['POST'])
@jwt_required()
def chat():
    # chat接口，对接聊天的api
    
    try:
        prompt = request.json['prompt']
        messages=request.json['messages']
        model=request.json['model']
         # 获取当前登录用户
        current_user = get_jwt_identity()
        user_info=getUserInfo(current_user)
        logger.info(f"开始处理对话,当用户信息:{user_info}")
        return jsonify(chatGpt.chat_v1(prompt=prompt,model=model,open_key=user_info['auth_key'],messages=messages)),200
    except BaseException:
        return jsonify({"msg": "请求OpenAI异常请重试!!!"}),500
