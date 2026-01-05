"""Physics Bridge - Connects C++ physics engine with Python/Manim."""

import sys
import os
from typing import Dict, List, Optional
from dataclasses import dataclass, field
import logging; logger = logging.getLogger(__name__)

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

try:
    import askit_physics_py as physics
except ImportError:
    logger.warning("askit_physics_py not found")
    physics = None


@dataclass
class PhysicsObject:
    """Physics object with visual counterpart."""
    body_id: int
    shape: str
    mobject: object = None
    params: dict = field(default_factory=dict)


class PhysicsBridge:
    """Bridge between C++ physics and Manim."""

    def __init__(self):
        if physics is None:
            raise RuntimeError("Physics engine not available")
        self.world = physics.PhysicsWorld()
        self.objects: Dict[int, PhysicsObject] = {}
        self.frame_data: List[dict] = []
        self._recording = False

    def set_gravity(self, gx=0, gy=-9.81, gz=0):
        self.world.set_gravity(gx, gy, gz)

    def create_sphere(self, radius, mass, x, y, z):
        body_id = self.world.create_sphere(radius, mass, x, y, z)
        self.objects[body_id] = PhysicsObject(
            body_id=body_id, shape='sphere',
            params={'radius': radius, 'mass': mass}
        )
        return body_id

    def create_box(self, hx, hy, hz, mass, x, y, z):
        body_id = self.world.create_box(hx, hy, hz, mass, x, y, z)
        self.objects[body_id] = PhysicsObject(
            body_id=body_id, shape='box',
            params={'hx': hx, 'hy': hy, 'hz': hz, 'mass': mass}
        )
        return body_id

    def get_position(self, body_id):
        return self.world.get_position(body_id)

    def get_velocity(self, body_id):
        return self.world.get_velocity(body_id)

    def set_velocity(self, body_id, vx, vy, vz):
        self.world.set_velocity(body_id, vx, vy, vz)

    def apply_force(self, body_id, fx, fy, fz):
        self.world.apply_force(body_id, fx, fy, fz)

    def apply_impulse(self, body_id, ix, iy, iz):
        self.world.apply_impulse(body_id, ix, iy, iz)

    def step(self, dt=1/60):
        self.world.step(dt)
        if self._recording:
            self._record_frame()

    def time(self):
        return self.world.time()

    def start_recording(self):
        self._recording = True
        self.frame_data = []

    def stop_recording(self):
        self._recording = False
        return self.frame_data

    def _record_frame(self):
        frame = {'time': self.time(), 'objects': {}}
        for body_id, obj in self.objects.items():
            pos = self.get_position(body_id)
            vel = self.get_velocity(body_id)
            frame['objects'][body_id] = {
                'position': pos, 'velocity': vel,
                'shape': obj.shape, 'params': obj.params
            }
        self.frame_data.append(frame)

    def bind_mobject(self, body_id, mobject):
        if body_id in self.objects:
            self.objects[body_id].mobject = mobject

    def sync_mobjects(self):
        for body_id, obj in self.objects.items():
            if obj.mobject is not None:
                pos = self.get_position(body_id)
                obj.mobject.move_to([pos[0], pos[1], pos[2]])
