import sys
from enum import Enum

import fire
from PyQt5.QtCore import QPointF, Qt
from PyQt5.QtGui import (QBrush, QColor, QImage, QPainter, QPainterPath, QPen,
                         QPixmap, QScreen)
from PyQt5.QtWidgets import (QApplication, QGraphicsItem, QGraphicsPixmapItem,
                             QGraphicsScene, QGraphicsView, QHBoxLayout,
                             QMainWindow, QVBoxLayout, QWidget)
from system_hotkey import SystemHotkey


class Zoom(Enum):
    Original = "原图"
    In = "缩小"
    Out = "放大"
    Fit = "自适应"


class GraphicsPixmapItem(QGraphicsPixmapItem):
    '''图像'''

    def __init__(self):
        super().__init__()
        # self.setTransformationMode(Qt.SmoothTransformation)

    def update(self):

        with open(r'D:\test\twg\20211018172755.jpg', 'rb') as f:
            img_bytes = f.read()
        pixmap = QPixmap()
        pixmap.loadFromData(img_bytes)
        # pixmap = pixmap.scaledToWidth(3000, Qt.SmoothTransformation)
        self.setPixmap(pixmap)
        # self.setPixmap(QPixmap.fromImage(QImage.fromData(img_bytes)))

        super().update()


    # def paint(self, painter, option, widget):
    #     '''重载绘图函数'''
    #     with open(r'D:\test\twg\20211018172755.jpg', 'rb') as f:
    #         img_bytes = f.read()
    #     pixmap = QPixmap()
    #     pixmap.loadFromData(img_bytes)
    #     # pixmap = pixmap.scaledToWidth(3000, Qt.SmoothTransformation)
    #     painter.setRenderHint(QPainter.SmoothPixmapTransform, True)

    #     painter.drawPixmap(QPointF(-1000, -500), pixmap)

    # def sceneEvent(self, event):
    #     # QEvent.GraphicsSceneWheel
    #     print(type(event.GraphicsSceneWheel))

    #     return super().sceneEvent(event)

    # def wheelEvent(self, event):
    #     print(1111111111111111111111111)
    #     zoom_in_factor = 1.25
    #     zoom_out_factor = 1 / zoom_in_factor
    
    #     # if event.delta() > 0:
    #     if event.delta() > 0:
    #         zoom_factor = zoom_in_factor
    #     else:
    #         zoom_factor = zoom_out_factor

    #     self.scale(zoom_factor, zoom_factor)


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
    '''主图像视图'''

    def __init__(self):
        super().__init__()
        self.scene = GraphicsScene()
        self.scene_box = QGraphicsScene()
        self.setScene(self.scene)
        # hk = SystemHotkey(check_queue_interval=1)
        # hk.register(['control', 'k'], callback=lambda x:self.reject())

        # self.setSceneRect(0, 0, _w, _h)
        # self.fitInView(self.scene.sceneRect(), Qt.KeepAspectRatio)
        self.setRenderHints(QPainter.Antialiasing | QPainter.SmoothPixmapTransform)

        self.scene_box.setBackgroundBrush(QBrush(QColor(50, 50, 50), Qt.SolidPattern))
        self.item = GraphicsPixmapItem()
        self.item.setTransformationMode(Qt.SmoothTransformation)
        self.scene.addItem(self.item)

        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.AnchorUnderMouse)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

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
        self.set_zoom(Zoom.In if event.delta() > 0 else Zoom.Out)
        event.accept()

    def set_zoom(self, action):

        pass

    def set_fit_window(self):
        """missing docstring"""
        self.scene.setSceneRect(self.scene.itemsBoundingRect())
        self.fitInView(self.scene.itemsBoundingRect().adjusted(-100, -100, 100, 100), Qt.KeepAspectRatio)

    def mouseDoubleClickEvent(self, event):
        """missing docstring"""
        self.item.update()
        print('mouseDouble')
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

        self.set_fit_window()
        super().mouseDoubleClickEvent(event)

    def reject(self):
        print('11111')


def main():
    app = QApplication([])

    # window = QMainWindow()
    Canvas = QWidget()
    layout0 = QHBoxLayout()
    layout0.setSpacing(0)
    layout0.setContentsMargins(0, 0, 0, 0)

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
