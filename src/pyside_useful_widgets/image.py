from typing import Optional, Union

from PySide6.QtCore import QPoint, Qt, QTimer
from PySide6.QtGui import QImage, QPainter, QPixmap
from PySide6.QtWidgets import QWidget


class ImageViewWidget(QWidget):
    _scale_mode = Qt.AspectRatioMode.KeepAspectRatio
    _scale_method = Qt.TransformationMode.FastTransformation
    _scale_factor = 1.05
    _scale_interval = 10  # ms
    _move_interval = 5  # ms

    def __init__(
        self,
        parent: Optional[QWidget] = None,
        scale_method: Optional[Qt.TransformationMode] = None,
    ):
        super().__init__(parent)
        if scale_method:
            self._scale_method = scale_method
        self._img: Union[QPixmap, None] = None
        self._scaled_img: Union[QPixmap, None] = None
        self._point: QPoint = QPoint(0, 0)
        self._painter: QPainter = QPainter()

        self._start_pos: QPoint = QPoint(0, 0)
        self._end_pos: QPoint = QPoint(0, 0)

        self._scale_timer: QTimer = QTimer()
        self._scale_timer.timeout.connect(lambda: self._scale_timer.stop())
        self._scale_timer.setSingleShot(True)
        self._scale_timer.setInterval(self._scale_interval)

        self._move_timer: QTimer = QTimer()
        self._move_timer.timeout.connect(lambda: self._move_timer.stop())
        self._move_timer.setSingleShot(True)
        self._move_timer.setInterval(self._move_interval)

    def set_img(self, img: Union[QPixmap, QImage]):
        if isinstance(img, QImage):
            img = QPixmap.fromImage(img)
        img.setDevicePixelRatio(self.devicePixelRatio())
        self._img = img
        self.__fit_size()

    def update_img(self, img: Union[QPixmap, QImage]):
        if isinstance(img, QImage):
            img = QPixmap.fromImage(img)
        img.setDevicePixelRatio(self.devicePixelRatio())
        size = self._scaled_img.size() if self._scaled_img else self.size()
        mode, method = self._scale_mode, self._scale_method
        self._img = img
        self._scaled_img = img.scaled(size, mode, method)
        self.repaint()

    def __fit_size(self):
        if not self._img:
            return
        dpi = self.devicePixelRatio()
        size = self.size() * dpi
        mode, method = self._scale_mode, self._scale_method
        self._scaled_img = self._img.scaled(size, mode, method)
        img_size = self._scaled_img.size()
        middle_width = round((size.width() - img_size.width()) // 2 / dpi)
        middle_height = round((size.height() - img_size.height()) // 2 / dpi)
        self._point = QPoint(middle_width, middle_height)
        self.repaint()

    def __scale_image(self, factor: float):
        if not self._img or not self._scaled_img:
            return
        size = self._scaled_img.size() * factor
        mode, method = self._scale_mode, self._scale_method
        self._scaled_img = self._img.scaled(size, mode, method)
        self.repaint()

    def resizeEvent(self, event):
        self.__fit_size()

    def paintEvent(self, event):
        if not self._scaled_img:
            return
        self._painter.begin(self)
        self._painter.drawPixmap(self._point, self._scaled_img)
        self._painter.end()

    def wheelEvent(self, event):
        if self._scale_timer.isActive():
            return
        self._scale_timer.start()
        factor = (
            self._scale_factor if event.angleDelta().y() > 0 else 1 / self._scale_factor
        )
        self.__scale_image(factor)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.setMouseTracking(True)
            self._start_pos = event.position().toPoint()
        elif event.button() == Qt.MouseButton.RightButton:
            self.__fit_size()

    def mouseMoveEvent(self, event):
        if not self._scaled_img:
            return
        if self._move_timer.isActive():
            return
        self._move_timer.start()
        self._end_pos = event.position().toPoint() - self._start_pos
        self._point = self._point + self._end_pos
        self._start_pos = event.position().toPoint()
        self.repaint()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.setMouseTracking(False)
