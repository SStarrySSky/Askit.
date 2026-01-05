"""Custom data types and enums for PAskit application."""

from enum import Enum
from typing import Tuple, Any
from dataclasses import dataclass, field
from datetime import datetime


# Type aliases
Vector3 = Tuple[float, float, float]
Vector2 = Tuple[float, float]
Color = Tuple[float, float, float]  # RGB values 0-1
ColorRGBA = Tuple[float, float, float, float]  # RGBA values 0-1


class AnimationState(Enum):
    """Animation playback state."""
    STOPPED = "stopped"
    PLAYING = "playing"
    PAUSED = "paused"


class EasingType(Enum):
    """Animation easing functions."""
    LINEAR = "linear"
    EASE_IN = "ease_in"
    EASE_OUT = "ease_out"
    EASE_IN_OUT = "ease_in_out"
    EASE_IN_QUAD = "ease_in_quad"
    EASE_OUT_QUAD = "ease_out_quad"
    EASE_IN_OUT_QUAD = "ease_in_out_quad"
    EASE_IN_CUBIC = "ease_in_cubic"
    EASE_OUT_CUBIC = "ease_out_cubic"
    EASE_IN_OUT_CUBIC = "ease_in_out_cubic"


class ObjectType(Enum):
    """Types of renderable objects."""
    SPHERE = "sphere"
    CUBE = "cube"
    CYLINDER = "cylinder"
    CONE = "cone"
    PLANE = "plane"
    LINE = "line"
    ARROW = "arrow"
    TEXT = "text"
    GRAPH_2D = "graph_2d"
    GRAPH_3D = "graph_3d"
    CUSTOM = "custom"


class ControlType(Enum):
    """Types of scene controls."""
    SLIDER = "slider"
    BUTTON = "button"
    LABEL = "label"
    DROPDOWN = "dropdown"


class AIProvider(Enum):
    """Supported AI providers."""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    OLLAMA = "ollama"


@dataclass
class Message:
    """Chat message data structure."""
    role: str  # "user" or "assistant"
    content: str
    timestamp: datetime = field(default_factory=datetime.now)
    code_blocks: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class ExecutionResult:
    """Result of code execution."""
    success: bool
    output: Any = None
    error: str = None
    traceback: str = None
    execution_time: float = 0.0


@dataclass
class SceneSnapshot:
    """Snapshot of scene state."""
    timestamp: datetime
    objects: dict[str, Any]
    camera: dict[str, Any]
    controls: dict[str, Any]
    animation_state: dict[str, Any]
    custom_data: dict[str, Any] = field(default_factory=dict)


@dataclass
class AnimationKeyframe:
    """Animation keyframe data."""
    time: float
    value: Any
    easing: EasingType = EasingType.LINEAR
