"""
Quick Start Example: Jessica GitHub Agent
Demonstrates full workflow: triage -> branch -> commit -> PR
"""
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from jessica.automation.github_agent import JessicaGitHubAgent


def demo_full_workflow():
    """
    Demonstrate complete GitHub workflow:
    1. Triage issues
    2. Create feature branch
    3. Make changes
    4. Commit
    5. Open PR
    """
    print("=" * 60)
    print("Jessica GitHub Agent - Full Workflow Demo")
    print("=" * 60)
    print()

    # Step 1: Initialize agent
    print("Step 1: Initializing GitHub Agent...")
    agent = JessicaGitHubAgent()
    
    status = agent.get_status()
    if not status['github_connected']:
        print("\n❌ GitHub not connected. Set JESSICA_GH_TOKEN environment variable.")
        print("See GITHUB_AGENT_GUIDE.md for setup instructions.")
        return
    
    print("✓ Agent initialized")
    print()

    # Step 2: Check rate limit
    print("Step 2: Checking API rate limit...")
    rate_info = agent.check_rate_limit()
    print(f"✓ API calls remaining: {rate_info.get('remaining', 'unknown')}/{rate_info.get('limit', 'unknown')}")
    print()

    # Step 3: Triage issues
    print("Step 3: Triaging open issues...")
    issues = agent.triage_issues(
        state="open",
        use_llm=False,  # Set to True if you have LLM configured
        auto_label=False  # Set to True to auto-apply labels
    )
    
    if issues and 'error' in issues[0]:
        print(f"✗ Error: {issues[0]['error']}")
        return
    
    print(f"✓ Found {len(issues)} open issues")
    
    if issues:
        print("\nIssue Summary:")
        for issue in issues[:3]:  # Show first 3
            print(f"  #{issue['number']}: {issue['title']}")
            print(f"    Labels: {', '.join(issue['analysis']['suggested_labels']) or 'none'}")
            print(f"    Priority: {issue['analysis']['priority']}")
        print()
    else:
        print("  No open issues found!")
        print()

    # Step 4: Demo branch creation (without actually creating)
    print("Step 4: Branch Creation Demo")
    print("  To create a branch for issue #42:")
    print("  result = agent.create_feature_branch(issue_number=42)")
    print()

    # Step 5: Demo commit (without actually committing)
    print("Step 5: Commit Demo")
    print("  To commit changes:")
    print("  result = agent.commit_evolution(")
    print("      branch_name='jessica/issue-42-description',")
    print("      file_path='jessica/skills/new_skill.py',")
    print("      changes='Added new skill functionality',")
    print("      issue_number=42")
    print("  )")
    print()

    # Step 6: Demo PR creation (without actually creating)
    print("Step 6: Pull Request Demo")
    print("  To create a PR:")
    print("  pr = agent.submit_for_review(")
    print("      branch_name='jessica/issue-42-description',")
    print("      issue_number=42")
    print("  )")
    print()

    # Step 7: List open PRs
    print("Step 7: Listing open Pull Requests...")
    prs = agent.list_open_prs()
    
    if prs:
        print(f"✓ Found {len(prs)} open PRs:")
        for pr in prs[:3]:  # Show first 3
            print(f"  #{pr['number']}: {pr['title']}")
            print(f"    Author: {pr['author']} | Branch: {pr['branch']}")
    else:
        print("  No open PRs")
    print()

    print("=" * 60)
    print("Demo Complete!")
    print()
    print("Next Steps:")
    print("1. Review GITHUB_AGENT_GUIDE.md for full documentation")
    print("2. Integrate with Code Evolution skill")
    print("3. Try creating a real branch and PR!")
    print("=" * 60)


def demo_simple_triage():
    """
    Simple example: just triage issues and show results.
    """
    print("\n=== Simple Issue Triage ===\n")
    
    agent = JessicaGitHubAgent()
    
    if not agent.get_status()['github_connected']:
        print("❌ Not connected to GitHub. Set JESSICA_GH_TOKEN.")
        return
    
    # Triage without auto-labeling
    issues = agent.triage_issues(auto_label=False)
    
    if not issues or 'error' in issues[0]:
        print("No issues or error occurred")
        return
    
    # Show analysis
    for issue in issues[:5]:  # First 5
        print(f"\n📋 Issue #{issue['number']}: {issue['title']}")
        print(f"   Current labels: {', '.join(issue['current_labels']) or 'none'}")
        print(f"   Suggested labels: {', '.join(issue['analysis']['suggested_labels'])}")
        print(f"   Priority: {issue['analysis']['priority']}")


def demo_create_branch_and_pr():
    """
    Example: Create a branch for an issue and open a PR.
    WARNING: This will actually create a branch and PR!
    """
    ISSUE_NUMBER = 42  # Change this!
    
    print("\n=== Create Branch and PR ===\n")
    print(f"⚠️  WARNING: This will create a real branch and PR for issue #{ISSUE_NUMBER}")
    print("Press Ctrl+C to cancel, or Enter to continue...")
    input()
    
    agent = JessicaGitHubAgent()
    
    # Step 1: Create branch
    print(f"\n1. Creating branch for issue #{ISSUE_NUMBER}...")
    branch_result = agent.create_feature_branch(ISSUE_NUMBER)
    
    if not branch_result.get('success'):
        print(f"✗ Failed: {branch_result.get('error')}")
        return
    
    branch_name = branch_result['branch_name']
    print(f"✓ Created branch: {branch_name}")
    
    # Step 2: Make a dummy change
    print("\n2. Making a change...")
    test_file = "jessica/automation/test_github_agent.txt"
    with open(test_file, 'w') as f:
        f.write(f"Test file created by Jessica GitHub Agent\nIssue: #{ISSUE_NUMBER}\n")
    print(f"✓ Created test file: {test_file}")
    
    # Step 3: Commit
    print("\n3. Committing changes...")
    commit_result = agent.commit_evolution(
        branch_name=branch_name,
        file_path=test_file,
        changes=f"Added test file for issue #{ISSUE_NUMBER} demonstration",
        issue_number=ISSUE_NUMBER
    )
    
    if not commit_result.get('success'):
        print(f"✗ Commit failed: {commit_result.get('error')}")
        return
    
    print(f"✓ Committed: {commit_result['commit_sha'][:7]}")
    
    # Step 4: Create PR
    print("\n4. Creating Pull Request...")
    pr_result = agent.submit_for_review(
        branch_name=branch_name,
        issue_number=ISSUE_NUMBER,
        watchdog_results={
            'passed': True,
            'tests_run': 1,
            'tests_passed': 1,
            'tests_failed': 0
        }
    )
    
    if not pr_result.get('success'):
        print(f"✗ PR creation failed: {pr_result.get('error')}")
        return
    
    print(f"✓ Pull Request created!")
    print(f"   PR #{pr_result['pr_number']}")
    print(f"   URL: {pr_result['pr_url']}")
    
    print("\n✅ Complete! Check GitHub for your new PR.")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "triage":
            demo_simple_triage()
        elif sys.argv[1] == "create":
            demo_create_branch_and_pr()
        elif sys.argv[1] == "full":
            demo_full_workflow()
        else:
            print("Usage:")
            print("  python quick_start_github_agent.py          # Full demo (read-only)")
            print("  python quick_start_github_agent.py triage   # Just triage issues")
            print("  python quick_start_github_agent.py create   # Create branch & PR (WRITES!)")
            print("  python quick_start_github_agent.py full     # Full workflow demo")
    else:
        demo_full_workflow()
