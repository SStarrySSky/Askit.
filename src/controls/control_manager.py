"""Control manager for scene interactive controls."""

from typing import Dict, Any, Optional
from loguru import logger


class ControlManager:
    """Manager for interactive controls in the scene."""

    def __init__(self, scene):
        """
        Initialize control manager.

        Args:
            scene: PaskitScene instance
        """
        self.scene = scene
        self.controls: Dict[str, Any] = {}
        logger.info("Control manager initialized")

    def create_slider(self, name: str, min_val: float, max_val: float, default: float) -> Dict[str, Any]:
        """
        Create a slider control.

        Args:
            name: Control name
            min_val: Minimum value
            max_val: Maximum value
            default: Default value

        Returns:
            Control data dictionary
        """
        control = {
            'type': 'slider',
            'name': name,
            'min': min_val,
            'max': max_val,
            'value': default
        }
        self.controls[name] = control
        logger.info(f"Created slider: {name}")
        return control

    def create_button(self, name: str, label: str) -> Dict[str, Any]:
        """
        Create a button control.

        Args:
            name: Control name
            label: Button label

        Returns:
            Control data dictionary
        """
        control = {
            'type': 'button',
            'name': name,
            'label': label,
            'pressed': False
        }
        self.controls[name] = control
        logger.info(f"Created button: {name}")
        return control

    def get_value(self, name: str) -> Optional[Any]:
        """Get control value."""
        control = self.controls.get(name)
        if control:
            return control.get('value')
        return None

    def set_value(self, name: str, value: Any):
        """Set control value."""
        if name in self.controls:
            self.controls[name]['value'] = value

    def remove_control(self, name: str):
        """Remove a control."""
        if name in self.controls:
            del self.controls[name]
            logger.info(f"Removed control: {name}")

    def clear_all(self):
        """Clear all controls."""
        self.controls.clear()
        logger.info("Cleared all controls")
