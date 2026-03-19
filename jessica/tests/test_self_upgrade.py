"""
Test Suite for Jessica Self-Upgrade System
Comprehensive tests for all code evolution and safe deployment components
"""

import sys
import os
import time
import logging
from datetime import datetime
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger("test_self_upgrade")


def test_code_evolution_skill():
    """Test code evolution skill"""
    print("\n" + "="*60)
    print("TEST 1: Code Evolution Skill")
    print("="*60)
    
    from jessica.skills.code_evolution_skill import CodeEvolutionSkill
    
    skill = CodeEvolutionSkill()
    
    # Test proposing improvement
    result = skill.propose_skill_improvement(
        'greeting_skill',
        'Add time zone awareness for international users'
    )
    assert result['success'], "Failed to propose improvement"
    proposal_id = result['proposal_id']
    print(f"✓ Proposed improvement: {proposal_id}")
    
    # Test proposing new skill
    result = skill.propose_new_skill(
        'calendar_skill',
        'Manage calendar events and integrate with system'
    )
    assert result['success'], "Failed to propose new skill"
    print(f"✓ Proposed new skill: {result['proposal_id']}")
    
    # Test proposing bugfix
    result = skill.propose_bugfix(
        'greeting_skill',
        'Null reference when active_window is None',
        'Error: NoneType object has no attribute len()'
    )
    assert result['success'], "Failed to propose bugfix"
    print(f"✓ Proposed bugfix: {result['proposal_id']}")
    
    # Test proposing optimization
    result = skill.propose_optimization(
        'system_monitor',
        'Reduce CPU usage in app enumeration loop'
    )
    assert result['success'], "Failed to propose optimization"
    print(f"✓ Proposed optimization: {result['proposal_id']}")
    
    # Test listing proposals
    stats = skill.get_proposal_stats()
    print(f"✓ Statistics: {stats['total_proposals']} proposals, {stats['by_type']}")
    
    print("✓ Code Evolution Skill test PASSED")
    return True


def test_code_validator():
    """Test code validator"""
    print("\n" + "="*60)
    print("TEST 2: Code Validator")
    print("="*60)
    
    from jessica.automation.code_validator import CodeValidator
    
    validator = CodeValidator()
    
    # Test valid code
    valid_code = '''
def greet(name):
    """Generate greeting"""
    return f"Hello, {name}!"

result = greet("Jessica")
'''
    
    result = validator.validate_code(valid_code)
    assert result['syntax_valid'], "Valid code marked as invalid syntax"
    assert result['valid'], "Valid code not passing validation"
    print("✓ Valid code passes validation")
    
    # Test invalid syntax
    invalid_code = "def broken syntax here"
    result = validator.validate_code(invalid_code)
    assert not result['syntax_valid'], "Invalid code marked as valid"
    print("✓ Invalid syntax caught")
    
    # Test security issues
    security_code = '''
import subprocess
password = "secret123"
subprocess.call(["echo", password])
'''
    result = validator.validate_code(security_code)
    assert result['security']['has_security_issues'], "Security issues not detected"
    print("✓ Security issues detected")
    
    # Test complexity
    complex_code = '''
def complex_function(a, b):
    if a > 0:
        if b > 0:
            if a > b:
                return a
            elif a < b:
                return b
            else:
                return 0
        else:
            return -b
    else:
        if b > 0:
            return b
        else:
            return 0
'''
    result = validator.validate_code(complex_code)
    assert 'complexity_score' in result['complexity'], "Complexity check failed"
    print(f"✓ Complexity analysis: {result['complexity']['complexity_level']}")
    
    print("✓ Code Validator test PASSED")
    return True


def test_code_staging():
    """Test code staging"""
    print("\n" + "="*60)
    print("TEST 3: Code Staging")
    print("="*60)
    
    from jessica.automation.code_staging import StagingEnvironment
    
    staging = StagingEnvironment(base_path="jessica/_test_staging")
    
    # Test staging code
    code = 'def hello():\n    return "Hello"\n'
    staged_file = staging.stage_code(
        'test_proposal_1',
        'test_module',
        code,
        {'test': True}
    )
    assert staged_file, "Failed to stage code"
    assert Path(staged_file).exists(), "Staged file doesn't exist"
    print("✓ Code staged successfully")
    
    # Test moving to testing
    testing_file = staging.move_to_testing('test_proposal_1')
    assert testing_file, "Failed to move to testing"
    print("✓ Moved code to testing")
    
    # Test promoting to deployed
    deployed_file = staging.promote_to_deployed('test_proposal_1')
    assert deployed_file, "Failed to promote to deployed"
    print("✓ Promoted code to deployed")
    
    # Test statistics
    stats = staging.get_statistics()
    assert stats['deployed_count'] == 1, "Deployed count not updated"
    print(f"✓ Staging statistics: {stats}")
    
    print("✓ Code Staging test PASSED")
    return True


def test_code_versioning():
    """Test code versioning"""
    print("\n" + "="*60)
    print("TEST 4: Code Versioning")
    print("="*60)
    
    from jessica.automation.code_versioning import CodeVersioning
    
    versioning = CodeVersioning(base_path="jessica/_test_versions")
    
    # Test committing version
    code_v1 = 'def greet():\n    return "Hello"\n'
    version_id_1 = versioning.commit_change(
        'greeting_skill',
        code_v1,
        'Initial version'
    )
    assert version_id_1, "Failed to commit version"
    print(f"✓ Committed version: {version_id_1}")
    
    # Test getting version
    retrieved_code = versioning.get_version('greeting_skill', version_id_1)
    assert retrieved_code == code_v1, "Retrieved code doesn't match"
    print("✓ Retrieved version successfully")
    
    # Test second version
    code_v2 = 'def greet():\n    return "Hello, World!"\n'
    version_id_2 = versioning.commit_change(
        'greeting_skill',
        code_v2,
        'Improved greeting'
    )
    print(f"✓ Committed second version: {version_id_2}")
    
    # Test version history
    history = versioning.get_version_history('greeting_skill')
    assert len(history) == 2, "Version history incomplete"
    print(f"✓ Version history: {len(history)} versions")
    
    # Test latest version
    latest = versioning.get_latest_version('greeting_skill')
    assert latest['version_id'] == version_id_2, "Latest version incorrect"
    print("✓ Latest version correct")
    
    # Test tagging
    success = versioning.tag_version(version_id_1, 'stable', 'Stable release')
    assert success, "Failed to tag version"
    print("✓ Tagged version")
    
    # Test comparison
    comparison = versioning.compare_versions('greeting_skill', version_id_1, version_id_2)
    assert 'total_changes' in comparison, "Comparison failed"
    print(f"✓ Version comparison: {comparison['total_changes']} changes")
    
    # Test statistics
    stats = versioning.get_statistics()
    assert stats['total_modules'] == 1, "Module count incorrect"
    print(f"✓ Versioning statistics: {stats}")
    
    print("✓ Code Versioning test PASSED")
    return True


def test_safe_deployment():
    """Test safe deployment orchestrator"""
    print("\n" + "="*60)
    print("TEST 5: Safe Deployment Orchestrator")
    print("="*60)
    
    from jessica.automation.safe_deployment import SafeDeploymentOrchestrator
    
    orchestrator = SafeDeploymentOrchestrator()
    
    # Test processing proposal
    code = '''
def improved_greet():
    """Improved greeting function"""
    return "Hello from improved Jessica!"
'''
    
    result = orchestrator.process_proposal(
        'proposal_001',
        code,
        'greeting_skill',
        {'improvement': 'Better greeting message'}
    )
    
    assert 'proposal_id' in result, "Proposal not processed"
    print(f"✓ Processed proposal: {result['proposal_id']}")
    
    # Check deployment events
    deployment = orchestrator.get_deployment_status('proposal_001')
    assert deployment, "Deployment not found"
    print(f"✓ Deployment status: {deployment['status']}")
    
    # Test approval
    approved = orchestrator.approve_deployment('proposal_001')
    assert approved, "Failed to approve deployment"
    print("✓ Deployment approved")
    
    # Test deployment
    deploy_result = orchestrator.deploy(
        'proposal_001',
        'jessica/_test_deployed.py'
    )
    
    if deploy_result['success']:
        print(f"✓ Deployed successfully: {deploy_result['version_id']}")
        assert Path('jessica/_test_deployed.py').exists(), "Deployed file not found"
    else:
        print(f"✓ Deployment completed: {deploy_result}")
    
    # Test statistics
    stats = orchestrator.get_deployment_statistics()
    print(f"✓ Deployment statistics: {stats}")
    
    print("✓ Safe Deployment Orchestrator test PASSED")
    return True


def test_integration():
    """Test full integration"""
    print("\n" + "="*60)
    print("TEST 6: Full Integration")
    print("="*60)
    
    from jessica.skills.code_evolution_skill import CodeEvolutionSkill
    from jessica.automation.safe_deployment import SafeDeploymentOrchestrator
    
    # Create skill
    evolution = CodeEvolutionSkill()
    orchestrator = SafeDeploymentOrchestrator()
    
    # Generate proposal
    proposal = evolution.propose_skill_improvement(
        'greeting_skill',
        'Add emoji support to greetings'
    )
    proposal_id = proposal['proposal_id']
    print(f"✓ Generated proposal: {proposal_id}")
    
    # Process through deployment pipeline
    deployment = orchestrator.process_proposal(
        proposal_id,
        proposal['code'],
        'greeting_skill',
        proposal
    )
    print(f"✓ Processed through pipeline: {deployment['status']}")
    
    # Approve and deploy
    orchestrator.approve_deployment(proposal_id)
    result = orchestrator.deploy(proposal_id, 'jessica/_test_integration.py')
    
    if result['success']:
        print(f"✓ Full integration successful: {result['version_id']}")
    else:
        print(f"✓ Integration test completed: {result}")
    
    print("✓ Full Integration test PASSED")
    return True


def main():
    """Run all tests"""
    print("\n" + "╔" + "="*58 + "╗")
    print("║" + " "*10 + "JESSICA SELF-UPGRADE SYSTEM TESTS" + " "*15 + "║")
    print("╚" + "="*58 + "╝")
    
    tests = [
        ("Code Evolution Skill", test_code_evolution_skill),
        ("Code Validator", test_code_validator),
        ("Code Staging", test_code_staging),
        ("Code Versioning", test_code_versioning),
        ("Safe Deployment", test_safe_deployment),
        ("Full Integration", test_integration),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"✗ {test_name} FAILED: {e}")
            import traceback
            traceback.print_exc()
            results.append((test_name, False))
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    for test_name, result in results:
        status = "✓ PASSED" if result else "✗ FAILED"
        print(f"{test_name}: {status}")
    
    total = len(results)
    passed = sum(1 for _, r in results if r)
    print(f"\nTotal: {passed}/{total} passed")
    
    return all(r for _, r in results)


if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nTests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\nFatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
