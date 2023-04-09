import logging
from logging.handlers import RotatingFileHandler

from requests.sessions import Session

# def setup_logger(logger_name, level=logging.INFO):
#     myapp = logging.getLogger(logger_name)
#     myapp.setLevel(level)

# 	# 设置格式
#     formatter = logging.Formatter("%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s")

# 	# 控制台输出
#     streamHandler = logging.StreamHandler()
#     streamHandler.setFormatter(formatter)

# 	# 滚动文件输出
#     rotatingHandler = RotatingFileHandler('logs/mylog.log', maxBytes=5*1024*1024, backupCount=3)
#     rotatingHandler.setFormatter(formatter)

#     myapp.addHandler(streamHandler)
#     myapp.addHandler(rotatingHandler)

# # 示例
# def main():
#     setup_logger('myapp')
#     myapp = logging.getLogger('myapp')
#     while(True):
#         myapp.info("file test")


# if __name__ == '__main__':
#     main()
