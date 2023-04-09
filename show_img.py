from cmath import pi
import imp
import sys
from enum import Enum
from queue import Queue
from tkinter import Scale
from urllib import request
from cv2 import transform

import fire

from PyQt5.QtCore import (
    QPointF,
    QRectF,
    Qt,
    QThread,
    QTimer,
    QMutex,
    QWaitCondition,
    QMetaObject,
    Q_ARG,
    pyqtSlot,
    QByteArray,
    QIODevice,
    QBuffer,
)
from PyQt5.QtGui import (
    QBrush,
    QColor,
    QImage,
    QPainter,
    QPainterPath,
    QPen,
    QImageReader,
    QPixmap,
    QScreen,
    QTransform,
)
from PyQt5.QtWidgets import (
    QApplication,
    QGraphicsItem,
    QGraphicsPixmapItem,
    QPushButton,
    QGraphicsScene,
    QGraphicsView,
    QHBoxLayout,
    QMainWindow,
    QVBoxLayout,
    QWidget,
)
from system_hotkey import SystemHotkey


class Zoom(Enum):
    Original = "原图"
    In = "缩小"
    Out = "放大"
    Fit = "自适应"


class HPStruct:
    """Struct从字典构造对象
    obj = HPStruct({'a':1, 'b':2})
    obj = HPStruct(a=1, b=2)
    obj.a==1
    obj.b==2
    """

    def __init__(self, *args, **kwargs):
        for arg in args:
            if isinstance(arg, dict):
                self.__dict__.update(arg)
        self.__dict__.update(kwargs)


class ScaleRequest:
    type = Enum("type", ("Scale", "Abort", "Quit"))

    def __init__(self):
        self.scale = float()
        # self.resolution = int()


class ScaleThread(QThread):
    def __init__(self, func):
        super().__init__()
        self.func = func

    def run(self) -> None:
        self.func()


class GraphicsPixmapItem(QGraphicsPixmapItem):
    """图像"""

    def __init__(self):
        self._pixmap = QPixmap()
        self._img_bytes = None
        super().__init__()
        # self.setTransformationMode(Qt.SmoothTransformation)
        with open(r"D:\test\twg\20211018172755.jpg", "rb") as f:
            self._img_bytes = f.read()

    # @property.setter
    # def pixmap(self, pixmap):
    #     if isinstance(pixmap, QPixmap):
    #         self._pixmap = pixmap

    @property
    def pixmap(self):
        return self._pixmap

    @property
    def img_bytes1(self):
        return self._img_bytes

    def img_reader(self, resolution):
        ba = QByteArray(self._img_bytes)
        buf = QBuffer(ba)
        buf.open(QBuffer.ReadOnly)
        self._img_reader = QImageReader(buf)
        self._img_reader.setScaledSize(self._img_reader.size() * resolution / 100.0)
        print(f"00000000000000000{self._img_reader.size()}")
        return self._img_reader.read().convertToFormat(QImage.Format_RGB32)

    def update(self):

        img = self.img_reader(200)
        # print(f"type(img):{type(img)}")
        self._pixmap = self._pixmap.fromImage(img)
        # pixmap = pixmap.scaledToWidth(3000, Qt.SmoothTransformation)
        self.setPixmap(self.pixmap)
        self.setScale(1.0)
        self.setTransformOriginPoint(self.boundingRect().center())
        self.setPos(self.pos() - self.sceneBoundingRect().center())

        super().update()


class GraphicsScene(QGraphicsScene):
    def __init__(self):
        super().__init__()

    # def wheelEvent(self, event):
    #     zoom_in_factor = 1.25
    #     zoom_out_factor = 1 / zoom_in_factor

    #     # if event.delta() > 0:
    #     if event.delta() > 0:
    #         zoom_factor = zoom_in_factor
    #     else:
    #         zoom_factor = zoom_out_factor

    #     self.scale(zoom_factor, zoom_factor)


class GraphicsView(QGraphicsView):
    """主图像视图"""

    def __init__(self):
        super().__init__()
        self.setRenderHints(QPainter.Antialiasing | QPainter.SmoothPixmapTransform)

        #######################################################################

        self.scene = GraphicsScene()
        self.setScene(self.scene)
        self.img_item = GraphicsPixmapItem()
        self.img_item.setTransformationMode(Qt.SmoothTransformation)
        self.scene.addItem(self.img_item)
        # Zoom require
        self.m_scale = 1.0
        self.scale_timer = QTimer()
        self.scale_timer.setSingleShot(True)
        self.scale_timer.timeout.connect(self.scaleTimerElapsed)

        self.scale_mutex = QMutex()

        self.scale_request = Queue()

        self.wait_condition = QWaitCondition()

        self.pending_scale_sequest = ScaleRequest()  # struct

        # self.scale_thread = ScaleThread(self.scaleThread)

        # if not self.scale_thread.isRunning():
        #     self.scale_thread.start()

        ##########################################################################

        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.AnchorUnderMouse)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        # self.scale_thread = ScaleThread()
        # self.scale_thread.start()

    # def wheelEvent(self, event):
    #     zoom_in_factor = 1.25
    #     zoom_out_factor = 0.8

    #     if event.angleDelta().y() > 0:
    #         zoom_factor = zoom_in_factor
    #     else:
    #         zoom_factor = zoom_out_factor

    #     self.scale(zoom_factor, zoom_factor)

    def wheelEvent(self, event):
        # https://github.com/manisandro/gImageReader/releases?page=1
        self.set_zoom(
            Zoom.In if event.angleDelta().y() > 0 else Zoom.Out,
            QGraphicsView.AnchorUnderMouse,
        )
        event.accept()

    def set_zoom(self, action, anchor):
        if not self.img_item:
            return
        # self.sendScaleRequest(ScaleRequest.Request.Abort)
        # m_scale = 1.0
        bb = QRectF()
        bb = self.img_item.sceneBoundingRect()
        fit = min(
            self.viewport().width() / bb.width(), self.viewport().height() / bb.height()
        )
        print(f"------------fit:{fit}")
        if action == Zoom.Original:
            self.m_scale = 1.0
        elif action == Zoom.In:
            self.m_scale = min(10.0, self.m_scale * 1.25)
        elif action == Zoom.Out:
            self.m_scale = max(0.03, self.m_scale * 0.8)

        if action == Zoom.Fit or (
            self.m_scale / fit >= 0.9 and self.m_scale / fit <= 1.09
        ):
            self.m_scale = fit

        self.setTransformationAnchor(anchor)
        t = QTransform()
        t.scale(self.m_scale, self.m_scale)
        self.setTransform(t)

        if self.m_scale < 1.0:
            self.pending_scale_sequest.type = ScaleRequest.type.Scale  # TODO
            self.pending_scale_sequest.scale = self.m_scale
            # self.scale_timer.start(100)
            reader = self.img_item.img_reader(self.m_scale * 200)
            # reader = self.img_item.img_reader(self.m_scale)

            self.setScaledImage(reader, self.m_scale)
        # else:
        #     pix_ = QPixmap()
        #     pix_.loadFromData(self.img_item.img_bytes1)
        #     self.img_item.setPixmap(pix_)
        #     self.img_item.
        #     self.img_item.setScale(1.)
        #     self.img_item.setTransformOriginPoint(self.img_item.boundingRect().center())
        #     self.img_item.setPos(self.img_item.pos() - self.img_item.sceneBoundingRect().center())
        #     print('2222222222222222222')

        self.update()
        # self.set_fit_window()

    def set_scale_image():
        pass

    def getCurrentImage():
        pass

    def getCurrentResolution():
        pass

    def getSceneBoundingRect():
        pass

    def scaleTimerElapsed(self):
        self.sendScaleRequest(self.pending_scale_sequest)

    def sendScaleRequest(self, request):
        self.scale_timer.stop()
        self.scale_mutex.lock()
        self.scale_request.put(request)
        self.wait_condition.wakeOne()
        self.scale_mutex.unlock()

    def scaleThread(self):
        self.scale_mutex.lock()
        while True:
            # while self.scale_request.empty():
            #     self.wait_condition.wait(self.scale_mutex)
            request = self.scale_request.get(block=True)
            if request.type == ScaleRequest.type.Quit:
                break
            # elif request.type == ScaleRequest.type.Scale:
            #     self.scale_mutex.unlock()
            self.scale_mutex.unlock()
            if request.type == ScaleRequest.type.Scale:
                img = QImage.fromData(self.img_item.img_bytes1)
                print("222222222222222222222222222")
                # QMetaObject.invokeMethod(self, "setScaledImage", Qt.BlockingQueuedConnection, Q_ARG(QImage, img), Q_ARG(float, request.scale))

                self.scale_mutex.lock()
        self.scale_mutex.unlock()

    # @pyqtSlot(str)
    def setScaledImage(self, image: QImage, scale: float):
        self.scale_mutex.lock()

        self.img_item.setPixmap(QPixmap.fromImage(image))
        print(f"====scale2=={1.0/scale}")
        self.img_item.setScale(1.0 / scale)
        self.img_item.setTransformOriginPoint(self.img_item.boundingRect().center())
        self.img_item.setPos(
            self.img_item.pos() - self.img_item.sceneBoundingRect().center()
        )
        self.scale_mutex.unlock()

    def set_fit_window(self):
        """missing docstring"""
        self.scene.setSceneRect(self.scene.itemsBoundingRect())
        # self.centerOn(self.scene.sceneRect().center())
        self.fitInView(
            self.scene.itemsBoundingRect().adjusted(-100, -100, 100, 100),
            Qt.KeepAspectRatio,
        )

    def mouseDoubleClickEvent(self, event):
        """missing docstring"""
        self.img_item.update()
        self.scene.setSceneRect(self.img_item.sceneBoundingRect())

        print("mouseDouble")
        # print(self.scene.sceneRect())

        # self.img_box = QImage(self.scene.sceneRect().size().toSize(), QImage.Format_RGB16)
        # painter = QPainter(self.img_box)
        # painter.setRenderHints(QPainter.SmoothPixmapTransform)
        # self.scene.render(painter)
        # img = self.img_box.scaledToWidth(3000, Qt.SmoothTransformation)
        # painter.end()
        # pixmap = QPixmap(img)
        # self.scene_box.addPixmap(pixmap)

        # self.setScene(self.scene_box)

        self.set_zoom(Zoom.Fit, GraphicsView.AnchorUnderMouse)
        # self.set_fit_window()
        # print(f'==itempos=={self.img_item.pos()}==item.boundingRect(){self.img_item.boundingRect().center()} ==========boundingRect.sceneBoundingRect().center(){self.img_item.sceneBoundingRect().center()}')

        super().mouseDoubleClickEvent(event)

    def reject(self):
        print("11111")


def main():
    app = QApplication([])

    # window = QMainWindow()
    Canvas = QWidget()
    layout0 = QHBoxLayout()
    layout0.setSpacing(0)
    layout0.setContentsMargins(0, 0, 0, 0)
    print("显示图片1212321")

    down = QPushButton(app.tr("显示图片"))
    layout0.addWidget(down)

    StackGraphicsView = QWidget()
    layout = QVBoxLayout()
    layout.setSpacing(0)
    layout.setContentsMargins(0, 0, 0, 0)

    # screen = QScreen()
    # print('size:', screen.primaryOrientation())

    view = GraphicsView()
    layout.addWidget(view)
    StackGraphicsView.setLayout(layout)

    layout0.addWidget(StackGraphicsView)

    Canvas.setLayout(layout0)

    Canvas.showMaximized()
    # view.setDragMode()
    # StackGraphicsView.setAlignment(Qt.AlignLeft | Qt.AlignTop)
    # view.setViewportUpdateMode(view.FullViewportUpdate)

    Canvas.show()
    # scene = QGraphicsScene()
    # item = GraphicsPixmapItem()

    # scene.addItem(item)
    # window.setCentralWidget(view)
    # window.showMaximized()
    # window.show()
    ret = app.exec_()
    sys.exit(ret)


if __name__ == "__main__":
    fire.Fire(main)
