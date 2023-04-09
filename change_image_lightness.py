import numpy as np
import cv2
import os

# 调整最大值
MAX_VALUE = 100


def change_image_lightness(input_img_path, output_img_path, lightness):
    """
    用于修改图片的亮度和饱和度
    :param input_img_path: 图片路径
    :param output_img_path: 输出图片路径
    :param lightness: 亮度
    :param saturation: 饱和度
    """

    # 加载彩色图像归一化且转换为浮点型
    image = cv2.imread(input_img_path, cv2.IMREAD_COLOR).astype(np.float32) / 255.0

    # 颜色空间转换 BGR转为HLS
    # HLS 有三个分量，hue（色相）、lightness（亮度）、saturation（饱和度）。
    hlsImg = cv2.cvtColor(image, cv2.COLOR_BGR2HLS)
    # 调整亮度（线性变换)
    # 改变hls中l的值，如：loghtness=5,MAX_VALUE=10 把三维矩阵中的第二列扩大1.5倍，即控制亮度l扩大原来的1.5倍
    hlsImg[:, :, 1] = (1.0 + lightness / 100.0) * hlsImg[:, :, 1]
    hlsImg[:, :, 1][hlsImg[:, :, 1] > 1] = 1
    # 饱和度
    # hlsImg[:, :, 2] = (1.0 + saturation / float(MAX_VALUE)) * hlsImg[:, :, 2]
    # hlsImg[:, :, 2][hlsImg[:, :, 2] > 1] = 1
    # HLS2BGR
    lsImg = cv2.cvtColor(hlsImg, cv2.COLOR_HLS2BGR) * 255
    lsImg = lsImg.astype(np.uint8)
    cv2.imwrite(output_img_path, lsImg)


if __name__ == "__main__":
    # img_path = './image_light/LRP904098210301203924.jpg'
    # output_dir = 'lightness_changed.jpg'
    lightness = 80  # 亮度-100~+100
    # change_image_lightness(img_path, output_dir, lightness)
    files = os.listdir("./image_light/wg")
    for file in files:
        print(file)
        change_image_lightness(
            "./image_light/wg/{}".format(file),
            os.path.splitext(file)[0] + "changed.jpg",
            lightness,
        )

    # saturation = 0    # 饱和度饱和度-100~+100
    # 转化图片
