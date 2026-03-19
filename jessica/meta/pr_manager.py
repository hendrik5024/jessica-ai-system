"""
Pull Request Manager - Handles self-improvement pull requests.

Workflow:
1. Create PR from improvement suggestions
2. Run safety gate (Self-Simulation)
3. If approved: Apply changes with backup
4. Run verification tests
5. If tests pass: Commit changes
6. If tests fail: Automatic rollback
7. Log results to autodidactic loop

This is the core loop for recursive self-code improvement (Singularity Loop).
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple
from enum import Enum
from datetime import datetime
import os
import shutil
import json
from pathlib import Path


class PRStatus(Enum):
    """Pull request lifecycle status."""
    CREATED = "created"            # Just created
    SAFETY_REVIEW = "safety_review"  # Awaiting safety gate
    APPROVED = "approved"          # Safety gate passed
    REJECTED = "rejected"          # Safety gate failed
    APPLYING = "applying"          # Applying changes
    TESTING = "testing"            # Running tests
    PASSED = "passed"              # All tests passed
    FAILED = "failed"              # Tests failed
    ROLLED_BACK = "rolled_back"    # Rolled back after failure
    COMMITTED = "committed"        # Merged and committed


@dataclass
class AppliedChange:
    """Record of a single applied code change."""
    file_path: str
    line_range: Tuple[int, int]
    backup_created: bool
    backup_path: str = ""
    original_hash: str = ""        # Hash of original code
    new_hash: str = ""             # Hash of new code
    applied_at: datetime = field(default_factory=datetime.now)
    rollback_successful: bool = False


@dataclass
class PRExecutionLog:
    """Complete log of PR execution."""
    pr_id: str
    status: PRStatus
    created_at: datetime
    completed_at: Optional[datetime]
    applied_changes: List[AppliedChange] = field(default_factory=list)
    test_results: Dict = field(default_factory=dict)
    performance_before: Dict = field(default_factory=dict)
    performance_after: Dict = field(default_factory=dict)
    performance_improvement: float = 0.0  # Speedup factor achieved
    errors: List[str] = field(default_factory=list)
    lessons_learned: List[str] = field(default_factory=list)


class PRManager:
    """Manages self-improvement pull requests through their lifecycle."""
    
    def __init__(self, jessica_root: str, pr_log_dir: str = ".jessica/pr_logs"):
        self.jessica_root = jessica_root
        self.pr_log_dir = os.path.join(jessica_root, pr_log_dir)
        os.makedirs(self.pr_log_dir, exist_ok=True)
        
        self.backup_dir = os.path.join(jessica_root, ".jessica/backups")
        os.makedirs(self.backup_dir, exist_ok=True)
    
    def create_pr_from_improvements(self, improvements) -> 'PullRequest':
        """Create a PR from improvement suggestions."""
        from improvement_generator import PullRequest
        return improvements
    
    def apply_changes(self, pull_request, dry_run: bool = False) -> PRExecutionLog:
        """
        Apply code changes from the pull request.
        
        Args:
            pull_request: The PR to apply
            dry_run: If True, don't actually modify files (for testing)
        
        Returns: Execution log
        """
        
        log = PRExecutionLog(
            pr_id=pull_request.pr_id,
            status=PRStatus.APPLYING,
            created_at=datetime.now(),
            completed_at=None,
        )
        
        # Create backup of all affected files
        backup_ids = {}
        for change in pull_request.changes:
            file_path = os.path.join(self.jessica_root, change.file_path)
            
            if not os.path.exists(file_path):
                log.errors.append(f"File not found: {change.file_path}")
                continue
            
            # Create backup
            backup_id = self._create_backup(file_path, pull_request.pr_id)
            backup_ids[change.file_path] = backup_id
        
        # Apply changes
        for change in pull_request.changes:
            file_path = os.path.join(self.jessica_root, change.file_path)
            
            try:
                applied = self._apply_single_change(
                    file_path,
                    change,
                    dry_run=dry_run
                )
                log.applied_changes.append(applied)
            except Exception as e:
                log.errors.append(f"Error applying change to {change.file_path}: {str(e)}")
                log.status = PRStatus.FAILED
                break
        
        log.status = PRStatus.TESTING if len(log.applied_changes) > 0 else PRStatus.FAILED
        return log
    
    def _create_backup(self, file_path: str, pr_id: str) -> str:
        """Create a backup of a file before modification."""
        backup_id = f"{pr_id}_{os.path.basename(file_path)}_{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        backup_path = os.path.join(self.backup_dir, backup_id)
        
        shutil.copy2(file_path, backup_path)
        return backup_id
    
    def _apply_single_change(self, file_path: str, change, 
                            dry_run: bool = False) -> AppliedChange:
        """Apply a single code change to a file."""
        
        with open(file_path, 'r') as f:
            original_content = f.read()
            original_hash = self._hash_content(original_content)
        
        # Parse file and apply change
        lines = original_content.split('\n')
        start_line, end_line = change.line_range
        
        # Replace lines
        new_lines = (
            lines[:start_line-1] +
            change.improved_code.split('\n') +
            lines[end_line:]
        )
        new_content = '\n'.join(new_lines)
        new_hash = self._hash_content(new_content)
        
        # Write back (unless dry run)
        if not dry_run:
            with open(file_path, 'w') as f:
                f.write(new_content)
        
        return AppliedChange(
            file_path=change.file_path,
            line_range=change.line_range,
            backup_created=True,
            original_hash=original_hash,
            new_hash=new_hash,
        )
    
    def _hash_content(self, content: str) -> str:
        """Create a hash of file content for integrity checking."""
        import hashlib
        return hashlib.sha256(content.encode()).hexdigest()[:16]
    
    def run_tests(self, pr_execution_log: PRExecutionLog, 
                 test_suite: str = "pytest tests/ -v") -> Tuple[bool, Dict]:
        """
        Run test suite to verify changes don't break anything.
        
        Returns: (tests_passed: bool, test_results: dict)
        """
        import subprocess
        
        try:
            result = subprocess.run(
                test_suite.split(),
                cwd=self.jessica_root,
                capture_output=True,
                timeout=300,
                text=True
            )
            
            tests_passed = result.returncode == 0
            
            test_results = {
                'return_code': result.returncode,
                'stdout': result.stdout[-1000:] if result.stdout else "",  # Last 1000 chars
                'stderr': result.stderr[-1000:] if result.stderr else "",
                'timestamp': datetime.now().isoformat(),
            }
            
            pr_execution_log.test_results = test_results
            pr_execution_log.status = PRStatus.PASSED if tests_passed else PRStatus.FAILED
            
            return tests_passed, test_results
        
        except subprocess.TimeoutExpired:
            pr_execution_log.errors.append("Test suite timeout (5 min)")
            pr_execution_log.status = PRStatus.FAILED
            return False, {'timeout': True}
        
        except Exception as e:
            pr_execution_log.errors.append(f"Test execution error: {str(e)}")
            pr_execution_log.status = PRStatus.FAILED
            return False, {'error': str(e)}
    
    def rollback_changes(self, pr_execution_log: PRExecutionLog,
                        backup_ids: Dict) -> bool:
        """Rollback applied changes in case of failure."""
        
        try:
            for change in pr_execution_log.applied_changes:
                file_path = os.path.join(self.jessica_root, change.file_path)
                
                # Find corresponding backup
                for backup_id in backup_ids.values():
                    if os.path.basename(change.file_path) in backup_id:
                        backup_path = os.path.join(self.backup_dir, backup_id)
                        if os.path.exists(backup_path):
                            shutil.copy2(backup_path, file_path)
                            change.rollback_successful = True
                            break
            
            pr_execution_log.status = PRStatus.ROLLED_BACK
            return True
        
        except Exception as e:
            pr_execution_log.errors.append(f"Rollback failed: {str(e)}")
            return False
    
    def commit_pr(self, pr_execution_log: PRExecutionLog) -> bool:
        """
        Commit the changes to the codebase.
        
        In a real Git scenario, this would create a commit.
        Here we just mark it as committed in the log.
        """
        
        pr_execution_log.status = PRStatus.COMMITTED
        pr_execution_log.completed_at = datetime.now()
        
        # Save execution log
        self._save_pr_log(pr_execution_log)
        
        return True
    
    def _save_pr_log(self, log: PRExecutionLog):
        """Save PR execution log to disk."""
        
        log_path = os.path.join(self.pr_log_dir, f"{log.pr_id}.json")
        
        log_dict = {
            'pr_id': log.pr_id,
            'status': log.status.value,
            'created_at': log.created_at.isoformat(),
            'completed_at': log.completed_at.isoformat() if log.completed_at else None,
            'applied_changes': [
                {
                    'file_path': c.file_path,
                    'line_range': c.line_range,
                    'backup_created': c.backup_created,
                    'original_hash': c.original_hash,
                    'new_hash': c.new_hash,
                }
                for c in log.applied_changes
            ],
            'test_results': log.test_results,
            'errors': log.errors,
            'lessons_learned': log.lessons_learned,
        }
        
        with open(log_path, 'w') as f:
            json.dump(log_dict, f, indent=2)
    
    def get_pr_history(self) -> List[PRExecutionLog]:
        """Get history of all self-improvement PRs."""
        
        logs = []
        for log_file in os.listdir(self.pr_log_dir):
            if log_file.endswith('.json'):
                with open(os.path.join(self.pr_log_dir, log_file), 'r') as f:
                    log_dict = json.load(f)
                    # TODO: Convert back to PRExecutionLog objects
                    logs.append(log_dict)
        
        return logs


def execute_self_improvement(pull_request, jessica_root: str,
                            safety_gate_fn = None) -> Tuple[bool, PRExecutionLog]:
    """
    Execute a complete self-improvement pull request.
    
    Workflow:
    1. Safety gate (using Self-Simulation)
    2. Apply changes with backup
    3. Run tests
    4. On failure: rollback
    5. On success: commit
    
    Returns: (success: bool, execution_log: PRExecutionLog)
    """
    
    manager = PRManager(jessica_root)
    
    # 1. Safety gate
    if safety_gate_fn:
        approved, impact = safety_gate_fn(pull_request)
        if not approved:
            log = PRExecutionLog(
                pr_id=pull_request.pr_id,
                status=PRStatus.REJECTED,
                created_at=datetime.now(),
                completed_at=datetime.now(),
            )
            log.errors.append(f"Rejected by safety gate: {impact.reasoning}")
            return False, log
    
    # 2. Apply changes
    log = manager.apply_changes(pull_request, dry_run=False)
    if log.status == PRStatus.FAILED:
        return False, log
    
    # 3. Run tests
    tests_passed, test_results = manager.run_tests(log)
    
    if not tests_passed:
        # 4. Rollback on failure
        print(f"Tests failed, rolling back PR {pull_request.pr_id}...")
        manager.rollback_changes(log, {})
        return False, log
    
    # 5. Commit on success
    manager.commit_pr(log)
    
    return True, log
