FROM python:3.9-slim as base

LABEL AUDTHOR="DINGLUPAN" 

# 创建服务目录
RUN mkdir -p /lilibot/lilibot-server

# 复制相关依赖文档
COPY ./ /lilibot/lilibot-server

COPY ./sources.list /etc/apt/

WORKDIR /lilibot/lilibot-server

# 安装相关依赖
RUN apt update && \
    apt install -y ffmpeg

# 安装python相关依赖,通过配置setup.py来做方便又快捷
RUN pip install -r requirements.txt


# 默认端口8088
EXPOSE 8088

# 执行
ENTRYPOINT [ "python" ,"/lilibot/lilibot-server/Main.py" ]



