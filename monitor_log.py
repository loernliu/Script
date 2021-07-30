import logging
import os
import sys
import threading
import asyncio
import time

import psutil
import win32api


LOCK = threading.Lock()

process_dict = {}


def monitor_log(file_path, time_chenge, process_dict, restart_list):
    try:
        logging.info("开始监控，监控的日志文件是：%s", file_path)
        file = open(file_path, 'r')
        file.seek(0, 2)
        num = 0
        while True:
            line = file.readline().strip()
            if not line:
                time.sleep(1)
                logging.info("日志停止变化")
                num += 1
                if num == int(60*time_chenge):
                    LOCK.acquire()
                    num = 0
                    logging.info("发现日志文件长时间没有变化，重启进程")
                    if process_dict == {}:
                        logging.info("没有找到进程，监控停止")
                        return
                    # 重启进程
                    for i in process_dict:
                        if i in restart_list:
                            restart_process(process_dict.get(i))
                    time.sleep(3)
                    LOCK.release()
            else:
                num = 0
                logging.info("监控到新日志：%s", line)
    finally:
        file.close()


def restart_process(process):
    # 重启进程
    process_path = process.exe()
    process_name = process.name()
    process.terminate()
    time.sleep(2)
    win32api.ShellExecute(0, 'open', process_path, '', '', 1)
    process = [i for i in psutil.process_iter() if i.name() == process_name][0]
    process_dict[process_name] = process
    logging.info("重启成功")
    logging.info("找到进程:\n%s", process)


def find_process(process_name_list):
    process_dict = {}
    for process_name in process_name_list:
        process = [i for i in psutil.process_iter() if i.name()
                   == process_name]
        if process:
            process_dict[process[0].name()] = process[0]
    logging.info("找到进程:\n%s", [i for i in process_dict])
    return process_dict


def monitor_process(process_dict, restart_list, limit_memory):
    if process_dict == {}:
        logging.info("没有找到进程，监控停止")
        return
    logging.info("开始监控")

    while True:
        memory = psutil.virtual_memory()
        system_memory = round(memory.total/1024/1024, 2)
        free = round(memory.free/1024/1024, 2)
        logging.info("系统总内存：%s，剩余内存：%s", system_memory, free)
        process_use_memory = 0
        for i in process_dict:
            current_process = process_dict.get(i)
            process_memory = round(
                current_process.memory_full_info().uss/1024/1024, 2)
            process_use_memory += process_memory
            memory_percent = round(current_process.memory_percent(), 2)
            logging.info("进程pid：%s,进程名称：%s,占用内存：%s,占用比例：%s", current_process.pid,
                         current_process.name(), process_memory, memory_percent)

        logging.info("监控进程使用总%s", process_use_memory)
        if process_use_memory > limit_memory:
            LOCK.acquire()
            logging.info("发现程序内存占用过多，重启程序")
            for i in process_dict:
                if i in restart_list:
                    restart_process(process_dict.get(i))
            LOCK.release()

        time.sleep(3)


def init_log():
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    logger.propagate = False
    abs_path = os.path.dirname(os.path.abspath(__file__))
    log_path = os.path.join(abs_path, 'logs/vi_monitor.log')
    formatter = logging.Formatter(
        "%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s")
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    ch.setFormatter(formatter)
    logger.addHandler(ch)
    if not os.path.exists(os.path.dirname(log_path)):
        os.makedirs(os.path.dirname(log_path))
    # fh = logging.RotatingFileHandler(
    #     log_path, mode='w', maxBytes=2 * 1024 * 1024, backupCount=100)
    fh = logging.FileHandler(log_path, mode="w", encoding="utf8")
    fh.setLevel(logging.INFO)
    fh.setFormatter(formatter)
    logger.addHandler(fh)


if __name__ == "__main__":
    com_args = sys.argv
    init_log()
    # 进程监控列表
    process_name_list = ["wg_vi.exe", "el_station.exe",
                         "wg_station.exe"]
    # 重启列表
    restart_list = ["wg_vi.exe", "el_station.exe", "wg_station.exe"]
    # 被监控的进程最大允许使用内存，大于这个值重启进程
    limit_memory = 3000
    # 日志文件路径
    file_path = "C:/Users/lwp/Documents/Gitee/el_app-el/src/app_station/output/log/app_station.log"
    # 日志文件无变化时间 单位：分钟
    time_chenge = 0.2

    process_dict = find_process(process_name_list)

    log_monitor = threading.Thread(
        target=monitor_log, args=(file_path, time_chenge, process_dict, restart_list))

    # process_monitor = threading.Thread(
    #     target=monitor_process, args=(process_name_list, restart_list, limit_memory))
    log_monitor.start()
    # process_monitor.start()
    # process_monitor.join()
    monitor_process(process_dict, restart_list, limit_memory)
    log_monitor.join()
