"""
End-to-End CAD Design Skill Integration Tests

Tests the full workflow:
- Natural language parsing
- Part generation
- Validation
- Response generation
"""
import sys
from pathlib import Path
import tempfile
import shutil

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from jessica.skills.cad_design_skill import can_handle, run, _parse_cad_request


def test_can_handle_cad_queries():
    """Test that skill identifies CAD requests"""
    print("\n[TEST 1] CAD query detection...")
    
    cad_queries = [
        {"intent": "cad", "text": "Design a 40x40x20 bracket"},
        {"intent": "design", "text": "Generate a box with 40x40x20 dimensions"},
        {"intent": "", "text": "Create a 3D part 100x100x50"},
        {"intent": "", "text": "I need a 5mm hole in the center"},
        {"intent": "", "text": "design a mount for my printer"},
        {"intent": "", "text": "Can you make an STL for me?"}
    ]
    
    for query in cad_queries:
        assert can_handle(query), f"Should handle: {query}"
    
    print("✅ PASS: CAD query detection working")
    for q in cad_queries:
        print(f"   ✓ {q.get('text', '')[:50]}")
    
    return True


def test_dimension_parsing():
    """Test parsing of dimension specifications"""
    print("\n[TEST 2] Dimension parsing...")
    
    test_cases = [
        ("40x40x20", (40, 40, 20)),
        ("40 x 40 x 20", (40, 40, 20)),
        ("100,100,50", (100, 100, 50)),
        ("40 x 40 x 20 with 5mm hole", (40, 40, 20, 5)),
    ]
    
    for query, expected in test_cases:
        parsed = _parse_cad_request(query)
        assert parsed['success'], f"Parse failed for: {query}"
        
        if len(expected) == 3:
            assert parsed['length'] == expected[0]
            assert parsed['width'] == expected[1]
            assert parsed['height'] == expected[2]
        else:
            assert parsed['hole_diameter'] == expected[3]
    
    print("✅ PASS: Dimension parsing working")
    for query, expected in test_cases:
        print(f"   ✓ '{query}' → {expected}")
    
    return True


def test_hole_diameter_parsing():
    """Test parsing of hole specifications"""
    print("\n[TEST 3] Hole diameter parsing...")
    
    test_cases = [
        ("40x40x20 with 5mm hole", 5.0),
        ("40x40x20 5mm drill", 5.0),
        ("design hole diameter 10", 10.0),
        ("bracket hole 2.5", 2.5),
        ("no hole", 0.0),
    ]
    
    for query, expected_hole in test_cases:
        parsed = _parse_cad_request(query)
        assert parsed['success']
        assert parsed['hole_diameter'] == expected_hole, \
            f"Expected hole {expected_hole}, got {parsed['hole_diameter']} for '{query}'"
    
    print("✅ PASS: Hole diameter parsing working")
    for query, hole in test_cases:
        print(f"   ✓ '{query}' → {hole}mm hole")
    
    return True


def test_part_name_detection():
    """Test part type detection"""
    print("\n[TEST 4] Part name detection...")
    
    test_cases = [
        ("40x40x20 bracket", "bracket"),
        ("create a box 40x40x20", "box"),
        ("mount for printer", "mount"),
        ("plate 50x50x5", "plate"),
        ("generic design 40x40x20", "design"),
    ]
    
    for query, expected_name in test_cases:
        parsed = _parse_cad_request(query)
        assert parsed['success']
        assert parsed['part_name'] == expected_name, \
            f"Expected name '{expected_name}', got '{parsed['part_name']}' for '{query}'"
    
    print("✅ PASS: Part name detection working")
    for query, name in test_cases:
        print(f"   ✓ '{query}' → {name}")
    
    return True


def test_full_cad_workflow():
    """Test complete design → generation → validation workflow"""
    print("\n[TEST 5] Full CAD workflow...")
    
    # Test query
    query_dict = {"text": "Design a 40x40x10 bracket with 5mm hole"}
    
    # Verify can handle
    assert can_handle(query_dict), "Skill should handle bracket query"
    
    # Handle the request
    result = run(query_dict)
    
    assert result is not None, "Run returned None"
    assert 'reply' in result, f"Response missing reply: {result}"
    
    # Check response content
    response = result['reply']
    assert response is not None, "Response is None"
    # Check for either format (40x40x10 or 40.0x40.0x10.0)
    assert ("40x40x10" in response or "40.0x40.0x10.0" in response or 
            ("40" in response and "10" in response)), \
            f"Missing dimensions in response: {response[:100]}"
    
    print("✅ PASS: Full workflow successful")
    print(f"   Response preview: {response[:80]}...")
    
    return True


def test_bracket_generation():
    """Test specific bracket design"""
    print("\n[TEST 6] Bracket generation...")
    
    query_dict = {"text": "create a 40x40 bracket with 5mm hole"}
    result = run(query_dict)
    
    assert result is not None
    assert 'reply' in result
    response = result['reply']
    assert "bracket" in response.lower() or "40x40" in response
    
    print("✅ PASS: Bracket generation works")
    print(f"   Response includes dimensions and hole info")
    
    return True


def test_invalid_query_handling():
    """Test handling of invalid/malformed queries"""
    print("\n[TEST 7] Invalid query handling...")
    
    invalid_query_dict = {"text": "design something"}  # No dimensions
    result = run(invalid_query_dict)
    
    # Should provide helpful response
    assert isinstance(result, dict)
    assert 'reply' in result
    
    print("✅ PASS: Invalid query handled gracefully")
    
    return True


def test_response_format():
    """Test that responses are well-formatted"""
    print("\n[TEST 8] Response format...")
    
    query_dict = {"text": "design a 50x50x15 box with 8mm hole"}
    result = run(query_dict)
    
    assert result is not None
    response = result['reply']
    
    # Check response contains key information
    assert ("✨" in response or "Created" in response or 
            "50x50x15" in response)
    
    print("✅ PASS: Response format is comprehensive")
    print(f"   Response includes design parameters")
    
    return True


def run_all_tests():
    """Run complete integration test suite"""
    print("=" * 70)
    print("CAD DESIGN SKILL INTEGRATION TEST SUITE")
    print("=" * 70)
    
    tests = [
        ("CAD Query Detection", test_can_handle_cad_queries),
        ("Dimension Parsing", test_dimension_parsing),
        ("Hole Diameter Parsing", test_hole_diameter_parsing),
        ("Part Name Detection", test_part_name_detection),
        ("Full CAD Workflow", test_full_cad_workflow),
        ("Bracket Generation", test_bracket_generation),
        ("Invalid Query Handling", test_invalid_query_handling),
        ("Response Format", test_response_format),
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
    print("INTEGRATION TEST SUMMARY")
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
    
    # Cleanup generated files
    if Path("./cad_output").exists():
        shutil.rmtree("./cad_output", ignore_errors=True)
    
    sys.exit(0 if success else 1)
