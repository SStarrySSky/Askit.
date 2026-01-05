"""Manim Physics Scene - Integrates physics with Manim rendering."""

from typing import Dict, Optional
import logging; logger = logging.getLogger(__name__)

try:
    from manimlib import Sphere, Cube, Circle, Square
except ImportError:
    Sphere = Cube = Circle = Square = None

from .physics_bridge import PhysicsBridge, PhysicsObject


class ManimPhysicsScene:
    """Physics-enabled Manim scene wrapper."""

    def __init__(self, scene):
        self.scene = scene
        self.physics = PhysicsBridge()
        self._updater_added = False

    def set_gravity(self, gx=0, gy=-9.81, gz=0):
        self.physics.set_gravity(gx, gy, gz)

    def add_sphere(self, radius, mass, x, y, z, color="#FF0000"):
        """Add a physics sphere with Manim visual."""
        body_id = self.physics.create_sphere(radius, mass, x, y, z)
        
        if Circle is not None:
            mob = Circle(radius=radius, color=color, fill_opacity=0.8)
            mob.move_to([x, y, 0])
            self.scene.add(mob)
            self.physics.bind_mobject(body_id, mob)
        
        return body_id

    def add_box(self, hx, hy, hz, mass, x, y, z, color="#0000FF"):
        """Add a physics box with Manim visual."""
        body_id = self.physics.create_box(hx, hy, hz, mass, x, y, z)
        
        if Square is not None:
            mob = Square(side_length=hx*2, color=color, fill_opacity=0.8)
            mob.move_to([x, y, 0])
            self.scene.add(mob)
            self.physics.bind_mobject(body_id, mob)
        
        return body_id

    def add_ground(self, y=-5, width=20):
        """Add a static ground plane."""
        body_id = self.physics.create_box(width/2, 0.1, 1, 0, 0, y, 0)
        
        if Square is not None:
            from manimlib import Rectangle
            mob = Rectangle(width=width, height=0.2, color="#444444")
            mob.move_to([0, y, 0])
            self.scene.add(mob)
        
        return body_id

    def step(self, dt=1/60):
        """Step physics and sync visuals."""
        self.physics.step(dt)
        self.physics.sync_mobjects()

    def create_updater(self):
        """Create Manim updater for physics."""
        def updater(mob, dt):
            self.step(dt)
        return updater

    def start_simulation(self):
        """Start physics simulation with Manim."""
        if not self._updater_added and self.scene.mobjects:
            self.scene.mobjects[0].add_updater(self.create_updater())
            self._updater_added = True

    def apply_force(self, body_id, fx, fy, fz):
        self.physics.apply_force(body_id, fx, fy, fz)

    def apply_impulse(self, body_id, ix, iy, iz):
        self.physics.apply_impulse(body_id, ix, iy, iz)
