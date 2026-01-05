"""Control panel widget for AI-created interactive controls.

This module provides a panel where AI can create sliders, buttons,
and other interactive controls that affect the ManimGL scene.
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QSlider,
    QPushButton, QDoubleSpinBox, QScrollArea, QFrame, QGroupBox
)
from PyQt5.QtCore import Qt, pyqtSignal
from typing import Dict, Any, Callable, Optional
from loguru import logger


class ControlItem(QWidget):
    """Base class for control items."""

    value_changed = pyqtSignal(str, object)  # control_name, new_value

    def __init__(self, name: str, parent=None):
        super().__init__(parent)
        self.name = name

    def get_value(self) -> Any:
        """Get current value of the control."""
        raise NotImplementedError

    def set_value(self, value: Any):
        """Set value of the control."""
        raise NotImplementedError


class SliderControl(ControlItem):
    """Slider control with label and value display."""

    def __init__(self, name: str, min_val: float = 0, max_val: float = 1,
                 default: float = 0.5, step: float = 0.01, parent=None):
        super().__init__(name, parent)

        self.min_val = min_val
        self.max_val = max_val
        self.step = step
        self._value = default

        # Create layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(2)

        # Header with name and value
        header = QHBoxLayout()
        self.label = QLabel(name)
        self.label.setStyleSheet("font-weight: bold; color: #ddd;")
        header.addWidget(self.label)

        self.value_display = QLabel(f"{default:.2f}")
        self.value_display.setStyleSheet("color: #88c0d0;")
        header.addWidget(self.value_display)

        layout.addLayout(header)

        # Slider
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setMinimum(0)
        self.slider.setMaximum(int((max_val - min_val) / step))
        self.slider.setValue(int((default - min_val) / step))
        self.slider.setStyleSheet("""
            QSlider::groove:horizontal {
                border: 1px solid #3d3d3d;
                height: 6px;
                background: #2d2d2d;
                border-radius: 3px;
            }
            QSlider::handle:horizontal {
                background: #88c0d0;
                border: 1px solid #5c5c5c;
                width: 14px;
                margin: -5px 0;
                border-radius: 7px;
            }
            QSlider::handle:horizontal:hover {
                background: #a3d4e0;
            }
        """)
        self.slider.valueChanged.connect(self._on_slider_changed)
        layout.addWidget(self.slider)

    def _on_slider_changed(self, value: int):
        self._value = self.min_val + value * self.step
        self.value_display.setText(f"{self._value:.2f}")
        self.value_changed.emit(self.name, self._value)

    def get_value(self) -> float:
        return self._value

    def set_value(self, value: float):
        self._value = max(self.min_val, min(self.max_val, value))
        slider_val = int((self._value - self.min_val) / self.step)
        self.slider.setValue(slider_val)


class ButtonControl(ControlItem):
    """Button control."""

    clicked = pyqtSignal(str)  # control_name

    def __init__(self, name: str, text: str = None, parent=None):
        super().__init__(name, parent)

        self._clicked_count = 0

        layout = QHBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)

        self.button = QPushButton(text or name)
        self.button.setStyleSheet("""
            QPushButton {
                background-color: #5e81ac;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #81a1c1;
            }
            QPushButton:pressed {
                background-color: #4c566a;
            }
        """)
        self.button.clicked.connect(self._on_clicked)
        layout.addWidget(self.button)

    def _on_clicked(self):
        self._clicked_count += 1
        self.clicked.emit(self.name)
        self.value_changed.emit(self.name, self._clicked_count)

    def get_value(self) -> int:
        """Returns the number of times the button was clicked."""
        return self._clicked_count

    def set_value(self, value: int):
        self._clicked_count = value


class ControlPanel(QWidget):
    """Panel containing AI-created controls."""

    control_changed = pyqtSignal(str, object)  # control_name, new_value

    def __init__(self, parent=None):
        super().__init__(parent)

        self.controls: Dict[str, ControlItem] = {}

        # Set up layout
        self.setMinimumWidth(200)
        self.setMaximumWidth(300)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Header
        header = QLabel("Controls")
        header.setStyleSheet("""
            QLabel {
                background-color: #3d3d3d;
                color: #d8dee9;
                padding: 8px;
                font-weight: bold;
                font-size: 14px;
            }
        """)
        main_layout.addWidget(header)

        # Scroll area for controls
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: #2d2d2d;
            }
        """)

        # Container for controls
        self.container = QWidget()
        self.container_layout = QVBoxLayout(self.container)
        self.container_layout.setContentsMargins(5, 5, 5, 5)
        self.container_layout.setSpacing(10)
        self.container_layout.addStretch()

        scroll.setWidget(self.container)
        main_layout.addWidget(scroll)

        # Style the panel
        self.setStyleSheet("""
            QWidget {
                background-color: #2d2d2d;
            }
        """)

        logger.info("[ControlPanel] Initialized")

    def add_slider(self, name: str, min_val: float = 0, max_val: float = 1,
                   default: float = 0.5, step: float = 0.01) -> SliderControl:
        """
        Add a slider control.

        Args:
            name: Unique name for the control
            min_val: Minimum value
            max_val: Maximum value
            default: Default value
            step: Step size

        Returns:
            The created SliderControl
        """
        if name in self.controls:
            logger.warning(f"[ControlPanel] Control '{name}' already exists, removing old one")
            self.remove_control(name)

        control = SliderControl(name, min_val, max_val, default, step)
        control.value_changed.connect(self._on_control_changed)

        self._add_control(name, control)
        logger.info(f"[ControlPanel] Added slider: {name} ({min_val} - {max_val})")
        return control

    def add_button(self, name: str, text: str = None) -> ButtonControl:
        """
        Add a button control.

        Args:
            name: Unique name for the control
            text: Button text (defaults to name)

        Returns:
            The created ButtonControl
        """
        if name in self.controls:
            logger.warning(f"[ControlPanel] Control '{name}' already exists, removing old one")
            self.remove_control(name)

        control = ButtonControl(name, text)
        control.value_changed.connect(self._on_control_changed)

        self._add_control(name, control)
        logger.info(f"[ControlPanel] Added button: {name}")
        return control

    def _add_control(self, name: str, control: ControlItem):
        """Add a control to the panel."""
        self.controls[name] = control
        # Insert before the stretch
        count = self.container_layout.count()
        self.container_layout.insertWidget(count - 1, control)

    def remove_control(self, name: str) -> bool:
        """
        Remove a control by name.

        Args:
            name: Name of the control to remove

        Returns:
            True if removed, False if not found
        """
        if name not in self.controls:
            return False

        control = self.controls.pop(name)
        control.setParent(None)
        control.deleteLater()
        logger.info(f"[ControlPanel] Removed control: {name}")
        return True

    def clear_controls(self):
        """Remove all controls."""
        for name in list(self.controls.keys()):
            self.remove_control(name)
        logger.info("[ControlPanel] Cleared all controls")

    def get_value(self, name: str) -> Optional[Any]:
        """
        Get the value of a control.

        Args:
            name: Name of the control

        Returns:
            The control's value, or None if not found
        """
        if name in self.controls:
            return self.controls[name].get_value()
        return None

    def set_value(self, name: str, value: Any) -> bool:
        """
        Set the value of a control.

        Args:
            name: Name of the control
            value: New value

        Returns:
            True if set, False if control not found
        """
        if name in self.controls:
            self.controls[name].set_value(value)
            return True
        return False

    def get_all_values(self) -> Dict[str, Any]:
        """Get all control values as a dictionary."""
        return {name: ctrl.get_value() for name, ctrl in self.controls.items()}

    def _on_control_changed(self, name: str, value: Any):
        """Handle control value change."""
        self.control_changed.emit(name, value)
        logger.debug(f"[ControlPanel] Control changed: {name} = {value}")
