import threading
import time
import logging
import uuid
import whisper
import json
from util import getLogger, ConfigUtil,getProxiesConfig
import requests

logger = getLogger("AsrServer")

textMap = {}


class Asr(object):
    def __init__(self) -> None:
        """
        初始化基础配置
        """
        pass

    def transcribe(self, audio):
        """
        转换方法定义
        audio:音频的二进制数据
        """

        pass


class WhipserAsrForOpenAI(Asr):
    """ 
        调用Open AI接口实现,适用于本地
    """

    def __init__(self) -> None:
        super().__init__()
        self.config = ConfigUtil.getAsrConfig()['whisper-net']
        logger.info("初始化ASR 配置:[%s]...", self.config)
        logger.info("初始化ASR 完成")

    def transcribe(self, audio, open_key):
        """
        转换方法定义
        audio:音频的二进制数据
        """
        files = [
            ('file', ('audio.mp3', audio, 'audio/mpeg'))
        ]
        headers = {
            'Authorization': f'Bearer {open_key}'
        }

        response = requests.request("POST", self.config['url'], headers=headers, data=self.config['payload'], files=files,proxies=getProxiesConfig())
        respJson = response.json()
        logger.info(f"请求ASR返回:{respJson}")
        return respJson


# class WhisperAsrForLocal(Asr):
#     def __init__(self) -> None:
#         super().__init__()
#         self.config = ConfigUtil.getAsrConfig()['whisper-local']
#         logger.info("初始化ASR 配置:[%s]...", self.config)
#         self.model = whisper.load_model("base")
#         logger.info("初始化ASR 完成")

#     def transcribe(self, audio):
#         """ 生成UID """
#         rid = ''.join(str(uuid.uuid1()).split('-')).upper()
#         logger.info(f"开始转义转义id:[{rid}]")
#         start_time = int(time.time())
#         threading.Thread(target=self._task_transcribe,
#                          args=(audio, rid)).start()
#         """ 开始组装请求 """
#         idx = 1
#         while True:
#             if rid in textMap and textMap[rid] and textMap[rid]["isComplete"]:
#                 """ 说明处理完成了 """
#                 logger.info(f"ASR处理完成..................100%")
#                 result = textMap[rid]['result']
#                 textMap.pop(rid)
#                 logger.info(f"ASR处理结果,result[{result}]")
#                 return result
#             if int(time.time())-start_time > 120:
#                 """ 超过两分钟抛出异常 """
#                 logger.info(f"ASR处理异常!!!")
#                 raise RuntimeError("运行异常，请重试")
#             """ 休眠0.1S """
#             idx += 1
#             logger.info(
#                 f"ASR处理中..................{str(idx*10) if idx<=9 else str(90)}%")
#             time.sleep(0.1*idx)

#     def _task_transcribe(self, audio, rid):
#         # 提交真实线程任务
#         audio.save(f'ASR_{rid}_file.mp3')
#         result = self.model.transcribe(f"ASR_{rid}_file.mp3", fp16=False)
#         textMap[rid] = {'result': result, 'isComplete': True}
