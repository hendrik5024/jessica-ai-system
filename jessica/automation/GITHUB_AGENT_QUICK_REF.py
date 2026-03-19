"""
JESSICA GITHUB AGENT - QUICK REFERENCE CARD
===========================================

🚀 SETUP (One-time)
-------------------
1. Generate token: https://github.com/settings/tokens (scopes: repo, workflow)
2. Set env var: $env:JESSICA_GH_TOKEN = 'ghp_your_token_here'
3. Test: python jessica\automation\github_agent.py


📋 BASIC USAGE
--------------
from jessica.automation.github_agent import JessicaGitHubAgent

# Initialize
agent = JessicaGitHubAgent(llm_router=your_model_router)

# Check status
status = agent.get_status()

# Check rate limit
rate = agent.check_rate_limit()


🏷️ ISSUE TRIAGE
----------------
# Triage all open issues (auto-label)
issues = agent.triage_issues(auto_label=True, use_llm=True)

# View results
for issue in issues:
    print(f"#{issue['number']}: {issue['title']}")
    print(f"  Labels: {issue['analysis']['suggested_labels']}")
    print(f"  Priority: {issue['analysis']['priority']}")


🌿 CREATE BRANCH
----------------
# Create branch for issue #42
result = agent.create_feature_branch(issue_number=42)

if result['success']:
    branch_name = result['branch_name']
    print(f"✓ Branch created: {branch_name}")


💾 COMMIT CHANGES
-----------------
# Commit your improvements
result = agent.commit_evolution(
    branch_name="jessica/issue-42-description",
    file_path="jessica/skills/improved_skill.py",
    changes="Fixed bug causing crash when X happens",
    issue_number=42
)

if result['success']:
    print(f"✓ Committed: {result['commit_sha']}")


🔀 OPEN PULL REQUEST
--------------------
# Submit PR with test results
pr = agent.submit_for_review(
    branch_name="jessica/issue-42-description",
    issue_number=42,
    watchdog_results={
        'passed': True,
        'tests_run': 5,
        'tests_passed': 5,
        'tests_failed': 0
    }
)

if pr['success']:
    print(f"✓ PR #{pr['pr_number']}: {pr['pr_url']}")


🔄 FULL WORKFLOW EXAMPLE
------------------------
# Complete autonomous workflow
agent = JessicaGitHubAgent(llm_router=router)

# 1. Triage to find bugs
issues = agent.triage_issues()
bugs = [i for i in issues if 'bug' in i['analysis']['suggested_labels']]

# 2. Fix first high-priority bug
bug = next((i for i in bugs if i['analysis']['priority'] == 'high'), None)

if bug:
    # 3. Create branch
    branch = agent.create_feature_branch(bug['number'])
    
    # 4. Make code improvements (your logic)
    improve_code(...)
    
    # 5. Commit
    agent.commit_evolution(
        branch_name=branch['branch_name'],
        file_path='path/to/fixed_file.py',
        changes='Fixed bug description',
        issue_number=bug['number']
    )
    
    # 6. Open PR
    pr = agent.submit_for_review(
        branch_name=branch['branch_name'],
        issue_number=bug['number']
    )


🛠️ UTILITY FUNCTIONS
---------------------
# List open PRs
prs = agent.list_open_prs()

# Close an issue
agent.close_issue(issue_number=42, comment="Fixed in PR #123")

# Check rate limit
rate_info = agent.check_rate_limit()
print(f"{rate_info['remaining']}/{rate_info['limit']} calls remaining")


🏷️ AVAILABLE LABELS
--------------------
bug              - Errors, crashes, broken functionality
refactor         - Code cleanup, optimization
new-feature      - New capabilities
documentation    - Docs, guides, comments
performance      - Speed, efficiency improvements
security         - Vulnerabilities, auth issues
test             - Testing, coverage


💬 COMMIT TYPES (Conventional Commits)
---------------------------------------
feat             - New features
fix              - Bug fixes
refactor         - Code restructuring
docs             - Documentation changes
chore            - Maintenance tasks
test             - Test additions/modifications


⚠️ ERROR HANDLING
------------------
# Rate limit exceeded
if 'error' in result and result['error'] == 'rate_limit_exceeded':
    print(f"Rate limit hit. Reset at: {result['reset_time']}")

# Merge conflicts
if 'error' in pr and pr['error'] == 'merge_conflicts':
    print(f"Conflicts in: {pr['conflicts']}")

# Branch already exists
if not branch['success'] and 'already exists' in branch['error']:
    print(f"Branch {branch['branch_name']} already exists")


📚 DOCUMENTATION
----------------
Full Guide:       jessica/automation/GITHUB_AGENT_GUIDE.md
Summary:          jessica/automation/GITHUB_AGENT_SUMMARY.md
Examples:         jessica/automation/quick_start_github_agent.py
Main Doc:         JESSICA_COMPLETE_ABILITIES.md
Quick Ref:        JESSICA_QUICK_REFERENCE.md


🔗 INTEGRATION WITH CODE EVOLUTION
-----------------------------------
# In your code_evolution_skill.py:
from jessica.automation.github_agent import JessicaGitHubAgent

class CodeEvolutionSkill:
    def __init__(self, model_router):
        self.github_agent = JessicaGitHubAgent(llm_router=model_router)
    
    def evolve_with_github(self, issue_number):
        # Use agent for full GitHub workflow
        # See GITHUB_AGENT_GUIDE.md for full integration example


🎯 QUICK TEST
-------------
# Read-only demo (safe)
python jessica\automation\quick_start_github_agent.py

# Triage issues only
python jessica\automation\quick_start_github_agent.py triage

# Full workflow (CAUTION: writes to GitHub!)
python jessica\automation\quick_start_github_agent.py create


📊 STATUS
---------
Version:          1.0.0
Status:           Production Ready ✅
Platform:         Windows (HP/Dell tested)
Dependencies:     PyGithub 2.8.1, GitPython 3.1.46
Lines of Code:    700+
Integration:      Code Evolution v2.0


🎉 JESSICA IS NOW AN AUTONOMOUS GITHUB AGENT!
===============================================
Created: January 13, 2026
"""

if __name__ == "__main__":
    print(__doc__)
