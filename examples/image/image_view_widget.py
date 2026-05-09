import datetime
import sys

from matplotlib.figure import Figure
from matplotlib.patches import Rectangle
from PIL import Image
from PIL.ImageQt import ImageQt
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QWidget,
)
from pyside_useful_widgets.image import ImageViewWidget


def _test_image():
    fig = Figure()
    ax = fig.add_subplot()
    left, width = 0, 1
    bottom, height = 0, 1
    right = left + width
    top = bottom + height
    p = Rectangle((left, bottom), width, height, fill=False)
    p.set_transform(ax.transAxes)
    p.set_clip_on(False)
    ax.add_patch(p)
    ax.text(
        0.5 * (left + right),
        0.5 * (bottom + top),
        f"{datetime.datetime.now():%Y-%m-%d %H:%M:%S_%f}",
        horizontalalignment="center",
        verticalalignment="center",
        transform=ax.transAxes,
        fontsize=20,
    )
    ax.set_axis_off()

    import io

    buf = io.BytesIO()
    fig.savefig(buf, dpi=600)
    buf.seek(0)
    return Image.open(buf)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Figure Widget Example")
        self.setGeometry(100, 100, 800, 600)

        layout = QVBoxLayout()
        layout.setContentsMargins(2, 2, 2, 2)
        layout.setSpacing(2)
        center_widget = QWidget()
        center_widget.setLayout(layout)
        self.setCentralWidget(center_widget)

        self._image_view_widget = ImageViewWidget()
        self._image_view_widget.set_img(ImageQt(_test_image()))
        self._refresh_button = QPushButton("Refresh Image")

        layout.addWidget(self._image_view_widget)
        layout.addWidget(self._refresh_button)

        self.__setup_connections()

    def __setup_connections(self):
        self._refresh_button.clicked.connect(
            lambda: self._image_view_widget.update_img(ImageQt(_test_image()))
        )


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec()
