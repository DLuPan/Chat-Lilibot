#!/usr/bin/env python

# -*- coding:utf-8 -*-


import io
import struct
import wave
from pydub import AudioSegment
from io import BytesIO
import json
import datetime
import pytz
import types
import threading
import uuid
import logging
import re
import websocket

from websocket import WebSocketConnectionClosedException
import os

import time

from util import getLogger,getTtsConfig

logger = getLogger("TTS")
# 定义header的解析正则表达式
headerPattern = re.compile(r'(.*)\r\n')

class TTS(object):
    """ TTS标准模块 """

    def __init__(self, config: None) -> None:
        """ 
            config:配置信息，不同模型，配置可能不同
        """
        self.config = config
        pass


def uid():
    return ''.join(str(uuid.uuid1()).split('-')).upper()


def utcTime():
    local_time = datetime.datetime.now()
    tz = pytz.timezone('Asia/Shanghai')
    tz_time = tz.localize(local_time)
    utc_time = tz_time.astimezone(pytz.utc)
    utc_str = utc_time.strftime('%Y-%m-%dT%H:%M:%S.000Z')
    return utc_str


def parseHeaders(headersString):
    """ 解析headers字符串 """
    headers = {}
    if headersString:
        # 获取匹配的所有header信息
        headerMatchs = headerPattern.findall(headersString)
        if headerMatchs:
            for header in headerMatchs:
                separatorIndex = header.find(":")
                headerName = header[0:separatorIndex].strip(
                ).lower() if separatorIndex > 0 else header
                headerValue = header[separatorIndex +
                                     1:].strip().lower() if len(header) > separatorIndex+1 else ""
                headers[headerName] = headerValue
    return headers


def connectionMessage(opcode, binaryMessage):
    """ 将二进制消息转换为标准对象 """
    connectionMessage = {'opcode': opcode, 'binaryMessage': binaryMessage}
    if opcode == websocket.ABNF.OPCODE_BINARY:
        """ 说明是二进制数据 """
        """ 首先判断二进制数据是否异常 """
        if binaryMessage is None and len(binaryMessage) < 2:
            raise RuntimeError(
                "Invalid binary message format. Header length missing.")
        """ 构建memoryview """
        dataView = memoryview(binaryMessage)
        headerLength = int.from_bytes(dataView[0:2].tobytes(), 'big')
        if len(binaryMessage) < headerLength+2:
            raise RuntimeError(
                "Invalid binary message format. Header content missing.")
        headersString = str(dataView[2:2+headerLength], encoding="utf-8")
        connectionMessage['headers'] = parseHeaders(headersString)
        if len(binaryMessage) > headerLength+2:
            connectionMessage['body'] = dataView[2+headerLength:].tobytes()
    elif opcode == websocket.ABNF.OPCODE_TEXT:
        """ 说明是文本数据 """
        textMessage = str(binaryMessage, 'utf-8')
        if textMessage:
            headerBodySplit = textMessage.split("\r\n\r\n")
            if headerBodySplit and len(headerBodySplit) > 0:
                connectionMessage['headers'] = parseHeaders(
                    headerBodySplit[0]+'\r\n')
                if len(headerBodySplit) > 1:
                    connectionMessage['body'] = headerBodySplit[1]
        pass
    return connectionMessage


rawMap = {}


def rawMessage(connMessage):
    """ 处理这里主要用于合成最终录音 """
    rid = connMessage['headers']['x-requestid']
    path = connMessage['headers']['path']
    rawMsg = rawMap[rid] if rid in rawMap else {
        rid: {}, "isComplete": False, "audio": b''}
    """ 开始处理 """
    if connMessage['opcode'] == websocket.ABNF.OPCODE_TEXT:
        """ 文本格式 """
        """ 注意几个指令 """
        if path == 'audio.metadata':
            """ 音频源信息 """
            rawMsg['metaData'] = json.loads(connMessage['body'])
        if path == 'turn.end':
            """ 表示已经结束了 """
            rawMsg['isComplete'] = True
        pass
    elif connMessage['opcode'] == websocket.ABNF.OPCODE_BINARY:
        """ 二进制格式 """
        if path == 'audio' and 'body' in connMessage:
            rawMsg['audio'] = rawMsg['audio']+connMessage['body']
        pass
    rawMap[rid] = rawMsg
    pass


class MicrosoftTTS(TTS):
    """ 微软TTS模块 """

    def __init__(self, config: None) -> None:
        """ 初始化 """
        super().__init__(config)
        logger.info(f"初始化TTS 配置:[{config}]...")
        self.ws: websocket.WebSocket = None
        self.wsOpen = False
        """ key为rid """
        # 改成懒加载，不要一开始就初始化
        # logger.info("初始化TTS 完成")
        # self.initWebSocket()
        self.defaultSpeechConfig = {
            "context": {
                "system": {
                    "name": "SpeechSDK",
                    "version": "1.26.0",
                    "build": "JavaScript",
                    "lang": "JavaScript"
                },
                "os": {
                    "platform": "Browser/Win32",
                    "name": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36",
                    "version": "5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36"
                }
            }
        }
        self.defaultSynthesisContext = {
            "synthesis": {
                "audio": {
                    "metadataOptions": {
                        "bookmarkEnabled": False,
                        "punctuationBoundaryEnabled": "false",
                        "sentenceBoundaryEnabled": "false",
                        "sessionEndEnabled": False,
                        "visemeEnabled": False,
                        "wordBoundaryEnabled": "false"
                    },
                    "outputFormat": "audio-24khz-96kbitrate-mono-mp3"
                },
                "language": {
                    "autoDetection": False
                }
            }
        }

    def initWebSocket(self):
        """ 初始化一个websocket """
        self.ws = websocket.create_connection("wss://eastus.api.speech.microsoft.com/cognitiveservices/websocket/v1?TrafficType=AzureDemo&Authorization=bearer%20undefined&X-ConnectionId=469A81DCF14B4B9BBCLDBC28CCFFB78F",
                                              origin="https://azure.microsoft.com",
                                              httP_proxy_host="127.0.0.1",
                                              http_proxy_port="7890")
        threading.Thread(target=self.startRecvData).start()
        self.wsOpen = True
        logger.info("初始化TTS 完成")

    def startRecvData(self):
        """ 启动消息接收 """
        while True:
            try:
                opcode, binaryMessage = self.ws.recv_data()
                logger.info(
                    f"Websocket获取消息,opcode:{opcode},message:{binaryMessage}")
                if opcode == websocket.ABNF.OPCODE_CLOSE:
                    """ 说明连接关闭了,关闭运行程序 """
                    logger.info(f'Websocket连接关闭')
                    self.wsOpen = False
                    return
                connMessage = connectionMessage(opcode, binaryMessage)
                rawMessage(connMessage)
                # time.sleep(0.1)
            except WebSocketConnectionClosedException:
                logger.info("Websocket关闭,设置全局状态为关闭")
                self.wsOpen = False
                return

    def text_to_speech(self, text: str):
        """ 文本转语音 """
        rid = uid().lower()
        """ 判断是否关闭 """
        if self.ws == None or self.wsOpen is False:
            self.initWebSocket()
        self.sendSppechConfig(rid)
        self.sendSynthesisContent(rid)
        self.sendSsml(rid, text)
        start_time = int(time.time())
        """ 开始组装请求 """
        idx = 1
        while True:
            if rid in rawMap and rawMap[rid] and rawMap[rid]["isComplete"]:
                """ 说明处理完成了 """
                logger.info(f"TTS处理完成..................100%")
                audio = rawMap[rid]['audio']
                rawMap.pop(rid)
                # 临时保存为文件，这样的好处是为了验证请求
                tts_config=getTtsConfig()
                if tts_config['is_save']:
                    with open(os.path.join(os.getcwd(),f'tts\TTS_{rid}_file.mp3'), 'wb') as f:
                        f.write(audio)
                return audio
            if int(time.time())-start_time > 120:
                """ 超过两分钟抛出异常 """
                logger.info(f"TTS处理异常!!!")
                raise RuntimeError("运行异常，请重试")
            """ 休眠0.1S """
            idx += 1
            if idx <= 9:
                logger.info(f"TTS处理中..................{str(idx*10)}%")
            # time.sleep(0.1)

    def sendSppechConfig(self, rid: str, speechConfig=None):
        if speechConfig is None:
            speechConfig = self.defaultSpeechConfig
        self.send(
            f'Path: speech.config\r\nX-RequestId: {rid}\r\nX-Timestamp: {utcTime()}\r\nContent-Type: application/json\r\n\r\n{json.dumps(speechConfig)}')

    def sendSynthesisContent(self, rid: str, synthesisContext=None):
        if synthesisContext is None:
            synthesisContext = self.defaultSynthesisContext
        self.send(
            f'Path: synthesis.context\r\nX-RequestId: {rid}\r\nX-Timestamp: {utcTime()}\r\nContent-Type: application/json\r\n\r\n{json.dumps(synthesisContext)}')

    def sendSsml(self, rid: str, text, styleAttribute='affectionate', rolePlayAttribute='Girl', voice="zh-CN-XiaoxiaoNeural", speed=0, pitch=0):
        ssmlProperties = f'<prosody rate="{speed}%" pitch="{pitch}%">{text}</prosody>'
        ssmlExpression = f'<mstts:express-as style="{styleAttribute}">{ssmlProperties}</mstts:express-as>'
        ssmlVoiceName = f'<voice name="{voice}">{ssmlExpression}</voice>'
        ssmlHeader = f'<speak xmlns="http://www.w3.org/2001/10/synthesis" xmlns:mstts="http://www.w3.org/2001/mstts" xmlns:emo="http://www.w3.org/2009/10/emotionml" version="1.0" xml:lang="en-US">{ssmlVoiceName}</speak>'
        self.send(
            f'Path: ssml\r\nX-RequestId: {rid}\r\nX-Timestamp: {utcTime()}\r\nContent-Type: application/ssml+xml\r\n\r\n{ssmlHeader}')

    def send(self, data: str):
        logger.info(f"WebSocket请求:{data}")
        if self.ws and self.wsOpen:
            self.ws.send(data)
        else:
            logger.info(f"WebSocket connection is closed!!!")
            raise RuntimeError('WebSocket connection is closed!!!')
