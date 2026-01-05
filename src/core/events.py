"""Event bus system for loose coupling between components."""

from typing import Callable, Dict, List, Any
from loguru import logger


class EventBus:
    """Central event bus for application-wide event handling."""

    def __init__(self):
        self._listeners: Dict[str, List[Callable]] = {}

    def subscribe(self, event_type: str, callback: Callable) -> None:
        """
        Subscribe to an event type.

        Args:
            event_type: The type of event to listen for
            callback: Function to call when event is published
        """
        if event_type not in self._listeners:
            self._listeners[event_type] = []

        self._listeners[event_type].append(callback)
        logger.debug(f"Subscribed to event: {event_type}")

    def unsubscribe(self, event_type: str, callback: Callable) -> None:
        """
        Unsubscribe from an event type.

        Args:
            event_type: The type of event to stop listening for
            callback: The callback function to remove
        """
        if event_type in self._listeners:
            try:
                self._listeners[event_type].remove(callback)
                logger.debug(f"Unsubscribed from event: {event_type}")
            except ValueError:
                logger.warning(f"Callback not found for event: {event_type}")

    def publish(self, event_type: str, data: Any = None) -> None:
        """
        Publish an event to all subscribers.

        Args:
            event_type: The type of event to publish
            data: Optional data to pass to subscribers
        """
        if event_type in self._listeners:
            logger.debug(f"Publishing event: {event_type} to {len(self._listeners[event_type])} listeners")
            for callback in self._listeners[event_type]:
                try:
                    callback(data)
                except Exception as e:
                    logger.error(f"Error in event handler for {event_type}: {e}")

    def clear(self, event_type: str = None) -> None:
        """
        Clear all listeners for a specific event type, or all events.

        Args:
            event_type: Optional event type to clear. If None, clears all.
        """
        if event_type:
            if event_type in self._listeners:
                del self._listeners[event_type]
                logger.debug(f"Cleared listeners for event: {event_type}")
        else:
            self._listeners.clear()
            logger.debug("Cleared all event listeners")


# Event type constants
class Events:
    """Standard event types used throughout the application."""

    # Scene events
    SCENE_OBJECT_ADDED = "scene.object_added"
    SCENE_OBJECT_REMOVED = "scene.object_removed"
    SCENE_CLEARED = "scene.cleared"

    # Animation events
    ANIMATION_STARTED = "animation.started"
    ANIMATION_PAUSED = "animation.paused"
    ANIMATION_COMPLETED = "animation.completed"
    ANIMATION_SEEKED = "animation.seeked"

    # Control events
    CONTROL_CREATED = "control.created"
    CONTROL_REMOVED = "control.removed"
    CONTROL_VALUE_CHANGED = "control.value_changed"

    # AI events
    AI_REQUEST_STARTED = "ai.request_started"
    AI_RESPONSE_RECEIVED = "ai.response_received"
    AI_ERROR = "ai.error"

    # Code execution events
    CODE_EXECUTION_STARTED = "code.execution_started"
    CODE_EXECUTION_COMPLETED = "code.execution_completed"
    CODE_EXECUTION_ERROR = "code.execution_error"

    # Session events
    SESSION_SAVED = "session.saved"
    SESSION_LOADED = "session.loaded"
    SESSION_CLEARED = "session.cleared"

    # UI events
    UI_SETTINGS_CHANGED = "ui.settings_changed"
    UI_PROVIDER_CHANGED = "ui.provider_changed"


# Global event bus instance
_event_bus = EventBus()


def get_event_bus() -> EventBus:
    """Get the global event bus instance."""
    return _event_bus
