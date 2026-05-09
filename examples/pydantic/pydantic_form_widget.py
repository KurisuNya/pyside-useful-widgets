import sys
from enum import Enum
from typing import Annotated, Literal

from pydantic import BaseModel, Field
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from pyside_useful_widgets.pydantic import DisplayName, PydanticFormWidget


class Role(Enum):
    ADMIN = "admin"
    USER = "user"
    GUEST = "guest"


class UserProfile(BaseModel):
    username: Annotated[
        str,
        DisplayName("User Name"),
        Field(max_length=20),
    ]
    age: Annotated[
        int,
        DisplayName("Age"),
        Field(ge=0, le=120),
    ]
    height: Annotated[
        float,
        DisplayName("Height (m)"),
        Field(ge=0.0),
    ]
    is_active: Annotated[
        bool,
        DisplayName("Is Active"),
    ] = True
    role: Annotated[
        Role,
        DisplayName("Role"),
    ] = Role.USER
    theme: Annotated[
        Literal["light", "dark", "system"],
        DisplayName("Theme"),
    ] = "system"
    tags: Annotated[
        list[str],
        DisplayName("Tags"),
    ] = ["new"]


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Pydantic Form Widget Example")
        self.setGeometry(100, 100, 800, 600)

        layout = QVBoxLayout()
        layout.setContentsMargins(2, 2, 2, 2)
        layout.setSpacing(2)
        center_widget = QWidget()
        center_widget.setLayout(layout)
        self.setCentralWidget(center_widget)

        self._form_widget = PydanticFormWidget()
        self._form_widget.load_model(UserProfile)

        self._submit_button = QPushButton("Submit")
        self._clear_button = QPushButton("Clear Form")
        self._load_button = QPushButton("Reload Model")

        layout.addWidget(self._form_widget)
        layout.addWidget(self._submit_button)
        layout.addWidget(self._clear_button)
        layout.addWidget(self._load_button)

        self.__setup_connections()

    def __setup_connections(self):
        self._submit_button.clicked.connect(self._on_submit)
        self._clear_button.clicked.connect(self._form_widget.clear)
        self._load_button.clicked.connect(
            lambda: self._form_widget.load_model(UserProfile)
        )

    def _on_submit(self):
        try:
            data = self._form_widget.get_form_data()
            QMessageBox.information(
                self,
                "Success",
                f"Form Validated Successfully!\n\n{data.model_dump_json(indent=2)}",
            )
        except Exception as e:
            QMessageBox.critical(self, "Validation Error", str(e))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec()
