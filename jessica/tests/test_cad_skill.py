"""
CAD Skill Tests - Parametric 3D part generation and validation.

Tests validate:
- Basic parametric box generation
- Hole drilling and feature generation
- STL file export
- Trimesh validation (watertightness check)
- Bracket generation
- File management and history
"""
import sys
import os
from pathlib import Path
import tempfile
import shutil

# Add jessica module to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from jessica.skills.cad_skill import JessicaCAD, get_jessica_cad


def test_basic_box_generation():
    """Test simple box generation without holes"""
    print("\n[TEST 1] Basic box generation...")
    
    # Create temp directory for test
    with tempfile.TemporaryDirectory() as tmpdir:
        cad = JessicaCAD(tmpdir)
        
        # Generate simple box
        result = cad.generate_parametric_part(
            length=40,
            width=40,
            height=20,
            hole_diameter=0,
            part_name="test_box"
        )
        
        assert result['success'], f"Generation failed: {result.get('error')}"
        assert Path(result['file_path']).exists(), "STL file not created"
        assert result['dimensions'] == (40, 40, 20)
        assert result['hole_diameter'] == 0
        
        print("✅ PASS: Basic box generated successfully")
        print(f"   File: {Path(result['file_path']).name}")
        print(f"   Size: {result['file_size_mb']} MB")
        
        return True


def test_bracket_with_hole():
    """Test parametric bracket with center hole"""
    print("\n[TEST 2] Bracket with center hole...")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        cad = JessicaCAD(tmpdir)
        
        # Generate bracket with hole
        result = cad.generate_parametric_part(
            length=40,
            width=40,
            height=10,
            hole_diameter=5.0,
            part_name="test_bracket"
        )
        
        assert result['success'], f"Generation failed: {result.get('error')}"
        assert Path(result['file_path']).exists(), "STL file not created"
        assert result['hole_diameter'] == 5.0
        
        print("✅ PASS: Bracket with hole generated")
        print(f"   Dimensions: {result['dimensions']}")
        print(f"   Hole diameter: {result['hole_diameter']}mm")
        
        return True


def test_hole_validation():
    """Test that hole parameters are correctly stored"""
    print("\n[TEST 3] Hole parameter validation...")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        cad = JessicaCAD(tmpdir)
        
        # Test with various hole sizes
        for hole_dia in [2.0, 5.0, 10.0]:
            result = cad.generate_parametric_part(
                length=50, width=50, height=15,
                hole_diameter=hole_dia,
                part_name=f"test_hole_{hole_dia}"
            )
            
            assert result['success'], f"Failed for hole diameter {hole_dia}"
            assert result['hole_diameter'] == hole_dia
        
        print("✅ PASS: Multiple hole sizes validated")
        print(f"   Tested: 2mm, 5mm, 10mm holes")
        
        return True


def test_invalid_dimensions():
    """Test that invalid dimensions are rejected"""
    print("\n[TEST 4] Invalid dimension rejection...")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        cad = JessicaCAD(tmpdir)
        
        # Test invalid inputs
        result = cad.generate_parametric_part(
            length=-10, width=20, height=10,
            part_name="invalid"
        )
        assert not result['success'], "Should reject negative length"
        
        result = cad.generate_parametric_part(
            length=0, width=20, height=10,
            part_name="invalid"
        )
        assert not result['success'], "Should reject zero length"
        
        print("✅ PASS: Invalid dimensions properly rejected")
        
        return True


def test_stl_validation():
    """Test STL file validation with Trimesh"""
    print("\n[TEST 5] STL watertightness validation...")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        cad = JessicaCAD(tmpdir)
        
        # Generate a valid box
        gen_result = cad.generate_parametric_part(
            length=40, width=40, height=20,
            part_name="test_valid"
        )
        
        assert gen_result['success'], "Generation failed"
        
        # Validate the generated STL
        val_result = cad.validate_stl_watertight(gen_result['file_path'])
        
        assert val_result['success'], f"Validation failed: {val_result.get('error')}"
        assert 'is_watertight' in val_result
        assert 'face_count' in val_result
        assert 'vertex_count' in val_result
        assert 'volume_cm3' in val_result
        
        print("✅ PASS: STL validation successful")
        print(f"   Watertight: {val_result['is_watertight']}")
        print(f"   Faces: {val_result['face_count']}")
        print(f"   Volume: {val_result['volume_cm3']} cm³")
        print(f"   Print ready: {val_result['ready_for_print']}")
        
        return True


def test_bracket_generation_convenience():
    """Test bracket convenience function"""
    print("\n[TEST 6] Bracket convenience function...")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        cad = JessicaCAD(tmpdir)
        
        # Use bracket function
        result = cad.generate_bracket(
            length=40, width=40, height=10,
            hole_diameter=5.0,
            chamfer_radius=0.5,
            part_name="fancy_bracket"
        )
        
        assert result['success'], f"Bracket generation failed: {result.get('error')}"
        assert result['type'] == 'bracket'
        assert result['chamfer_radius'] == 0.5
        assert Path(result['file_path']).exists()
        
        print("✅ PASS: Bracket convenience function works")
        print(f"   Chamfer: {result['chamfer_radius']}mm")
        
        return True


def test_generation_history():
    """Test history tracking"""
    print("\n[TEST 7] Generation history tracking...")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        cad = JessicaCAD(tmpdir)
        
        # Generate multiple parts
        for i in range(3):
            result = cad.generate_parametric_part(
                length=30 + i*5,
                width=30 + i*5,
                height=10 + i*2,
                part_name=f"history_test_{i}"
            )
            assert result['success']
        
        # Check history
        history = cad.get_generation_history()
        assert len(history) == 3, f"Expected 3 items, got {len(history)}"
        
        print("✅ PASS: History tracking functional")
        print(f"   Generated {len(history)} parts")
        print(f"   Last part: {history[-1]['part_name']}")
        
        return True


def test_validate_last_generated():
    """Test validation of last generated file"""
    print("\n[TEST 8] Validate last generated file...")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        cad = JessicaCAD(tmpdir)
        
        # Generate a part
        gen_result = cad.generate_parametric_part(
            length=40, width=40, height=20,
            part_name="last_test"
        )
        assert gen_result['success']
        
        # Validate without specifying path
        val_result = cad.validate_last_generated()
        assert val_result['success'], f"Validation failed: {val_result.get('error')}"
        assert 'is_watertight' in val_result
        
        print("✅ PASS: Last generated validation works")
        print(f"   Watertight: {val_result['is_watertight']}")
        
        return True


def test_singleton():
    """Test singleton pattern"""
    print("\n[TEST 9] Singleton pattern...")
    
    cad1 = get_jessica_cad("./test_output_1")
    cad2 = get_jessica_cad("./test_output_2")
    
    # Should return same instance
    assert cad1 is cad2, "Singleton not working - got different instances"
    
    print("✅ PASS: Singleton pattern works correctly")
    
    # Cleanup
    try:
        if Path("./test_output_1").exists():
            shutil.rmtree("./test_output_1")
        if Path("./test_output_2").exists():
            shutil.rmtree("./test_output_2")
    except:
        pass
    
    return True


def run_all_tests():
    """Run complete test suite"""
    print("=" * 60)
    print("JESSICA CAD SKILL TEST SUITE")
    print("=" * 60)
    
    tests = [
        ("Basic Box Generation", test_basic_box_generation),
        ("Bracket with Hole", test_bracket_with_hole),
        ("Hole Validation", test_hole_validation),
        ("Invalid Dimension Rejection", test_invalid_dimensions),
        ("STL Validation", test_stl_validation),
        ("Bracket Convenience Function", test_bracket_generation_convenience),
        ("Generation History", test_generation_history),
        ("Validate Last Generated", test_validate_last_generated),
        ("Singleton Pattern", test_singleton),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            success = test_func()
            results.append((test_name, "PASS" if success else "FAIL"))
        except AssertionError as e:
            print(f"❌ FAIL: {str(e)}")
            results.append((test_name, "FAIL"))
        except Exception as e:
            print(f"❌ ERROR: {str(e)}")
            results.append((test_name, "ERROR"))
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, status in results if status == "PASS")
    total = len(results)
    
    for test_name, status in results:
        symbol = "✅" if status == "PASS" else "❌"
        print(f"{symbol} {test_name}: {status}")
    
    print("=" * 60)
    print(f"TOTAL: {passed}/{total} tests passed")
    print("=" * 60)
    
    return passed == total


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
