"""Utility functions for PAskit."""

import os
import sys


def get_resource_path(relative_path: str) -> str:
    """Get absolute path to resource, works for dev and PyInstaller."""
    if hasattr(sys, '_MEIPASS'):
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    else:
        # Running in development
        base_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    return os.path.join(base_path, relative_path)


def get_icon_path(icon_name: str) -> str:
    """Get path to an icon file."""
    return get_resource_path(os.path.join("assets", "icons", f"{icon_name}.svg"))
