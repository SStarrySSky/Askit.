"""HUD-style control overlay for the render panel.

This module provides controls that overlay on top of the ManimGL scene,
positioned in the top-right corner like game HUD elements.
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QSlider,
    QPushButton, QFrame, QGraphicsOpacityEffect
)
from PyQt5.QtCore import Qt, pyqtSignal, QPropertyAnimation
from PyQt5.QtGui import QPainter, QColor, QFont
from typing import Dict, Any, Optional
from loguru import logger


class HUDSlider(QFrame):
    """Slider control with minimal styling matching timeline."""

    value_changed = pyqtSignal(str, float)  # name, value

    def __init__(self, name: str, min_val: float = 0, max_val: float = 1,
                 default: float = 0.5, step: float = 0.01, parent=None):
        super().__init__(parent)
        self.name = name
        self.min_val = min_val
        self.max_val = max_val
        self.step = step
        self._value = default

        self.setFixedWidth(200)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 6, 10, 6)
        layout.setSpacing(4)

        # Header with name and value
        header = QHBoxLayout()
        header.setSpacing(8)

        self.label = QLabel(self.name)
        self.label.setStyleSheet("color: #ffffff; font-family: 'Segoe UI'; font-size: 10pt;")
        header.addWidget(self.label)

        header.addStretch()

        self.value_label = QLabel(f"{self._value:.2f}")
        self.value_label.setStyleSheet("color: #ffffff; font-family: 'Consolas'; font-size: 10pt; font-weight: bold;")
        header.addWidget(self.value_label)
        layout.addLayout(header)

        # Slider - matching timeline style
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setMinimum(0)
        self.slider.setMaximum(int((self.max_val - self.min_val) / self.step))
        self.slider.setValue(int((self._value - self.min_val) / self.step))
        self.slider.valueChanged.connect(self._on_value_changed)
        layout.addWidget(self.slider)

        # Minimal style matching timeline
        self.setStyleSheet("""
            QFrame {
                background-color: rgba(60, 60, 60, 0.8);
                border: none;
                border-radius: 6px;
            }
            QSlider::groove:horizontal {
                border: none;
                height: 6px;
                background: rgba(255, 255, 255, 0.3);
                border-radius: 3px;
            }
            QSlider::handle:horizontal {
                background: #ffffff;
                border: none;
                width: 14px;
                margin: -5px 0;
                border-radius: 7px;
            }
            QSlider::handle:horizontal:hover {
                background: #e0e0e0;
            }
            QSlider::sub-page:horizontal {
                background: #ffffff;
                border-radius: 3px;
            }
        """)

    def _on_value_changed(self, slider_val):
        self._value = self.min_val + slider_val * self.step
        self.value_label.setText(f"{self._value:.2f}")
        self.value_changed.emit(self.name, self._value)

    def get_value(self) -> float:
        return self._value

    def set_value(self, value: float):
        self._value = max(self.min_val, min(self.max_val, value))
        slider_val = int((self._value - self.min_val) / self.step)
        self.slider.blockSignals(True)
        self.slider.setValue(slider_val)
        self.slider.blockSignals(False)
        self.value_label.setText(f"{self._value:.2f}")


class HUDButton(QFrame):
    """Button control with minimal styling matching timeline."""

    clicked = pyqtSignal(str)  # name

    def __init__(self, name: str, text: str = None, parent=None):
        super().__init__(parent)
        self.name = name
        self._click_count = 0

        self.setFixedWidth(200)
        self.setup_ui(text or name)

    def setup_ui(self, text: str):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 6, 10, 6)

        self.button = QPushButton(text)
        self.button.clicked.connect(self._on_clicked)
        layout.addWidget(self.button)

        # Minimal style matching timeline buttons
        self.setStyleSheet("""
            QFrame {
                background-color: transparent;
                border: none;
            }
            QPushButton {
                background-color: rgba(60, 60, 60, 0.8);
                color: #ffffff;
                border: none;
                padding: 8px 16px;
                border-radius: 6px;
                font-family: 'Segoe UI';
                font-size: 10pt;
            }
            QPushButton:hover {
                background-color: rgba(80, 80, 80, 0.9);
            }
            QPushButton:pressed {
                background-color: rgba(100, 100, 100, 0.9);
            }
        """)

    def _on_clicked(self):
        self._click_count += 1
        self.clicked.emit(self.name)

    def get_value(self) -> int:
        return self._click_count


class HUDControlOverlay(QWidget):
    """Overlay widget that displays controls in the top-right corner."""

    control_changed = pyqtSignal(str, object)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.controls: Dict[str, QWidget] = {}

        # Make transparent and don't receive mouse events on empty areas
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_TransparentForMouseEvents, False)

        # Create layout - align to top-right
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(10, 10, 10, 10)
        self.layout.setSpacing(6)
        self.layout.setAlignment(Qt.AlignTop | Qt.AlignRight)

        logger.info("[HUDControlOverlay] Initialized")

    def wheelEvent(self, event):
        """Ignore wheel events, let parent handle zoom."""
        event.ignore()

    def add_slider(self, name: str, min_val: float = 0, max_val: float = 1,
                   default: float = 0.5, step: float = 0.01) -> HUDSlider:
        """Add a slider control."""
        if name in self.controls:
            self.remove_control(name)

        slider = HUDSlider(name, min_val, max_val, default, step)
        slider.value_changed.connect(self._on_control_changed)

        self.controls[name] = slider
        self.layout.addWidget(slider, alignment=Qt.AlignRight)

        logger.info(f"[HUDControlOverlay] Added slider: {name}")
        return slider

    def add_button(self, name: str, text: str = None) -> HUDButton:
        """Add a button control."""
        if name in self.controls:
            self.remove_control(name)

        button = HUDButton(name, text)
        button.clicked.connect(lambda n: self._on_control_changed(n, self.controls[n].get_value()))

        self.controls[name] = button
        self.layout.addWidget(button, alignment=Qt.AlignRight)

        logger.info(f"[HUDControlOverlay] Added button: {name}")
        return button

    def remove_control(self, name: str) -> bool:
        """Remove a control by name."""
        if name not in self.controls:
            return False

        control = self.controls.pop(name)
        self.layout.removeWidget(control)
        control.deleteLater()

        logger.info(f"[HUDControlOverlay] Removed control: {name}")
        return True

    def clear_controls(self):
        """Remove all controls."""
        for name in list(self.controls.keys()):
            self.remove_control(name)
        logger.info("[HUDControlOverlay] Cleared all controls")

    def get_value(self, name: str) -> Optional[Any]:
        """Get control value."""
        if name in self.controls:
            return self.controls[name].get_value()
        return None

    def set_value(self, name: str, value: Any) -> bool:
        """Set control value."""
        if name in self.controls and hasattr(self.controls[name], 'set_value'):
            self.controls[name].set_value(value)
            return True
        return False

    def get_all_values(self) -> Dict[str, Any]:
        """Get all control values."""
        return {name: ctrl.get_value() for name, ctrl in self.controls.items()}

    def _on_control_changed(self, name: str, value: Any):
        """Handle control value change."""
        self.control_changed.emit(name, value)

    def resizeEvent(self, event):
        """Handle resize to match parent."""
        super().resizeEvent(event)

    def paintEvent(self, event):
        """Paint transparent background."""
        # Don't paint anything - fully transparent
        pass
