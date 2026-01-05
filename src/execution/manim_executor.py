"""Code execution engine for running AI-generated Manim code."""

from typing import Dict, Any, Optional
import traceback


class ManimExecutor:
    """Executes AI-generated code in ManimGL Scene context."""

    def __init__(self, scene, control_panel=None):
        """
        Initialize executor.

        Args:
            scene: PaskitScene instance
            control_panel: ControlPanel instance for creating interactive controls
        """
        self.scene = scene
        self.control_panel = control_panel

    def execute(self, code: str) -> Dict[str, Any]:
        """
        Execute code in scene context.

        Args:
            code: Python code to execute

        Returns:
            Execution result dictionary
        """
        # Prepare execution environment
        # Use same dict for globals and locals to fix closure variable lookup
        globals_dict = self._build_globals()

        try:
            # Execute code with same namespace for globals/locals
            # This fixes the "state not defined" error in nested functions
            exec(code, globals_dict)

            # Auto-cache frames after execution
            self._auto_cache_frames()

            return {
                'success': True,
                'output': 'Code executed successfully',
                'error': None
            }

        except Exception as e:
            return {
                'success': False,
                'output': None,
                'error': str(e),
                'traceback': traceback.format_exc()
            }

    def _auto_cache_frames(self):
        """Auto-cache frames after code execution."""
        if not hasattr(self.scene, 'snapshot_manager'):
            return
        if not hasattr(self.scene, 'timeline'):
            return

        duration = self.scene.timeline.total_duration
        if duration > 0:
            self.scene.snapshot_manager.cache_all_frames(duration)

    def _build_globals(self) -> Dict[str, Any]:
        """Build globals dictionary for code execution."""
        import manimlib
        from loguru import logger

        globals_dict = {
            '__builtins__': __builtins__,
            'self': self.scene,  # Scene context
            'scene': self.scene,  # Alias for clarity
        }

        # Add all Manim imports
        for name in dir(manimlib):
            if not name.startswith('_'):
                globals_dict[name] = getattr(manimlib, name)

        # Add helper function for physics updaters with logging
        def add_physics_updater(mobject, updater_func):
            """Add an updater to a mobject with logging."""
            logger.info(f"[ManimExecutor] Adding updater to {type(mobject).__name__}")
            mobject.add_updater(updater_func)
            # Verify updater was added
            updaters = getattr(mobject, 'updaters', [])
            logger.info(f"[ManimExecutor] Mobject now has {len(updaters)} updaters")

        globals_dict['add_physics_updater'] = add_physics_updater

        # Add color aliases for common color names that AI might use
        if 'TEAL' in globals_dict:
            globals_dict['CYAN'] = globals_dict['TEAL']  # CYAN -> TEAL

        # Add camera movement helper function
        def move_camera(direction=None, distance=1.0, run_time=1.0):
            """
            Move camera in a direction.

            Args:
                direction: Direction vector (e.g., UP, DOWN, LEFT, RIGHT)
                distance: Distance to move
                run_time: Animation duration
            """
            if direction is None:
                direction = globals_dict.get('UP', [0, 1, 0])

            from manimlib import ApplyMethod
            target_pos = self.scene.camera.frame.get_center() + direction * distance
            self.scene.play(
                ApplyMethod(self.scene.camera.frame.move_to, target_pos),
                run_time=run_time
            )

        globals_dict['move_camera'] = move_camera

        # Add test function to verify updaters are working
        def test_physics():
            """Test function to verify physics updaters work."""
            from manimlib import Circle, RED, UP
            logger.info("[ManimExecutor] Running physics test...")

            # Create test ball
            test_ball = Circle(radius=0.3, color=RED, fill_opacity=1)
            test_ball.move_to(UP * 2)
            self.scene.add(test_ball)

            # Add simple updater
            test_state = {"y": 2.0, "vy": 0.0}
            def test_updater(mob, dt):
                test_state["vy"] += -10.0 * dt  # gravity
                test_state["y"] += test_state["vy"] * dt
                mob.move_to([0, test_state["y"], 0])
                logger.debug(f"[test_physics] y={test_state['y']:.2f}, vy={test_state['vy']:.2f}")

            test_ball.add_updater(test_updater)
            logger.info(f"[ManimExecutor] Test ball has {len(test_ball.updaters)} updaters")

            # Start wait
            self.scene.wait(3)
            logger.info("[ManimExecutor] Physics test started")

        globals_dict['test_physics'] = test_physics

        # Add control panel functions if available (HUD overlay or ControlPanel)
        if self.control_panel:
            globals_dict['controls'] = self.control_panel
            globals_dict['add_slider'] = self.control_panel.add_slider
            globals_dict['add_button'] = self.control_panel.add_button
            globals_dict['remove_control'] = self.control_panel.remove_control
            globals_dict['get_control_value'] = self.control_panel.get_value
            globals_dict['set_control_value'] = self.control_panel.set_value
            globals_dict['get_all_controls'] = self.control_panel.get_all_values
            globals_dict['clear_controls'] = self.control_panel.clear_controls

        # Add snapshot manager functions if scene has one
        if hasattr(self.scene, 'snapshot_manager'):
            sm = self.scene.snapshot_manager
            globals_dict['snapshot_manager'] = sm
            globals_dict['get_current_context'] = sm.get_current_context

            # Scene variable functions
            globals_dict['set_variable'] = sm.set_variable
            globals_dict['get_variable'] = sm.get_variable
            globals_dict['get_all_variables'] = sm.get_all_variables

            # Frame query API (for AI to query scene at specific time)
            globals_dict['query_at_time'] = sm.query_at_time
            globals_dict['get_frame_at'] = sm.get_frame_at

            # Label/annotation functions
            globals_dict['add_label'] = sm.add_label
            globals_dict['get_label'] = sm.get_label
            globals_dict['get_all_labels'] = sm.get_all_labels

            # Physics state functions
            globals_dict['set_physics_state'] = sm.set_physics_state
            globals_dict['get_physics_state'] = sm.get_physics_state
            globals_dict['update_physics'] = sm.update_physics
            globals_dict['set_formula'] = sm.set_formula

        # Import PhysicsState for AI to create instances
        from src.manim_bridge.snapshot import PhysicsState
        globals_dict['PhysicsState'] = PhysicsState

        return globals_dict
