"""ManimGL integration bridge for PyQt6.

This module provides the integration layer between ManimGL and PyQt6,
allowing ManimGL scenes to be rendered in a QOpenGLWidget.
"""

from .scene_wrapper import PaskitScene
from .animation_controller import AnimationController
from .animation_timeline import AnimationTimeline
from .snapshot import FrameSnapshot, SnapshotManager, PhysicsState

__all__ = ['PaskitScene', 'AnimationController', 'AnimationTimeline', 'FrameSnapshot', 'SnapshotManager', 'PhysicsState']
