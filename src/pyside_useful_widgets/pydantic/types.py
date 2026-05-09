import types
from abc import ABC, abstractmethod
from ast import literal_eval
from enum import Enum
from typing import Any, Generic, Literal, TypeVar, get_args, get_origin

from annotated_types import Ge, Gt, Le, Lt, MaxLen, MultipleOf
from pydantic.fields import FieldInfo
from pydantic_core import PydanticUndefined
from PySide6.QtWidgets import QComboBox, QDoubleSpinBox, QLineEdit, QSpinBox, QWidget


class DisplayName:
    def __init__(self, name: str):
        self.name = name

    @classmethod
    def get(cls, field_name: str, field_info: FieldInfo) -> str:
        for meta in field_info.metadata:
            if isinstance(meta, cls):
                return meta.name
        return field_name


T = TypeVar("T")
W = TypeVar("W", bound=QWidget, covariant=True)


class TypeWidget(ABC, Generic[T, W]):
    @abstractmethod
    def __init__(self, field_info: FieldInfo):
        pass

    @property
    @abstractmethod
    def qwidget(self) -> W:
        pass

    @property
    @abstractmethod
    def value(self) -> T:
        pass


_widgets_registry: dict[Any, type[TypeWidget[Any, QWidget]]] = {}


TW = TypeVar("TW", bound=TypeWidget[Any, QWidget])


def _register_widget(type_: Any):
    def decorator(cls: type[TW]) -> type[TW]:
        _widgets_registry[type_] = cls
        return cls

    return decorator


def create_field_widget(field_info: FieldInfo) -> TypeWidget[Any, QWidget]:
    valid_origins = {Literal, list, tuple}
    invalid_types_list = []
    if hasattr(types, "UnionType"):
        invalid_types_list.append(getattr(types, "UnionType"))
    invalid_types = tuple(invalid_types_list)

    annotation = field_info.annotation
    origin = get_origin(annotation)
    if annotation is None:
        raise ValueError("Field has no type annotation")
    if origin not in valid_origins | {None} or isinstance(annotation, invalid_types):
        raise NotImplementedError(f"Unsupported type annotation: {annotation}")

    if origin in valid_origins:
        cls = _widgets_registry.get(origin, DefaultWidget)
    elif isinstance(annotation, type) and issubclass(annotation, Enum):
        cls = _widgets_registry.get(Enum, DefaultWidget)
    else:
        cls = _widgets_registry.get(annotation, DefaultWidget)
    return cls(field_info)


@_register_widget(int)
class IntWidget(TypeWidget[int, QSpinBox]):
    def __init__(self, field_info: FieldInfo):
        self._field_info = field_info
        widget = QSpinBox()
        widget.setRange(-(2**31), 2**31 - 1)
        for meta in self._field_info.metadata:
            if isinstance(meta, Ge):
                widget.setMinimum(meta.ge)  # type: ignore
            elif isinstance(meta, Le):
                widget.setMaximum(meta.le)  # type: ignore
            elif isinstance(meta, Gt):
                widget.setMinimum(meta.gt + 1)  # type: ignore
            elif isinstance(meta, Lt):
                widget.setMaximum(meta.lt - 1)  # type: ignore
            elif isinstance(meta, MultipleOf):
                widget.setSingleStep(meta.multiple_of)  # type: ignore
        if self._field_info.default is not PydanticUndefined:
            widget.setValue(self._field_info.default)
        self._widget = widget

    @property
    def qwidget(self) -> QSpinBox:
        return self._widget

    @property
    def value(self) -> int:
        return self._widget.value()


@_register_widget(float)
class FloatWidget(TypeWidget[float, QDoubleSpinBox]):
    decimals = 5

    def __init__(self, field_info: FieldInfo):
        self._field_info = field_info
        widget = QDoubleSpinBox()
        widget.setDecimals(self.decimals)
        widget.setRange(-1e10, 1e10)
        for meta in self._field_info.metadata:
            if isinstance(meta, Ge):
                widget.setMinimum(meta.ge)  # type: ignore
            elif isinstance(meta, Le):
                widget.setMaximum(meta.le)  # type: ignore
            elif isinstance(meta, Gt):
                widget.setMinimum(meta.gt + 1 / (10**self.decimals))
            elif isinstance(meta, Lt):
                widget.setMaximum(meta.lt - 1 / (10**self.decimals))
            elif isinstance(meta, MultipleOf):
                widget.setSingleStep(meta.multiple_of)  # type: ignore
        if self._field_info.default is not PydanticUndefined:
            widget.setValue(self._field_info.default)
        self._widget = widget

    @property
    def qwidget(self) -> QDoubleSpinBox:
        return self._widget

    @property
    def value(self) -> float:
        return self._widget.value()


@_register_widget(str)
class StringWidget(TypeWidget[str, QLineEdit]):
    def __init__(self, field_info: FieldInfo):
        self._field_info = field_info
        widget = QLineEdit()
        for meta in self._field_info.metadata:
            if isinstance(meta, MaxLen):
                widget.setMaxLength(meta.max_length)  # type: ignore
        if self._field_info.default is not PydanticUndefined:
            widget.setText(self._field_info.default)
        self._widget = widget

    @property
    def qwidget(self) -> QLineEdit:
        return self._widget

    @property
    def value(self) -> str:
        return self._widget.text()


@_register_widget(bool)
class BoolWidget(TypeWidget[bool, QComboBox]):
    def __init__(self, field_info: FieldInfo):
        self._field_info = field_info
        widget = QComboBox()
        widget.addItem(str(True), userData=True)
        widget.addItem(str(False), userData=False)
        if self._field_info.default is not PydanticUndefined:
            widget.setCurrentText(str(self._field_info.default))
        self._widget = widget

    @property
    def qwidget(self) -> QComboBox:
        return self._widget

    @property
    def value(self) -> bool:
        return self._widget.currentData()


@_register_widget(Enum)
class EnumWidget(TypeWidget[Enum, QComboBox]):
    def __init__(self, field_info: FieldInfo):
        self._field_info = field_info
        choices = {x.name: x for x in field_info.annotation}  # type: ignore
        widget = QComboBox()
        for name, choice in choices.items():
            widget.addItem(name, userData=choice)
        if self._field_info.default is not PydanticUndefined:
            widget.setCurrentText(str(self._field_info.default))
        self._widget = widget

    @property
    def qwidget(self) -> QComboBox:
        return self._widget

    @property
    def value(self) -> Enum:
        return self._widget.currentData()


@_register_widget(Literal)
class LiteralWidget(TypeWidget[Any, QComboBox]):
    def __init__(self, field_info: FieldInfo):
        self._field_info = field_info
        choices = {str(x): x for x in get_args(field_info.annotation)}
        widget = QComboBox()
        for name, choice in choices.items():
            widget.addItem(name, userData=choice)
        if self._field_info.default is not PydanticUndefined:
            widget.setCurrentText(str(self._field_info.default))
        self._widget = widget

    @property
    def qwidget(self) -> QComboBox:
        return self._widget

    @property
    def value(self) -> Any:
        return self._widget.currentData()


@_register_widget(list)
@_register_widget(tuple)
class SequenceWidget(TypeWidget[Any, QLineEdit]):
    def __init__(self, field_info: FieldInfo):
        self._field_info = field_info
        widget = QLineEdit()
        if self._field_info.default is not PydanticUndefined:
            widget.setText(str(self._field_info.default))
        self._widget = widget

    @property
    def qwidget(self) -> QLineEdit:
        return self._widget

    @property
    def value(self) -> Any:
        text = self._widget.text().strip()
        try:
            return literal_eval(text)
        except (ValueError, SyntaxError):
            return text.split(",")


@_register_widget(Any)
class DefaultWidget(TypeWidget[Any, QLineEdit]):
    def __init__(self, field_info: FieldInfo):
        self._field_info = field_info
        widget = QLineEdit()
        if self._field_info.default is not PydanticUndefined:
            widget.setText(str(self._field_info.default))
        self._widget = widget

    @property
    def qwidget(self) -> QLineEdit:
        return self._widget

    @property
    def value(self) -> Any:
        return self._widget.text()
