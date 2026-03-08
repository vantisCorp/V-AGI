"""
Tests for CAD Integration Module.
"""

import asyncio
from dataclasses import asdict
from unittest.mock import AsyncMock, Mock, patch

import pytest

from src.tools.cad_integration import (CADAssembly, CADComponent, CADFormat,
                                       CADIntegration, CADOperation)


class TestCADFormat:
    """Tests for CADFormat enum."""

    def test_cad_format_values(self):
        """Test CADFormat enum values."""
        assert CADFormat.STEP.value == "step"
        assert CADFormat.STL.value == "stl"
        assert CADFormat.OBJ.value == "obj"
        assert CADFormat.IGS.value == "igs"
        assert CADFormat.PLY.value == "ply"
        assert CADFormat.DXF.value == "dxf"
        assert CADFormat.DWG.value == "dwg"

    def test_cad_format_count(self):
        """Test number of supported formats."""
        assert len(CADFormat) == 7

    def test_cad_format_from_string(self):
        """Test creating CADFormat from string."""
        assert CADFormat("step") == CADFormat.STEP
        assert CADFormat("stl") == CADFormat.STL


class TestCADOperation:
    """Tests for CADOperation enum."""

    def test_cad_operation_values(self):
        """Test CADOperation enum values."""
        assert CADOperation.EXTRUDE.value == "extrude"
        assert CADOperation.REVOLVE.value == "revolve"
        assert CADOperation.LOFT.value == "loft"
        assert CADOperation.SWEEP.value == "sweep"
        assert CADOperation.BOOLEAN_UNION.value == "boolean_union"
        assert CADOperation.BOOLEAN_DIFFERENCE.value == "boolean_difference"
        assert CADOperation.BOOLEAN_INTERSECTION.value == "boolean_intersection"
        assert CADOperation.FILLET.value == "fillet"
        assert CADOperation.CHAMFER.value == "chamfer"
        assert CADOperation.MIRROR.value == "mirror"
        assert CADOperation.PATTERN_LINEAR.value == "pattern_linear"
        assert CADOperation.PATTERN_CIRCULAR.value == "pattern_circular"

    def test_cad_operation_count(self):
        """Test number of supported operations."""
        assert len(CADOperation) == 12

    def test_cad_operation_from_string(self):
        """Test creating CADOperation from string."""
        assert CADOperation("extrude") == CADOperation.EXTRUDE
        assert CADOperation("boolean_union") == CADOperation.BOOLEAN_UNION


class TestCADComponent:
    """Tests for CADComponent dataclass."""

    def test_cad_component_creation(self):
        """Test creating a CADComponent."""
        geometry = {"type": "box", "parameters": {"length": 10, "width": 5}}
        component = CADComponent(id="comp_1", name="test_component", geometry=geometry)

        assert component.id == "comp_1"
        assert component.name == "test_component"
        assert component.geometry == geometry
        assert component.material is None
        assert component.dimensions is None
        assert component.metadata == {}

    def test_cad_component_with_all_fields(self):
        """Test creating CADComponent with all fields."""
        geometry = {"type": "sphere", "parameters": {"radius": 5}}
        dimensions = {"radius": 5.0}

        component = CADComponent(
            id="comp_2",
            name="sphere_component",
            geometry=geometry,
            material="steel",
            dimensions=dimensions,
            metadata={"author": "test", "version": "1.0"},
        )

        assert component.material == "steel"
        assert component.dimensions == dimensions
        assert component.metadata["author"] == "test"

    def test_cad_component_default_metadata(self):
        """Test that metadata defaults to empty dict."""
        component = CADComponent(id="comp_3", name="test", geometry={})
        assert component.metadata == {}


class TestCADAssembly:
    """Tests for CADAssembly dataclass."""

    def test_cad_assembly_creation(self):
        """Test creating a CADAssembly."""
        component = CADComponent(id="comp_1", name="test", geometry={})

        assembly = CADAssembly(id="assembly_1", name="test_assembly", components=[component])

        assert assembly.id == "assembly_1"
        assert assembly.name == "test_assembly"
        assert len(assembly.components) == 1
        assert assembly.constraints == []
        assert assembly.metadata == {}

    def test_cad_assembly_with_constraints(self):
        """Test creating CADAssembly with constraints."""
        component1 = CADComponent(id="c1", name="comp1", geometry={})
        component2 = CADComponent(id="c2", name="comp2", geometry={})

        constraints = [{"type": "mate", "components": ["c1", "c2"]}, {"type": "align", "axis": "z"}]

        assembly = CADAssembly(
            id="assembly_2",
            name="constrained_assembly",
            components=[component1, component2],
            constraints=constraints,
            metadata={"project": "test"},
        )

        assert len(assembly.constraints) == 2
        assert assembly.metadata["project"] == "test"


class TestCADIntegration:
    """Tests for CADIntegration class."""

    @pytest.fixture
    def cad(self):
        """Create a CADIntegration instance for testing."""
        return CADIntegration()

    @pytest.fixture
    def cad_with_config(self):
        """Create a CADIntegration instance with config."""
        config = {"default_material": "aluminum", "precision": 0.001, "units": "mm"}
        return CADIntegration(config=config)

    def test_cad_initialization(self, cad):
        """Test CADIntegration initialization."""
        assert cad.config == {}
        assert cad.components == {}
        assert cad.assemblies == {}
        assert cad.design_history == []
        assert len(cad.supported_engines) == 4

    def test_cad_initialization_with_config(self, cad_with_config):
        """Test CADIntegration initialization with config."""
        assert cad_with_config.config["default_material"] == "aluminum"
        assert cad_with_config.config["precision"] == 0.001

    @pytest.mark.asyncio
    async def test_create_primitive_box(self, cad):
        """Test creating a box primitive."""
        component = await cad.create_primitive(
            "box", {"length": 10.0, "width": 5.0, "height": 3.0}, "test_box"
        )

        assert component.id == "primitive_0"
        assert component.name == "test_box"
        assert component.geometry["type"] == "box"
        assert component.geometry["parameters"]["length"] == 10.0
        assert component.dimensions["length"] == 10.0

    @pytest.mark.asyncio
    async def test_create_primitive_sphere(self, cad):
        """Test creating a sphere primitive."""
        component = await cad.create_primitive("sphere", {"radius": 5.0}, "test_sphere")

        assert component.geometry["type"] == "sphere"
        assert component.geometry["parameters"]["radius"] == 5.0

    @pytest.mark.asyncio
    async def test_create_primitive_cylinder(self, cad):
        """Test creating a cylinder primitive."""
        component = await cad.create_primitive(
            "cylinder", {"radius": 2.0, "height": 10.0}, "test_cylinder"
        )

        assert component.geometry["type"] == "cylinder"
        assert component.dimensions["radius"] == 2.0

    @pytest.mark.asyncio
    async def test_create_primitive_default_name(self, cad):
        """Test creating primitive with default name."""
        component = await cad.create_primitive("box", {"length": 1.0, "width": 1.0, "height": 1.0})

        assert "box" in component.name

    @pytest.mark.asyncio
    async def test_create_multiple_primitives(self, cad):
        """Test creating multiple primitives."""
        comp1 = await cad.create_primitive("box", {"length": 1.0, "width": 1.0, "height": 1.0})
        comp2 = await cad.create_primitive("sphere", {"radius": 1.0})
        comp3 = await cad.create_primitive("cylinder", {"radius": 1.0, "height": 1.0})

        assert len(cad.components) == 3
        assert comp1.id == "primitive_0"
        assert comp2.id == "primitive_1"
        assert comp3.id == "primitive_2"

    @pytest.mark.asyncio
    async def test_perform_operation_extrude(self, cad):
        """Test performing extrude operation."""
        component = await cad.create_primitive("box", {"length": 10.0, "width": 5.0, "height": 3.0})

        result = await cad.perform_operation(
            [component.id], CADOperation.EXTRUDE, {"distance": 5.0}
        )

        assert result.id.startswith("op_extrude")
        assert result.geometry["operation"] == "extrude"

    @pytest.mark.asyncio
    async def test_perform_operation_boolean_union(self, cad):
        """Test performing boolean union operation."""
        box = await cad.create_primitive("box", {"length": 10.0, "width": 5.0, "height": 3.0})
        sphere = await cad.create_primitive("sphere", {"radius": 2.0})

        result = await cad.perform_operation([box.id, sphere.id], CADOperation.BOOLEAN_UNION, {})

        assert result.geometry["operation"] == "boolean_union"
        assert result.geometry["source_ids"] == [box.id, sphere.id]

    @pytest.mark.asyncio
    async def test_perform_operation_boolean_difference(self, cad):
        """Test performing boolean difference operation."""
        box = await cad.create_primitive("box", {"length": 10.0, "width": 5.0, "height": 3.0})
        cylinder = await cad.create_primitive("cylinder", {"radius": 1.0, "height": 5.0})

        result = await cad.perform_operation(
            [box.id, cylinder.id], CADOperation.BOOLEAN_DIFFERENCE, {}
        )

        assert result.geometry["operation"] == "boolean_difference"

    @pytest.mark.asyncio
    async def test_perform_operation_fillet(self, cad):
        """Test performing fillet operation."""
        box = await cad.create_primitive("box", {"length": 10.0, "width": 5.0, "height": 3.0})

        result = await cad.perform_operation([box.id], CADOperation.FILLET, {"radius": 0.5})

        assert result.geometry["operation"] == "fillet"

    @pytest.mark.asyncio
    async def test_perform_operation_chamfer(self, cad):
        """Test performing chamfer operation."""
        box = await cad.create_primitive("box", {"length": 10.0, "width": 5.0, "height": 3.0})

        result = await cad.perform_operation([box.id], CADOperation.CHAMFER, {"distance": 0.5})

        assert result.geometry["operation"] == "chamfer"

    @pytest.mark.asyncio
    async def test_perform_operation_invalid_component(self, cad):
        """Test performing operation with invalid component ID."""
        with pytest.raises(ValueError, match="One or more component IDs not found"):
            await cad.perform_operation(["nonexistent"], CADOperation.EXTRUDE, {})

    @pytest.mark.asyncio
    async def test_create_assembly(self, cad):
        """Test creating an assembly."""
        box = await cad.create_primitive("box", {"length": 10.0, "width": 5.0, "height": 3.0})
        cylinder = await cad.create_primitive("cylinder", {"radius": 1.0, "height": 5.0})

        assembly = await cad.create_assembly("test_assembly", [box.id, cylinder.id])

        assert assembly.id == "assembly_0"
        assert assembly.name == "test_assembly"
        assert len(assembly.components) == 2
        assert assembly.constraints == []

    @pytest.mark.asyncio
    async def test_create_assembly_with_constraints(self, cad):
        """Test creating an assembly with constraints."""
        box = await cad.create_primitive("box", {"length": 10.0, "width": 5.0, "height": 3.0})
        cylinder = await cad.create_primitive("cylinder", {"radius": 1.0, "height": 5.0})

        constraints = [
            {"type": "mate", "faces": ["box_top", "cylinder_bottom"]},
            {"type": "align", "axes": ["z"]},
        ]

        assembly = await cad.create_assembly(
            "constrained_assembly", [box.id, cylinder.id], constraints=constraints
        )

        assert len(assembly.constraints) == 2

    @pytest.mark.asyncio
    async def test_create_assembly_invalid_component(self, cad):
        """Test creating assembly with invalid component ID."""
        with pytest.raises(ValueError, match="One or more component IDs not found"):
            await cad.create_assembly("test_assembly", ["nonexistent"])

    @pytest.mark.asyncio
    async def test_analyze_mass_properties_box(self, cad):
        """Test analyzing mass properties of a box."""
        box = await cad.create_primitive("box", {"length": 2.0, "width": 2.0, "height": 2.0})

        properties = await cad.analyze_mass_properties(box.id)

        assert properties["component_id"] == box.id
        assert properties["volume"] == 8.0  # 2*2*2
        assert "mass" in properties
        assert "density" in properties
        assert "centroid" in properties
        assert "inertia_tensor" in properties
        assert "surface_area" in properties

    @pytest.mark.asyncio
    async def test_analyze_mass_properties_sphere(self, cad):
        """Test analyzing mass properties of a sphere."""
        sphere = await cad.create_primitive("sphere", {"radius": 1.0})

        properties = await cad.analyze_mass_properties(sphere.id)

        # Volume of sphere = 4/3 * pi * r^3
        expected_volume = (4 / 3) * 3.14159 * (1.0**3)
        assert abs(properties["volume"] - expected_volume) < 0.01

    @pytest.mark.asyncio
    async def test_analyze_mass_properties_cylinder(self, cad):
        """Test analyzing mass properties of a cylinder."""
        cylinder = await cad.create_primitive("cylinder", {"radius": 1.0, "height": 2.0})

        properties = await cad.analyze_mass_properties(cylinder.id)

        # Volume of cylinder = pi * r^2 * h
        expected_volume = 3.14159 * (1.0**2) * 2.0
        assert abs(properties["volume"] - expected_volume) < 0.01

    @pytest.mark.asyncio
    async def test_analyze_mass_properties_with_material(self, cad):
        """Test analyzing mass properties with material."""
        box = await cad.create_primitive("box", {"length": 1.0, "width": 1.0, "height": 1.0})
        box.material = "aluminum"

        properties = await cad.analyze_mass_properties(box.id)

        # Aluminum density is 2700 kg/m^3
        assert properties["density"] == 2700

    @pytest.mark.asyncio
    async def test_analyze_mass_properties_invalid_component(self, cad):
        """Test analyzing mass properties with invalid component."""
        with pytest.raises(ValueError, match="Component ID not found"):
            await cad.analyze_mass_properties("nonexistent")

    @pytest.mark.asyncio
    async def test_export_model_step(self, cad):
        """Test exporting model to STEP format."""
        box = await cad.create_primitive("box", {"length": 10.0, "width": 5.0, "height": 3.0})

        export_path = await cad.export_model(box.id, CADFormat.STEP, "test_model")

        assert export_path.endswith(".step")
        assert "test_model" in export_path

    @pytest.mark.asyncio
    async def test_export_model_stl(self, cad):
        """Test exporting model to STL format."""
        sphere = await cad.create_primitive("sphere", {"radius": 5.0})

        export_path = await cad.export_model(sphere.id, CADFormat.STL, "sphere_model")

        assert export_path.endswith(".stl")

    @pytest.mark.asyncio
    async def test_export_model_invalid_component(self, cad):
        """Test exporting with invalid component ID."""
        with pytest.raises(ValueError, match="Component ID not found"):
            await cad.export_model("nonexistent", CADFormat.STEP, "test")

    @pytest.mark.asyncio
    async def test_validate_design_pass(self, cad):
        """Test design validation that passes."""
        box = await cad.create_primitive("box", {"length": 1.0, "width": 1.0, "height": 1.0})

        result = await cad.validate_design(box.id, {"max_mass": 100000.0, "max_volume": 10.0})

        assert result["overall_status"] == "pass"
        assert result["results"]["mass"]["status"] == "pass"
        assert result["results"]["volume"]["status"] == "pass"

    @pytest.mark.asyncio
    async def test_validate_design_fail_mass(self, cad):
        """Test design validation that fails mass criterion."""
        box = await cad.create_primitive("box", {"length": 10.0, "width": 10.0, "height": 10.0})

        result = await cad.validate_design(box.id, {"max_mass": 1.0})

        assert result["overall_status"] == "fail"
        assert result["results"]["mass"]["status"] == "fail"

    @pytest.mark.asyncio
    async def test_validate_design_fail_volume(self, cad):
        """Test design validation that fails volume criterion."""
        box = await cad.create_primitive("box", {"length": 10.0, "width": 10.0, "height": 10.0})

        result = await cad.validate_design(box.id, {"max_volume": 1.0})

        assert result["overall_status"] == "fail"
        assert result["results"]["volume"]["status"] == "fail"

    @pytest.mark.asyncio
    async def test_validate_design_safety_factor(self, cad):
        """Test design validation with safety factor."""
        box = await cad.create_primitive("box", {"length": 1.0, "width": 1.0, "height": 1.0})

        result = await cad.validate_design(box.id, {"min_safety_factor": 2.0})

        # Default safety factor is 2.5
        assert result["results"]["safety_factor"]["status"] == "pass"

    @pytest.mark.asyncio
    async def test_validate_design_invalid_component(self, cad):
        """Test design validation with invalid component."""
        with pytest.raises(ValueError, match="Component ID not found"):
            await cad.validate_design("nonexistent", {"max_mass": 100.0})

    @pytest.mark.asyncio
    async def test_optimize_design_minimize_mass(self, cad):
        """Test design optimization for minimizing mass."""
        box = await cad.create_primitive("box", {"length": 10.0, "width": 10.0, "height": 10.0})

        optimized = await cad.optimize_design(box.id, "minimize_mass", {})

        assert optimized.id == f"optimized_{box.id}"
        assert optimized.name == f"{box.name}_optimized"
        # Dimensions should be scaled by 0.95
        assert optimized.dimensions["length"] == 9.5

    @pytest.mark.asyncio
    async def test_optimize_design_minimize_volume(self, cad):
        """Test design optimization for minimizing volume."""
        box = await cad.create_primitive("box", {"length": 10.0, "width": 10.0, "height": 10.0})

        optimized = await cad.optimize_design(box.id, "minimize_volume", {})

        # Dimensions should be scaled by 0.9
        assert optimized.dimensions["length"] == 9.0

    @pytest.mark.asyncio
    async def test_optimize_design_preserves_material(self, cad):
        """Test that optimization preserves material."""
        box = await cad.create_primitive("box", {"length": 10.0, "width": 10.0, "height": 10.0})
        box.material = "titanium"

        optimized = await cad.optimize_design(box.id, "minimize_mass", {})

        assert optimized.material == "titanium"

    @pytest.mark.asyncio
    async def test_optimize_design_invalid_component(self, cad):
        """Test optimization with invalid component."""
        with pytest.raises(ValueError, match="Component ID not found"):
            await cad.optimize_design("nonexistent", "minimize_mass", {})

    def test_get_design_history(self, cad):
        """Test getting design history."""
        assert cad.get_design_history() == []

    @pytest.mark.asyncio
    async def test_design_history_logging(self, cad):
        """Test that operations are logged to design history."""
        await cad.create_primitive("box", {"length": 1.0, "width": 1.0, "height": 1.0})

        history = cad.get_design_history()
        assert len(history) == 1
        assert history[0]["operation"] == "create_primitive"

    @pytest.mark.asyncio
    async def test_get_component(self, cad):
        """Test getting a component by ID."""
        box = await cad.create_primitive("box", {"length": 1.0, "width": 1.0, "height": 1.0})

        retrieved = cad.get_component(box.id)
        assert retrieved == box

    def test_get_component_nonexistent(self, cad):
        """Test getting nonexistent component."""
        assert cad.get_component("nonexistent") is None

    @pytest.mark.asyncio
    async def test_get_assembly(self, cad):
        """Test getting an assembly by ID."""
        box = await cad.create_primitive("box", {"length": 1.0, "width": 1.0, "height": 1.0})
        assembly = await cad.create_assembly("test", [box.id])

        retrieved = cad.get_assembly(assembly.id)
        assert retrieved == assembly

    def test_get_assembly_nonexistent(self, cad):
        """Test getting nonexistent assembly."""
        assert cad.get_assembly("nonexistent") is None

    @pytest.mark.asyncio
    async def test_list_components(self, cad):
        """Test listing all component IDs."""
        await cad.create_primitive("box", {"length": 1.0, "width": 1.0, "height": 1.0})
        await cad.create_primitive("sphere", {"radius": 1.0})

        component_ids = cad.list_components()
        assert len(component_ids) == 2

    @pytest.mark.asyncio
    async def test_list_assemblies(self, cad):
        """Test listing all assembly IDs."""
        box = await cad.create_primitive("box", {"length": 1.0, "width": 1.0, "height": 1.0})
        await cad.create_assembly("assembly1", [box.id])
        await cad.create_assembly("assembly2", [box.id])

        assembly_ids = cad.list_assemblies()
        assert len(assembly_ids) == 2

    def test_calculate_volume_box(self, cad):
        """Test volume calculation for box."""
        dimensions = {"length": 2.0, "width": 3.0, "height": 4.0}
        volume = cad._calculate_volume(dimensions, "box")
        assert volume == 24.0

    def test_calculate_volume_sphere(self, cad):
        """Test volume calculation for sphere."""
        dimensions = {"radius": 2.0}
        volume = cad._calculate_volume(dimensions, "sphere")
        # V = 4/3 * pi * r^3
        expected = (4 / 3) * 3.14159 * 8.0
        assert abs(volume - expected) < 0.01

    def test_calculate_volume_cylinder(self, cad):
        """Test volume calculation for cylinder."""
        dimensions = {"radius": 2.0, "height": 5.0}
        volume = cad._calculate_volume(dimensions, "cylinder")
        # V = pi * r^2 * h
        expected = 3.14159 * 4.0 * 5.0
        assert abs(volume - expected) < 0.01

    def test_calculate_volume_unknown(self, cad):
        """Test volume calculation for unknown shape."""
        dimensions = {"length": 1.0}
        volume = cad._calculate_volume(dimensions, "unknown")
        assert volume == 1.0  # Default

    def test_calculate_centroid(self, cad):
        """Test centroid calculation."""
        dimensions = {"length": 10.0, "width": 6.0, "height": 4.0}
        centroid = cad._calculate_centroid(dimensions)

        assert centroid["x"] == 5.0
        assert centroid["y"] == 3.0
        assert centroid["z"] == 2.0

    def test_calculate_inertia_tensor(self, cad):
        """Test inertia tensor calculation."""
        dimensions = {"length": 2.0, "width": 2.0, "height": 2.0}
        mass = 8.0

        inertia = cad._calculate_inertia_tensor(dimensions, mass)

        assert "ixx" in inertia
        assert "iyy" in inertia
        assert "izz" in inertia

    def test_calculate_surface_area(self, cad):
        """Test surface area calculation."""
        dimensions = {"length": 2.0, "width": 3.0, "height": 4.0}
        area = cad._calculate_surface_area(dimensions)
        # SA = 2(lw + lh + wh) = 2(6 + 8 + 12) = 52
        assert area == 52.0

    def test_get_material_density_steel(self, cad):
        """Test getting density for steel."""
        assert cad._get_material_density("steel") == 7850

    def test_get_material_density_aluminum(self, cad):
        """Test getting density for aluminum."""
        assert cad._get_material_density("aluminum") == 2700

    def test_get_material_density_titanium(self, cad):
        """Test getting density for titanium."""
        assert cad._get_material_density("titanium") == 4500

    def test_get_material_density_plastic(self, cad):
        """Test getting density for plastic."""
        assert cad._get_material_density("plastic") == 1200

    def test_get_material_density_wood(self, cad):
        """Test getting density for wood."""
        assert cad._get_material_density("wood") == 700

    def test_get_material_density_unknown(self, cad):
        """Test getting density for unknown material."""
        assert cad._get_material_density("unknown") == 7850  # Default steel

    def test_scale_dimensions(self, cad):
        """Test scaling dimensions."""
        dimensions = {"length": 10.0, "width": 5.0, "height": 2.0}
        scaled = cad._scale_dimensions(dimensions, 0.5)

        assert scaled["length"] == 5.0
        assert scaled["width"] == 2.5
        assert scaled["height"] == 1.0

    @pytest.mark.asyncio
    async def test_calculate_result_dimensions_union(self, cad):
        """Test calculating result dimensions for union."""
        box = await cad.create_primitive("box", {"length": 10.0, "width": 5.0, "height": 3.0})
        box2 = await cad.create_primitive("box", {"length": 5.0, "width": 10.0, "height": 2.0})

        dims = cad._calculate_result_dimensions([box, box2], CADOperation.BOOLEAN_UNION, {})

        assert dims["length"] == 10.0
        assert dims["width"] == 10.0
        assert dims["height"] == 3.0

    def test_calculate_safety_factor(self, cad):
        """Test safety factor calculation."""
        component = CADComponent(id="test", name="test", geometry={})

        sf = cad._calculate_safety_factor(component, {})
        assert sf == 2.5  # Default


class TestCADIntegrationIntegration:
    """Integration tests for CAD Integration workflow."""

    @pytest.mark.asyncio
    async def test_full_design_workflow(self):
        """Test a complete design workflow."""
        cad = CADIntegration()

        # Create components
        base = await cad.create_primitive(
            "box", {"length": 100.0, "width": 50.0, "height": 10.0}, "base_plate"
        )

        hole = await cad.create_primitive(
            "cylinder", {"radius": 5.0, "height": 15.0}, "mounting_hole"
        )

        # Perform boolean difference to create hole
        result = await cad.perform_operation(
            [base.id, hole.id], CADOperation.BOOLEAN_DIFFERENCE, {}
        )

        # Analyze the result
        properties = await cad.analyze_mass_properties(result.id)

        # Validate design
        validation = await cad.validate_design(
            result.id, {"max_mass": 50000.0, "max_volume": 60000.0}
        )

        assert validation["overall_status"] == "pass"

        # Export the design
        export_path = await cad.export_model(result.id, CADFormat.STEP, "final_design")

        assert export_path.endswith(".step")

    @pytest.mark.asyncio
    async def test_assembly_workflow(self):
        """Test assembly creation workflow."""
        cad = CADIntegration()

        # Create parts
        base = await cad.create_primitive("box", {"length": 20.0, "width": 20.0, "height": 5.0})
        post = await cad.create_primitive("cylinder", {"radius": 2.0, "height": 15.0})
        cap = await cad.create_primitive("sphere", {"radius": 4.0})

        # Create assembly
        assembly = await cad.create_assembly(
            "table_assembly",
            [base.id, post.id, cap.id],
            [
                {"type": "mate", "components": [base.id, post.id]},
                {"type": "mate", "components": [post.id, cap.id]},
            ],
        )

        assert len(assembly.components) == 3
        assert len(assembly.constraints) == 2

    @pytest.mark.asyncio
    async def test_optimization_workflow(self):
        """Test design optimization workflow."""
        cad = CADIntegration()

        # Create initial design
        part = await cad.create_primitive("box", {"length": 50.0, "width": 50.0, "height": 10.0})

        # Analyze initial mass
        initial_props = await cad.analyze_mass_properties(part.id)
        initial_mass = initial_props["mass"]

        # Optimize for minimum mass
        optimized = await cad.optimize_design(part.id, "minimize_mass", {"min_safety_factor": 1.5})

        # Analyze optimized mass
        optimized_props = await cad.analyze_mass_properties(optimized.id)
        optimized_mass = optimized_props["mass"]

        # Optimized should have lower mass
        assert optimized_mass < initial_mass
