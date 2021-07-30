import os
import time
import subprocess
from shutil import copy
import uiautomation as auto


def del_pic(picpath):
    for i in os.listdir(picpath):
        pic = os.path.join(picpath, i)
        os.remove(pic)


def cppic(interval_time=10):
    """
    打开客户端
    设置pkl
    设置检测目录
    设置检测结果目录
    设置行数、列数、单多晶、全半片
    自主检测模式
    所有缺陷类型取消勾选

    每12张复制一次
    等待10秒，点击确认NG
    """
    pic_dir = ('G:/elec_pic/2021-01-20/2021-01-20/black/MAN/NG/A',
               'G:/elec_pic/2021-01-20/2021-01-20/black/MAN/NG/B',
               'G:/elec_pic/2021-01-20/2021-01-20/black/MAN/OK/A',
               'G:/elec_pic/2021-01-20/2021-01-20/black/MAN/OK/B',
               'G:/elec_pic/2021-01-20/2021-01-20/white/MAN/NG/B',
               'G:/elec_pic/2021-01-20/2021-01-20/white/MAN/NG/A',
               'G:/elec_pic/2021-01-20/2021-01-20/white/MAN/OK/A',
               'G:/elec_pic/2021-01-20/2021-01-20/white/MANOK/B',
    )
    front_file = 'G:/ccc'
    for i in pic_dir:
        piclist = os.listdir(i)
        for j in piclist:
            x = os.path.join(i, j)
            copy(x, front_file)
            time.sleep(3)
            # if cindex % 12 == 0:
            #     time.sleep(10)


def cppic2(pic_dir1, pic_dir2, front_file1, front_file2):
    pic_list1 = os.listdir(pic_dir1)
    pic_list2 = os.listdir(pic_dir2)
    for val in pic_list1:
        x = os.path.join(pic_dir1, val)
        copy(x, front_file1)
    for val2 in pic_list2:
        x = os.path.join(pic_dir2, val2)
        copy(x, front_file2)


def take():
    pic_dir1 = 'C:/Users/lwp/Downloads/el_image_bak'
    pic_dir2 = 'C:/Users/lwp/Downloads/wg_image_bak'
    front_file1 = 'E:/test/el'
    front_file2 = 'E:/test/wg'
    # mainwin = auto.WindowControl()
    # ct = mainwin.ToolBarControl(searchDepth=2, foundIndex=1)
    # ng = ct.ButtonControl(searchDepth=3, foundIndex=4)
    # ct2 = auto.WindowControl()
    # selectionA1 = ct2.CustomControl(searchDepth=3, foundIndex=1)
    # A1 = selectionA1.ButtonControl(searchDepth=4, foundIndex=2)
    # selectdefect = ct2.CustomControl(searchDepth=3, foundIndex=2)
    # yl = selectdefect.CheckBoxControl(searchDepth=6, foundIndex=1)
    # confirm = ct2.CustomControl(searchDepth=3, foundIndex=3)
    # confirmok = confirm.ButtonControl(searchDepth=4, foundIndex=3)

    # 放图
    while True:
        cppic2(pic_dir1, pic_dir2, front_file1, front_file2)
        time.sleep(30)
        # ng.Click()


if __name__ == '__main__':
    time.sleep(5)
    take()
