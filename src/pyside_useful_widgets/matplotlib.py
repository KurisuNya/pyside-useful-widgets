from copy import deepcopy

from PySide6.QtCore import QTimer, Qt
from PySide6.QtGui import QResizeEvent
from PySide6.QtWidgets import QWidget
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure


class FigureWidget(FigureCanvas):
    __move_interval = 3  # ms

    def __init__(self):
        super().__init__()
        self.__move_timer = QTimer()
        self.__move_timer.timeout.connect(lambda: self.__move_timer.stop())
        self.__move_timer.setSingleShot(True)
        self.__move_timer.setInterval(self.__move_interval)

    def set(self, fig: Figure):
        dpi = self.figure.dpi
        new_fig = deepcopy(fig)
        new_fig.set_dpi(dpi)
        self.figure = new_fig
        event = QResizeEvent(self.size(), self.size())
        self.resizeEvent(event)

    def clear(self):
        self.set(Figure())

    def mousePressEvent(self, event):
        super().mousePressEvent(event)
        if event.button() == Qt.MouseButton.LeftButton:
            self.setMouseTracking(True)

    def mouseMoveEvent(self, event):
        super().mouseMoveEvent(event)
        if self.__move_timer.isActive():
            return
        self.__move_timer.start()
        self.draw_idle()

    def mouseReleaseEvent(self, event):
        super().mouseReleaseEvent(event)
        if event.button() == Qt.MouseButton.LeftButton:
            self.setMouseTracking(False)

    def sizeHint(self):
        return QWidget.sizeHint(self)
