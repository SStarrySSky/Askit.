"""Animation timeline widget for controlling animation playback."""

import os
from PyQt5.QtWidgets import (
    QWidget, QHBoxLayout, QSlider, QPushButton, QLabel
)
from PyQt5.QtCore import Qt, pyqtSignal, QSize
from PyQt5.QtGui import QIcon, QFont


class NoWheelSlider(QSlider):
    """QSlider that ignores wheel events (allows parent to handle zoom)."""

    def wheelEvent(self, event):
        # Ignore wheel events, let parent handle zoom
        event.ignore()


class AnimationTimeline(QWidget):
    """Widget for controlling animation timeline with play/pause/reverse and seek."""

    # Signals
    play_requested = pyqtSignal()
    play_reverse_requested = pyqtSignal()
    pause_requested = pyqtSignal()
    seek_requested = pyqtSignal(float, bool)  # time in seconds, snap to keyframe
    reset_requested = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.total_duration = 0.0
        self.current_time = 0.0
        self.is_playing = False
        self.is_reversing = False
        self.is_dragging = False  # Track if user is dragging the slider
        self.setup_ui()

    def setup_ui(self):
        """Setup the UI."""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(5, 5, 15, 5)
        layout.setSpacing(4)

        # Icon path helper
        icon_dir = os.path.join(os.path.dirname(__file__), "..", "..", "..", "assets", "icons")

        # Reverse play button
        self.reverse_button = QPushButton()
        self.reverse_button.setFixedSize(40, 32)
        self.reverse_button.setIconSize(QSize(20, 20))
        self.reverse_button.setToolTip("Play Reverse")
        self.reverse_button.clicked.connect(self.on_reverse_clicked)
        rewind_path = os.path.join(icon_dir, "rewind.svg")
        if os.path.exists(rewind_path):
            self.reverse_button.setIcon(QIcon(rewind_path))
        layout.addWidget(self.reverse_button)

        # Play/Pause button
        self.play_button = QPushButton()
        self.play_button.setFixedSize(40, 32)
        self.play_button.setIconSize(QSize(20, 20))
        self.play_button.setToolTip("Play/Pause")
        self.play_button.clicked.connect(self.toggle_play_pause)
        play_path = os.path.join(icon_dir, "play.svg")
        if os.path.exists(play_path):
            self.play_button.setIcon(QIcon(play_path))
        layout.addWidget(self.play_button)

        # Reset button
        self.reset_button = QPushButton()
        self.reset_button.setFixedSize(40, 32)
        self.reset_button.setIconSize(QSize(20, 20))
        self.reset_button.setToolTip("Reset to beginning")
        self.reset_button.clicked.connect(self.on_reset_clicked)
        reset_path = os.path.join(icon_dir, "reset.svg")
        if os.path.exists(reset_path):
            self.reset_button.setIcon(QIcon(reset_path))
        layout.addWidget(self.reset_button)

        # Current time label (code font, bold)
        self.time_label = QLabel("0.00s")
        self.time_label.setFixedWidth(60)
        self.time_label.setFont(QFont("Consolas", 10, QFont.Bold))
        layout.addWidget(self.time_label)

        # Timeline slider (disable wheel events to allow parent zoom)
        self.slider = NoWheelSlider(Qt.Horizontal)
        self.slider.setMinimum(0)
        self.slider.setMaximum(1000)
        self.slider.setValue(0)
        self.slider.sliderPressed.connect(self.on_slider_pressed)
        self.slider.sliderMoved.connect(self.on_slider_moved)
        self.slider.sliderReleased.connect(self.on_slider_released)
        layout.addWidget(self.slider)

        # Total duration label (code font, bold)
        self.duration_label = QLabel("/ 0.00s")
        self.duration_label.setFixedWidth(70)
        self.duration_label.setFont(QFont("Consolas", 10, QFont.Bold))
        layout.addWidget(self.duration_label)

        # Style the widget (match right panel background #2b2b2b)
        self.setStyleSheet("""
            QWidget {
                background-color: #2b2b2b;
            }
            QPushButton {
                background-color: rgba(60, 60, 60, 0.8);
                border: none;
                border-radius: 4px;
                padding: 4px;
            }
            QPushButton:hover {
                background-color: rgba(80, 80, 80, 0.9);
            }
            QPushButton:pressed {
                background-color: rgba(100, 100, 100, 0.9);
            }
            QLabel {
                color: #ffffff;
                background: transparent;
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

    def toggle_play_pause(self):
        """Toggle between play and pause."""
        if self.is_playing:
            self.pause()
        else:
            self.play()

    def play(self):
        """Start forward playback."""
        self.is_playing = True
        self.is_reversing = False
        # Switch to pause icon
        pause_path = os.path.join(os.path.dirname(__file__), "..", "..", "..", "assets", "icons", "pause.svg")
        if os.path.exists(pause_path):
            self.play_button.setIcon(QIcon(pause_path))
        self.reverse_button.setStyleSheet("")
        self.play_requested.emit()

    def on_reverse_clicked(self):
        """Handle reverse button click."""
        if self.is_playing and self.is_reversing:
            self.pause()
        else:
            self.is_playing = True
            self.is_reversing = True
            # Switch to pause icon
            pause_path = os.path.join(os.path.dirname(__file__), "..", "..", "..", "assets", "icons", "pause.svg")
            if os.path.exists(pause_path):
                self.play_button.setIcon(QIcon(pause_path))
            self.play_reverse_requested.emit()

    def pause(self):
        """Pause playback."""
        self.is_playing = False
        self.is_reversing = False
        # Switch to play icon
        play_path = os.path.join(os.path.dirname(__file__), "..", "..", "..", "assets", "icons", "play.svg")
        if os.path.exists(play_path):
            self.play_button.setIcon(QIcon(play_path))
        self.pause_requested.emit()

    def on_reset_clicked(self):
        """Handle reset button click."""
        self.pause()
        self.seek_requested.emit(0.0, False)  # Reset doesn't need snap
        self.reset_requested.emit()

    def on_slider_pressed(self):
        """Handle slider press - start dragging and pause playback."""
        self.is_dragging = True
        # Pause playback while dragging for smooth seeking
        if self.is_playing:
            self.pause()

    def on_slider_moved(self, value):
        """Handle slider movement - update scene in real-time without snapping."""
        if self.total_duration > 0:
            time = (value / 1000.0) * self.total_duration
            self.current_time = time
            self.time_label.setText(f"{time:.2f}s")
            self.seek_requested.emit(time, False)  # Don't snap while dragging

    def on_slider_released(self):
        """Handle slider release - snap to keyframe if needed."""
        self.is_dragging = False
        if self.total_duration > 0:
            time = (self.slider.value() / 1000.0) * self.total_duration
            self.seek_requested.emit(time, True)  # Snap on release

    def set_duration(self, duration: float):
        """Set total animation duration."""
        self.total_duration = duration
        self.duration_label.setText(f"/ {duration:.2f}s")

    def set_current_time(self, time: float):
        """Set current playback time."""
        if self.is_dragging:
            return

        self.current_time = time
        self.time_label.setText(f"{time:.2f}s")

        if self.total_duration > 0:
            value = int((time / self.total_duration) * 1000)
            self.slider.blockSignals(True)
            self.slider.setValue(value)
            self.slider.blockSignals(False)

    def set_reversing(self, is_reversing: bool):
        """Update UI to reflect reverse playback state."""
        self.is_reversing = is_reversing

    def reset(self):
        """Reset timeline to initial state."""
        self.current_time = 0.0
        self.is_playing = False
        self.is_reversing = False
        # Switch to play icon
        play_path = os.path.join(os.path.dirname(__file__), "..", "..", "..", "assets", "icons", "play.svg")
        if os.path.exists(play_path):
            self.play_button.setIcon(QIcon(play_path))
        self.slider.setValue(0)
        self.time_label.setText("0.00s")
