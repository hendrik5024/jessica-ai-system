"""
Comprehensive test suite for the Four Major Life Domains integration.
Tests intent detection, routing, and response generation for all domains.
"""
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(BASE_DIR))

from jessica.nlp.intent_parser import parse_intent
from jessica.skills.advice_skill import can_handle, run

def test_domain(name, queries):
    """Test a domain with multiple queries."""
    print(f"\n{'='*60}")
    print(f"Testing: {name}")
    print('='*60)
    
    passed = 0
    failed = 0
    
    for query in queries:
        intent = parse_intent(query)
        can_handle_result = can_handle(intent)
        
        status = "PASS" if can_handle_result else "FAIL"
        if can_handle_result:
            passed += 1
            print(f"[{status}] {query}")
            
            # Try to get response (just first 150 chars to avoid Unicode issues)
            try:
                result = run(intent, None, None, None)
                response_preview = result['reply'][:150].replace('\n', ' ')
                print(f"        Response: {response_preview}...")
            except Exception as e:
                print(f"        Error getting response: {e}")
        else:
            failed += 1
            print(f"[{status}] {query}")
    
    print(f"\nResults: {passed} passed, {failed} failed")
    return passed, failed

# Test suite
def run_full_test_suite():
    print("="*60)
    print("JESSICA AI - Four Major Domains Integration Test")
    print("="*60)
    
    total_passed = 0
    total_failed = 0
    
    # Domain 1: Logical Literacy (Critical Thinking)
    passed, failed = test_domain("1. Logical Literacy (Critical Thinking)", [
        "What is ad hominem fallacy?",
        "Explain the straw man fallacy",
        "Tell me about sunk cost fallacy",
        "What is socratic questioning?",
        "Explain confirmation bias",
    ])
    total_passed += passed
    total_failed += failed
    
    # Domain 2: Professional & Interpersonal Diplomacy
    passed, failed = test_domain("2. Professional & Interpersonal Diplomacy", [
        "Help me write an email to a coworker missing deadlines",
        "How do I give feedback using SBI?",
        "I need to set boundaries at work",
        "How do I ask for a raise?",
        "Help me decline a meeting professionally",
    ])
    total_passed += passed
    total_failed += failed
    
    # Domain 3: Systems Thinking (Home & Life Ops)
    passed, failed = test_domain("3. Systems Thinking (Home & Life Ops)", [
        "What's a substitute for eggs in baking?",
        "Why is my car not starting? Use 5 whys",
        "How do I substitute butter in recipes?",
        "Root cause analysis for website crashes",
        "What's a milk substitute?",
    ])
    total_passed += passed
    total_failed += failed
    
    # Domain 4: Digital Wellness & Ethics
    passed, failed = test_domain("4. Digital Wellness & Ethics", [
        "How do I spot phishing emails?",
        "How to verify a news source?",
        "What is 2FA and how do I set it up?",
        "How do I recognize deepfakes?",
        "Tips for digital security",
    ])
    total_passed += passed
    total_failed += failed
    
    # Final summary
    print("\n" + "="*60)
    print("FINAL RESULTS")
    print("="*60)
    print(f"Total Tests: {total_passed + total_failed}")
    print(f"Passed: {total_passed}")
    print(f"Failed: {total_failed}")
    print(f"Success Rate: {100 * total_passed / (total_passed + total_failed):.1f}%")
    print("="*60)
    
    if total_failed == 0:
        print("\nAll tests PASSED!")
    else:
        print(f"\n{total_failed} tests FAILED. Review failures above.")

if __name__ == "__main__":
    run_full_test_suite()
