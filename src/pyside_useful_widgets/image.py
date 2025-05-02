from typing import Optional, Union

from PySide6.QtCore import QPoint, QTimer, Qt
from PySide6.QtGui import QImage, QPainter, QPixmap
from PySide6.QtWidgets import QWidget


class ImageViewWidget(QWidget):
    __scale_mode = Qt.AspectRatioMode.KeepAspectRatio
    __scale_method = Qt.TransformationMode.FastTransformation
    __scale_factor = 1.05
    __scale_interval = 10  # ms
    __move_interval = 5  # ms

    def __init__(self, scale_method: Optional[Qt.TransformationMode] = None):
        super().__init__()
        if scale_method:
            self.__scale_method = scale_method
        self.__img: Union[QPixmap, None] = None
        self.__scaled_img: Union[QPixmap, None] = None
        self.__point: QPoint = QPoint(0, 0)
        self.__painter: QPainter = QPainter()

        self.__start_pos: QPoint = QPoint(0, 0)
        self.__end_pos: QPoint = QPoint(0, 0)

        self.__scale_timer: QTimer = QTimer()
        self.__scale_timer.timeout.connect(lambda: self.__scale_timer.stop())
        self.__scale_timer.setSingleShot(True)
        self.__scale_timer.setInterval(self.__scale_interval)

        self.__move_timer: QTimer = QTimer()
        self.__move_timer.timeout.connect(lambda: self.__move_timer.stop())
        self.__move_timer.setSingleShot(True)
        self.__move_timer.setInterval(self.__move_interval)

    def set_img(self, img: Union[QPixmap, QImage]):
        if isinstance(img, QImage):
            img = QPixmap.fromImage(img)
        img.setDevicePixelRatio(self.devicePixelRatio())
        self.__img = img
        self.__fit_size()

    def update_img(self, img: Union[QPixmap, QImage]):
        if isinstance(img, QImage):
            img = QPixmap.fromImage(img)
        img.setDevicePixelRatio(self.devicePixelRatio())
        size = self.__scaled_img.size() if self.__scaled_img else self.size()
        mode, method = self.__scale_mode, self.__scale_method
        self.__img = img
        self.__scaled_img = img.scaled(size, mode, method)
        self.repaint()

    def __fit_size(self):
        if not self.__img:
            return
        dpi = self.devicePixelRatio()
        size = self.size() * dpi
        mode, method = self.__scale_mode, self.__scale_method
        self.__scaled_img = self.__img.scaled(size, mode, method)
        img_size = self.__scaled_img.size()
        middle_width = round((size.width() - img_size.width()) // 2 / dpi)
        middle_height = round((size.height() - img_size.height()) // 2 / dpi)
        self.__point = QPoint(middle_width, middle_height)
        self.repaint()

    def __scale_image(self, factor: float):
        if not self.__img or not self.__scaled_img:
            return
        size = self.__scaled_img.size() * factor
        mode, method = self.__scale_mode, self.__scale_method
        self.__scaled_img = self.__img.scaled(size, mode, method)
        self.repaint()

    def resizeEvent(self, event):
        self.__fit_size()

    def paintEvent(self, event):
        if not self.__scaled_img:
            return
        self.__painter.begin(self)
        self.__painter.drawPixmap(self.__point, self.__scaled_img)
        self.__painter.end()

    def wheelEvent(self, event):
        if self.__scale_timer.isActive():
            return
        self.__scale_timer.start()
        factor = (
            self.__scale_factor
            if event.angleDelta().y() > 0
            else 1 / self.__scale_factor
        )
        self.__scale_image(factor)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.setMouseTracking(True)
            self.__start_pos = event.position().toPoint()
        elif event.button() == Qt.MouseButton.RightButton:
            self.__fit_size()

    def mouseMoveEvent(self, event):
        if not self.__scaled_img:
            return
        if self.__move_timer.isActive():
            return
        self.__move_timer.start()
        self.__end_pos = event.position().toPoint() - self.__start_pos
        self.__point = self.__point + self.__end_pos
        self.__start_pos = event.position().toPoint()
        self.repaint()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.setMouseTracking(False)
