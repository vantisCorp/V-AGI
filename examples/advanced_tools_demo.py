"""
Advanced Tools Demonstration Script
Shows examples of using CAD Integration, Physics Engine, Digital Twin, and Code Sandbox
"""

import asyncio
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.tools.cad_integration import CADIntegration, CADOperation, CADFormat
from src.tools.physics_engine import PhysicsEngine, ConstraintType
from src.tools.digital_twin import DigitalTwin, TwinType
from src.tools.code_sandbox import CodeSandbox, CodeLanguage, SandboxConfig


async def demo_cad_integration():
    """Demonstrate CAD Integration capabilities."""
    print("\n" + "="*60)
    print("CAD INTEGRATION DEMO")
    print("="*60)
    
    cad = CADIntegration()
    
    # Create primitives
    print("\n1. Creating primitives...")
    box = await cad.create_primitive("box", {"length": 10.0, "width": 5.0, "height": 3.0}, "base_plate")
    cylinder = await cad.create_primitive("cylinder", {"radius": 2.0, "height": 8.0}, "shaft")
    sphere = await cad.create_primitive("sphere", {"radius": 1.5}, "bearing")
    
    print(f"   Created box: {box.name}")
    print(f"   Created cylinder: {cylinder.name}")
    print(f"   Created sphere: {sphere.name}")
    
    # Perform boolean operation
    print("\n2. Performing boolean union...")
    result = await cad.perform_operation(
        [box.id, cylinder.id],
        CADOperation.BOOLEAN_UNION,
        {}
    )
    print(f"   Result: {result.name}")
    
    # Create assembly
    print("\n3. Creating assembly...")
    assembly = await cad.create_assembly(
        "mechanical_assembly",
        [box.id, cylinder.id, sphere.id],
        []
    )
    print(f"   Assembly: {assembly.name} with {len(assembly.components)} components")
    
    # Analyze mass properties
    print("\n4. Analyzing mass properties...")
    properties = await cad.analyze_mass_properties(box.id)
    print(f"   Mass: {properties['mass']:.2f} kg")
    print(f"   Volume: {properties['volume']:.2f} m³")
    print(f"   Surface Area: {properties['surface_area']:.2f} m²")
    
    # Validate design
    print("\n5. Validating design...")
    validation = await cad.validate_design(
        box.id,
        {"max_mass": 1000.0, "max_volume": 200.0}
    )
    print(f"   Validation status: {validation['overall_status']}")
    
    # Optimize design
    print("\n6. Optimizing design for minimal mass...")
    optimized = await cad.optimize_design(box.id, "minimize_mass", {})
    print(f"   Optimized component: {optimized.name}")
    
    return cad


async def demo_physics_engine():
    """Demonstrate Physics Engine capabilities."""
    print("\n" + "="*60)
    print("PHYSICS ENGINE DEMO")
    print("="*60)
    
    engine = PhysicsEngine()
    
    # Create floor
    print("\n1. Creating static floor...")
    floor = await engine.create_body(
        "floor",
        mass=0.0,
        position=[0.0, 0.0, 0.0],
        shape="box",
        dimensions={"length": 10.0, "width": 10.0, "height": 1.0},
        is_static=True
    )
    print(f"   Created: {floor.name} (static)")
    
    # Create falling objects
    print("\n2. Creating dynamic objects...")
    ball = await engine.create_body(
        "ball",
        mass=1.0,
        position=[0.0, 5.0, 0.0],
        shape="sphere",
        dimensions={"radius": 0.5},
        material_properties={"restitution": 0.8, "friction": 0.3}
    )
    print(f"   Created: {ball.name} at height 5.0m")
    
    box = await engine.create_body(
        "box",
        mass=2.0,
        position=[2.0, 4.0, 0.0],
        shape="box",
        dimensions={"length": 1.0, "width": 1.0, "height": 1.0},
        material_properties={"restitution": 0.5, "friction": 0.5}
    )
    print(f"   Created: {box.name} at height 4.0m")
    
    # Create spring constraint
    print("\n3. Creating spring constraint...")
    constraint = await engine.create_constraint(
        "spring_constraint",
        ConstraintType.SPRING,
        ball.id,
        floor.id,
        parameters={"rest_length": 2.0, "stiffness": 50.0}
    )
    print(f"   Created: {constraint.id}")
    
    # Apply force
    print("\n4. Applying lateral force to ball...")
    await engine.apply_force(ball.id, [10.0, 0.0, 0.0])
    
    # Run simulation
    print("\n5. Running simulation for 2 seconds...")
    states = await engine.simulate(duration=2.0, time_step=1.0/60.0)
    print(f"   Completed {len(states)} simulation steps")
    
    # Analyze energy
    print("\n6. Analyzing energy...")
    energy = await engine.analyze_energy()
    print(f"   Kinetic energy: {energy['kinetic_energy']:.4f} J")
    print(f"   Potential energy: {energy['potential_energy']:.4f} J")
    print(f"   Total energy: {energy['total_energy']:.4f} J")
    
    # Get final states
    print("\n7. Final object states:")
    ball_state = await engine.get_body_state(ball.id)
    print(f"   Ball position: [{ball_state['position'][0]:.2f}, {ball_state['position'][1]:.2f}, {ball_state['position'][2]:.2f}]")
    
    box_state = await engine.get_body_state(box.id)
    print(f"   Box position: [{box_state['position'][0]:.2f}, {box_state['position'][1]:.2f}, {box_state['position'][2]:.2f}]")
    
    return engine


async def demo_digital_twin():
    """Demonstrate Digital Twin Platform capabilities."""
    print("\n" + "="*60)
    print("DIGITAL TWIN PLATFORM DEMO")
    print("="*60)
    
    twin_platform = DigitalTwin()
    
    # Create digital twin
    print("\n1. Creating digital twin...")
    twin = await twin_platform.create_twin(
        "motor_001",
        "Industrial Motor",
        TwinType.ASSET,
        "Large industrial motor for manufacturing line",
        metadata={"manufacturer": "ACME", "model": "X5000"}
    )
    print(f"   Created: {twin['name']} ({twin['type']})")
    
    # Sync with physical data
    print("\n2. Syncing with physical system...")
    await twin_platform.sync_with_physical(
        "motor_001",
        {
            "temperature": {"value": 85.5, "unit": "°C"},
            "vibration": {"value": 2.3, "unit": "mm/s"},
            "speed": {"value": 1800, "unit": "RPM"},
            "current": {"value": 12.5, "unit": "A"}
        }
    )
    print("   Sync completed")
    
    # Update metrics
    print("\n3. Updating metrics...")
    await twin_platform.update_metric("motor_001", "temperature", 86.2, "°C")
    await twin_platform.update_metric("motor_001", "vibration", 2.1, "mm/s")
    await twin_platform.update_metric("motor_001", "speed", 1805, "RPM")
    print("   Metrics updated")
    
    # Create event
    print("\n4. Creating event...")
    event = await twin_platform.create_event(
        "motor_001",
        "operational_change",
        {"parameter": "speed", "old_value": 1800, "new_value": 1805},
        severity="info"
    )
    print(f"   Event: {event.event_type}")
    
    # Predict future values
    print("\n5. Predicting future values...")
    predictions = await twin_platform.predict_metrics("motor_001", "temperature", horizon=5)
    print(f"   Generated {len(predictions)} predictions:")
    for i, pred in enumerate(predictions[:3]):
        print(f"   Step {i+1}: {pred['value']:.2f}°C (confidence: {pred['confidence']:.2f})")
    
    # Simulate scenario
    print("\n6. Simulating scenario...")
    scenario_result = await twin_platform.simulate_scenario(
        "motor_001",
        {
            "changes": {
                "speed": {"type": "relative", "value": 0.1}
            },
            "duration": 30
        }
    )
    print(f"   Scenario completed with {len(scenario_result['results'])} results")
    
    # Detect anomalies
    print("\n7. Detecting anomalies...")
    anomalies = await twin_platform.detect_anomalies("motor_001")
    if anomalies:
        print(f"   Found {len(anomalies)} anomalies")
    else:
        print("   No anomalies detected")
    
    # Optimize parameters
    print("\n8. Getting optimization recommendations...")
    recommendations = await twin_platform.optimize_parameters(
        "motor_001",
        {"temperature": "minimize", "efficiency": "maximize"}
    )
    print(f"   Generated {len(recommendations['recommendations'])} recommendations")
    
    # Get twin status
    print("\n9. Twin status:")
    status = await twin_platform.get_twin_status("motor_001")
    print(f"   State: {status['twin']['state']}")
    print(f"   Metrics tracked: {status['metric_count']}")
    print(f"   Events logged: {status['event_count']}")
    
    return twin_platform


async def demo_code_sandbox():
    """Demonstrate Code Sandbox capabilities."""
    print("\n" + "="*60)
    print("CODE SANDBOX DEMO")
    print("="*60)
    
    sandbox = CodeSandbox()
    
    # Python code example
    print("\n1. Executing Python code...")
    python_code = """
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

# Calculate first 10 Fibonacci numbers
results = []
for i in range(10):
    results.append(fibonacci(i))

# Print results
for i, val in enumerate(results):
    print(f"F({i}) = {val}")
"""
    
    result = await sandbox.execute_code(python_code, CodeLanguage.PYTHON)
    print(f"   Status: {result.status.value}")
    print(f"   Execution time: {result.execution_time:.3f}s")
    print(f"   Output:\n{result.output}")
    
    # Validate code
    print("\n2. Validating code...")
    validation = await sandbox.validate_code(python_code, CodeLanguage.PYTHON)
    print(f"   Valid: {validation['valid']}")
    if validation['warnings']:
        print(f"   Warnings: {validation['warnings']}")
    
    # Analyze code
    print("\n3. Analyzing code...")
    analysis = await sandbox.analyze_code(python_code, CodeLanguage.PYTHON)
    print(f"   Lines of code: {analysis['lines']}")
    print(f"   Functions: {analysis['functions']}")
    print(f"   Complexity: {analysis['complexity']}")
    print(f"   Imports: {', '.join(analysis['imports']) if analysis['imports'] else 'None'}")
    
    # Test with timeout
    print("\n4. Testing with timeout protection...")
    slow_code = """
import time
for i in range(10):
    time.sleep(1)
    print(f"Step {i}")
"""
    
    result = await sandbox.execute_code(
        slow_code,
        CodeLanguage.PYTHON,
        config=SandboxConfig(max_execution_time=2.0)
    )
    print(f"   Status: {result.status.value}")
    if result.status.value == "timeout":
        print("   ✓ Timeout protection working!")
    
    return sandbox


async def main():
    """Run all demonstrations."""
    print("\n" + "="*60)
    print("OMNI-AI ADVANCED TOOLS DEMONSTRATION")
    print("="*60)
    
    try:
        # Run each demo
        await demo_cad_integration()
        await demo_physics_engine()
        await demo_digital_twin()
        await demo_code_sandbox()
        
        print("\n" + "="*60)
        print("ALL DEMONSTRATIONS COMPLETED SUCCESSFULLY")
        print("="*60)
        
    except Exception as e:
        print(f"\n❌ Error during demonstration: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())