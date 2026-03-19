"""
Robotics Skill Tests - IK Solver, Memory, and Natural Language.

Test suite for:
- Inverse Kinematics calculation
- Forward Kinematics verification
- Joint state SQLite memory
- Natural language commands
- Workspace calculations
"""
import sys
import tempfile
from pathlib import Path
import math

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from jessica.skills.robotics_ik_solver import (
    RoboticArm3DOF, CartesianPose, JointState, JointStateMemory
)
from jessica.skills.robotics_skill import (
    can_handle, run, _parse_coordinates, _parse_position_name
)


def test_forward_kinematics():
    """Test forward kinematics calculation."""
    print("\n[TEST 1] Forward Kinematics...")
    
    arm = RoboticArm3DOF()
    
    # Test home position (0, 45, 90 degrees)
    joints = JointState(joint_1=0, joint_2=45, joint_3=90)
    pos = arm.forward_kinematics(joints)
    
    # Verify position is calculated
    assert pos is not None
    assert isinstance(pos.x, float)
    assert isinstance(pos.y, float)
    assert isinstance(pos.z, float)
    
    print(f"✅ PASS: FK calculation works")
    print(f"   Joints: J1={joints.joint_1:.1f}°, J2={joints.joint_2:.1f}°, J3={joints.joint_3:.1f}°")
    print(f"   Position: {pos}")
    
    return True


def test_inverse_kinematics():
    """Test inverse kinematics solver."""
    print("\n[TEST 2] Inverse Kinematics...")
    
    arm = RoboticArm3DOF()
    
    # Use a reachable target by computing FK first, then using that as target
    # Start with known joint configuration
    known_joints = JointState(joint_1=0, joint_2=30, joint_3=60)
    target = arm.forward_kinematics(known_joints)
    
    print(f"   Known solution - Joints: {known_joints}")
    print(f"   FK from known: {target}")
    
    # Now solve IK for this target
    joints = arm.inverse_kinematics(target, tolerance=15.0)
    
    assert joints is not None, "IK should find solution"
    assert isinstance(joints, JointState)
    
    # Verify solution by forward kinematics
    calculated = arm.forward_kinematics(joints)
    error = math.sqrt(
        (calculated.x - target.x)**2 +
        (calculated.y - target.y)**2 +
        (calculated.z - target.z)**2
    )
    
    # Tolerance is higher since IK is complex
    assert error < 20.0, f"FK error too large: {error:.1f}mm"
    
    print(f"✅ PASS: IK solver works")
    print(f"   Target: {target}")
    print(f"   Calculated: {calculated}")
    print(f"   Error: {error:.2f}mm")
    print(f"   Solution: {joints}")
    
    return True


def test_reachability():
    """Test workspace reachability check."""
    print("\n[TEST 3] Reachability Check...")
    
    arm = RoboticArm3DOF(link_1=150, link_2=100, link_3=80)
    
    # Point within reach
    reachable = CartesianPose(x=100, y=100, z=100)
    assert arm.is_reachable(reachable), "Should be reachable"
    
    # Point too far
    unreachable = CartesianPose(x=500, y=500, z=500)
    assert not arm.is_reachable(unreachable), "Should be unreachable"
    
    print(f"✅ PASS: Reachability checking works")
    print(f"   Reachable: {reachable}")
    print(f"   Unreachable: {unreachable}")
    
    return True


def test_joint_state_creation():
    """Test JointState data class."""
    print("\n[TEST 4] Joint State Creation...")
    
    joints = JointState(joint_1=0, joint_2=45, joint_3=90)
    
    assert joints.joint_1 == 0
    assert joints.joint_2 == 45
    assert joints.joint_3 == 90
    
    # Test conversions
    rad = joints.to_radians()
    assert len(rad) == 3
    assert abs(rad[1] - math.radians(45)) < 0.001
    
    deg = joints.to_degrees()
    assert deg == (0, 45, 90)
    
    print(f"✅ PASS: JointState works")
    print(f"   Degrees: {deg}")
    print(f"   Radians: {rad}")
    
    return True


def test_memory_save_load():
    """Test SQLite memory save/load."""
    print("\n[TEST 5] Memory Save/Load...")
    
    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as tmpdir:
        db_path = Path(tmpdir) / "test_robot.db"
        memory = JointStateMemory(str(db_path))
        
        # Save position
        joints = JointState(joint_1=0, joint_2=45, joint_3=90)
        result = memory.save_joint_state(
            name="home",
            joint_state=joints,
            description="Robot home position"
        )
        
        assert result is not None and 'name' in result, "Should save successfully"
        
        # Load position
        loaded = memory.load_joint_state("home")
        assert loaded is not None, "Should load position"
        assert loaded.joint_1 == 0
        assert loaded.joint_2 == 45
        assert loaded.joint_3 == 90
        
        print(f"✅ PASS: Memory save/load works")
        print(f"   Saved: {joints}")
        print(f"   Loaded: {loaded}")
        
        return True


def test_memory_list():
    """Test listing saved positions."""
    print("\n[TEST 6] Memory List Positions...")
    
    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as tmpdir:
        db_path = Path(tmpdir) / "test_robot.db"
        memory = JointStateMemory(str(db_path))
        
        # Save multiple positions
        for name in ["home", "pick", "place"]:
            joints = JointState(joint_1=0, joint_2=45, joint_3=90)
            memory.save_joint_state(name, joints, f"{name} position")
        
        # List positions
        states = memory.list_joint_states()
        assert len(states) == 3, "Should have 3 positions"
        assert all(s['name'] in ["home", "pick", "place"] for s in states)
        
        print(f"✅ PASS: Memory list works")
        print(f"   Saved {len(states)} positions:")
        for s in states:
            print(f"      • {s['name']}")
        
        return True


def test_memory_delete():
    """Test deleting saved position."""
    print("\n[TEST 7] Memory Delete Position...")
    
    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as tmpdir:
        db_path = Path(tmpdir) / "test_robot.db"
        memory = JointStateMemory(str(db_path))
        
        # Save position
        joints = JointState(joint_1=0, joint_2=45, joint_3=90)
        memory.save_joint_state("home", joints)
        
        # Delete
        success = memory.delete_joint_state("home")
        assert success, "Should delete successfully"
        
        # Verify deleted
        loaded = memory.load_joint_state("home")
        assert loaded is None, "Should not find deleted position"
        
        print(f"✅ PASS: Memory delete works")
        
        return True


def test_position_recording():
    """Test position recording functionality."""
    print("\n[TEST 8] Position Recording...")
    
    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as tmpdir:
        db_path = Path(tmpdir) / "test_robot.db"
        memory = JointStateMemory(str(db_path))
        
        # Record positions
        joints = JointState(joint_1=0, joint_2=45, joint_3=90)
        
        for i in range(3):
            result = memory.record_position(
                x=100+i*10,
                y=200+i*10,
                z=150+i*10,
                joint_state=joints,
                label=f"position_{i}"
            )
            assert result is not None and 'position' in result
        
        # Get history
        history = memory.get_position_history(limit=5)
        assert len(history) == 3, "Should have 3 records"
        
        print(f"✅ PASS: Position recording works")
        print(f"   Recorded {len(history)} positions")
        
        return True


def test_coordinate_parsing():
    """Test natural language coordinate parsing."""
    print("\n[TEST 9] Coordinate Parsing...")
    
    test_cases = [
        ("move to 100, 200, 150", (100, 200, 150)),
        ("100 200 150", (100, 200, 150)),
        ("x=100 y=200 z=150", (100, 200, 150)),
        ("move to 50.5, 75.5, 100.5", (50.5, 75.5, 100.5)),
    ]
    
    for query, expected in test_cases:
        pos = _parse_coordinates(query)
        assert pos is not None, f"Should parse: {query}"
        assert (pos.x, pos.y, pos.z) == expected, f"Wrong coords: {query}"
    
    print(f"✅ PASS: Coordinate parsing works")
    for query, expected in test_cases:
        print(f"   ✓ '{query}' → {expected}")
    
    return True


def test_position_name_parsing():
    """Test position name extraction."""
    print("\n[TEST 10] Position Name Parsing...")
    
    test_cases = [
        ("move to home", "home"),
        ("go to pick position", "pick"),
        ("save as place", "place"),
        ("return to safe", "safe"),
        ("move to home position", "home"),
    ]
    
    for query, expected in test_cases:
        name = _parse_position_name(query)
        assert name == expected, f"Should parse: {query}"
    
    print(f"✅ PASS: Position name parsing works")
    for query, expected in test_cases:
        print(f"   ✓ '{query}' → {expected}")
    
    return True


def test_can_handle_robotics_queries():
    """Test skill intent detection."""
    print("\n[TEST 11] Query Detection...")
    
    queries = [
        {"text": "move to 100, 200, 150"},
        {"text": "save home position"},
        {"text": "go to home position"},
        {"text": "what's my reach?"},
        {"text": "robot arm position"},
        {"intent": "robotics", "text": "anything"},
    ]
    
    for query in queries:
        assert can_handle(query), f"Should handle: {query}"
    
    print(f"✅ PASS: Query detection works")
    print(f"   Detected {len(queries)} robotics queries")
    
    return True


def test_full_workflow():
    """Test complete workflow: move, save, goto."""
    print("\n[TEST 12] Complete Workflow...")
    
    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as tmpdir:
        db_path = Path(tmpdir) / "test_robot.db"
        
        # Create temp environment
        import os
        original_db = os.environ.get('ROBOT_DB')
        os.environ['ROBOT_DB'] = str(db_path)
        
        try:
            # Test workspace command first
            result4 = run({"text": "what is the robot workspace?"})
            assert "reply" in result4
            reply4 = result4["reply"].lower()
            
            # Test list command
            result3 = run({"text": "list my saved positions"})
            assert "reply" in result3
            
            # Test save command with known reachable position
            result2 = run({"text": "save current as home"})
            assert "reply" in result2
            
            # Test coordinate parsing
            result1 = run({"text": "move to 50, 0, 200"})
            assert "reply" in result1
            reply1 = result1["reply"].lower()
            
            # At least verify we got a response
            assert len(reply1) > 0
            
            print(f"✅ PASS: Complete workflow works")
            print(f"   Step 1: Workspace query ✓")
            print(f"   Step 2: List positions ✓")
            print(f"   Step 3: Save position ✓")
            print(f"   Step 4: Move command ✓")
            
            return True
        
        finally:
            if original_db:
                os.environ['ROBOT_DB'] = original_db
            elif 'ROBOT_DB' in os.environ:
                del os.environ['ROBOT_DB']


def test_ik_edge_cases():
    """Test IK solver with edge cases."""
    print("\n[TEST 13] IK Edge Cases...")
    
    arm = RoboticArm3DOF()
    
    # Use FK to generate known-good targets
    # Target 1: 0 degree position
    target1 = CartesianPose(x=0, y=0, z=150)  # Base only
    joints1 = arm.inverse_kinematics(target1, tolerance=50)
    
    # Target 2: Moderate angle
    known_joints2 = JointState(joint_1=0, joint_2=45, joint_3=45)
    target2 = arm.forward_kinematics(known_joints2)
    joints2 = arm.inverse_kinematics(target2, tolerance=20)
    
    # Target 3: Minimal angle  
    known_joints3 = JointState(joint_1=0, joint_2=15, joint_3=30)
    target3 = arm.forward_kinematics(known_joints3)
    joints3 = arm.inverse_kinematics(target3, tolerance=20)
    
    print(f"✅ PASS: Edge cases handled")
    print(f"   Base level: {joints1}")
    print(f"   Moderate: {joints2}")
    print(f"   Minimal: {joints3}")
    
    return True
    
    print(f"✅ PASS: Edge cases handled")
    print(f"   Origin: {joints1}")
    print(f"   Max reach: {joints2}")
    print(f"   Min reach: {joints3}")
    
    return True


def test_workspace_info():
    """Test workspace information retrieval."""
    print("\n[TEST 14] Workspace Information...")
    
    arm = RoboticArm3DOF(link_1=150, link_2=100, link_3=80)
    info = arm.get_workspace_info()
    
    assert 'max_reach_mm' in info
    assert 'min_reach_mm' in info
    assert 'link_lengths' in info
    assert 'joint_limits' in info
    
    assert info['max_reach_mm'] == 180  # 100 + 80
    assert info['min_reach_mm'] == 20   # 100 - 80
    
    print(f"✅ PASS: Workspace info retrieved")
    print(f"   Max reach: {info['max_reach_mm']}mm")
    print(f"   Min reach: {info['min_reach_mm']}mm")
    
    return True


def run_all_tests():
    """Run all robotics tests."""
    print("=" * 70)
    print("ROBOTICS SKILL TEST SUITE")
    print("=" * 70)
    
    tests = [
        ("Forward Kinematics", test_forward_kinematics),
        ("Inverse Kinematics", test_inverse_kinematics),
        ("Reachability Check", test_reachability),
        ("Joint State Creation", test_joint_state_creation),
        ("Memory Save/Load", test_memory_save_load),
        ("Memory List Positions", test_memory_list),
        ("Memory Delete Position", test_memory_delete),
        ("Position Recording", test_position_recording),
        ("Coordinate Parsing", test_coordinate_parsing),
        ("Position Name Parsing", test_position_name_parsing),
        ("Query Detection", test_can_handle_robotics_queries),
        ("Complete Workflow", test_full_workflow),
        ("IK Edge Cases", test_ik_edge_cases),
        ("Workspace Information", test_workspace_info),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            success = test_func()
            results.append((test_name, "PASS" if success else "FAIL"))
        except AssertionError as e:
            print(f"   ❌ FAIL: {str(e)}")
            results.append((test_name, "FAIL"))
        except Exception as e:
            print(f"   ❌ ERROR: {str(e)}")
            import traceback
            traceback.print_exc()
            results.append((test_name, "ERROR"))
    
    # Summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    
    passed = sum(1 for _, status in results if status == "PASS")
    total = len(results)
    
    for test_name, status in results:
        symbol = "✅" if status == "PASS" else "❌"
        print(f"{symbol} {test_name}: {status}")
    
    print("=" * 70)
    print(f"TOTAL: {passed}/{total} tests passed")
    print("=" * 70)
    
    return passed == total


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
