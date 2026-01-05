"""Settings dialog with modern design."""

import sys
import os
import ctypes
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QWidget,
    QLabel, QLineEdit, QPushButton, QComboBox,
    QScrollArea, QFrame, QCompleter, QMessageBox,
    QListWidget, QListWidgetItem, QStackedWidget,
    QGridLayout, QSizePolicy, QGraphicsOpacityEffect
)
from PyQt5.QtCore import Qt, pyqtSignal, QPropertyAnimation, QEasingCurve, QSize, QTimer
from PyQt5.QtGui import QFont, QIcon, QColor
from qasync import asyncSlot
from typing import Optional, List

from src.core.config import Config
from src.ai.openai_provider import OpenAIProvider

COLORS = {
    "bg": "#1e1e1e",
    "sidebar": "#1e1e1e",
    "content": "#1e1e1e",
    "border": "#3d3d3d",
    "text": "#ffffff",
    "text_muted": "#aaa",
    "accent": "#7f6df2",
    "accent_hover": "#9d8df4",
    "accent_pressed": "#6a5cd6",
    "input_bg": "#2a2a2a",
    "hover": "#404040",
    "card_bg": "#2d2d2d"
}


def set_title_bar_color(hwnd, color):
    """Set Windows title bar color using DWM API."""
    if sys.platform != 'win32':
        return
    try:
        DWMWA_CAPTION_COLOR = 35
        ctypes.windll.dwmapi.DwmSetWindowAttribute(
            hwnd,
            DWMWA_CAPTION_COLOR,
            ctypes.byref(ctypes.c_int(color)),
            ctypes.sizeof(ctypes.c_int)
        )
    except Exception:
        pass


class ModelCard(QFrame):
    """Model card for grid display."""
    clicked = pyqtSignal(str)

    def __init__(self, model_id: str, model_name: str, description: str = "", parent=None):
        super().__init__(parent)
        self.model_id = model_id
        self.selected = False
        self.setup_ui(model_name, description)

    def setup_ui(self, model_name: str, description: str):
        self.setFixedSize(200, 120)
        self.setCursor(Qt.PointingHandCursor)
        self.update_style()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(8)

        # Model name
        name_label = QLabel(model_name)
        name_label.setFont(QFont("Segoe UI", 12, QFont.Bold))
        name_label.setStyleSheet(f"color: {COLORS['text']}; background: transparent;")
        name_label.setWordWrap(True)
        layout.addWidget(name_label)

        # Description
        if description:
            desc_label = QLabel(description)
            desc_label.setFont(QFont("Segoe UI", 9))
            desc_label.setStyleSheet(f"color: {COLORS['text_muted']}; background: transparent;")
            desc_label.setWordWrap(True)
            layout.addWidget(desc_label)

        layout.addStretch()

    def update_style(self):
        if self.selected:
            self.setStyleSheet(f"""
                ModelCard {{
                    background: {COLORS['accent']};
                    border: 2px solid {COLORS['accent']};
                    border-radius: 12px;
                }}
                ModelCard:hover {{
                    background: {COLORS['accent_hover']};
                }}
            """)
        else:
            self.setStyleSheet(f"""
                ModelCard {{
                    background: {COLORS['card_bg']};
                    border: 1px solid {COLORS['border']};
                    border-radius: 12px;
                }}
                ModelCard:hover {{
                    border-color: {COLORS['accent']};
                    background: {COLORS['hover']};
                }}
            """)

    def set_selected(self, selected: bool):
        self.selected = selected
        self.update_style()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked.emit(self.model_id)
        super().mousePressEvent(event)


class ModelGridSelector(QWidget):
    """Grid selector for models with animation."""
    model_selected = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.cards = {}
        self.all_models = []
        self.current_model = None
        self.setup_ui()
        self.setMaximumHeight(0)
        self._target_height = 400

    def setup_ui(self):
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 16, 0, 16)
        self.main_layout.setSpacing(12)

        # Title
        title = QLabel("Select Model")
        title.setFont(QFont("Segoe UI", 12, QFont.Bold))
        title.setStyleSheet(f"color: {COLORS['text']};")
        self.main_layout.addWidget(title)

        # Search box
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Search models...")
        self.search_box.setStyleSheet(f"""
            QLineEdit {{
                background: {COLORS['input_bg']};
                border: 1px solid {COLORS['border']};
                border-radius: 8px;
                padding: 10px;
                color: {COLORS['text']};
            }}
            QLineEdit:focus {{
                border-color: {COLORS['accent']};
            }}
        """)
        self.search_box.textChanged.connect(self.filter_models)
        self.main_layout.addWidget(self.search_box)

        # Scroll area for grid
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setStyleSheet(f"""
            QScrollArea {{
                background: transparent;
                border: none;
            }}
            QScrollArea > QWidget > QWidget {{
                background: transparent;
            }}
        """)

        # Grid container
        self.grid_widget = QWidget()
        self.grid_layout = QGridLayout(self.grid_widget)
        self.grid_layout.setSpacing(12)
        self.grid_layout.setContentsMargins(0, 8, 0, 8)

        scroll.setWidget(self.grid_widget)
        self.main_layout.addWidget(scroll)

    def set_models(self, models: List[dict]):
        """Set models to display. Each model: {id, name, description}"""
        self.all_models = models
        self._display_models(models)

    def _display_models(self, models: List[dict]):
        """Display filtered models in grid."""
        for card in self.cards.values():
            card.deleteLater()
        self.cards.clear()

        for i, model in enumerate(models):
            card = ModelCard(
                model.get('id', ''),
                model.get('name', model.get('id', '')),
                model.get('description', '')
            )
            card.clicked.connect(self.on_card_clicked)
            row, col = divmod(i, 3)
            self.grid_layout.addWidget(card, row, col)
            self.cards[model.get('id', '')] = card
            if model.get('id') == self.current_model:
                card.set_selected(True)

    def filter_models(self, text: str):
        """Filter models by search text."""
        if not text:
            self._display_models(self.all_models)
        else:
            filtered = [m for m in self.all_models
                       if text.lower() in m.get('name', '').lower()
                       or text.lower() in m.get('id', '').lower()]
            self._display_models(filtered)

    def on_card_clicked(self, model_id: str):
        # Deselect previous
        if self.current_model and self.current_model in self.cards:
            self.cards[self.current_model].set_selected(False)
        # Select new
        self.current_model = model_id
        if model_id in self.cards:
            self.cards[model_id].set_selected(True)
        self.model_selected.emit(model_id)

    def show_animated(self):
        """Show with slide-down animation."""
        self.anim = QPropertyAnimation(self, b"maximumHeight")
        self.anim.setDuration(300)
        self.anim.setStartValue(0)
        self.anim.setEndValue(self._target_height)
        self.anim.setEasingCurve(QEasingCurve.OutCubic)
        self.anim.start()

    def hide_animated(self):
        """Hide with slide-up animation."""
        self.anim = QPropertyAnimation(self, b"maximumHeight")
        self.anim.setDuration(200)
        self.anim.setStartValue(self.height())
        self.anim.setEndValue(0)
        self.anim.setEasingCurve(QEasingCurve.InCubic)
        self.anim.start()

    def get_selected_model(self):
        return self.current_model


class ProviderConfigWidget(QWidget):
    """Provider config widget without model input."""
    def __init__(self, provider_name, parent=None):
        super().__init__(parent)
        self.provider_name = provider_name
        self.selected_model = None
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 16, 0, 0)
        layout.setSpacing(12)

        label_style = f"color: {COLORS['text']};"
        input_style = f"""
            QLineEdit {{
                background: {COLORS['input_bg']};
                border: 1px solid {COLORS['border']};
                border-radius: 8px;
                padding: 10px;
                color: {COLORS['text']};
            }}
            QLineEdit:focus {{
                border-color: {COLORS['accent']};
            }}
        """

        # API Key
        api_label = QLabel("API Key")
        api_label.setStyleSheet(label_style)
        layout.addWidget(api_label)

        self.api_key = QLineEdit()
        self.api_key.setEchoMode(QLineEdit.Password)
        self.api_key.setPlaceholderText("Enter your API key")
        self.api_key.setStyleSheet(input_style)
        layout.addWidget(self.api_key)

        # Base URL
        url_label = QLabel("Base URL")
        url_label.setStyleSheet(label_style)
        layout.addWidget(url_label)

        self.base_url = QLineEdit()
        self.base_url.setPlaceholderText("https://api.openai.com/v1")
        self.base_url.setStyleSheet(input_style)
        layout.addWidget(self.base_url)

    def get_config(self):
        return {
            "api_key": self.api_key.text(),
            "base_url": self.base_url.text(),
            "model": self.selected_model
        }

    def set_config(self, cfg):
        self.api_key.setText(cfg.get("api_key", ""))
        self.base_url.setText(cfg.get("base_url", ""))


class SettingsDialog(QDialog):
    """Settings dialog with modern design."""
    def __init__(self, config: Config, parent=None):
        super().__init__(parent)
        self.config = config
        self.provider_widgets = {}
        self.model_selector_visible = False
        self.setup_ui()
        self.load_settings()
        QTimer.singleShot(10, self._set_title_bar_color)

    def _set_title_bar_color(self):
        dark_color = 0x001e1e1e
        set_title_bar_color(int(self.winId()), dark_color)

    def setup_ui(self):
        self.setWindowTitle("Settings")
        icon_path = os.path.join(os.path.dirname(__file__), "..", "assets", "icons", "settings.svg")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        self.setMinimumSize(1100, 750)
        self.resize(1100, 750)
        self.setStyleSheet(f"background: {COLORS['bg']};")

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(16)

        # Content area
        content_layout = QHBoxLayout()
        content_layout.setSpacing(16)

        self.setup_sidebar()
        content_layout.addWidget(self.sidebar)

        self.stack = QStackedWidget()
        self.stack.setStyleSheet(f"background: {COLORS['bg']};")
        self.setup_providers_page()
        self.setup_graphics_page()
        self.setup_feature_page()
        self.setup_about_page()
        content_layout.addWidget(self.stack, 1)

        main_layout.addLayout(content_layout, 1)

        # Save button at bottom right
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        self.save_btn = QPushButton("Save")
        self.save_btn.setCursor(Qt.PointingHandCursor)
        self.save_btn.setStyleSheet(f"""
            QPushButton {{
                background: {COLORS['accent']};
                border: none;
                border-radius: 8px;
                padding: 12px 32px;
                color: {COLORS['text']};
                font-weight: bold;
            }}
            QPushButton:hover {{
                background: {COLORS['accent_hover']};
            }}
            QPushButton:pressed {{
                background: {COLORS['accent_pressed']};
            }}
        """)
        self.save_btn.clicked.connect(self.on_save)
        btn_layout.addWidget(self.save_btn)
        main_layout.addLayout(btn_layout)

    def setup_sidebar(self):
        self.sidebar = QListWidget()
        self.sidebar.setFixedWidth(200)
        self.sidebar.setStyleSheet(f"""
            QListWidget {{
                background: {COLORS['bg']};
                border: none;
                color: {COLORS['text']};
                outline: none;
            }}
            QListWidget::item {{
                padding: 16px 18px;
                margin: 4px 0px;
                border-radius: 8px;
                color: {COLORS['text']};
                font-weight: bold;
            }}
            QListWidget::item:selected {{
                background: {COLORS['accent']};
                color: {COLORS['text']};
            }}
            QListWidget::item:hover:!selected {{
                background: {COLORS['hover']};
            }}
        """)
        self.sidebar.setFocusPolicy(Qt.NoFocus)
        self.sidebar.addItem("AI Providers")
        self.sidebar.addItem("Graphics")
        self.sidebar.addItem("Feature")
        self.sidebar.addItem("About")
        self.sidebar.setCurrentRow(0)
        self.sidebar.currentRowChanged.connect(self.on_page_changed)

    def on_page_changed(self, idx):
        self.stack.setCurrentIndex(idx)

    def setup_providers_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(32, 32, 32, 32)
        layout.setSpacing(16)

        title = QLabel("AI Providers")
        title.setFont(QFont("Segoe UI", 18, QFont.Bold))
        title.setStyleSheet(f"color: {COLORS['text']};")
        layout.addWidget(title)

        self.claude_widget = ProviderConfigWidget("Claude")
        layout.addWidget(self.claude_widget)

        # Fetch models button
        self.fetch_btn = QPushButton("Fetch Models")
        self.fetch_btn.setCursor(Qt.PointingHandCursor)
        self.fetch_btn.setStyleSheet(f"""
            QPushButton {{
                background: {COLORS['accent']};
                border: none;
                border-radius: 8px;
                padding: 12px 24px;
                color: {COLORS['text']};
                font-weight: bold;
            }}
            QPushButton:hover {{
                background: {COLORS['accent_hover']};
            }}
            QPushButton:pressed {{
                background: {COLORS['accent_pressed']};
            }}
        """)
        self.fetch_btn.clicked.connect(self.on_fetch_models)
        layout.addWidget(self.fetch_btn)

        # Model grid selector (hidden initially)
        self.model_grid = ModelGridSelector()
        self.model_grid.model_selected.connect(self.on_model_selected)
        layout.addWidget(self.model_grid)

        layout.addStretch()
        self.stack.addWidget(page)

    def setup_graphics_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(32, 32, 32, 32)
        layout.setSpacing(16)

        title = QLabel("Graphics")
        title.setFont(QFont("Segoe UI", 18, QFont.Bold))
        title.setStyleSheet(f"color: {COLORS['text']};")
        layout.addWidget(title)

        fps_label = QLabel("Frame Rate")
        fps_label.setStyleSheet(f"color: {COLORS['text']};")
        layout.addWidget(fps_label)

        self.fps_combo = QComboBox()
        self.fps_combo.addItems(["30 FPS", "60 FPS", "120 FPS"])
        self.fps_combo.setStyleSheet(f"""
            QComboBox {{
                background: {COLORS['input_bg']};
                border: 1px solid {COLORS['border']};
                border-radius: 8px;
                padding: 10px;
                color: {COLORS['text']};
            }}
            QComboBox::drop-down {{ border: none; }}
            QComboBox QAbstractItemView {{
                background: {COLORS['input_bg']};
                border: 1px solid {COLORS['border']};
                border-radius: 8px;
                color: {COLORS['text']};
                selection-background-color: {COLORS['accent']};
            }}
        """)
        layout.addWidget(self.fps_combo)
        layout.addStretch()
        self.stack.addWidget(page)

    def setup_feature_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(32, 32, 32, 32)
        layout.setSpacing(20)

        title = QLabel("Feature Mode")
        title.setFont(QFont("Segoe UI", 18, QFont.Bold))
        title.setStyleSheet(f"color: {COLORS['text']};")
        layout.addWidget(title)

        desc = QLabel("Select a mode based on your needs")
        desc.setStyleSheet(f"color: {COLORS['text_muted']};")
        layout.addWidget(desc)

        # Mode buttons
        self.mode_buttons = {}
        modes = [
            ("student", "Student Mode", "Basic features with guidance"),
            ("competition", "Competition Mode", "Optimized for contests"),
            ("engineering", "Engineering Mode", "Full features, no limits"),
        ]
        for mode_id, name, tip in modes:
            btn = QPushButton(name)
            btn.setToolTip(tip)
            btn.setCursor(Qt.PointingHandCursor)
            btn.setCheckable(True)
            btn.clicked.connect(lambda c, m=mode_id: self._on_mode_selected(m))
            self.mode_buttons[mode_id] = btn
            layout.addWidget(btn)
        self._update_mode_buttons()
        self._apply_mode_button_style()

        layout.addStretch()
        self.stack.addWidget(page)

    def _apply_mode_button_style(self):
        for btn in self.mode_buttons.values():
            btn.setStyleSheet(f"""
                QPushButton {{
                    background: {COLORS['input_bg']};
                    border: 1px solid {COLORS['border']};
                    border-radius: 8px;
                    padding: 16px;
                    color: {COLORS['text']};
                    font-size: 14px;
                    text-align: left;
                }}
                QPushButton:hover {{
                    border-color: {COLORS['accent']};
                }}
                QPushButton:checked {{
                    background: {COLORS['accent']};
                    border-color: {COLORS['accent']};
                }}
            """)

    def _on_mode_selected(self, mode_id: str):
        self.config.feature_mode = mode_id
        self._update_mode_buttons()

    def _update_mode_buttons(self):
        current = self.config.feature_mode
        for m, btn in self.mode_buttons.items():
            btn.setChecked(m == current)

    def setup_about_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(32, 32, 32, 32)
        layout.setSpacing(8)
        layout.setAlignment(Qt.AlignTop | Qt.AlignLeft)

        title = QLabel("About")
        title.setFont(QFont("Segoe UI", 18, QFont.Bold))
        title.setStyleSheet(f"color: {COLORS['text']};")
        layout.addWidget(title)

        layout.addSpacing(16)

        app_name = QLabel("Askit.")
        app_name.setFont(QFont("Consolas", 36, QFont.Bold))
        app_name.setStyleSheet(f"color: {COLORS['text']};")
        layout.addWidget(app_name)

        version = QLabel("Version 1.1")
        version.setFont(QFont("Segoe UI", 14))
        version.setStyleSheet(f"color: {COLORS['text_muted']};")
        layout.addWidget(version)

        layout.addSpacing(8)

        author = QLabel("Made by Starry Sky.")
        author.setFont(QFont("Segoe UI", 12))
        author.setStyleSheet(f"color: {COLORS['text_muted']};")
        layout.addWidget(author)

        layout.addStretch()
        self.stack.addWidget(page)

    def on_fetch_models(self):
        """Fetch models from API."""
        api_key = self.claude_widget.api_key.text().strip()
        base_url = self.claude_widget.base_url.text().strip()

        if not api_key:
            QMessageBox.warning(self, "Error", "Please enter API Key first")
            return

        self.fetch_btn.setText("Fetching...")
        self.fetch_btn.setEnabled(False)
        QTimer.singleShot(100, lambda: self._do_fetch_models(api_key, base_url))

    def _do_fetch_models(self, api_key: str, base_url: str):
        """Actually fetch models."""
        try:
            provider = OpenAIProvider(
                api_key=api_key,
                base_url=base_url if base_url else None
            )
            model_ids = provider._list_models_sync()
            models = [{"id": m, "name": m, "description": ""} for m in model_ids]

            if models:
                self.model_grid.set_models(models)
                if not self.model_selector_visible:
                    self.model_grid.show_animated()
                    self.model_selector_visible = True
            else:
                QMessageBox.warning(self, "Error", "No models found")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed: {e}")
        finally:
            self.fetch_btn.setText("Fetch Models")
            self.fetch_btn.setEnabled(True)

    def on_model_selected(self, model_id: str):
        self.claude_widget.selected_model = model_id

    def on_save(self):
        """Save settings and close dialog."""
        self.save_settings()
        self.accept()

    def load_settings(self):
        """Load settings from config."""
        # Load OpenAI/compatible provider settings
        openai_cfg = self.config.openai
        if openai_cfg:
            self.claude_widget.api_key.setText(openai_cfg.api_key or "")
            self.claude_widget.base_url.setText(openai_cfg.base_url or "")

    def save_settings(self):
        """Save settings to config."""
        # Update config
        self.config.openai.api_key = self.claude_widget.api_key.text()
        self.config.openai.base_url = self.claude_widget.base_url.text()
        if self.claude_widget.selected_model:
            self.config.openai.default_model = self.claude_widget.selected_model
        # Save to file
        self.config.save()
