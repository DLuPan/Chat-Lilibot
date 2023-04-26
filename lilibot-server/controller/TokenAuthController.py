# token鉴权相关服务
from flask import Blueprint, jsonify, request, send_file
from flask_jwt_extended import create_access_token

from util import getLogger
from util import DataUtil

logger = getLogger("TokenAuthController")

tokenAuthController = Blueprint("tokenAuthController", __name__, url_prefix="")


@tokenAuthController.route('/getToken', methods=['POST'])
def getToken():
    try:
        username = request.json["username"]
        password = request.json["password"]

        if verify_password(username, password):
            # 用户名和密码验证通过，生成token
            access_token = create_access_token(identity=username)
            return jsonify(access_token=access_token), 200
        else:
            return jsonify({'msg': '用户名或密码错误'}), 401
    except BaseException as e:
        logger.exception(e)
        return jsonify({'msg': '获取token异常请重试'}), 401


def verify_password(username: str, password: str) -> bool:
    """ 校验密码 """
    logger.info(f"用户[{username}]登录")
    if username is None or username == "" or password is None or password == "":
        return False
    userInfo = DataUtil.getUserInfo(username)
    logger.info(f"用户信息:[{userInfo}]")
    return userInfo is not None and userInfo['password'] == password
