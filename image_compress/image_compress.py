# from PIL import Image
import os
import cv2
import numpy as np
import time
from PIL import Image


class CompressImage(object):
    """图片压缩"""

    def __init__(self, infile, outfile="", mb=1500, quality=50):
        """不改变图片尺寸对图片进行压缩
        :param infile: 压缩源文件
        :param outfile: 压缩文件保存地址
        :param mb: 压缩目标，KB
        :param quality: 初始压缩比率,取值为[0,100],0时图像可以得到最大地压缩
        :return: 压缩文件地址，压缩文件大小
        """
        self.infile = infile
        self.outfile = outfile
        self.mb = mb
        self.quality = quality
        self.dir, suffix = os.path.splitext(self.infile)
        if suffix != ".jpg":
            self.png_to_jpg(infile)

    @staticmethod
    def _get_size(file):
        """获取文件大小:KB"""
        size = os.path.getsize(file)
        return size / 1024

    def get_outfile(self):
        """压缩文件保存地址"""
        if self.outfile:
            return self.outfile
        self.outfile = "{}-transformed.jpg".format(self.dir)
        return self.outfile

    def compress_image(self):
        """压缩图片"""
        o_size = self._get_size(self.infile)
        if o_size <= self.mb:
            return self.infile, o_size
        outfile = self.get_outfile()
        img = Image.open(self.infile)
        while o_size > self.mb:
            img.save(outfile, quality=self.quality)
            self.quality = int(self.quality * 0.8)
            o_size = self._get_size(outfile)
            if self.quality == 0:
                break
        return outfile, o_size

    def png_to_jpg(self, PngPath):
        """把PNG格式装换为JPG"""
        outfile = self.dir + ".jpg"
        img = Image.open(self.infile)
        try:
            if len(img.split()) == 4:
                # prevent IOError: cannot write mode RGBA as BMP
                r, g, b, self.a = img.split()
                img = Image.merge("RGB", (r, g, b))
                img.convert("RGB").save(outfile, quality=70)
                os.remove(PngPath)
            else:
                img.convert("RGB").save(outfile, quality=70)
                os.remove(PngPath)
            self.infile = outfile
            return outfile
        except Exception as e:
            print("PNG转换JPG 错误", e)

    # def jpg_to_png(self, jpg_path):
    #     """把JPG转化为PNG"""
    #     outfile = self.dir + ".png"
    #     img = Image.open(self.infile)
    #     r, g, b = img.split()
    #     img = Image.merge("RGBA", (b, g, r, self.a))
    #     img.save(outfile)


if __name__ == "__main__":
    time1 = time.time()
    src_file_path = "./images/LRP904032210302131652.png"
    # print('压缩前图片大小：%d KB' % int(os.path.getsize(src_file_path)/1024))
    compress = CompressImage(src_file_path, mb=2000)
    i_dir, size = compress.compress_image()
    # compress.jpg_to_png(i_dir)
    # print('压缩后图片大小：%d KB' % int(size))

    # files = os.listdir('./images')
    # for file in files:
    #     compress = CompressImage('./images/{}'.format(file), mb=2000)
    #     compress.compress_image()
    # time2 = time.time()
    # print('总共耗时：' + str(time2 - time1) + 's')


# def convertPNG(img1):
#     img = img1.convert('RGBA')
#     r, g, b, a = img.split()
#     a0 = np.array(b) #转换为np矩阵
#     a1 = cv2.threshold(a0, 10, 255, cv2.THRESH_BINARY) #设定阈值
#     a2 = Image.fromarray(a1[1]) #转换为Image的tube格式，注意为a1[1]
#     a3 = np.array(a2)
#     a4 = Image.fromarray(a3.astype('uint8')) #由float16转换为uint8
#     img = Image.merge("RGBA", (b, g, r, a4))
#     return img


# if __name__ == '__main__':
#     img=Image.open('LRP904032210302131652.jpg')
#     img1=convertPNG(img)
#     img1.save('img2.png')
