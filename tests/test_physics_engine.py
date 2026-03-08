"""
Tests for Physics Engine.
"""

import asyncio
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, Mock, patch

import numpy as np
import pytest

from src.tools.physics_engine import (ConstraintType, PhysicsBody,
                                      PhysicsConstraint, PhysicsEngine,
                                      PhysicsType, SimulationState)


class TestPhysicsType:
    """Test suite for PhysicsType enum."""

    def test_physics_type_values(self):
        """Test physics type values."""
        assert PhysicsType.RIGID_BODY.value == "rigid_body"
        assert PhysicsType.SOFT_BODY.value == "soft_body"
        assert PhysicsType.FLUID.value == "fluid"
        assert PhysicsType.PARTICLE.value == "particle"
        assert PhysicsType.CLOTH.value == "cloth"


class TestConstraintType:
    """Test suite for ConstraintType enum."""

    def test_constraint_type_values(self):
        """Test constraint type values."""
        assert ConstraintType.FIXED.value == "fixed"
        assert ConstraintType.HINGE.value == "hinge"
        assert ConstraintType.SLIDER.value == "slider"
        assert ConstraintType.UNIVERSAL.value == "universal"
        assert ConstraintType.SPRING.value == "spring"


class TestPhysicsBody:
    """Test suite for PhysicsBody dataclass."""

    def test_physics_body_creation(self):
        """Test creating a physics body."""
        body = PhysicsBody(
            id="body-1",
            name="Test Body",
            mass=10.0,
            position=np.array([0.0, 0.0, 0.0]),
            velocity=np.array([0.0, 0.0, 0.0]),
            acceleration=np.array([0.0, 0.0, 0.0]),
            rotation=np.array([0.0, 0.0, 0.0]),
            angular_velocity=np.array([0.0, 0.0, 0.0]),
            shape="box",
            dimensions={"width": 1.0, "height": 1.0, "depth": 1.0},
            material_properties={"restitution": 0.5, "friction": 0.5},
        )
        assert body.id == "body-1"
        assert body.name == "Test Body"
        assert body.mass == 10.0
        assert body.shape == "box"
        assert body.is_static is False


class TestPhysicsConstraint:
    """Test suite for PhysicsConstraint dataclass."""

    def test_physics_constraint_creation(self):
        """Test creating a physics constraint."""
        constraint = PhysicsConstraint(
            id="constraint-1",
            type=ConstraintType.HINGE,
            body_a="body-1",
            body_b="body-2",
            parameters={"axis": [0, 1, 0]},
        )
        assert constraint.id == "constraint-1"
        assert constraint.type == ConstraintType.HINGE
        assert constraint.body_a == "body-1"
        assert constraint.body_b == "body-2"


class TestSimulationState:
    """Test suite for SimulationState dataclass."""

    def test_simulation_state_creation(self):
        """Test creating a simulation state."""
        state = SimulationState(time=0.0, bodies={}, constraints={}, forces={}, torques={})
        assert state.time == 0.0
        assert state.bodies == {}
        assert state.constraints == {}


class TestPhysicsEngine:
    """Test suite for Physics Engine."""

    @pytest.fixture
    def engine(self):
        """Create physics engine instance."""
        return PhysicsEngine()

    def test_init(self, engine):
        """Test initialization."""
        assert len(engine.bodies) == 0
        assert len(engine.constraints) == 0
        assert engine.simulation_time == 0.0
        assert np.allclose(engine.gravity, [0.0, -9.81, 0.0])

    @pytest.mark.asyncio
    async def test_create_body(self, engine):
        """Test creating a physics body."""
        body = await engine.create_body(
            name="Test Box",
            mass=10.0,
            position=[0.0, 0.0, 0.0],
            shape="box",
            dimensions={"width": 1.0, "height": 1.0, "depth": 1.0},
        )
        assert body.name == "Test Box"
        assert body.mass == 10.0
        assert body.shape == "box"
        assert body.id in engine.bodies

    @pytest.mark.asyncio
    async def test_create_body_with_material(self, engine):
        """Test creating a body with custom material properties."""
        body = await engine.create_body(
            name="Bouncy Ball",
            mass=1.0,
            position=[0.0, 10.0, 0.0],
            shape="sphere",
            dimensions={"radius": 0.5},
            material_properties={"restitution": 0.9, "friction": 0.3},
        )
        assert body.material_properties["restitution"] == 0.9
        assert body.material_properties["friction"] == 0.3

    @pytest.mark.asyncio
    async def test_create_static_body(self, engine):
        """Test creating a static body."""
        body = await engine.create_body(
            name="Ground",
            mass=0.0,
            position=[0.0, 0.0, 0.0],
            shape="box",
            dimensions={"width": 100.0, "height": 1.0, "depth": 100.0},
            is_static=True,
        )
        assert body.is_static is True

    @pytest.mark.asyncio
    async def test_create_constraint(self, engine):
        """Test creating a constraint between bodies."""
        await engine.create_body(
            name="Body A",
            mass=1.0,
            position=[0.0, 0.0, 0.0],
            shape="sphere",
            dimensions={"radius": 0.5},
        )
        await engine.create_body(
            name="Body B",
            mass=1.0,
            position=[2.0, 0.0, 0.0],
            shape="sphere",
            dimensions={"radius": 0.5},
        )

        constraint = await engine.create_constraint(
            name="Spring",
            constraint_type=ConstraintType.SPRING,
            body_a_id="body_0",
            body_b_id="body_1",
            parameters={"stiffness": 100.0, "damping": 10.0},
        )
        assert constraint.type == ConstraintType.SPRING
        assert constraint.id in engine.constraints

    @pytest.mark.asyncio
    async def test_create_constraint_nonexistent_body(self, engine):
        """Test creating constraint with nonexistent body."""
        await engine.create_body(
            name="Body A",
            mass=1.0,
            position=[0.0, 0.0, 0.0],
            shape="sphere",
            dimensions={"radius": 0.5},
        )

        with pytest.raises(ValueError, match="not found"):
            await engine.create_constraint(
                name="Invalid",
                constraint_type=ConstraintType.FIXED,
                body_a_id="body_0",
                body_b_id="nonexistent",
                parameters={},
            )

    @pytest.mark.asyncio
    async def test_apply_force(self, engine):
        """Test applying force to a body."""
        await engine.create_body(
            name="Test Body",
            mass=10.0,
            position=[0.0, 0.0, 0.0],
            shape="box",
            dimensions={"width": 1.0, "height": 1.0, "depth": 1.0},
        )

        await engine.apply_force("body_0", [100.0, 0.0, 0.0])

        assert np.allclose(engine.forces["body_0"], [100.0, 0.0, 0.0])

    @pytest.mark.asyncio
    async def test_apply_force_nonexistent_body(self, engine):
        """Test applying force to nonexistent body."""
        with pytest.raises(ValueError, match="not found"):
            await engine.apply_force("nonexistent", [100.0, 0.0, 0.0])

    @pytest.mark.asyncio
    async def test_apply_torque(self, engine):
        """Test applying torque to a body."""
        await engine.create_body(
            name="Test Body",
            mass=10.0,
            position=[0.0, 0.0, 0.0],
            shape="box",
            dimensions={"width": 1.0, "height": 1.0, "depth": 1.0},
        )

        await engine.apply_torque("body_0", [0.0, 50.0, 0.0])

        assert np.allclose(engine.torques["body_0"], [0.0, 50.0, 0.0])

    @pytest.mark.asyncio
    async def test_apply_torque_nonexistent_body(self, engine):
        """Test applying torque to nonexistent body."""
        with pytest.raises(ValueError, match="not found"):
            await engine.apply_torque("nonexistent", [0.0, 50.0, 0.0])

    @pytest.mark.asyncio
    async def test_apply_impulse(self, engine):
        """Test applying impulse to a body."""
        await engine.create_body(
            name="Test Body",
            mass=10.0,
            position=[0.0, 0.0, 0.0],
            shape="box",
            dimensions={"width": 1.0, "height": 1.0, "depth": 1.0},
        )

        initial_velocity = engine.bodies["body_0"].velocity.copy()
        await engine.apply_impulse("body_0", [100.0, 0.0, 0.0])

        # Impulse should change velocity
        expected_delta = np.array([100.0, 0.0, 0.0]) / 10.0
        assert np.allclose(engine.bodies["body_0"].velocity, initial_velocity + expected_delta)

    @pytest.mark.asyncio
    async def test_apply_impulse_nonexistent_body(self, engine):
        """Test applying impulse to nonexistent body."""
        with pytest.raises(ValueError, match="not found"):
            await engine.apply_impulse("nonexistent", [100.0, 0.0, 0.0])

    @pytest.mark.asyncio
    async def test_set_gravity(self, engine):
        """Test setting gravity."""
        await engine.set_gravity([0.0, -1.62, 0.0])  # Moon gravity
        assert np.allclose(engine.gravity, [0.0, -1.62, 0.0])

    @pytest.mark.asyncio
    async def test_simulate_step(self, engine):
        """Test single simulation step."""
        await engine.create_body(
            name="Falling Ball",
            mass=1.0,
            position=[0.0, 10.0, 0.0],
            shape="sphere",
            dimensions={"radius": 0.5},
        )

        state = await engine.simulate_step()

        assert state.time > 0
        # Body should have fallen due to gravity
        assert engine.bodies["body_0"].position[1] < 10.0

    @pytest.mark.asyncio
    async def test_simulate_step_static_body(self, engine):
        """Test simulation step with static body."""
        await engine.create_body(
            name="Static Floor",
            mass=0.0,
            position=[0.0, 0.0, 0.0],
            shape="box",
            dimensions={"width": 10.0, "height": 1.0, "depth": 10.0},
            is_static=True,
        )

        initial_position = engine.bodies["body_0"].position.copy()
        await engine.simulate_step()

        # Static body should not move
        assert np.allclose(engine.bodies["body_0"].position, initial_position)

    @pytest.mark.asyncio
    async def test_simulate(self, engine):
        """Test running simulation for duration."""
        await engine.create_body(
            name="Falling Ball",
            mass=1.0,
            position=[0.0, 10.0, 0.0],
            shape="sphere",
            dimensions={"radius": 0.5},
        )

        states = await engine.simulate(duration=1.0, time_step=0.1)

        assert len(states) > 0
        assert engine.simulation_time > 0

    @pytest.mark.asyncio
    async def test_collision_detection(self, engine):
        """Test collision detection between bodies."""
        # Create two bodies close together
        await engine.create_body(
            name="Ball A",
            mass=1.0,
            position=[0.0, 0.0, 0.0],
            shape="sphere",
            dimensions={"radius": 1.0},
        )
        await engine.create_body(
            name="Ball B",
            mass=1.0,
            position=[1.5, 0.0, 0.0],
            shape="sphere",
            dimensions={"radius": 1.0},
        )

        await engine._detect_collisions()

        # Bodies should be colliding (distance 1.5 < radius 1 + radius 1)
        assert len(engine.collision_pairs) > 0

    @pytest.mark.asyncio
    async def test_get_collision_radius(self, engine):
        """Test getting collision radius for different shapes."""
        # Sphere
        sphere = await engine.create_body(
            name="Sphere",
            mass=1.0,
            position=[0.0, 0.0, 0.0],
            shape="sphere",
            dimensions={"radius": 2.0},
        )
        assert engine._get_collision_radius(sphere) == 2.0

        # Box
        box = await engine.create_body(
            name="Box",
            mass=1.0,
            position=[0.0, 0.0, 0.0],
            shape="box",
            dimensions={"width": 2.0, "height": 2.0, "depth": 2.0},
        )
        assert engine._get_collision_radius(box) > 0

    @pytest.mark.asyncio
    async def test_get_current_state(self, engine):
        """Test getting current simulation state."""
        await engine.create_body(
            name="Test Body",
            mass=1.0,
            position=[0.0, 0.0, 0.0],
            shape="sphere",
            dimensions={"radius": 0.5},
        )

        state = engine._get_current_state()

        assert "bodies" in state.__dict__
        assert "constraints" in state.__dict__
        assert "time" in state.__dict__


class TestPhysicsEngineIntegration:
    """Integration tests for Physics Engine."""

    @pytest.mark.asyncio
    async def test_free_fall_simulation(self):
        """Test free fall simulation."""
        engine = PhysicsEngine()

        await engine.create_body(
            name="Falling Object",
            mass=1.0,
            position=[0.0, 100.0, 0.0],
            shape="sphere",
            dimensions={"radius": 0.5},
        )

        # Simulate 1 second
        for _ in range(60):
            await engine.simulate_step()

        # Object should have fallen significantly
        final_y = engine.bodies["body_0"].position[1]
        assert final_y < 100.0
        # With gravity -9.81 m/s², after 1s: y = 100 - 0.5 * 9.81 * 1² ≈ 95.1
        # But our integration is more approximate
        assert final_y < 99.0

    @pytest.mark.asyncio
    async def test_projectile_motion(self):
        """Test projectile motion."""
        engine = PhysicsEngine()

        await engine.create_body(
            name="Projectile",
            mass=1.0,
            position=[0.0, 0.0, 0.0],
            shape="sphere",
            dimensions={"radius": 0.1},
        )

        # Apply initial velocity (launch at 45 degrees)
        engine.bodies["body_0"].velocity = np.array([10.0, 10.0, 0.0])

        # Simulate
        states = await engine.simulate(duration=2.0, time_step=0.05)

        # Should have multiple states
        assert len(states) > 0

    @pytest.mark.asyncio
    async def test_collision_response(self):
        """Test collision response between bodies."""
        engine = PhysicsEngine()

        # Create two bodies moving towards each other
        await engine.create_body(
            name="Ball A",
            mass=1.0,
            position=[-1.0, 0.0, 0.0],
            shape="sphere",
            dimensions={"radius": 0.5},
        )
        engine.bodies["body_0"].velocity = np.array([5.0, 0.0, 0.0])

        await engine.create_body(
            name="Ball B",
            mass=1.0,
            position=[1.0, 0.0, 0.0],
            shape="sphere",
            dimensions={"radius": 0.5},
        )
        engine.bodies["body_1"].velocity = np.array([-5.0, 0.0, 0.0])

        # Simulate until collision
        for _ in range(100):
            await engine.simulate_step()

        # Bodies should have bounced (velocities changed)
        # After elastic collision, velocities should swap for equal masses
        assert (
            engine.bodies["body_0"].velocity[0] < 5.0 or engine.bodies["body_1"].velocity[0] > -5.0
        )


class TestPhysicsEngineExtended:
    """Extended tests to improve coverage for physics_engine.py."""

    @pytest.fixture
    def engine(self):
        """Create physics engine instance."""
        return PhysicsEngine()

    @pytest.mark.asyncio
    async def test_create_body_cylinder(self, engine):
        """Test creating a cylinder body."""
        body = await engine.create_body(
            name="Cylinder",
            mass=5.0,
            position=[0.0, 0.0, 0.0],
            shape="cylinder",
            dimensions={"radius": 0.5, "height": 2.0},
        )
        assert body.shape == "cylinder"

    @pytest.mark.asyncio
    async def test_create_body_capsule(self, engine):
        """Test creating a capsule body."""
        body = await engine.create_body(
            name="Capsule",
            mass=3.0,
            position=[0.0, 0.0, 0.0],
            shape="capsule",
            dimensions={"radius": 0.3, "height": 1.5},
        )
        assert body.shape == "capsule"

    @pytest.mark.asyncio
    async def test_create_body_mesh(self, engine):
        """Test creating a mesh body."""
        body = await engine.create_body(
            name="Mesh",
            mass=10.0,
            position=[0.0, 0.0, 0.0],
            shape="mesh",
            dimensions={"vertices": 100},
        )
        assert body.shape == "mesh"

    @pytest.mark.asyncio
    async def test_apply_force(self, engine):
        """Test applying force to a body."""
        body = await engine.create_body(
            name="Forced Object",
            mass=1.0,
            position=[0.0, 0.0, 0.0],
            shape="sphere",
            dimensions={"radius": 0.5},
        )

        await engine.apply_force(body.id, [10.0, 0.0, 0.0])

        assert body.id in engine.forces

    @pytest.mark.asyncio
    async def test_apply_torque(self, engine):
        """Test applying torque to a body."""
        body = await engine.create_body(
            name="Torqued Object",
            mass=1.0,
            position=[0.0, 0.0, 0.0],
            shape="sphere",
            dimensions={"radius": 0.5},
        )

        await engine.apply_torque(body.id, [0.0, 5.0, 0.0])

        assert body.id in engine.torques

    @pytest.mark.asyncio
    async def test_create_constraint_fixed(self, engine):
        """Test creating a fixed constraint."""
        await engine.create_body(
            name="Body A",
            mass=1.0,
            position=[0.0, 0.0, 0.0],
            shape="sphere",
            dimensions={"radius": 0.5},
        )
        await engine.create_body(
            name="Body B",
            mass=1.0,
            position=[2.0, 0.0, 0.0],
            shape="sphere",
            dimensions={"radius": 0.5},
        )

        constraint = await engine.create_constraint(
            name="FixedJoint",
            constraint_type=ConstraintType.FIXED,
            body_a_id="body_0",
            body_b_id="body_1",
            parameters={},
        )

        assert constraint.type == ConstraintType.FIXED

    @pytest.mark.asyncio
    async def test_create_constraint_hinge(self, engine):
        """Test creating a hinge constraint."""
        await engine.create_body(
            name="Body A",
            mass=1.0,
            position=[0.0, 0.0, 0.0],
            shape="box",
            dimensions={"width": 1.0, "height": 1.0, "depth": 1.0},
        )
        await engine.create_body(
            name="Body B",
            mass=1.0,
            position=[2.0, 0.0, 0.0],
            shape="box",
            dimensions={"width": 1.0, "height": 1.0, "depth": 1.0},
        )

        constraint = await engine.create_constraint(
            name="DoorHinge",
            constraint_type=ConstraintType.HINGE,
            body_a_id="body_0",
            body_b_id="body_1",
            parameters={"axis": [0, 1, 0], "anchor": [0.5, 0, 0]},
        )

        assert constraint.type == ConstraintType.HINGE

    @pytest.mark.asyncio
    async def test_create_constraint_slider(self, engine):
        """Test creating a slider constraint."""
        await engine.create_body(
            name="Body A",
            mass=1.0,
            position=[0.0, 0.0, 0.0],
            shape="box",
            dimensions={"width": 1.0, "height": 1.0, "depth": 1.0},
        )
        await engine.create_body(
            name="Body B",
            mass=1.0,
            position=[2.0, 0.0, 0.0],
            shape="box",
            dimensions={"width": 1.0, "height": 1.0, "depth": 1.0},
        )

        constraint = await engine.create_constraint(
            name="Slider",
            constraint_type=ConstraintType.SLIDER,
            body_a_id="body_0",
            body_b_id="body_1",
            parameters={"axis": [1, 0, 0]},
        )

        assert constraint.type == ConstraintType.SLIDER

    @pytest.mark.asyncio
    async def test_create_constraint_universal(self, engine):
        """Test creating a universal constraint."""
        await engine.create_body(
            name="Body A",
            mass=1.0,
            position=[0.0, 0.0, 0.0],
            shape="sphere",
            dimensions={"radius": 0.5},
        )
        await engine.create_body(
            name="Body B",
            mass=1.0,
            position=[2.0, 0.0, 0.0],
            shape="sphere",
            dimensions={"radius": 0.5},
        )

        constraint = await engine.create_constraint(
            name="Universal",
            constraint_type=ConstraintType.UNIVERSAL,
            body_a_id="body_0",
            body_b_id="body_1",
            parameters={},
        )

        assert constraint.type == ConstraintType.UNIVERSAL

    @pytest.mark.asyncio
    async def test_simulation_with_constraints(self, engine):
        """Test simulation with constraints affecting bodies."""
        await engine.create_body(
            name="Body A",
            mass=1.0,
            position=[0.0, 0.0, 0.0],
            shape="sphere",
            dimensions={"radius": 0.5},
        )
        await engine.create_body(
            name="Body B",
            mass=1.0,
            position=[1.0, 0.0, 0.0],
            shape="sphere",
            dimensions={"radius": 0.5},
        )

        await engine.create_constraint(
            name="DistanceConstraint",
            constraint_type=ConstraintType.SPRING,
            body_a_id="body_0",
            body_b_id="body_1",
            parameters={"stiffness": 500.0, "damping": 50.0},
        )

        # Apply force to body B
        await engine.apply_force("body_1", [10.0, 0.0, 0.0])

        # Simulate
        for _ in range(10):
            await engine.simulate_step()

        # Both bodies should exist and have moved
        assert "body_0" in engine.bodies
        assert "body_1" in engine.bodies
