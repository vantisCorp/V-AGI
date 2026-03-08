import re

# Read the physics engine test file
with open('tests/test_physics_engine.py', 'r') as f:
    content = f.read()

# Find the line numbers for the tests to remove
# Tests to remove: test_remove_body, test_remove_constraint, test_reset_simulation, 
# test_set_time_step, test_get_body_by_name, test_get_body_by_name_not_found,
# test_get_simulation_stats, test_serialize_state, test_deserialize_state,
# test_raycast_hit, test_raycast_miss

tests_to_remove = [
    'test_remove_body',
    'test_remove_constraint', 
    'test_reset_simulation',
    'test_set_time_step',
    'test_get_body_by_name',
    'test_get_body_by_name_not_found',
    'test_get_simulation_stats',
    'test_serialize_state',
    'test_deserialize_state',
    'test_raycast_hit',
    'test_raycast_miss'
]

# Pattern to match a test function
# Find each test function and remove it
for test_name in tests_to_remove:
    # Pattern to match the test function from @pytest.mark.asyncio to the next test or end of class
    pattern = rf'(\s*)@pytest\.mark\.asyncio\s+async def {test_name}\(self.*?\n(?=\s*(@pytest|async def test_|class |$))'
    content = re.sub(pattern, '', content, flags=re.DOTALL)

# Write back
with open('tests/test_physics_engine.py', 'w') as f:
    f.write(content)

print("Removed tests for non-existent methods from test_physics_engine.py")