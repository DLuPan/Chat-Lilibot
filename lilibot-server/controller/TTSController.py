# TTS相关对外接口
import asyncio
import requests
from flask import Blueprint, jsonify, request, send_file
import websocket
import logging
import io
from flask_jwt_extended import jwt_required
from server.TtsServer import MicrosoftTTS
from util import getLogger

tts = MicrosoftTTS({})

ttsController = Blueprint("ttsController", __name__, url_prefix="")

# 创建Logger对象
logger = getLogger("TtsController")


@ttsController.route('/txtToSppech', methods=['POST'])
@jwt_required()
def text_to_speech():
    # 文本
    # config = request.json['config']
    # 需要转tts的文本
    try:
        text = request.json['text']
        logger.info(f"请求参数text=[{text}]")
        if text is not None:
            return send_file(io.BytesIO(tts.text_to_speech(text)), mimetype='application/octet-stream')
    except BaseException as e:
        logger.info("TTS处理异常，请重试", BaseException)
        return jsonify({"msg": "TTS处理异常，请重试"}), 500
