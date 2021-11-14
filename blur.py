import cv2
import numpy as np
import copy


# 读取图片
image = cv2.imread('D:/test/wg/20211018172751.jpg', 0)

# 初始化参数
rows, cols = image.shape
sigma = 2.84089642
kernel_size = np.int(np.round(sigma*3)*2+1)  # 一般高斯核尺寸通过计算得到：6*sigma+1 要保证尺寸的宽度和高度都为奇数
radium = kernel_size//2

# 通过函数 cv2.GaussianBlur 进行滤波处理(模糊处理)
result1 = cv2.GaussianBlur(image, ksize=(kernel_size, kernel_size), sigmaX=sigma)
new_img_data = cv2.resize(result1, (10916, 1846), interpolation=cv2.INTER_AREA)
cv2.imshow('result1', new_img_data)

# 生成高斯核
# kernel_1d = cv2.getGaussianKernel(ksize=kernel_size, sigma=sigma, ktype=cv2.CV_32F)
# kernel_2d = kernel_1d * kernel_1d.T
# print(kernel_2d)

# # 边缘保留原图想的像素值
# result2 = copy.deepcopy(image)
# for i in range(radium, rows-radium, 1):
#     for j in range(radium, rows-radium, 1):
#         result2[i, j] = (image[i-radium:i+radium+1, j-radium:j+radium+1] * kernel_2d).sum()
# result2 = np.uint8(result2)

# cv2.imshow(result1)
cv2.waitKey()
cv2.destroyAllWindows()
