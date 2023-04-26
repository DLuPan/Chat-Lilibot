from flask import Flask
from .ChatGptController import chatGptController
from .TtsController import ttsController
from .AsrController import asrController
from .TokenAuthController import tokenAuthController

# 配置默认路径
DEFAULT_BLUEPRINT = (
    # 蓝本，前缀
    (chatGptController, "/chatGpt"),
    (ttsController, "/tts"),
    (asrController, "/asr"),
    (tokenAuthController,"/auth")
)


# 配置蓝图
def config_blueprint(app: Flask):
    for blueprint, url_prefix in DEFAULT_BLUEPRINT:
        """ 注册蓝图 """
        app.register_blueprint(blueprint, url_prefix=url_prefix)
