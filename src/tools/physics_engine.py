"""
Physics Engine Integration Module
Provides realistic physics simulation capabilities for engineering and gaming applications.
Supports rigid body dynamics, soft body physics, fluids, and particle systems.
"""

import asyncio
import json
import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PhysicsType(Enum):
    """Types of physics simulations."""

    RIGID_BODY = "rigid_body"
    SOFT_BODY = "soft_body"
    FLUID = "fluid"
    PARTICLE = "particle"
    CLOTH = "cloth"


class ConstraintType(Enum):
    """Types of physics constraints."""

    FIXED = "fixed"
    HINGE = "hinge"
    SLIDER = "slider"
    UNIVERSAL = "universal"
    SPRING = "spring"


@dataclass
class PhysicsBody:
    """Represents a physics body in the simulation."""

    id: str
    name: str
    mass: float
    position: np.ndarray  # [x, y, z]
    velocity: np.ndarray
    acceleration: np.ndarray
    rotation: np.ndarray  # quaternion or Euler angles
    angular_velocity: np.ndarray
    shape: str  # box, sphere, cylinder, capsule, mesh
    dimensions: Dict[str, float]
    material_properties: Dict[str, float]
    is_static: bool = False


@dataclass
class PhysicsConstraint:
    """Represents a constraint between physics bodies."""

    id: str
    type: ConstraintType
    body_a: str
    body_b: str
    parameters: Dict[str, Any]


@dataclass
class SimulationState:
    """Represents the state of a physics simulation."""

    time: float
    bodies: Dict[str, PhysicsBody]
    constraints: Dict[str, PhysicsConstraint]
    forces: Dict[str, np.ndarray]
    torques: Dict[str, np.ndarray]


class PhysicsEngine:
    """
    Physics Engine for OMNI-AI.

    Provides comprehensive physics simulation capabilities including:
    - Rigid body dynamics
    - Soft body physics
    - Fluid simulation
    - Particle systems
    - Collision detection and response
    - Constraint solving
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize Physics Engine.

        Args:
            config: Configuration dictionary for physics settings
        """
        self.config = config or {}
        self.gravity = np.array([0.0, -9.81, 0.0])  # Default gravity
        self.time_step = 1.0 / 60.0  # 60 Hz default
        self.simulation_time = 0.0

        # Simulation state
        self.bodies: Dict[str, PhysicsBody] = {}
        self.constraints: Dict[str, PhysicsConstraint] = {}
        self.forces: Dict[str, np.ndarray] = {}
        self.torques: Dict[str, np.ndarray] = {}

        # Collision detection
        self.collision_pairs: List[Tuple[str, str]] = []

        logger.info("Physics Engine initialized")

    async def create_body(
        self,
        name: str,
        mass: float,
        position: List[float],
        shape: str,
        dimensions: Dict[str, float],
        material_properties: Optional[Dict[str, float]] = None,
        is_static: bool = False,
    ) -> PhysicsBody:
        """
        Create a physics body.

        Args:
            name: Name of the body
            mass: Mass in kg
            position: Initial position [x, y, z]
            shape: Shape type (box, sphere, cylinder, capsule, mesh)
            dimensions: Shape dimensions
            material_properties: Material properties (restitution, friction, density)
            is_static: Whether the body is static (immovable)

        Returns:
            PhysicsBody object
        """
        body_id = f"body_{len(self.bodies)}"

        position_array = np.array(position, dtype=float)

        material_properties = material_properties or {
            "restitution": 0.5,
            "friction": 0.5,
            "density": 1000.0,
        }

        body = PhysicsBody(
            id=body_id,
            name=name,
            mass=mass,
            position=position_array,
            velocity=np.zeros(3),
            acceleration=np.zeros(3),
            rotation=np.zeros(3),
            angular_velocity=np.zeros(3),
            shape=shape,
            dimensions=dimensions,
            material_properties=material_properties,
            is_static=is_static,
        )

        self.bodies[body_id] = body
        self.forces[body_id] = np.zeros(3)
        self.torques[body_id] = np.zeros(3)

        logger.info(f"Created physics body: {name} ({shape})")
        return body

    async def create_constraint(
        self,
        name: str,
        constraint_type: ConstraintType,
        body_a_id: str,
        body_b_id: str,
        parameters: Dict[str, Any],
    ) -> PhysicsConstraint:
        """
        Create a constraint between two bodies.

        Args:
            name: Name of the constraint
            constraint_type: Type of constraint
            body_a_id: ID of first body
            body_b_id: ID of second body (or None for world constraint)
            parameters: Constraint-specific parameters

        Returns:
            PhysicsConstraint object
        """
        if body_a_id not in self.bodies:
            raise ValueError(f"Body {body_a_id} not found")
        if body_b_id and body_b_id not in self.bodies:
            raise ValueError(f"Body {body_b_id} not found")

        constraint_id = f"constraint_{len(self.constraints)}"

        constraint = PhysicsConstraint(
            id=constraint_id,
            type=constraint_type,
            body_a=body_a_id,
            body_b=body_b_id or "",
            parameters=parameters,
        )

        self.constraints[constraint_id] = constraint

        logger.info(f"Created constraint: {name} ({constraint_type.value})")
        return constraint

    async def apply_force(self, body_id: str, force: List[float]):
        """
        Apply a force to a body.

        Args:
            body_id: ID of the body
            force: Force vector [fx, fy, fz] in Newtons
        """
        if body_id not in self.bodies:
            raise ValueError(f"Body {body_id} not found")

        force_array = np.array(force, dtype=float)
        self.forces[body_id] += force_array

        logger.debug(f"Applied force {force} to body {body_id}")

    async def apply_torque(self, body_id: str, torque: List[float]):
        """
        Apply a torque to a body.

        Args:
            body_id: ID of the body
            torque: Torque vector [tx, ty, tz] in N·m
        """
        if body_id not in self.bodies:
            raise ValueError(f"Body {body_id} not found")

        torque_array = np.array(torque, dtype=float)
        self.torques[body_id] += torque_array

        logger.debug(f"Applied torque {torque} to body {body_id}")

    async def apply_impulse(self, body_id: str, impulse: List[float]):
        """
        Apply an instantaneous impulse to a body.

        Args:
            body_id: ID of the body
            impulse: Impulse vector [ix, iy, iz] in N·s
        """
        if body_id not in self.bodies:
            raise ValueError(f"Body {body_id} not found")

        body = self.bodies[body_id]
        impulse_array = np.array(impulse, dtype=float)

        # Apply impulse to velocity
        body.velocity += impulse_array / body.mass

        logger.debug(f"Applied impulse {impulse} to body {body_id}")

    async def set_gravity(self, gravity: List[float]):
        """
        Set the gravity vector for the simulation.

        Args:
            gravity: Gravity vector [gx, gy, gz] in m/s²
        """
        self.gravity = np.array(gravity, dtype=float)
        logger.info(f"Set gravity to {gravity}")

    async def simulate_step(self, dt: Optional[float] = None) -> SimulationState:
        """
        Perform one simulation step.

        Args:
            dt: Time step duration (uses default if None)

        Returns:
            Current simulation state
        """
        dt = dt or self.time_step
        self.simulation_time += dt

        # Update each body
        for body_id, body in self.bodies.items():
            if body.is_static:
                continue

            # Calculate total force (gravity + applied forces)
            total_force = self.forces[body_id] + self.gravity * body.mass
            total_torque = self.torques[body_id]

            # Update acceleration (F = ma)
            body.acceleration = total_force / body.mass

            # Update velocity (v = v0 + at)
            body.velocity += body.acceleration * dt

            # Update position (p = p0 + vt)
            body.position += body.velocity * dt

            # Update angular velocity (simplified)
            body.angular_velocity += total_torque / (body.mass * 0.1) * dt
            body.rotation += body.angular_velocity * dt

            # Clear forces and torques for next step
            self.forces[body_id] = np.zeros(3)
            self.torques[body_id] = np.zeros(3)

        # Detect and resolve collisions
        await self._detect_collisions()
        await self._resolve_collisions()

        # Solve constraints
        await self._solve_constraints()

        state = self._get_current_state()

        logger.debug(f"Simulation step completed at t={self.simulation_time:.3f}s")
        return state

    async def simulate(
        self, duration: float, time_step: Optional[float] = None
    ) -> List[SimulationState]:
        """
        Run simulation for a specified duration.

        Args:
            duration: Total simulation time in seconds
            time_step: Time step duration (uses default if None)

        Returns:
            List of simulation states at each step
        """
        if time_step:
            self.time_step = time_step

        states = []
        num_steps = int(duration / self.time_step)

        logger.info(f"Starting simulation for {duration}s ({num_steps} steps)")

        for i in range(num_steps):
            state = await self.simulate_step()
            if i % 10 == 0:  # Save every 10th step to save memory
                states.append(state)

        logger.info(f"Simulation completed: {num_steps} steps")
        return states

    async def _detect_collisions(self):
        """Detect collisions between bodies."""
        self.collision_pairs = []

        body_ids = list(self.bodies.keys())
        for i in range(len(body_ids)):
            for j in range(i + 1, len(body_ids)):
                body_a = self.bodies[body_ids[i]]
                body_b = self.bodies[body_ids[j]]

                # Simple bounding sphere check
                distance = np.linalg.norm(body_a.position - body_b.position)
                min_dist = self._get_collision_radius(body_a) + self._get_collision_radius(body_b)

                if distance < min_dist:
                    self.collision_pairs.append((body_ids[i], body_ids[j]))

    async def _resolve_collisions(self):
        """Resolve detected collisions."""
        for body_a_id, body_b_id in self.collision_pairs:
            body_a = self.bodies[body_a_id]
            body_b = self.bodies[body_b_id]

            # Calculate collision normal
            normal = body_b.position - body_a.position
            distance = np.linalg.norm(normal)

            if distance > 0:
                normal = normal / distance
            else:
                normal = np.array([0.0, 1.0, 0.0])

            # Calculate relative velocity
            rel_velocity = body_a.velocity - body_b.velocity
            velocity_along_normal = np.dot(rel_velocity, normal)

            # Only resolve if objects are moving towards each other
            if velocity_along_normal > 0:
                continue

            # Calculate restitution (bounciness)
            restitution = min(
                body_a.material_properties.get("restitution", 0.5),
                body_b.material_properties.get("restitution", 0.5),
            )

            # Calculate impulse scalar
            j_impulse = -(1 + restitution) * velocity_along_normal
            j_impulse /= 1 / body_a.mass + 1 / body_b.mass

            # Apply impulse
            impulse = j_impulse * normal

            if not body_a.is_static:
                body_a.velocity += impulse / body_a.mass
            if not body_b.is_static:
                body_b.velocity -= impulse / body_b.mass

    async def _solve_constraints(self):
        """Solve all constraints."""
        for constraint_id, constraint in self.constraints.items():
            body_a = self.bodies.get(constraint.body_a)
            body_b = self.bodies.get(constraint.body_b) if constraint.body_b else None

            if not body_a:
                continue

            if constraint.type == ConstraintType.FIXED:
                # Keep body at fixed position
                pass  # Implementation depends on specific constraint

            elif constraint.type == ConstraintType.SPRING:
                if body_b:
                    # Spring constraint: F = -k * (x - x0)
                    rest_length = constraint.parameters.get("rest_length", 1.0)
                    stiffness = constraint.parameters.get("stiffness", 100.0)

                    direction = body_b.position - body_a.position
                    distance = np.linalg.norm(direction)

                    if distance > 0:
                        force_magnitude = stiffness * (distance - rest_length)
                        force = (direction / distance) * force_magnitude

                        if not body_a.is_static:
                            body_a.velocity += (force / body_a.mass) * self.time_step
                        if not body_b.is_static:
                            body_b.velocity -= (force / body_b.mass) * self.time_step

    def _get_collision_radius(self, body: PhysicsBody) -> float:
        """Get collision radius for a body."""
        if body.shape == "sphere":
            return body.dimensions.get("radius", 1.0)
        elif body.shape == "box":
            # Approximate as sphere from dimensions
            dims = body.dimensions
            return max(dims.get("length", 1.0), dims.get("width", 1.0), dims.get("height", 1.0)) / 2
        elif body.shape == "cylinder":
            return max(body.dimensions.get("radius", 1.0), body.dimensions.get("height", 1.0) / 2)
        return 1.0

    def _get_current_state(self) -> SimulationState:
        """Get current simulation state."""
        return SimulationState(
            time=self.simulation_time,
            bodies=self.bodies.copy(),
            constraints=self.constraints.copy(),
            forces=self.forces.copy(),
            torques=self.torques.copy(),
        )

    async def analyze_energy(self) -> Dict[str, float]:
        """
        Analyze total energy in the system.

        Returns:
            Dictionary with kinetic, potential, and total energy
        """
        kinetic_energy = 0.0
        potential_energy = 0.0

        for body in self.bodies.values():
            if body.is_static:
                continue

            # Kinetic energy: KE = 0.5 * m * v²
            v_squared = np.dot(body.velocity, body.velocity)
            kinetic_energy += 0.5 * body.mass * v_squared

            # Potential energy (gravity): PE = m * g * h
            potential_energy += body.mass * abs(self.gravity[1]) * body.position[1]

        total_energy = kinetic_energy + potential_energy

        return {
            "kinetic_energy": kinetic_energy,
            "potential_energy": potential_energy,
            "total_energy": total_energy,
            "time": self.simulation_time,
        }

    async def get_body_state(self, body_id: str) -> Optional[Dict[str, Any]]:
        """
        Get current state of a specific body.

        Args:
            body_id: ID of the body

        Returns:
            Dictionary with body state
        """
        if body_id not in self.bodies:
            return None

        body = self.bodies[body_id]
        return {
            "id": body.id,
            "name": body.name,
            "position": body.position.tolist(),
            "velocity": body.velocity.tolist(),
            "acceleration": body.acceleration.tolist(),
            "rotation": body.rotation.tolist(),
            "angular_velocity": body.angular_velocity.tolist(),
            "mass": body.mass,
        }

    def reset_simulation(self):
        """Reset simulation to initial state."""
        self.simulation_time = 0.0
        self.collision_pairs = []

        for body in self.bodies.values():
            body.velocity = np.zeros(3)
            body.acceleration = np.zeros(3)
            body.angular_velocity = np.zeros(3)

        self.forces = {bid: np.zeros(3) for bid in self.bodies}
        self.torques = {bid: np.zeros(3) for bid in self.bodies}

        logger.info("Simulation reset")


async def main():
    """Example usage of Physics Engine."""
    engine = PhysicsEngine()

    # Create bodies
    floor = await engine.create_body(
        "floor",
        mass=0.0,
        position=[0.0, 0.0, 0.0],
        shape="box",
        dimensions={"length": 10.0, "width": 10.0, "height": 1.0},
        is_static=True,
    )

    ball = await engine.create_body(
        "ball",
        mass=1.0,
        position=[0.0, 5.0, 0.0],
        shape="sphere",
        dimensions={"radius": 0.5},
        material_properties={"restitution": 0.8, "friction": 0.3},
    )

    # Run simulation
    states = await engine.simulate(duration=2.0, time_step=1.0 / 60.0)

    # Analyze energy
    energy = await engine.analyze_energy()
    print(f"Final energy: {json.dumps(energy, indent=2)}")

    # Get body state
    state = await engine.get_body_state(ball.id)
    print(f"Ball state: {json.dumps(state, indent=2)}")


if __name__ == "__main__":
    asyncio.run(main())
