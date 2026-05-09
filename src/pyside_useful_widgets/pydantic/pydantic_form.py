from typing import Any, Optional

from pydantic import BaseModel
from PySide6.QtWidgets import QFormLayout, QWidget

from .types import DisplayName, TypeWidget, create_field_widget


class PydanticFormWidget(QWidget):
    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self._model_class: Optional[type[BaseModel]] = None
        self._widgets: dict[str, TypeWidget[Any, QWidget]] = {}
        self._form_layout = QFormLayout(self)

    def clear(self) -> None:
        for widget in self._widgets.values():
            widget.qwidget.deleteLater()
        self._widgets.clear()
        while self._form_layout.rowCount() > 0:
            self._form_layout.removeRow(0)
        self._model_class = None

    def load_model(self, model_class: type[BaseModel]) -> None:
        self.clear()
        for field_name, field_info in model_class.model_fields.items():
            display_name = DisplayName.get(field_name, field_info)
            widget = create_field_widget(field_info)
            self._model_class = model_class
            self._widgets[field_name] = widget
            self._form_layout.addRow(display_name + ":", widget.qwidget)

    def get_form_data(self) -> BaseModel:
        if self._model_class is None:
            raise ValueError("Model class not loaded")
        raw_data = {name: widget.value for name, widget in self._widgets.items()}
        return self._model_class.model_validate(raw_data)
