import time


def timestamp() -> int:
    """ 获取当前时间时间戳 """
    return int(round(time.time()))


def compare(data1, data2) -> int:
    """ 判断两个时间是否一致 """
    if data1 == data2:
        return 0
    elif data1 > data2:
        return 1
    else:
        return -1


def parser(dataStr, format) -> int:
    """ 拿时间戳 """
    timeTuple = time.strptime(dataStr, format)
    return int(time.mktime(timeTuple))


def format(data, format) -> str:
    return time.strftime(format, time.localtime(data))


# if __name__ == '__main__':
#     print(f"当前时间戳:{timestamp()}")
#     print(f"生成时间戳:{parser('2019-5-10 23:40:10','%Y-%m-%d %H:%M:%S')}")
#     print(f"当前时间字符串:{format(timestamp(),'%Y-%m-%d %H:%M:%S')}")
