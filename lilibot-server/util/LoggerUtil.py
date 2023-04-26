import logging
from logging import Logger
from concurrent_log import ConcurrentTimedRotatingFileHandler
import os

_LOG_PATH = "log/lilibot-server.log"


def getLogger(name="ROOT") -> Logger:
    """ 获取日志对象 """
    # 创建Logger对象
    logger = logging.getLogger('root')
    logger.setLevel(logging.INFO)
    if logger.handlers == []:  # 避免重复日志
        # 创建一个StreamHandler，将日志写入控制台
        stream_fh = logging.StreamHandler()
        stream_fh.setLevel(logging.INFO)

        # 创建一个Formatter，用于定义日志格式
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(threadName)s - %(levelname)s - %(message)s')
        """
        %(asctime)s 字符串形式的当前时间。默认格式是“2021-09-08 16:49:45,896”。逗号后面的是毫秒
        %(created)f 时间戳, 等同于time.time()
        %(relativeCreated)d 日志发生的时间相对于logging模块加载时间的相对毫秒数
        %(msecs)d 日志时间发生的毫秒部分
        %(levelname)s 日志级别str格式
        %(levelno)s 日志级别数字形式(10, 20, 30, 40, 50)
        %(name)s 日志器名称, 默认root
        %(message)s 日志内容
        %(pathname)s 日志全路径
        %(filename)s 文件名含后缀
        %(module)s 文件名不含后缀
        %(lineno)d 调用日志记录函数源代码的行号
        %(funcName)s 调用日志记录函数的函数名
        %(process)d 进程id
        %(processName)s 进程名称
        %(thread)d 线程ID
        %(threadName)s 线程名称
        """
        stream_fh.setFormatter(formatter)

        # 将StreamHandler添加到Logger对象中
        logger.addHandler(stream_fh)

        # 添加一个FileHandler，将日志写入文件
        # 建立一个循环文件handler来把日志记录在文件里
        file_handler = ConcurrentTimedRotatingFileHandler(
            filename=os.path.join(os.getcwd(),_LOG_PATH),  # 定义日志的存储
            when="D",  # 按照日期进行切分when = D： 表示按天进行切分,or self.when == 'MIDNIGHT'
            interval=1,  # interval = 1： 每天都切分。 比如interval = 2就表示两天切分一下。
            backupCount=30,  # 最多存放日志的数量
            encoding="UTF-8",  # 使用UTF - 8的编码来写日志
            delay=False,
            # utc = True: 使用UTC + 0的时间来记录 （一般docker镜像默认也是UTC + 0）
        )
        file_handler.doRollover()
        file_handler.suffix = "%Y-%m-%d.log"
        file_handler.setLevel(logging.DEBUG)  # 设置日志级别
        file_handler.setFormatter(formatter)  # 设置日志格式
        logger.addHandler(file_handler)

    return logger
