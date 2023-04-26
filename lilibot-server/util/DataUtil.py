import os
import json
from util.LoggerUtil import getLogger

# 数据管理工具，提供简单数据访问，数据采用json存放
DATA_MAP_CACHE = {}
_IS_INIT_PULL = False
_CONFIG_PATH = "config/db.json"
_CONFIG_USER_KEY = "user"

logger = getLogger("DataUtil")


def getUserInfo(username):
    """ 获取用户信息 """
    if username is not None and username != "":
        users = getData(_CONFIG_USER_KEY)
        if username in users:
            return users[username]
    return None


def setData(key, value) -> bool:
    global DATA_MAP_CACHE
    """ 
    保存数据 
    key:保存的key
    value:保存的值
    """
    DATA_MAP_CACHE[key] = value
    push_data()
    return False


def getData(key):
    global DATA_MAP_CACHE, _IS_INIT_PULL
    """
    获取数据内容
    """
    if not _IS_INIT_PULL:
        pull_data()
        _IS_INIT_PULL = True
    if key in DATA_MAP_CACHE:
        return DATA_MAP_CACHE[key]
    return None


def push_data():
    global DATA_MAP_CACHE
    """
    保存数据到文件
    """
    with open(os.path.join(os.getcwd(), _CONFIG_PATH), mode='w+') as _db_f:
        json.dump(DATA_MAP_CACHE, _db_f)


def pull_data():
    global DATA_MAP_CACHE
    """
    拉取新数据
    """
    with open(os.path.join(os.getcwd(), _CONFIG_PATH), mode='r') as _db_f:
        DATA_MAP_CACHE = json.load(_db_f)
        logger.info(f"获取db内容:{DATA_MAP_CACHE}")
