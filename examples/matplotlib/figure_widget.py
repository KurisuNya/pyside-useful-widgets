import sys

import numpy as np
from matplotlib.figure import Figure
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QWidget,
)
from pyside_useful_widgets.matplotlib import FigureWidget


def _random_2d_figure() -> Figure:
    x = np.linspace(0, 10, 100)
    y = np.sin(x) + np.random.normal(0, 0.1, size=x.shape)

    fig = Figure()
    ax = fig.add_subplot()
    ax.plot(x, y)
    ax.set_title("Random 2D Plot")
    ax.set_xlabel("X-axis")
    ax.set_ylabel("Y-axis")
    ax.grid()

    return fig


def _random_3d_figure() -> Figure:
    x = np.sin(np.linspace(0, 10, 100))
    y = np.cos(np.linspace(0, 10, 100))
    z = np.random.normal(0, 1, size=x.shape)

    fig = Figure()
    ax = fig.add_subplot(projection="3d")
    ax.scatter(x, y, z)
    ax.set_title("Random 3D Plot")
    ax.set_xlabel("X-axis")
    ax.set_ylabel("Y-axis")
    ax.set_zlabel("Z-axis")  # type: ignore[assignment]
    ax.grid()
    return fig


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

        self._figure_widget = FigureWidget()
        self._random_2d_button = QPushButton("Random 2D Plot")
        self._random_3d_button = QPushButton("Random 3D Plot")
        self._clear_button = QPushButton("Clear Figure")

        layout.addWidget(self._figure_widget)
        layout.addWidget(self._random_2d_button)
        layout.addWidget(self._random_3d_button)
        layout.addWidget(self._clear_button)

        self.__setup_connections()

    def __setup_connections(self):
        on_2d_button_clicked = lambda: self._figure_widget.set(_random_2d_figure())
        on_3d_button_clicked = lambda: self._figure_widget.set(_random_3d_figure())

        self._random_2d_button.clicked.connect(on_2d_button_clicked)
        self._random_3d_button.clicked.connect(on_3d_button_clicked)
        self._clear_button.clicked.connect(lambda: self._figure_widget.clear())


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec()
