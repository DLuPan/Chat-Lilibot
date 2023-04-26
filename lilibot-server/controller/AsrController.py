import logging
import threading

# whisper 模型使用
import whisper
from flask import Blueprint, jsonify, request, send_file

from server.AsrServer import WhipserAsrForOpenAI
from flask_jwt_extended import jwt_required,get_jwt_identity

from util import getUserInfo,getLogger
# 创建Logger对象
logger = getLogger("AsrController")

asrController = Blueprint("asrController", __name__, url_prefix="")

asr=WhipserAsrForOpenAI()

@asrController.route('/translations', methods=['POST'])
@jwt_required()
def translations():
    try:
        # 获取当前登录用户
        current_user = get_jwt_identity()
        user_info=getUserInfo(current_user)
        logger.info(f"开始处理音频文件,当用户信息:{user_info}")
        file = request.files['file']
        return jsonify(asr.transcribe(file,user_info['auth_key'])),200
    except BaseException as e:
        logger.exception(e)
        return jsonify({"msg": "ASR处理异常，请重试"}),500
