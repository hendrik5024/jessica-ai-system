# Jessica GitHub Agent - Complete Integration Guide

## Overview

The **Jessica GitHub Agent** extends Jessica's Code Evolution skill with autonomous GitHub repository management capabilities. She can now triage issues, create branches, commit improvements, and open pull requests automatically.

---

## 🚀 Quick Start

### Step 1: Install Dependencies

```powershell
cd C:\Jessica
.\.venv\Scripts\Activate.ps1
pip install -r jessica\automation\github_agent_requirements.txt
```

Required packages:
- **PyGithub** (v2.1.1+): GitHub API client
- **GitPython** (v3.1.40+): Git operations

### Step 2: Generate GitHub Personal Access Token

1. Go to: https://github.com/settings/tokens
2. Click **"Generate new token (classic)"**
3. Set expiration (recommend: 90 days)
4. Select scopes:
   - ✅ **repo** (full control)
   - ✅ **workflow** (if using GitHub Actions)
5. Click **"Generate token"**
6. **Copy token immediately** (you won't see it again!)

### Step 3: Set Environment Variable

**PowerShell:**
```powershell
$env:JESSICA_GH_TOKEN = "ghp_your_token_here"
```

**CMD:**
```cmd
set JESSICA_GH_TOKEN=ghp_your_token_here
```

**Permanent (Windows System):**
```powershell
[System.Environment]::SetEnvironmentVariable('JESSICA_GH_TOKEN', 'ghp_your_token_here', 'User')
```

### Step 4: Test the Agent

```powershell
python jessica\automation\github_agent.py
```

You should see:
```
[GitHub Agent] ✓ Connected to GitHub API
[GitHub Agent] ✓ Loaded Git repository: C:\Jessica
[GitHub Agent] ✓ Connected to GitHub repo: your-username/AGI
```

---

## 📋 Features

### 1. **Issue Triage** 
Automatically analyze and label GitHub issues.

**Features:**
- Keyword-based analysis (fast)
- LLM-based analysis (intelligent)
- Automatic labeling
- Priority assessment

**Example:**
```python
from jessica.automation.github_agent import JessicaGitHubAgent

agent = JessicaGitHubAgent(llm_router=your_model_router)

# Triage all open issues
issues = agent.triage_issues(
    state="open",
    use_llm=True,
    auto_label=True
)

for issue in issues:
    print(f"Issue #{issue['number']}: {issue['title']}")
    print(f"Suggested labels: {issue['analysis']['suggested_labels']}")
    print(f"Priority: {issue['analysis']['priority']}")
```

**Supported Labels:**
- `bug` - Errors, crashes, broken functionality
- `refactor` - Code cleanup, optimization
- `new-feature` - New capabilities
- `documentation` - Docs, guides, comments
- `performance` - Speed, efficiency improvements
- `security` - Vulnerabilities, auth issues
- `test` - Testing, coverage

### 2. **Autonomous Branching**
Create feature branches automatically.

**Features:**
- Clean branch naming: `jessica/issue-[number]-[description]`
- Checks for existing branches
- Fetches latest changes
- Auto-checkout

**Example:**
```python
# Create branch for issue #42
result = agent.create_feature_branch(
    issue_number=42,
    base_branch="main"
)

if result['success']:
    print(f"Created branch: {result['branch_name']}")
    print(f"Working on: {result['issue_title']}")
```

### 3. **Smart Commits**
Commit with professional, conventional commit messages.

**Features:**
- Conventional Commits format
- Automatic commit type detection (feat, fix, refactor, etc.)
- Issue referencing
- Jessica AI signature
- Auto-push to remote

**Example:**
```python
# Commit code evolution improvements
result = agent.commit_evolution(
    branch_name="jessica/issue-42-add-github-agent",
    file_path="jessica/automation/github_agent.py",
    changes="Added autonomous GitHub agent with issue triage and PR automation",
    issue_number=42
)

print(f"Committed: {result['commit_sha']}")
print(f"Pushed: {result['pushed']}")
```

**Generated Commit Message:**
```
feat: Added autonomous GitHub agent with issue triage and PR automation

Modified: jessica/automation/github_agent.py

Changes:
- Added autonomous GitHub agent with issue triage and PR automation

[Code Evolution - Automated by Jessica AI]
Refs #42
```

### 4. **Pull Request Automation**
Open PRs automatically with comprehensive descriptions.

**Features:**
- Merge conflict detection
- Auto-generate title and description
- Include test results (WatchDog)
- Link to issues
- Apply labels from issues

**Example:**
```python
# Submit PR for review
pr = agent.submit_for_review(
    branch_name="jessica/issue-42-add-github-agent",
    base_branch="main",
    issue_number=42,
    watchdog_results={
        'passed': True,
        'tests_run': 10,
        'tests_passed': 10,
        'tests_failed': 0
    }
)

if pr['success']:
    print(f"PR #{pr['pr_number']} created!")
    print(f"URL: {pr['pr_url']}")
```

**Generated PR:**
- **Title:** `Fix #42: Add GitHub Agent for autonomous repository management`
- **Body:** Includes description, changes list, test results, checklist
- **Labels:** Auto-applied from issue
- **Links:** Auto-links to issue with "Fixes #42"

---

## 🔧 Integration with Code Evolution

### Method 1: Direct Integration in `code_evolution_skill.py`

Add to your Code Evolution skill:

```python
from jessica.automation.github_agent import JessicaGitHubAgent

class CodeEvolutionSkill:
    def __init__(self, model_router):
        self.model_router = model_router
        # Initialize GitHub agent
        self.github_agent = JessicaGitHubAgent(
            llm_router=model_router
        )
    
    def evolve_with_github(self, issue_number: int):
        """
        Full workflow: branch -> improve -> commit -> PR
        """
        # 1. Create feature branch
        branch = self.github_agent.create_feature_branch(issue_number)
        if not branch['success']:
            return f"Failed to create branch: {branch.get('error')}"
        
        # 2. Make code improvements
        improved_code = self.improve_code(...)  # Your existing logic
        
        # 3. Write improved code to file
        file_path = "jessica/skills/improved_skill.py"
        with open(file_path, 'w') as f:
            f.write(improved_code)
        
        # 4. Commit changes
        commit = self.github_agent.commit_evolution(
            branch_name=branch['branch_name'],
            file_path=file_path,
            changes="Improved skill based on user feedback",
            issue_number=issue_number
        )
        
        # 5. Submit PR
        pr = self.github_agent.submit_for_review(
            branch_name=branch['branch_name'],
            issue_number=issue_number,
            watchdog_results=self.run_tests()  # Your test results
        )
        
        return f"✓ Created PR #{pr['pr_number']}: {pr['pr_url']}"
```

### Method 2: Standalone Workflow Script

Create `jessica/automation/github_workflow.py`:

```python
"""
Automated GitHub workflow for Code Evolution
"""
from jessica.automation.github_agent import JessicaGitHubAgent
from jessica.llama_cpp_engine.model_router import ModelRouter

def auto_triage_and_evolve():
    """
    Nightly workflow:
    1. Triage all open issues
    2. Identify high-priority bugs
    3. Create branches and attempt fixes
    """
    # Initialize
    model_router = ModelRouter()
    agent = JessicaGitHubAgent(llm_router=model_router)
    
    # Triage issues
    print("Triaging issues...")
    issues = agent.triage_issues(auto_label=True)
    
    # Find high-priority bugs
    high_priority_bugs = [
        issue for issue in issues
        if 'bug' in issue['analysis']['suggested_labels']
        and issue['analysis']['priority'] == 'high'
    ]
    
    print(f"Found {len(high_priority_bugs)} high-priority bugs")
    
    # Attempt to fix each one
    for issue in high_priority_bugs[:3]:  # Limit to 3
        print(f"\nWorking on #{issue['number']}: {issue['title']}")
        
        # Create branch
        branch = agent.create_feature_branch(issue['number'])
        
        # TODO: Use LLM to analyze bug and generate fix
        # TODO: Apply fix to codebase
        # TODO: Commit and create PR
        
    print("\n✓ Workflow complete!")

if __name__ == "__main__":
    auto_triage_and_evolve()
```

### Method 3: Scheduled Task (Windows)

Create a Windows Task Scheduler job:

```powershell
# Create scheduled task for nightly triage
$action = New-ScheduledTaskAction -Execute "python" -Argument "C:\Jessica\jessica\automation\github_workflow.py" -WorkingDirectory "C:\Jessica"
$trigger = New-ScheduledTaskTrigger -Daily -At 2am
$principal = New-ScheduledTaskPrincipal -UserId "$env:USERNAME" -LogonType Interactive
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries

Register-ScheduledTask -TaskName "JessicaGitHubTriage" -Action $action -Trigger $trigger -Principal $principal -Settings $settings
```

---

## 🛡️ Error Handling

### 1. Rate Limit Protection

GitHub API has rate limits:
- **Authenticated:** 5,000 requests/hour
- **Unauthenticated:** 60 requests/hour

Check rate limit:
```python
rate_info = agent.check_rate_limit()
print(f"Remaining: {rate_info['remaining']}/{rate_info['limit']}")
print(f"Resets at: {rate_info['reset_time']}")
```

If rate limit exceeded:
```python
issues = agent.triage_issues()
if issues and 'error' in issues[0]:
    if issues[0]['error'] == 'rate_limit_exceeded':
        print(f"Rate limit hit. Try again at: {issues[0]['reset_time']}")
```

### 2. Merge Conflict Detection

Before creating a PR, the agent checks for conflicts:

```python
pr = agent.submit_for_review(branch_name="jessica/issue-42")

if 'error' in pr and pr['error'] == 'merge_conflicts':
    print("Merge conflicts detected!")
    print(f"Conflicting files: {pr['conflicts']}")
    
    # Manual resolution required
    # Or: Implement auto-resolution logic
```

### 3. Git Errors

Handle Git command failures:

```python
commit = agent.commit_evolution(...)

if not commit.get('success'):
    error = commit.get('error', '')
    
    if 'nothing to commit' in error:
        print("No changes to commit")
    elif 'permission denied' in error:
        print("Git push permission denied - check credentials")
    else:
        print(f"Git error: {error}")
```

---

## 🔐 Security Best Practices

### Token Storage

**✅ DO:**
- Store in environment variables
- Use GitHub secrets in Actions
- Use Windows Credential Manager
- Rotate tokens every 90 days

**❌ DON'T:**
- Hardcode in source code
- Commit to repository
- Share in plaintext
- Use personal tokens in production

### Token Permissions

Minimum required scopes:
- `repo` - For private repos
- `public_repo` - For public repos only
- `workflow` - If using GitHub Actions

### Revoke if Compromised

If token is leaked:
1. Go to: https://github.com/settings/tokens
2. Find the token
3. Click **"Delete"**
4. Generate new token immediately

---

## 📊 Advanced Usage

### Custom Issue Analysis

Add your own label keywords:

```python
agent = JessicaGitHubAgent()

# Add custom labels
agent.label_keywords['urgent'] = ['asap', 'critical', 'hotfix']
agent.label_keywords['ui-ux'] = ['design', 'interface', 'layout', 'css']

# Now triage will detect these too
issues = agent.triage_issues()
```

### Batch Operations

Process multiple issues:

```python
# Get all high-priority bugs
issues = agent.triage_issues()
bugs = [i for i in issues if 'bug' in i['analysis']['suggested_labels']]

for bug in bugs:
    # Create branch
    branch = agent.create_feature_branch(bug['number'])
    
    # Your fix logic here...
    
    # Commit and PR
    agent.commit_evolution(...)
    agent.submit_for_review(...)
```

### Integration with WatchDog Monitoring

Pass test results to PRs:

```python
from jessica.monitoring.watchdog import WatchDog

watchdog = WatchDog()
test_results = watchdog.run_tests()

pr = agent.submit_for_review(
    branch_name="jessica/issue-42",
    watchdog_results={
        'passed': test_results.all_passed,
        'tests_run': test_results.total,
        'tests_passed': test_results.passed,
        'tests_failed': test_results.failed,
    }
)
```

---

## 🎯 Use Cases

### 1. Automated Bug Triage

Every morning, Jessica triages new issues:

```python
# In your morning routine
issues = agent.triage_issues(state="open", auto_label=True)

# Email you a summary
summary = f"Found {len(issues)} open issues:\n"
for issue in issues:
    if issue['analysis']['priority'] == 'high':
        summary += f"🔴 #{issue['number']}: {issue['title']}\n"
```

### 2. Self-Improvement Cycle

Jessica identifies code debt and fixes it:

```python
# Find all 'refactor' issues
issues = agent.triage_issues()
refactor_issues = [i for i in issues if 'refactor' in i['analysis']['suggested_labels']]

for issue in refactor_issues[:1]:  # One at a time
    # Create branch
    branch = agent.create_feature_branch(issue['number'])
    
    # Use LLM to refactor code
    file_path = extract_file_from_issue(issue)
    refactored = llm_refactor(file_path)
    
    # Write and commit
    write_file(file_path, refactored)
    agent.commit_evolution(branch['branch_name'], file_path, "Refactored code")
    
    # Submit PR
    agent.submit_for_review(branch['branch_name'])
```

### 3. Documentation Automation

Auto-create docs from code:

```python
# Find documentation issues
doc_issues = [i for i in agent.triage_issues() if 'documentation' in i['analysis']['suggested_labels']]

for issue in doc_issues:
    # Generate docs with LLM
    docs = generate_documentation_from_code()
    
    # Create branch, commit, PR
    branch = agent.create_feature_branch(issue['number'])
    write_file('docs/NEW_FEATURE.md', docs)
    agent.commit_evolution(branch['branch_name'], 'docs/NEW_FEATURE.md', 'Added documentation')
    agent.submit_for_review(branch['branch_name'])
```

---

## 🐛 Troubleshooting

### "GitHub client not initialized"

**Problem:** Token not set or invalid

**Solution:**
```powershell
# Check if token is set
$env:JESSICA_GH_TOKEN

# If empty, set it
$env:JESSICA_GH_TOKEN = "ghp_your_token"

# Test
python -c "from jessica.automation.github_agent import JessicaGitHubAgent; JessicaGitHubAgent()"
```

### "Not a Git repository"

**Problem:** Running from wrong directory

**Solution:**
```powershell
# Must be in repo root
cd C:\Jessica

# Or specify path explicitly
python -c "from jessica.automation.github_agent import JessicaGitHubAgent; agent = JessicaGitHubAgent(repo_path='D:/Coding/Jessica')"
```

### "Could not connect to GitHub repo"

**Problem:** Remote URL not set or incorrect

**Solution:**
```powershell
# Check remote
git remote -v

# If missing, add it
git remote add origin https://github.com/yourusername/AGI.git

# If wrong, update it
git remote set-url origin https://github.com/yourusername/AGI.git
```

### "Permission denied (publickey)"

**Problem:** SSH key not configured

**Solution:**
```powershell
# Option 1: Use HTTPS instead
git remote set-url origin https://github.com/yourusername/AGI.git

# Option 2: Configure SSH key
# Follow: https://docs.github.com/en/authentication/connecting-to-github-with-ssh
```

### "Rate limit exceeded"

**Problem:** Too many API requests

**Solution:**
```python
# Check when limit resets
rate_info = agent.check_rate_limit()
print(f"Resets at: {rate_info['reset_time']}")

# Wait or reduce requests
```

---

## 📚 API Reference

### `JessicaGitHubAgent.__init__(...)`

Initialize the agent.

**Parameters:**
- `repo_path` (str, optional): Path to Git repository (default: Jessica's root)
- `github_token` (str, optional): GitHub PAT (default: from `JESSICA_GH_TOKEN` env var)
- `llm_router` (ModelRouter, optional): Jessica's LLM for intelligent analysis

### `triage_issues(...)`

Analyze and label issues.

**Parameters:**
- `state` (str): "open", "closed", or "all" (default: "open")
- `use_llm` (bool): Use LLM for analysis (default: True)
- `auto_label` (bool): Automatically apply labels (default: True)

**Returns:** List of issue dictionaries with analysis

### `create_feature_branch(...)`

Create a new feature branch.

**Parameters:**
- `issue_number` (int): GitHub issue number
- `base_branch` (str): Base branch to branch from (default: "main")

**Returns:** Dictionary with branch info and status

### `commit_evolution(...)`

Commit code improvements.

**Parameters:**
- `branch_name` (str): Branch to commit to
- `file_path` (str): Path to modified file (relative to repo root)
- `changes` (str): Description of changes
- `issue_number` (int, optional): Issue number to reference

**Returns:** Dictionary with commit info

### `submit_for_review(...)`

Open a Pull Request.

**Parameters:**
- `branch_name` (str): Feature branch name
- `base_branch` (str): Target branch (default: "main")
- `issue_number` (int, optional): Issue being addressed
- `watchdog_results` (dict, optional): Test results to include

**Returns:** Dictionary with PR info

### `check_rate_limit()`

Check GitHub API rate limit status.

**Returns:** Dictionary with rate limit info

### `get_status()`

Get current status of the agent.

**Returns:** Dictionary with connection status, branch info, etc.

---

## 🎓 Next Steps

1. **Install dependencies** and set up token
2. **Test the agent** with `python jessica\automation\github_agent.py`
3. **Integrate with Code Evolution** skill
4. **Set up automated workflows** (optional)
5. **Create your first autonomous PR!**

---

## 📞 Support

If you encounter issues:

1. Check **Troubleshooting** section above
2. Verify token permissions and expiration
3. Check Git repository setup (`git remote -v`)
4. Review error messages carefully

---

## 🏆 What's Next?

Potential enhancements:

- **Auto-Fix Simple Bugs:** Use LLM to generate fixes
- **Code Review Agent:** Comment on PRs with suggestions
- **Release Automation:** Auto-create releases from PRs
- **Issue Templates:** Auto-fill issue templates
- **Dependency Updates:** Auto-update requirements.txt

---

**Created:** January 13, 2026  
**Version:** 1.0  
**Status:** Production Ready  
**Integration:** Code Evolution Skill

🤖 **Jessica AI - Autonomous GitHub Agent**
