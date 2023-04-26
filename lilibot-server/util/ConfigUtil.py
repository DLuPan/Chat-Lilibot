from util import getLogger, TimeUtil
import os
import json


logger = getLogger("ConfigUtil")

_CONFIG_PATH = "config/config.json"

CONFIG_CACHE = {}

""" 缓存过期时间 """
_CONFIG_CACHE_EXPIRATION_TIME = 3600

CONFIG_CACHE_TIME = TimeUtil.timestamp()

CONFIG_CAHCE_INIT = False


def getPortConfig() -> int:
    """ 获取启动端口 """
    getConfig()
    return CONFIG_CACHE['port']


def getTtsConfig() -> dict:
    """ 获取tts配置 """
    getConfig()
    return CONFIG_CACHE['tts']


def getAsrConfig() -> dict:
    """
    获取ASR相关配置
    """
    getConfig()
    return CONFIG_CACHE['asr']


def getProxiesConfig() -> dict:
    """ 获取代理配置 """
    getConfig()
    return CONFIG_CACHE['proxies']


def getChatGptConfig() -> dict:
    """ 获取ChatGpt配置 """
    getConfig()
    return CONFIG_CACHE['chat_gpt']


def getJwtSecretKeyConfig():
    """ 
    获取jwt配置 
    """
    getConfig()
    return CONFIG_CACHE['JWT_SECRET_KEY']


def getConfig():
    """ 获取配置MAP """
    global CONFIG_CACHE
    global CONFIG_CACHE_TIME
    global CONFIG_CAHCE_INIT
    if not CONFIG_CAHCE_INIT or (TimeUtil.timestamp()-CONFIG_CACHE_TIME) > _CONFIG_CACHE_EXPIRATION_TIME:
        # 未初始化或者超过缓存时间重新拉取
        with open(os.path.join(os.getcwd(), _CONFIG_PATH), mode='r') as _db_f:
            CONFIG_CACHE = json.load(_db_f)
            logger.info(f"获取db内容:{CONFIG_CACHE}")
