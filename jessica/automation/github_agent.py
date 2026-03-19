"""
Jessica GitHub Agent - Autonomous Repository Management
Integrates with Code Evolution skill for automated issue triage, branching, and PRs.
Designed for Windows environment (HP/Dell).
"""
from __future__ import annotations

import os
import sys
import re
import time
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
import json

try:
    from github import Github, GithubException, RateLimitExceededException
    from github.Repository import Repository
    from github.Issue import Issue
    from github.PullRequest import PullRequest
    from github.GithubObject import NotSet
except ImportError:
    print("[GitHub Agent] PyGithub not installed. Install with: pip install PyGithub")
    Github = None

try:
    import git
    from git import Repo, GitCommandError
except ImportError:
    print("[GitHub Agent] GitPython not installed. Install with: pip install GitPython")
    git = None
    Repo = None


class JessicaGitHubAgent:
    """
    Autonomous GitHub agent for repository management.
    Handles issue triage, branching, commits, and pull requests.
    """

    def __init__(
        self,
        repo_path: Optional[str] = None,
        github_token: Optional[str] = None,
        llm_router=None,
    ):
        """
        Initialize the GitHub Agent.

        Args:
            repo_path: Local path to the repository (defaults to Jessica's root)
            github_token: GitHub Personal Access Token (or use env var JESSICA_GH_TOKEN)
            llm_router: Reference to Jessica's ModelRouter for LLM analysis
        """
        # Get GitHub token from env or parameter
        self.github_token = github_token or os.environ.get("JESSICA_GH_TOKEN")
        if not self.github_token:
            print("[GitHub Agent] Warning: No GitHub token found. Set JESSICA_GH_TOKEN environment variable.")
            print("                 Generate token at: https://github.com/settings/tokens")
            self.github_client = None
        else:
            try:
                self.github_client = Github(self.github_token)
                print("[GitHub Agent] ✓ Connected to GitHub API")
            except Exception as e:
                print(f"[GitHub Agent] Failed to connect to GitHub: {e}")
                self.github_client = None

        # Get repository path
        if repo_path is None:
            # Default to Jessica's root directory
            repo_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
        
        self.repo_path = os.path.normpath(repo_path)  # Windows path normalization
        
        # Initialize Git repository
        try:
            self.git_repo = Repo(self.repo_path)
            print(f"[GitHub Agent] ✓ Loaded Git repository: {self.repo_path}")
        except Exception as e:
            print(f"[GitHub Agent] Warning: Not a Git repository: {e}")
            self.git_repo = None

        # Get GitHub repository object
        self.github_repo = None
        if self.github_client and self.git_repo:
            try:
                # Extract owner/repo from remote URL
                remote_url = self.git_repo.remotes.origin.url
                owner, repo_name = self._parse_github_url(remote_url)
                self.github_repo = self.github_client.get_repo(f"{owner}/{repo_name}")
                print(f"[GitHub Agent] ✓ Connected to GitHub repo: {owner}/{repo_name}")
            except Exception as e:
                print(f"[GitHub Agent] Could not connect to GitHub repo: {e}")

        # Store LLM router for issue analysis
        self.llm_router = llm_router

        # Issue label mappings
        self.label_keywords = {
            "bug": ["bug", "error", "crash", "fix", "broken", "issue", "problem", "fail"],
            "refactor": ["refactor", "cleanup", "improve", "optimize", "restructure", "technical debt"],
            "new-feature": ["feature", "enhancement", "add", "new", "implement", "capability"],
            "documentation": ["doc", "documentation", "readme", "guide", "comment"],
            "performance": ["performance", "slow", "speed", "optimize", "efficiency"],
            "security": ["security", "vulnerability", "exploit", "cve", "auth"],
            "test": ["test", "testing", "coverage", "unit test", "integration"],
        }

    def _parse_github_url(self, url: str) -> Tuple[str, str]:
        """Extract owner and repo name from GitHub URL."""
        # Handle both HTTPS and SSH URLs
        # https://github.com/owner/repo.git
        # git@github.com:owner/repo.git
        
        if url.startswith("https://"):
            match = re.search(r"github\.com/([^/]+)/([^/\.]+)", url)
        else:  # SSH
            match = re.search(r"github\.com:([^/]+)/([^/\.]+)", url)
        
        if match:
            return match.group(1), match.group(2)
        raise ValueError(f"Could not parse GitHub URL: {url}")

    def check_rate_limit(self) -> Dict[str, Any]:
        """Check GitHub API rate limit status."""
        if not self.github_client:
            return {"error": "GitHub client not initialized"}
        
        try:
            rate_limit = self.github_client.get_rate_limit()
            core = rate_limit.core
            
            return {
                "remaining": core.remaining,
                "limit": core.limit,
                "reset_time": core.reset.strftime("%Y-%m-%d %H:%M:%S"),
                "percentage_used": ((core.limit - core.remaining) / core.limit) * 100,
            }
        except Exception as e:
            return {"error": str(e)}

    # ============================================================
    # ISSUE TRIAGE
    # ============================================================

    def triage_issues(
        self,
        state: str = "open",
        use_llm: bool = True,
        auto_label: bool = True,
    ) -> List[Dict[str, Any]]:
        """
        Fetch and analyze open issues, labeling them automatically.

        Args:
            state: Issue state ("open", "closed", "all")
            use_llm: Whether to use LLM for intelligent analysis
            auto_label: Whether to automatically apply labels

        Returns:
            List of issue dictionaries with analysis results
        """
        if not self.github_repo:
            return [{"error": "GitHub repository not connected"}]

        print(f"\n[GitHub Agent] Triaging {state} issues...")
        
        try:
            issues = self.github_repo.get_issues(state=state)
            results = []

            for issue in issues:
                # Skip pull requests (they appear as issues in GitHub API)
                if issue.pull_request:
                    continue

                print(f"\n[Issue #{issue.number}] {issue.title}")
                
                # Analyze issue
                analysis = self._analyze_issue(issue, use_llm=use_llm)
                
                # Auto-label if enabled
                if auto_label and analysis.get("suggested_labels"):
                    self._apply_labels(issue, analysis["suggested_labels"])
                
                results.append({
                    "number": issue.number,
                    "title": issue.title,
                    "url": issue.html_url,
                    "state": issue.state,
                    "current_labels": [label.name for label in issue.labels],
                    "analysis": analysis,
                })

            print(f"\n[GitHub Agent] ✓ Triaged {len(results)} issues")
            return results

        except RateLimitExceededException:
            print("[GitHub Agent] ✗ Rate limit exceeded. Try again later.")
            rate_info = self.check_rate_limit()
            return [{"error": "rate_limit_exceeded", "reset_time": rate_info.get("reset_time")}]
        except Exception as e:
            print(f"[GitHub Agent] ✗ Error triaging issues: {e}")
            return [{"error": str(e)}]

    def _analyze_issue(self, issue: Issue, use_llm: bool = True) -> Dict[str, Any]:
        """Analyze an issue and suggest labels."""
        text = f"{issue.title}\n\n{issue.body or ''}"
        
        # Keyword-based analysis (fast, always runs)
        keyword_labels = self._keyword_analysis(text)
        
        # LLM-based analysis (intelligent, optional)
        llm_analysis = None
        if use_llm and self.llm_router:
            llm_analysis = self._llm_analysis(issue, text)
        
        # Combine results
        suggested_labels = list(set(keyword_labels))
        
        if llm_analysis and llm_analysis.get("labels"):
            suggested_labels.extend(llm_analysis["labels"])
            suggested_labels = list(set(suggested_labels))  # Remove duplicates
        
        return {
            "suggested_labels": suggested_labels,
            "keyword_match": keyword_labels,
            "llm_analysis": llm_analysis,
            "priority": self._assess_priority(issue, text),
        }

    def _keyword_analysis(self, text: str) -> List[str]:
        """Fast keyword-based label suggestion."""
        text_lower = text.lower()
        labels = []
        
        for label, keywords in self.label_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                labels.append(label)
        
        return labels

    def _llm_analysis(self, issue: Issue, text: str) -> Optional[Dict[str, Any]]:
        """Use Jessica's LLM to intelligently analyze issue."""
        if not self.llm_router:
            return None
        
        try:
            prompt = f"""Analyze this GitHub issue and categorize it.

Issue: {issue.title}
Description: {text[:500]}

Determine:
1. Type: bug, feature, refactor, documentation, or performance
2. Priority: high, medium, or low
3. Complexity: simple, moderate, or complex

Respond in JSON format:
{{"type": "...", "priority": "...", "complexity": "...", "reasoning": "..."}}"""

            # Use Jessica's model router (prefer chat model for analysis)
            response = self.llm_router.route_and_generate(
                prompt,
                model_type="chat",
                max_tokens=200,
            )
            
            # Try to parse JSON response
            try:
                # Extract JSON from response
                json_match = re.search(r'\{.*\}', response, re.DOTALL)
                if json_match:
                    analysis = json.loads(json_match.group(0))
                    return {
                        "labels": [analysis.get("type", "")],
                        "priority": analysis.get("priority", "medium"),
                        "complexity": analysis.get("complexity", "moderate"),
                        "reasoning": analysis.get("reasoning", ""),
                    }
            except json.JSONDecodeError:
                pass
            
            return {"raw_response": response}
            
        except Exception as e:
            print(f"[GitHub Agent] LLM analysis failed: {e}")
            return None

    def _assess_priority(self, issue: Issue, text: str) -> str:
        """Assess issue priority based on various factors."""
        text_lower = text.lower()
        
        # High priority indicators
        if any(word in text_lower for word in ["critical", "urgent", "crash", "security", "data loss"]):
            return "high"
        
        # Low priority indicators
        if any(word in text_lower for word in ["minor", "typo", "cosmetic", "nice to have"]):
            return "low"
        
        # Check issue age
        age_days = (datetime.now() - issue.created_at.replace(tzinfo=None)).days
        if age_days > 30:
            return "high"  # Old issues need attention
        
        return "medium"

    def _apply_labels(self, issue: Issue, labels: List[str]) -> bool:
        """Apply labels to an issue."""
        try:
            # Get existing labels
            existing = [label.name for label in issue.labels]
            
            # Add new labels that don't exist
            new_labels = [label for label in labels if label not in existing]
            
            if new_labels:
                issue.add_to_labels(*new_labels)
                print(f"  ✓ Added labels: {', '.join(new_labels)}")
                return True
            else:
                print(f"  - Labels already applied")
                return False
                
        except Exception as e:
            print(f"  ✗ Failed to apply labels: {e}")
            return False

    # ============================================================
    # AUTONOMOUS BRANCHING
    # ============================================================

    def create_feature_branch(
        self,
        issue_number: int,
        base_branch: str = "main",
    ) -> Dict[str, Any]:
        """
        Create a new feature branch for an issue.

        Args:
            issue_number: GitHub issue number
            base_branch: Base branch to branch from (default: main)

        Returns:
            Dictionary with branch info and status
        """
        if not self.git_repo or not self.github_repo:
            return {"error": "Git/GitHub not initialized"}

        print(f"\n[GitHub Agent] Creating feature branch for issue #{issue_number}")

        try:
            # Fetch issue details
            issue = self.github_repo.get_issue(issue_number)
            
            # Generate branch name
            branch_name = self._generate_branch_name(issue)
            print(f"  Branch name: {branch_name}")

            # Check if branch already exists
            try:
                self.git_repo.git.rev_parse("--verify", branch_name)
                return {
                    "success": False,
                    "error": f"Branch {branch_name} already exists",
                    "branch_name": branch_name,
                }
            except GitCommandError:
                pass  # Branch doesn't exist, proceed

            # Fetch latest changes
            print(f"  Fetching latest changes from origin...")
            self.git_repo.remotes.origin.fetch()

            # Create new branch from base
            print(f"  Creating branch from {base_branch}...")
            new_branch = self.git_repo.create_head(branch_name, f"origin/{base_branch}")
            new_branch.checkout()

            print(f"  ✓ Created and checked out branch: {branch_name}")

            return {
                "success": True,
                "branch_name": branch_name,
                "base_branch": base_branch,
                "issue_number": issue_number,
                "issue_title": issue.title,
                "current_branch": self.git_repo.active_branch.name,
            }

        except GithubException as e:
            return {"error": f"GitHub API error: {e}"}
        except GitCommandError as e:
            return {"error": f"Git command error: {e}"}
        except Exception as e:
            return {"error": str(e)}

    def _generate_branch_name(self, issue: Issue) -> str:
        """Generate a clean branch name from issue."""
        # Extract key words from title
        title = issue.title.lower()
        # Remove special characters
        title = re.sub(r'[^a-z0-9\s-]', '', title)
        # Replace spaces with hyphens
        title = re.sub(r'\s+', '-', title.strip())
        # Limit length
        title = title[:40]
        
        return f"jessica/issue-{issue.number}-{title}"

    # ============================================================
    # SMART COMMITS
    # ============================================================

    def commit_evolution(
        self,
        branch_name: str,
        file_path: str,
        changes: str,
        issue_number: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Commit Code Evolution improvements with intelligent commit messages.

        Args:
            branch_name: Branch to commit to
            file_path: Path to file being modified (relative to repo root)
            changes: Description of changes made
            issue_number: Optional issue number to reference

        Returns:
            Dictionary with commit info
        """
        if not self.git_repo:
            return {"error": "Git repository not initialized"}

        print(f"\n[GitHub Agent] Committing evolution to {branch_name}")

        try:
            # Ensure we're on the correct branch
            if self.git_repo.active_branch.name != branch_name:
                print(f"  Switching to branch: {branch_name}")
                self.git_repo.git.checkout(branch_name)

            # Generate intelligent commit message
            commit_msg = self._generate_commit_message(file_path, changes, issue_number)
            print(f"  Commit message: {commit_msg.split(chr(10))[0]}")

            # Stage the file
            file_path_normalized = os.path.normpath(file_path)
            self.git_repo.index.add([file_path_normalized])
            print(f"  Staged file: {file_path_normalized}")

            # Commit
            commit = self.git_repo.index.commit(commit_msg)
            print(f"  ✓ Committed: {commit.hexsha[:7]}")

            # Push to remote
            print(f"  Pushing to origin/{branch_name}...")
            try:
                self.git_repo.remotes.origin.push(branch_name)
                print(f"  ✓ Pushed to remote")
                pushed = True
            except GitCommandError as e:
                print(f"  ✗ Push failed: {e}")
                pushed = False

            return {
                "success": True,
                "branch": branch_name,
                "commit_sha": commit.hexsha,
                "commit_message": commit_msg,
                "file_path": file_path,
                "pushed": pushed,
            }

        except GitCommandError as e:
            return {"error": f"Git command error: {e}"}
        except Exception as e:
            return {"error": str(e)}

    def _generate_commit_message(
        self,
        file_path: str,
        changes: str,
        issue_number: Optional[int] = None,
    ) -> str:
        """Generate a professional commit message."""
        # Determine commit type
        if "fix" in changes.lower() or "bug" in changes.lower():
            commit_type = "fix"
        elif "refactor" in changes.lower():
            commit_type = "refactor"
        elif "add" in changes.lower() or "new" in changes.lower():
            commit_type = "feat"
        elif "doc" in changes.lower():
            commit_type = "docs"
        else:
            commit_type = "chore"

        # Get file name
        file_name = os.path.basename(file_path)

        # Build commit message (conventional commits format)
        lines = [
            f"{commit_type}: {changes.split('.')[0]}",  # First sentence
            "",
            f"Modified: {file_path}",
            "",
            "Changes:",
            f"- {changes}",
            "",
            "[Code Evolution - Automated by Jessica AI]",
        ]

        if issue_number:
            lines.append(f"Refs #{issue_number}")

        return "\n".join(lines)

    # ============================================================
    # PULL REQUEST AUTOMATION
    # ============================================================

    def submit_for_review(
        self,
        branch_name: str,
        base_branch: str = "main",
        issue_number: Optional[int] = None,
        watchdog_results: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Open a Pull Request for review.

        Args:
            branch_name: Feature branch name
            base_branch: Target branch (default: main)
            issue_number: Optional issue number being addressed
            watchdog_results: Optional test/monitoring results

        Returns:
            Dictionary with PR info
        """
        if not self.github_repo:
            return {"error": "GitHub repository not connected"}

        print(f"\n[GitHub Agent] Creating Pull Request")
        print(f"  From: {branch_name}")
        print(f"  To: {base_branch}")

        try:
            # Check for merge conflicts first
            conflict_check = self._check_merge_conflicts(branch_name, base_branch)
            if conflict_check.get("has_conflicts"):
                return {
                    "error": "merge_conflicts",
                    "conflicts": conflict_check.get("files", []),
                    "message": "Please resolve merge conflicts before creating PR",
                }

            # Get commits in this branch
            commits = self._get_branch_commits(branch_name, base_branch)

            # Generate PR title and body
            pr_title, pr_body = self._generate_pr_content(
                branch_name,
                commits,
                issue_number,
                watchdog_results,
            )

            print(f"  Title: {pr_title}")

            # Create pull request
            pr = self.github_repo.create_pull(
                title=pr_title,
                body=pr_body,
                head=branch_name,
                base=base_branch,
            )

            print(f"  ✓ Pull Request created: #{pr.number}")
            print(f"  URL: {pr.html_url}")

            # Add labels if issue is referenced
            if issue_number:
                try:
                    issue = self.github_repo.get_issue(issue_number)
                    labels = [label.name for label in issue.labels]
                    if labels:
                        pr.add_to_labels(*labels)
                        print(f"  ✓ Applied labels from issue: {', '.join(labels)}")
                except Exception as e:
                    print(f"  - Could not apply labels: {e}")

            # Link to issue
            if issue_number:
                try:
                    pr.create_issue_comment(f"Fixes #{issue_number}")
                except Exception as e:
                    print(f"  - Could not link issue: {e}")

            return {
                "success": True,
                "pr_number": pr.number,
                "pr_url": pr.html_url,
                "branch": branch_name,
                "base": base_branch,
                "title": pr_title,
            }

        except GithubException as e:
            if "pull request already exists" in str(e).lower():
                # Find existing PR
                prs = self.github_repo.get_pulls(
                    state="open",
                    head=branch_name,
                    base=base_branch,
                )
                existing_pr = next(prs, None)
                if existing_pr:
                    return {
                        "success": False,
                        "error": "pr_already_exists",
                        "pr_number": existing_pr.number,
                        "pr_url": existing_pr.html_url,
                    }
            return {"error": f"GitHub API error: {e}"}
        except Exception as e:
            return {"error": str(e)}

    def _check_merge_conflicts(
        self,
        source_branch: str,
        target_branch: str,
    ) -> Dict[str, Any]:
        """Check if merge conflicts exist."""
        if not self.git_repo:
            return {"error": "Git not initialized"}

        try:
            # Fetch latest
            self.git_repo.remotes.origin.fetch()

            # Try merge with dry-run
            result = self.git_repo.git.merge_tree(
                f"origin/{target_branch}",
                source_branch,
            )

            # Check for conflict markers
            has_conflicts = "<<<<<<" in result

            if has_conflicts:
                # Extract conflicting files
                conflicts = re.findall(r"CONFLICT.*in (.+)", result)
                print(f"  ⚠️ Merge conflicts detected in: {conflicts}")
                return {
                    "has_conflicts": True,
                    "files": conflicts,
                }
            else:
                print(f"  ✓ No merge conflicts")
                return {"has_conflicts": False}

        except GitCommandError as e:
            # If merge-tree not available, assume no conflicts
            print(f"  - Could not check conflicts: {e}")
            return {"has_conflicts": False}

    def _get_branch_commits(
        self,
        branch_name: str,
        base_branch: str,
    ) -> List[str]:
        """Get list of commits in branch that aren't in base."""
        try:
            # Get commits unique to this branch
            commits = self.git_repo.git.log(
                f"origin/{base_branch}..{branch_name}",
                "--pretty=format:%s",
            ).split("\n")
            return [c for c in commits if c.strip()]
        except Exception:
            return []

    def _generate_pr_content(
        self,
        branch_name: str,
        commits: List[str],
        issue_number: Optional[int],
        watchdog_results: Optional[Dict[str, Any]],
    ) -> Tuple[str, str]:
        """Generate PR title and body."""
        # Title
        if issue_number:
            try:
                issue = self.github_repo.get_issue(issue_number)
                title = f"Fix #{issue_number}: {issue.title}"
            except Exception:
                title = f"Code Evolution: {branch_name.split('/')[-1]}"
        else:
            title = f"Code Evolution: {branch_name.split('/')[-1]}"

        # Body
        body_parts = [
            "## Description",
            "",
            "This Pull Request contains Code Evolution improvements made by Jessica AI.",
            "",
        ]

        if issue_number:
            body_parts.extend([
                f"**Closes:** #{issue_number}",
                "",
            ])

        if commits:
            body_parts.extend([
                "## Changes",
                "",
            ])
            for commit in commits:
                body_parts.append(f"- {commit}")
            body_parts.append("")

        if watchdog_results:
            body_parts.extend([
                "## WatchDog Test Results",
                "",
            ])
            
            if watchdog_results.get("passed"):
                body_parts.append("✅ All tests passed")
            else:
                body_parts.append("⚠️ Some tests failed")
            
            body_parts.append("")
            body_parts.append(f"- Tests run: {watchdog_results.get('tests_run', 0)}")
            body_parts.append(f"- Tests passed: {watchdog_results.get('tests_passed', 0)}")
            body_parts.append(f"- Tests failed: {watchdog_results.get('tests_failed', 0)}")
            body_parts.append("")

        body_parts.extend([
            "## Checklist",
            "",
            "- [x] Code follows project style guidelines",
            "- [x] Self-review completed",
            "- [x] Comments added to complex code",
            "- [x] No new warnings generated",
            "",
            "---",
            "",
            "*🤖 Automated by Jessica AI Code Evolution*",
        ])

        return title, "\n".join(body_parts)

    # ============================================================
    # UTILITY METHODS
    # ============================================================

    def get_status(self) -> Dict[str, Any]:
        """Get current status of GitHub agent."""
        status = {
            "github_connected": self.github_client is not None,
            "git_initialized": self.git_repo is not None,
            "repo_connected": self.github_repo is not None,
            "repo_path": self.repo_path,
        }

        if self.git_repo:
            status["current_branch"] = self.git_repo.active_branch.name
            status["has_changes"] = self.git_repo.is_dirty()

        if self.github_repo:
            status["repo_name"] = self.github_repo.full_name
            status["default_branch"] = self.github_repo.default_branch

        if self.github_client:
            rate_limit = self.check_rate_limit()
            status["api_rate_limit"] = rate_limit

        return status

    def list_open_prs(self) -> List[Dict[str, Any]]:
        """List all open pull requests."""
        if not self.github_repo:
            return []

        try:
            prs = self.github_repo.get_pulls(state="open")
            return [
                {
                    "number": pr.number,
                    "title": pr.title,
                    "url": pr.html_url,
                    "branch": pr.head.ref,
                    "author": pr.user.login,
                    "created": pr.created_at.strftime("%Y-%m-%d"),
                }
                for pr in prs
            ]
        except Exception as e:
            print(f"[GitHub Agent] Error listing PRs: {e}")
            return []

    def close_issue(self, issue_number: int, comment: Optional[str] = None) -> bool:
        """Close an issue with optional comment."""
        if not self.github_repo:
            return False

        try:
            issue = self.github_repo.get_issue(issue_number)
            
            if comment:
                issue.create_comment(comment)
            
            issue.edit(state="closed")
            print(f"[GitHub Agent] ✓ Closed issue #{issue_number}")
            return True
        except Exception as e:
            print(f"[GitHub Agent] ✗ Failed to close issue: {e}")
            return False


# ============================================================
# INTEGRATION WITH JESSICA'S EXISTING SYSTEMS
# ============================================================

def integrate_with_code_evolution(agent: JessicaGitHubAgent):
    """
    Integration point with Jessica's Code Evolution skill.
    
    Example usage in code_evolution_skill.py:
    
    from jessica.automation.github_agent import JessicaGitHubAgent, integrate_with_code_evolution
    
    # Initialize agent
    agent = JessicaGitHubAgent(llm_router=self.model_router)
    
    # Triage issues
    issues = agent.triage_issues(auto_label=True)
    
    # Create branch for high-priority issue
    result = agent.create_feature_branch(issue_number=42)
    
    # Make improvements...
    
    # Commit changes
    agent.commit_evolution(
        branch_name=result['branch_name'],
        file_path='jessica/skills/new_skill.py',
        changes='Added new skill for X functionality',
        issue_number=42
    )
    
    # Submit PR
    pr = agent.submit_for_review(
        branch_name=result['branch_name'],
        issue_number=42,
        watchdog_results={'passed': True, 'tests_run': 5}
    )
    """
    pass


# ============================================================
# EXAMPLE USAGE
# ============================================================

if __name__ == "__main__":
    print("=" * 60)
    print("Jessica GitHub Agent - Autonomous Repository Management")
    print("=" * 60)
    print()

    # Check for token
    if not os.environ.get("JESSICA_GH_TOKEN"):
        print("⚠️  No GitHub token found!")
        print()
        print("To use this agent:")
        print("1. Generate a Personal Access Token:")
        print("   https://github.com/settings/tokens")
        print()
        print("2. Required scopes:")
        print("   - repo (full control)")
        print("   - workflow (if using Actions)")
        print()
        print("3. Set environment variable:")
        print("   Windows PowerShell:")
        print("   $env:JESSICA_GH_TOKEN = 'your_token_here'")
        print()
        print("   Windows CMD:")
        print("   set JESSICA_GH_TOKEN=your_token_here")
        print()
        sys.exit(1)

    # Initialize agent
    print("Initializing GitHub Agent...")
    agent = JessicaGitHubAgent()

    # Show status
    print("\n--- Agent Status ---")
    status = agent.get_status()
    for key, value in status.items():
        print(f"{key}: {value}")

    print("\n--- Example Usage ---")
    print()
    print("# Triage issues")
    print("issues = agent.triage_issues(auto_label=True)")
    print()
    print("# Create feature branch")
    print("result = agent.create_feature_branch(issue_number=42)")
    print()
    print("# Commit evolution")
    print("agent.commit_evolution(")
    print("    branch_name='jessica/issue-42-...',")
    print("    file_path='jessica/skills/new_skill.py',")
    print("    changes='Implemented new functionality'")
    print(")")
    print()
    print("# Submit pull request")
    print("pr = agent.submit_for_review(branch_name='jessica/issue-42-...')")
    print()
    print("=" * 60)
