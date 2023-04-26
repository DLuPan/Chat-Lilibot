# 主要入口用于服务端启动

""" 
依赖列表
pip install Flask
pip install requests
"""
from util import getLogger

from flask import Flask
from controller import config_blueprint
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from util import getJwtSecretKeyConfig, getPortConfig
from datetime import timedelta

jwt = JWTManager()
cors = CORS()

logger = getLogger("Main")


def create_app():
    app = Flask(__name__)
    # 初始化Flask-JWT-Extended插件
    app.config["JWT_SECRET_KEY"] = getJwtSecretKeyConfig()  # Change this!
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(days=30)
    jwt.init_app(app)
    cors.init_app(app)
    return app


if __name__ == '__main__':
    logger.info("初始化LILIBOT-Server")
    app = create_app()
    # 配置视图
    config_blueprint(app)
    app.run(port=getPortConfig())
    # 获取当前用户 current_user = get_jwt_identity()
