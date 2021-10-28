import sys
import fire

from PySide6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, QMainWindow, QGraphicsPixmapItem, QGraphicsItem,
                               QGraphicsView, QGraphicsScene)
from PySide6.QtCore import Qt, QPointF
from PySide6.QtGui import QColor, QPainterPath, QPen, QPixmap, QImage, QPainter, QBrush, QScreen


class GraphicsPixmapItem(QGraphicsPixmapItem):
    '''图像'''

    def __init__(self):
        super().__init__()
        self.setTransformationMode(Qt.SmoothTransformation)

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
        self.setScene(self.scene)

        # self.setSceneRect(0, 0, _w, _h)
        # self.fitInView(self.scene.sceneRect(), Qt.KeepAspectRatio)
        self.setRenderHints(QPainter.Antialiasing | QPainter.SmoothPixmapTransform)

        self.scene.setBackgroundBrush(QBrush(QColor(50, 50, 50), Qt.SolidPattern))
        self.item = GraphicsPixmapItem()
        self.scene.addItem(self.item)

        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.AnchorUnderMouse)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

    def wheelEvent(self, event):
        zoom_in_factor = 1.25
        zoom_out_factor = 1 / zoom_in_factor

        # if event.delta() > 0:
        if event.angleDelta().y() > 0:
            zoom_factor = zoom_in_factor
        else:
            zoom_factor = zoom_out_factor

        self.scale(zoom_factor, zoom_factor)

    def set_fit_window(self):
        """missing docstring"""
        self.scene.setSceneRect(self.scene.itemsBoundingRect())
        self.fitInView(self.scene.itemsBoundingRect().adjusted(-100, -100, 100, 100), Qt.KeepAspectRatio)

    def mouseDoubleClickEvent(self, event):
        """missing docstring"""
        self.item.update()
        print('mouseDouble')
        print(self.scene.sceneRect())
        scene_box = QGraphicsScene()
        img_box = QImage(self.scene.sceneRect().size().toSize(), QImage.Format_RGB16)
        painter = QPainter(img_box)
        painter.setRenderHints(QPainter.SmoothPixmapTransform)
        self.scene.render(painter)
        img = img_box.scaledToWidth(3000, Qt.SmoothTransformation)
        painter.end()
        print("img_box:%s", img)
        img.save("2222222222222.jpg")
        pixmap = QPixmap(img)
        # pixmap.fromImage(img_box)
        print("pixmap:", pixmap)
        print('isActive:', painter.isActive())
        # pixmap = pixmap.scaledToWidth(3000, Qt.SmoothTransformation)
        # print("pixmap:", pixmap)
        scene_box.addPixmap(pixmap)
        print('===============')
        print(scene_box.width())
        self.setScene(scene_box)

        self.set_fit_window()
        super().mouseDoubleClickEvent(event)


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

    screen = QScreen()
    print('size:', screen.primaryOrientation())

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
